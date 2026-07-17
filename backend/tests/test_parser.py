"""
Cloud Guardian — Unit Tests for Log Parser.
"""

import pytest
from app.parser.log_parser import LogParser


@pytest.fixture
def parser():
    return LogParser()


class TestCloudTrailParser:
    """Tests for AWS CloudTrail log parsing."""

    def test_parse_successful_login(self, parser):
        raw = {
            "eventVersion": "1.08",
            "eventTime": "2026-07-17T10:25:30Z",
            "eventSource": "signin.amazonaws.com",
            "eventName": "ConsoleLogin",
            "awsRegion": "ap-south-1",
            "sourceIPAddress": "192.168.1.15",
            "userIdentity": {"userName": "admin", "type": "IAMUser"},
            "responseElements": {"ConsoleLogin": "Success"},
        }
        result = parser.parse("cloudtrail", raw)

        assert result["cloud_provider"] == "AWS"
        assert result["event_name"] == "ConsoleLogin"
        assert result["user"] == "admin"
        assert result["source_ip"] == "192.168.1.15"
        assert result["status"] == "Success"
        assert result["region"] == "ap-south-1"
        assert result["event_category"] == "Authentication"

    def test_parse_failed_event(self, parser):
        raw = {
            "eventTime": "2026-07-17T10:30:00Z",
            "eventSource": "iam.amazonaws.com",
            "eventName": "CreateUser",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "10.0.0.1",
            "userIdentity": {"userName": "attacker"},
            "errorCode": "AccessDenied",
            "errorMessage": "User is not authorized",
        }
        result = parser.parse("cloudtrail", raw)

        assert result["status"] == "Failure"
        assert result["event_category"] == "IAM"

    def test_parse_unknown_event(self, parser):
        raw = {
            "eventTime": "2026-07-17T11:00:00Z",
            "eventSource": "unknown.amazonaws.com",
            "eventName": "CustomAction",
            "awsRegion": "eu-west-1",
            "userIdentity": {"principalId": "AIDAEXAMPLE"},
        }
        result = parser.parse("cloudtrail", raw)

        assert result["event_category"] == "Unknown"
        assert result["service"] == "CloudTrail"


class TestVPCFlowParser:
    """Tests for AWS VPC Flow Log parsing."""

    def test_parse_accepted_flow(self, parser):
        raw = {
            "version": 2,
            "account_id": "123456789012",
            "interface_id": "eni-abc123",
            "srcaddr": "10.0.0.1",
            "dstaddr": "10.0.0.2",
            "srcport": 49152,
            "dstport": 443,
            "protocol": 6,
            "packets": 10,
            "bytes": 5000,
            "start": 1721208000,
            "end": 1721208060,
            "action": "ACCEPT",
            "log_status": "OK",
        }
        result = parser.parse("vpc_flow", raw)

        assert result["cloud_provider"] == "AWS"
        assert result["service"] == "VPC Flow Logs"
        assert result["source_ip"] == "10.0.0.1"
        assert result["destination_ip"] == "10.0.0.2"
        assert result["status"] == "Success"
        assert result["event_category"] == "Network"

    def test_parse_rejected_flow(self, parser):
        raw = {
            "srcaddr": "192.168.1.100",
            "dstaddr": "10.0.0.5",
            "srcport": 12345,
            "dstport": 22,
            "protocol": 6,
            "start": 1721208000,
            "end": 1721208060,
            "action": "REJECT",
        }
        result = parser.parse("vpc_flow", raw)

        assert result["status"] == "Failure"
        assert "REJECT" in result["event_name"]


class TestAzureActivityParser:
    """Tests for Azure Activity Log parsing."""

    def test_parse_vm_start(self, parser):
        raw = {
            "time": "2026-07-17T12:00:00Z",
            "resourceId": "/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-01",
            "operationName": {
                "value": "Microsoft.Compute/virtualMachines/start/action",
                "localizedValue": "Start Virtual Machine",
            },
            "resultType": "Success",
            "caller": "user@example.com",
            "callerIpAddress": "203.0.113.10",
        }
        result = parser.parse("azure_activity", raw)

        assert result["cloud_provider"] == "Azure"
        assert result["event_category"] == "Compute"
        assert result["user"] == "user@example.com"
        assert result["status"] == "Success"

    def test_parse_failed_operation(self, parser):
        raw = {
            "time": "2026-07-17T12:30:00Z",
            "operationName": {"value": "Microsoft.Network/networkSecurityGroups/write", "localizedValue": "Create NSG"},
            "resultType": "Failed",
            "caller": "admin@example.com",
            "callerIpAddress": "198.51.100.5",
        }
        result = parser.parse("azure_activity", raw)

        assert result["status"] == "Failure"
        assert result["event_category"] == "Network"


class TestParserRouting:
    """Tests for parser routing and error handling."""

    def test_unsupported_log_type(self, parser):
        with pytest.raises(ValueError, match="Unsupported log type"):
            parser.parse("gcp_audit", {"some": "data"})

    def test_case_insensitive_log_type(self, parser):
        raw = {
            "eventTime": "2026-07-17T10:00:00Z",
            "eventSource": "s3.amazonaws.com",
            "eventName": "GetObject",
            "awsRegion": "us-east-1",
            "userIdentity": {"userName": "user1"},
        }
        result = parser.parse("CLOUDTRAIL", raw)
        assert result["cloud_provider"] == "AWS"
