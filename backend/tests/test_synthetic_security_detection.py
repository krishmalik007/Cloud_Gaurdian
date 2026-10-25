"""
Automated Security Detection Verification Suite: Synthetic CloudTrail Events
=============================================================================

Validates the security detection pipeline behavior using isolated synthetic
CloudTrail events without making live AWS calls, changing IAM policies,
or accessing external infrastructure.

Scenarios verified:
1. An AWS AccessDenied event (e.g. CloudGuardianS3IngestionUser calling ec2:DescribeVpcs)
   is normalized and evaluated correctly.
2. The event is stored in the OpenSearch `events` repository.
3. It does NOT automatically become a high-severity incident merely because it contains
   an AccessDenied error.
4. A separate synthetic high-risk event triggers an incident when existing detection rules justify it.
5. The created incident is retrievable through the existing FastAPI incidents API.
6. Duplicate delivery of an event does not create duplicate incidents or redundant notifications.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.auth.jwt_handler import create_access_token
from app.main import app
from app.normalizer.aws import aws_normalizer
from app.pipeline.incident_pipeline import incident_pipeline
from app.services.event_service import EventService
from app.services.log_processor import LogProcessor
from app.storage.event_repository import EventRepository
from app.storage.incident_repository import IncidentRepository


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def test_client():
    """Isolated FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def analyst_headers():
    """JWT Bearer headers with ANALYST role."""
    token = create_access_token({
        "user_id": "USR-synthetic-analyst-01",
        "username": "security_analyst",
        "role": "ANALYST",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def synthetic_access_denied_event():
    """
    Synthetic CloudTrail event representing an AccessDenied failure.
    Simulates CloudGuardianS3IngestionUser attempting ec2:DescribeVpcs without permissions.
    """
    return {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAJEXAMPLEUSER12345",
            "arn": "arn:aws:iam::195236889241:user/CloudGuardianS3IngestionUser",
            "accountId": "195236889241",
            "accessKeyId": "AKIAS25IGQKM4FZYJX5K",
            "userName": "CloudGuardianS3IngestionUser"
        },
        "eventTime": "2026-10-20T13:40:00Z",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "DescribeVpcs",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "203.0.113.19",
        "userAgent": "aws-cli/2.15.0 Python/3.11.6 Windows/10 exe/AMD64 prompt/off",
        "errorCode": "AccessDenied",
        "errorMessage": "User: arn:aws:iam::195236889241:user/CloudGuardianS3IngestionUser is not authorized to perform: ec2:DescribeVpcs because no identity-based policy allows the ec2:DescribeVpcs action",
        "requestParameters": None,
        "responseElements": None,
        "requestID": "synthetic-access-denied-req-001",
        "eventID": "synthetic-access-denied-evt-001",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }


@pytest.fixture
def synthetic_high_risk_event():
    """
    Synthetic CloudTrail event representing a genuine high-risk security threat:
    An unauthorized attempt to attach the AdministratorAccess policy originating
    from a known malicious C2 IP.
    """
    return {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAINFILTRATOR9999",
            "arn": "arn:aws:iam::195236889241:user/infiltrator-user",
            "accountId": "195236889241",
            "accessKeyId": "AKIAEXAMPLEINFILTRATE",
            "userName": "infiltrator-user"
        },
        "eventTime": "2026-10-20T13:45:00Z",
        "eventSource": "iam.amazonaws.com",
        "eventName": "AttachUserPolicy",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.222",
        "userAgent": "boto3/1.28.0 Python/3.10 Linux/x86_64",
        "requestParameters": {
            "userName": "infiltrator-user",
            "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        },
        "responseElements": None,
        "requestID": "synthetic-high-risk-req-002",
        "eventID": "synthetic-high-risk-evt-002",
        "readOnly": False,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }


# ==============================================================================
# Verification 1: The event is normalized and evaluated correctly
# ==============================================================================

def test_01_access_denied_event_normalized_correctly(synthetic_access_denied_event):
    """
    Verify that an AWS AccessDenied event is normalized with correct field extraction,
    user identity, provider, error indicators, and read-only status.
    """
    normalized = aws_normalizer.normalize(synthetic_access_denied_event)

    assert normalized["provider"] == "AWS"
    assert normalized["username"] == "CloudGuardianS3IngestionUser"
    assert normalized["event_name"] == "DescribeVpcs"
    assert normalized["region"] == "ap-south-1"
    assert normalized["source_ip"] == "203.0.113.19"
    assert normalized["event_id"] == "synthetic-access-denied-evt-001"
    assert normalized["is_read_only"] is True
    assert normalized["raw_log"] is not None
    # Ensure sensitive data redaction was applied
    assert "password" not in str(normalized["raw_log"]).lower()


# ==============================================================================
# Verification 2: The event is stored as an event when using test repository
# ==============================================================================

def test_02_access_denied_event_stored_in_events_repository(synthetic_access_denied_event):
    """
    Verify that the AccessDenied event is stored in the OpenSearch `events` repository
    using the CloudTrail eventID as document ID for idempotency.
    """
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True

    repo = EventRepository(opensearch_client=mock_os)
    normalized = aws_normalizer.normalize(synthetic_access_denied_event)

    saved = repo.save_event(normalized)

    assert saved["event_id"] == "synthetic-access-denied-evt-001"
    mock_os.index.assert_called_once()
    call_kwargs = mock_os.index.call_args[1]
    assert call_kwargs["index"] == "events"
    assert call_kwargs["id"] == "synthetic-access-denied-evt-001"
    assert call_kwargs["body"]["event_name"] == "DescribeVpcs"


# ==============================================================================
# Verification 3: AccessDenied does NOT automatically become high-severity incident
# ==============================================================================

def test_03_access_denied_does_not_create_incident(synthetic_access_denied_event):
    """
    Verify that a routine/benign AccessDenied error does not become a high-severity
    security incident or trigger WebSocket incident notifications.
    """
    mock_event_os = MagicMock()
    mock_incident_os = MagicMock()

    mock_event_repo = EventRepository(opensearch_client=mock_event_os)
    mock_incident_repo = IncidentRepository(opensearch_client=mock_incident_os)

    processor = LogProcessor()

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.threat_service.threat_service.lookup", return_value=None), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        result = processor.process_log(synthetic_access_denied_event)

        # 1. Event was saved to the events index
        mock_event_os.index.assert_called_once()
        assert mock_event_os.index.call_args[1]["index"] == "events"

        # 2. Pipeline result marked as non-incident
        assert result.get("is_incident") is False
        assert result.get("incident_id") is None
        assert result.get("risk_score") == 0
        assert result.get("risk_level") == "LOW"
        assert result.get("status") == "INFORMATIONAL"

        # 3. Incident repository was NOT called to create an incident
        mock_incident_os.index.assert_not_called()

        # 4. WebSocket was NOT triggered with a security incident toast
        mock_ws.assert_not_called()


# ==============================================================================
# Verification 4: Separate synthetic high-risk event triggers an incident
# ==============================================================================

def test_04_high_risk_event_triggers_security_incident(synthetic_high_risk_event):
    """
    Verify that a genuine high-risk event (unauthorized policy escalation from a malicious IP)
    triggers risk escalation, generates a security incident, saves it to the incidents index,
    and broadcasts a WebSocket notification.
    """
    mock_event_os = MagicMock()
    mock_incident_os = MagicMock()
    mock_incident_os.get.return_value = None

    mock_event_repo = EventRepository(opensearch_client=mock_event_os)
    mock_incident_repo = IncidentRepository(opensearch_client=mock_incident_os)

    processor = LogProcessor()

    mock_ioc = {
        "value": "198.51.100.222",
        "enabled": True,
        "severity": "CRITICAL",
        "source": "THREAT_INTEL",
        "description": "Known Command and Control IP"
    }

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.threat_service.threat_service.lookup", return_value=mock_ioc), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        result = processor.process_log(synthetic_high_risk_event)

        # 1. Event was saved to events index
        mock_event_os.index.assert_called_once()

        # 2. Pipeline created an incident
        assert result.get("is_incident") is True
        assert result.get("incident_id") is not None
        assert result["incident_id"].startswith("INC-")
        assert result.get("risk_score") >= 70
        assert result.get("risk_level") in ["HIGH", "CRITICAL"]
        assert result.get("status") == "OPEN"

        # 3. Incident repository was called to store the incident
        mock_incident_os.index.assert_called_once()
        incident_call_kwargs = mock_incident_os.index.call_args[1]
        assert incident_call_kwargs["index"] == "incidents"
        assert incident_call_kwargs["id"] == result["incident_id"]

        # 4. WebSocket broadcast was emitted for the new incident
        assert mock_ws.call_count == 1
        broadcast_msg = mock_ws.call_args[0][0]
        assert broadcast_msg["type"] == "incident_created"
        assert broadcast_msg["data"]["incident_id"] == result["incident_id"]
        assert broadcast_msg["data"]["event_name"] == "AttachUserPolicy"


# ==============================================================================
# Verification 5: The incident is retrievable through the existing API
# ==============================================================================

def test_05_incident_retrievable_through_api(test_client, analyst_headers):
    """
    Verify that an incident stored in the incidents repository is retrievable
    via the FastAPI `/incidents/{incident_id}` and `/incidents/search` endpoints
    with valid authentication, and that unauthenticated requests are rejected.
    """
    sample_incident = {
        "incident_id": "INC-20261020-syn005",
        "title": "AttachUserPolicy Activity",
        "event_name": "AttachUserPolicy",
        "status": "OPEN",
        "priority": "CRITICAL",
        "risk_score": 95,
        "risk_level": "CRITICAL",
        "username": "infiltrator-user",
        "provider": "AWS",
        "created_at": "2026-10-20T13:45:00Z",
        "event_id": "synthetic-high-risk-evt-002",
        "threat_score": 70,
        "threat_level": "HIGH",
        "threat_tags": ["MALICIOUS_IP"]
    }

    # 1. Successful authenticated retrieval
    with patch("app.services.incident_service.incident_service.get_incident", return_value=sample_incident), \
         patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):

        response = test_client.get("/incidents/INC-20261020-syn005", headers=analyst_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == "INC-20261020-syn005"
        assert data["risk_score"] == 95
        assert data["username"] == "infiltrator-user"
        assert data["event_name"] == "AttachUserPolicy"

    # 2. Search endpoint retrieves incident
    search_mock_result = {
        "page": 1,
        "size": 10,
        "total": 1,
        "incidents": [sample_incident]
    }
    with patch("app.services.incident_service.incident_service.search_incidents", return_value=search_mock_result), \
         patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):

        search_response = test_client.get("/incidents/search?username=infiltrator-user", headers=analyst_headers)
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["total"] == 1
        assert search_data["incidents"][0]["incident_id"] == "INC-20261020-syn005"

    # 3. Unauthenticated request is rejected
    unauth_response = test_client.get("/incidents/INC-20261020-syn005")
    assert unauth_response.status_code == 401


# ==============================================================================
# Verification 6: Duplicate delivery does not create duplicate incidents
# ==============================================================================

def test_06_duplicate_delivery_does_not_create_duplicate_incidents(synthetic_high_risk_event):
    """
    Verify that delivering the same high-risk event multiple times does not create
    duplicate incidents or emit redundant WebSocket notifications.
    """
    mock_event_os = MagicMock()
    mock_incident_os = MagicMock()

    mock_event_repo = EventRepository(opensearch_client=mock_event_os)
    mock_incident_repo = IncidentRepository(opensearch_client=mock_incident_os)

    processor = LogProcessor()

    mock_ioc = {
        "value": "198.51.100.222",
        "enabled": True,
        "severity": "CRITICAL",
        "source": "THREAT_INTEL",
        "description": "Known Command and Control IP"
    }

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.threat_service.threat_service.lookup", return_value=mock_ioc), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        # First delivery: creates the incident
        first_result = processor.process_log(synthetic_high_risk_event)
        incident_id = first_result["incident_id"]
        assert mock_incident_os.index.call_count == 1
        assert mock_ws.call_count == 1

        # Second delivery of the exact same event:
        # IncidentRepository now has it in its local cache, so get_incident returns the existing incident
        second_result = processor.process_log(synthetic_high_risk_event)

        # Persistence was NOT called a second time
        assert mock_incident_os.index.call_count == 1

        # WebSocket broadcast was NOT called a second time
        assert mock_ws.call_count == 1

        # Returned result corresponds to the existing incident
        assert second_result["incident_id"] == incident_id
