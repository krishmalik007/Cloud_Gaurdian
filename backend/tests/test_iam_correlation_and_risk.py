"""
Regression and Verification Test Suite: IAM Correlation and Risk Scoring
========================================================================

Verifies:
1. `CreatePolicyVersion` correctly matches `IAM_POLICY_CHANGED`.
2. `GetPolicy` and `ListPolicies` do not trigger `IAM_POLICY_CHANGED`.
3. Non-administrative policy attachment does not trigger `IAM_PRIVILEGE_ESCALATION`.
4. Administrative policy attachment triggers `IAM_PRIVILEGE_ESCALATION` only when conditions are satisfied.
5. Root identity fields are correctly parsed and evaluated by `ROOT_ACCOUNT_USAGE` (ConsoleLogin vs API calls).
6. Matching correlation alert contributes to risk scoring correctly (MEDIUM -> MEDIUM, CRITICAL -> CRITICAL, no alerts -> 0).
7. Existing unrelated correlation rules and normalizations remain intact.
"""

from datetime import datetime, timezone
import pytest

from app.normalizer.aws import aws_normalizer
from app.correlation.correlation_engine import correlation_engine
from app.correlation.rules import iam_rules
from app.risk.risk_engine import risk_engine
from app.pipeline.incident_pipeline import incident_pipeline


@pytest.fixture(autouse=True)
def clean_event_store():
    """Ensure correlation engine event store is clean before and after each test."""
    correlation_engine.event_store.clear()
    yield
    correlation_engine.event_store.clear()


# ==============================================================================
# 1. CreatePolicyVersion correctly matches IAM_POLICY_CHANGED
# ==============================================================================

def test_01_create_policy_version_matches_iam_policy_changed():
    """
    Verified test event:
    - AWS event name: CreatePolicyVersion
    - Event source: iam.amazonaws.com
    - Policy ARN: arn:aws:iam::195236889241:policy/CloudGuardian-Correlation-Test
    - Actor identity type: Root
    - MFA authenticated: true
    Must trigger IAM_POLICY_CHANGED (MEDIUM), but NOT IAM_PRIVILEGE_ESCALATION or ROOT_ACCOUNT_USAGE.
    """
    event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "Root",
            "principalId": "195236889241",
            "arn": "arn:aws:iam::195236889241:root",
            "accountId": "195236889241",
            "userName": "root"
        },
        "eventTime": "2026-10-22T03:00:00Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "CreatePolicyVersion",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.1",
        "userAgent": "aws-cli/2.15.0",
        "requestParameters": {
            "policyArn": "arn:aws:iam::195236889241:policy/CloudGuardian-Correlation-Test",
            "policyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"sts:GetCallerIdentity\",\"Resource\":\"*\"}]}",
            "setAsDefault": True
        },
        "additionalEventData": {
            "MFAUsed": "Yes"
        },
        "readOnly": False,
        "eventID": "evt-create-policy-version-001",
        "provider": "AWS"
    }

    normalized = aws_normalizer.normalize(event)
    assert normalized["event_name"] == "CreatePolicyVersion"
    assert normalized["event_type"] == "UPDATE_POLICY"
    assert normalized["username"] == "root"

    alerts = correlation_engine.process_event(normalized)
    alert_types = [a["alert_type"] for a in alerts]

    # Must trigger IAM_POLICY_CHANGED
    assert "IAM_POLICY_CHANGED" in alert_types

    policy_alert = next(a for a in alerts if a["alert_type"] == "IAM_POLICY_CHANGED")
    assert policy_alert["severity"] == "MEDIUM"

    # Must NOT trigger privilege escalation (permissions were restricted to sts:GetCallerIdentity)
    assert "IAM_PRIVILEGE_ESCALATION" not in alert_types

    # Must NOT trigger root login usage (it is an API call, not a console login)
    assert "ROOT_ACCOUNT_USAGE" not in alert_types


# ==============================================================================
# 2. GetPolicy and ListPolicies do not trigger IAM_POLICY_CHANGED
# ==============================================================================

def test_02_read_only_iam_events_do_not_trigger_policy_changed():
    """
    Read-only inspection API calls like GetPolicy and ListPolicies
    must NOT trigger IAM_POLICY_CHANGED.
    """
    for event_name in ["GetPolicy", "ListPolicies", "GetPolicyVersion", "ListAttachedUserPolicies"]:
        event = {
            "eventVersion": "1.08",
            "userIdentity": {
                "type": "IAMUser",
                "userName": "auditor"
            },
            "eventTime": "2026-10-22T03:05:00Z",
            "eventSource": "iam.amazonaws.com",
            "eventName": event_name,
            "awsRegion": "us-east-1",
            "sourceIPAddress": "198.51.100.2",
            "readOnly": True,
            "eventID": f"evt-ro-{event_name}",
            "provider": "AWS"
        }

        normalized = aws_normalizer.normalize(event)
        alerts = correlation_engine.process_event(normalized)
        alert_types = [a["alert_type"] for a in alerts]

        assert "IAM_POLICY_CHANGED" not in alert_types
        assert len(alerts) == 0


# ==============================================================================
# 3. Non-administrative policy attachment does not trigger IAM_PRIVILEGE_ESCALATION
# ==============================================================================

def test_03_non_administrative_policy_attachment_no_privilege_escalation():
    """
    Attaching a standard non-admin policy (e.g. AmazonS3ReadOnlyAccess or custom restricted policy)
    must trigger IAM_POLICY_CHANGED, but must NOT trigger IAM_PRIVILEGE_ESCALATION.
    """
    event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "userName": "lead-dev"
        },
        "eventTime": "2026-10-22T03:10:00Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "AttachUserPolicy",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.3",
        "requestParameters": {
            "userName": "junior-dev",
            "policyArn": "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        },
        "readOnly": False,
        "eventID": "evt-attach-non-admin-001",
        "provider": "AWS"
    }

    normalized = aws_normalizer.normalize(event)
    assert normalized["event_type"] == "ATTACH_POLICY"

    alerts = correlation_engine.process_event(normalized)
    alert_types = [a["alert_type"] for a in alerts]

    assert "IAM_POLICY_CHANGED" in alert_types
    assert "IAM_PRIVILEGE_ESCALATION" not in alert_types


# ==============================================================================
# 4. Administrative policy attachment triggers IAM_PRIVILEGE_ESCALATION
# ==============================================================================

def test_04_administrative_policy_attachment_triggers_privilege_escalation():
    """
    Attaching AdministratorAccess policy must trigger IAM_PRIVILEGE_ESCALATION (CRITICAL)
    as well as IAM_POLICY_CHANGED (MEDIUM).
    """
    event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "userName": "bad-actor"
        },
        "eventTime": "2026-10-22T03:15:00Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "AttachUserPolicy",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.4",
        "requestParameters": {
            "userName": "target-user",
            "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        "readOnly": False,
        "eventID": "evt-attach-admin-001",
        "provider": "AWS"
    }

    normalized = aws_normalizer.normalize(event)
    assert normalized["event_type"] == "ATTACH_ADMIN_POLICY"

    alerts = correlation_engine.process_event(normalized)
    alert_types = [a["alert_type"] for a in alerts]

    assert "IAM_PRIVILEGE_ESCALATION" in alert_types
    assert "IAM_POLICY_CHANGED" in alert_types

    priv_alert = next(a for a in alerts if a["alert_type"] == "IAM_PRIVILEGE_ESCALATION")
    assert priv_alert["severity"] == "CRITICAL"


# ==============================================================================
# 5. Root identity fields parsed and evaluated by ROOT_ACCOUNT_USAGE
# ==============================================================================

def test_05_root_identity_fields_and_root_account_usage():
    """
    5A. Real Root ConsoleLogin triggers ROOT_ACCOUNT_USAGE (CRITICAL).
    5B. Root ConsoleLogin with MFA authenticated still triggers ROOT_ACCOUNT_USAGE.
    5C. API request by Root (e.g. CreatePolicyVersion, DescribeInstances) does NOT trigger ROOT_ACCOUNT_USAGE.
    """
    # 5A: Root ConsoleLogin without MFA
    root_login_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "Root",
            "principalId": "195236889241",
            "arn": "arn:aws:iam::195236889241:root",
            "accountId": "195236889241"
        },
        "eventTime": "2026-10-22T03:20:00Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.5",
        "responseElements": {
            "ConsoleLogin": "Success"
        },
        "readOnly": False,
        "eventID": "evt-root-login-001",
        "provider": "AWS"
    }

    norm_root_login = aws_normalizer.normalize(root_login_event)
    assert norm_root_login["username"] == "root"
    assert norm_root_login["event_type"] == "ROOT_LOGIN"

    alerts_login = correlation_engine.process_event(norm_root_login)
    alert_types_login = [a["alert_type"] for a in alerts_login]
    assert "ROOT_ACCOUNT_USAGE" in alert_types_login
    root_alert = next(a for a in alerts_login if a["alert_type"] == "ROOT_ACCOUNT_USAGE")
    assert root_alert["severity"] == "CRITICAL"

    correlation_engine.event_store.clear()

    # 5B: Root ConsoleLogin with MFA authenticated
    root_login_mfa_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "Root",
            "principalId": "195236889241",
            "arn": "arn:aws:iam::195236889241:root",
            "accountId": "195236889241",
            "userName": "root"
        },
        "eventTime": "2026-10-22T03:21:00Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.6",
        "responseElements": {
            "ConsoleLogin": "Success"
        },
        "additionalEventData": {
            "MFAUsed": "Yes"
        },
        "readOnly": False,
        "eventID": "evt-root-login-mfa-002",
        "provider": "AWS"
    }

    norm_root_mfa = aws_normalizer.normalize(root_login_mfa_event)
    alerts_mfa = correlation_engine.process_event(norm_root_mfa)
    alert_types_mfa = [a["alert_type"] for a in alerts_mfa]
    assert "ROOT_ACCOUNT_USAGE" in alert_types_mfa

    correlation_engine.event_store.clear()

    # 5C: Non-login API call by root (e.g. DescribeInstances) must NOT trigger ROOT_ACCOUNT_USAGE
    root_api_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "Root",
            "principalId": "195236889241",
            "arn": "arn:aws:iam::195236889241:root",
            "accountId": "195236889241"
        },
        "eventTime": "2026-10-22T03:22:00Z",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "DescribeInstances",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.7",
        "readOnly": True,
        "eventID": "evt-root-api-003",
        "provider": "AWS"
    }

    norm_root_api = aws_normalizer.normalize(root_api_event)
    alerts_api = correlation_engine.process_event(norm_root_api)
    alert_types_api = [a["alert_type"] for a in alerts_api]
    assert "ROOT_ACCOUNT_USAGE" not in alert_types_api


# ==============================================================================
# 6. Matching correlation alert contributes to risk scoring correctly
# ==============================================================================

def test_06_matching_correlation_alert_contributes_to_risk_scoring():
    """
    Risk scoring engine must:
    - Return score=0, level='LOW' when no alerts and no IOCs exist.
    - Return MEDIUM level (score >= 40) when an IAM_POLICY_CHANGED alert is present.
    - Return CRITICAL level (score >= 80) when an IAM_PRIVILEGE_ESCALATION alert is present.
    - Pipeline evaluation reflects consistent incident priority and risk score.
    """
    # 6A: Routine event with no alerts -> score 0, level LOW
    no_alert_event = {"provider": "AWS", "username": "auditor"}
    risk_none = risk_engine.calculate_risk(no_alert_event, [])
    assert risk_none["score"] == 0
    assert risk_none["level"] == "LOW"

    # 6B: Event with IAM_POLICY_CHANGED alert (MEDIUM)
    medium_alert = [{
        "alert_type": "IAM_POLICY_CHANGED",
        "severity": "MEDIUM",
        "username": "root"
    }]
    risk_medium = risk_engine.calculate_risk(no_alert_event, medium_alert)
    assert risk_medium["score"] >= 40
    assert risk_medium["level"] == "MEDIUM"

    # 6C: Event with IAM_PRIVILEGE_ESCALATION alert (CRITICAL)
    critical_alert = [{
        "alert_type": "IAM_PRIVILEGE_ESCALATION",
        "severity": "CRITICAL",
        "username": "attacker"
    }]
    risk_critical = risk_engine.calculate_risk(no_alert_event, critical_alert)
    assert risk_critical["score"] >= 80
    assert risk_critical["level"] == "CRITICAL"

    # 6D: End-to-end through incident pipeline for CreatePolicyVersion event
    test_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "Root",
            "principalId": "195236889241",
            "arn": "arn:aws:iam::195236889241:root",
            "accountId": "195236889241",
            "userName": "root"
        },
        "eventTime": "2026-10-22T03:30:00Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "CreatePolicyVersion",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.8",
        "requestParameters": {
            "policyArn": "arn:aws:iam::195236889241:policy/CloudGuardian-Correlation-Test",
            "setAsDefault": True
        },
        "readOnly": False,
        "eventID": "evt-cpv-pipeline-001",
        "provider": "AWS"
    }

    result = incident_pipeline.process_event(test_event)
    assert result["is_incident"] is True
    assert result["priority"] == "MEDIUM"
    assert result["risk_level"] == "MEDIUM"
    assert result["risk_score"] >= 40
    alert_types_in_incident = [a["alert_type"] for a in result["alerts"]]
    assert "IAM_POLICY_CHANGED" in alert_types_in_incident


# ==============================================================================
# 7. Unrelated correlation rules and event processing remain unchanged
# ==============================================================================

def test_07_unrelated_rules_and_event_processing_remain_unchanged():
    """
    Ensure other IAM rules (CREATE_ADMIN_USER, DISABLE_MFA, CREATE_ACCESS_KEY)
    and non-IAM normalizations continue to function as expected.
    """
    # 7A: CREATE_ADMIN_USER
    admin_user_event = {
        "username": "sec-admin",
        "provider": "AWS",
        "event_type": "CREATE_ADMIN_USER",
        "timestamp": datetime.now(timezone.utc)
    }
    alerts = correlation_engine.process_event(admin_user_event)
    assert any(a["alert_type"] == "NEW_ADMIN_USER" for a in alerts)

    correlation_engine.event_store.clear()

    # 7B: DISABLE_MFA
    mfa_event = {
        "username": "user1",
        "provider": "AWS",
        "event_type": "DISABLE_MFA",
        "timestamp": datetime.now(timezone.utc)
    }
    alerts = correlation_engine.process_event(mfa_event)
    assert any(a["alert_type"] == "MFA_DISABLED" for a in alerts)

    correlation_engine.event_store.clear()

    # 7C: CREATE_ACCESS_KEY
    key_event = {
        "username": "user2",
        "provider": "AWS",
        "event_type": "CREATE_ACCESS_KEY",
        "timestamp": datetime.now(timezone.utc)
    }
    alerts = correlation_engine.process_event(key_event)
    assert any(a["alert_type"] == "ACCESS_KEY_CREATED" for a in alerts)

    # 7D: Non-IAM service event normalization
    ec2_event = {
        "eventName": "RunInstances",
        "eventSource": "ec2.amazonaws.com",
        "provider": "AWS"
    }
    norm_ec2 = aws_normalizer.normalize(ec2_event)
    assert norm_ec2["event_type"] == "COMPUTE"
