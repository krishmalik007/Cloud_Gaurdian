from app.normalizer.aws import aws_normalizer


def test_console_login():
    """ConsoleLogin via signin service → AUTHENTICATION"""

    log = {
        "provider": "AWS",
        "eventName": "ConsoleLogin",
        "eventSource": "signin.amazonaws.com",
        "eventTime": "2026-07-27T12:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "10.0.0.5",
        "userIdentity": {
            "userName": "krish"
        }
    }

    result = aws_normalizer.normalize(log)

    assert result["provider"] == "AWS"
    assert result["username"] == "krish"
    assert result["event_name"] == "ConsoleLogin"
    assert result["event_type"] == "AUTHENTICATION"
    assert result["region"] == "ap-south-1"
    assert result["source_ip"] == "10.0.0.5"
    assert result["event_time"] == "2026-07-27T12:00:00Z"


def test_assume_role():
    """AssumeRole via STS → AUTHENTICATION"""

    log = {
        "provider": "AWS",
        "eventName": "AssumeRole",
        "eventSource": "sts.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "events.amazonaws.com",
        "userIdentity": {
            "principalId": "AROA123456:session"
        }
    }

    result = aws_normalizer.normalize(log)

    assert result["provider"] == "AWS"
    assert result["event_name"] == "AssumeRole"
    assert result["event_type"] == "AUTHENTICATION"
    assert result["region"] == "ap-south-1"
    assert result["source_ip"] == "events.amazonaws.com"


def test_create_user():
    """CreateUser via IAM → IAM"""

    log = {
        "provider": "AWS",
        "eventName": "CreateUser",
        "eventSource": "iam.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "admin"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "CreateUser"
    assert result["event_type"] == "IAM"


def test_run_instances():
    """RunInstances via EC2 → COMPUTE"""

    log = {
        "provider": "AWS",
        "eventName": "RunInstances",
        "eventSource": "ec2.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "devops"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "RunInstances"
    assert result["event_type"] == "COMPUTE"


def test_create_bucket():
    """CreateBucket via S3 → STORAGE"""

    log = {
        "provider": "AWS",
        "eventName": "CreateBucket",
        "eventSource": "s3.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "developer"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "CreateBucket"
    assert result["event_type"] == "STORAGE"


def test_authorize_sg_ingress():
    """AuthorizeSecurityGroupIngress via EC2 → NETWORK"""

    log = {
        "provider": "AWS",
        "eventName": "AuthorizeSecurityGroupIngress",
        "eventSource": "ec2.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "netadmin"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "AuthorizeSecurityGroupIngress"
    assert result["event_type"] == "NETWORK"


def test_stop_logging():
    """StopLogging via CloudTrail → LOGGING"""

    log = {
        "provider": "AWS",
        "eventName": "StopLogging",
        "eventSource": "cloudtrail.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "attacker"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "StopLogging"
    assert result["event_type"] == "LOGGING"


def test_unknown_event():
    """Unknown event name with unknown source → UNKNOWN"""

    log = {
        "provider": "AWS",
        "eventName": "SomeObscureAction",
        "eventSource": "someservice.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "1.2.3.4",
        "userIdentity": {"userName": "user"}
    }

    result = aws_normalizer.normalize(log)

    assert result["event_name"] == "SomeObscureAction"
    assert result["event_type"] == "UNKNOWN"


def test_credentials_redacted():
    """Credentials in responseElements must be [REDACTED] in raw_log."""

    log = {
        "provider": "AWS",
        "eventName": "AssumeRole",
        "eventSource": "sts.amazonaws.com",
        "eventTime": "2026-09-04T07:00:00Z",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "events.amazonaws.com",
        "userIdentity": {"principalId": "AROA123:session"},
        "responseElements": {
            "credentials": {
                "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
                "secretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "sessionToken": "AQoXnyc..."
            }
        }
    }

    result = aws_normalizer.normalize(log)

    raw = result["raw_log"]
    creds = raw.get("responseElements", {}).get("credentials")
    assert creds == "[REDACTED]", f"Expected [REDACTED], got: {creds}"


if __name__ == "__main__":
    test_console_login()
    print("[PASS] ConsoleLogin -> AUTHENTICATION")

    test_assume_role()
    print("[PASS] AssumeRole -> AUTHENTICATION")

    test_create_user()
    print("[PASS] CreateUser -> IAM")

    test_run_instances()
    print("[PASS] RunInstances -> COMPUTE")

    test_create_bucket()
    print("[PASS] CreateBucket -> STORAGE")

    test_authorize_sg_ingress()
    print("[PASS] AuthorizeSecurityGroupIngress -> NETWORK")

    test_stop_logging()
    print("[PASS] StopLogging -> LOGGING")

    test_unknown_event()
    print("[PASS] SomeObscureAction -> UNKNOWN")

    test_credentials_redacted()
    print("[PASS] Credentials are [REDACTED]")

    print("\n[PASS] All AWS Normalizer Tests Passed")