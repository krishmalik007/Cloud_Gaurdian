"""
Cloud Guardian — Unit Tests for Log Normalizer.
"""

import pytest
from datetime import datetime, timezone

from app.normalizer.log_normalizer import LogNormalizer
from app.models.log_models import Severity, EventCategory, CloudProvider, EventStatus


@pytest.fixture
def normalizer():
    return LogNormalizer()


class TestNormalization:
    """Tests for log normalization."""

    def test_normalize_basic_log(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:25:30Z",
            "cloud_provider": "AWS",
            "service": "CloudTrail",
            "event_name": "ConsoleLogin",
            "event_category": "Authentication",
            "user": "admin",
            "source_ip": "192.168.1.15",
            "destination_ip": "",
            "resource": "signin.amazonaws.com",
            "action": "ConsoleLogin",
            "status": "Success",
            "region": "ap-south-1",
            "raw_log": {},
        }
        result = normalizer.normalize(parsed)

        assert result.log_id.startswith("LOG-")
        assert result.cloud_provider == CloudProvider.AWS
        assert result.event_name == "ConsoleLogin"
        assert result.event_category == EventCategory.AUTHENTICATION
        assert result.user == "admin"
        assert result.risk_score == 0  # Not scored yet
        assert isinstance(result.timestamp, datetime)

    def test_severity_assignment_high_risk_event(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:30:00Z",
            "cloud_provider": "AWS",
            "service": "IAM",
            "event_name": "DeleteUser",
            "event_category": "IAM",
            "user": "attacker",
            "source_ip": "10.0.0.1",
            "action": "DeleteUser",
            "status": "Success",
            "raw_log": {},
        }
        result = normalizer.normalize(parsed)
        assert result.severity == Severity.HIGH

    def test_severity_assignment_critical_event(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:30:00Z",
            "cloud_provider": "AWS",
            "service": "S3",
            "event_name": "PutBucketPolicy",
            "event_category": "Storage",
            "user": "admin",
            "source_ip": "10.0.0.1",
            "action": "PutBucketPolicy",
            "status": "Success",
            "raw_log": {},
        }
        result = normalizer.normalize(parsed)
        assert result.severity == Severity.CRITICAL

    def test_failed_auth_elevated_severity(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:30:00Z",
            "cloud_provider": "AWS",
            "service": "IAM",
            "event_name": "ConsoleLogin",
            "event_category": "Authentication",
            "user": "admin",
            "source_ip": "10.0.0.1",
            "action": "ConsoleLogin",
            "status": "Failure",
            "raw_log": {},
        }
        result = normalizer.normalize(parsed)
        assert result.severity == Severity.HIGH

    def test_unique_log_ids(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:00:00Z",
            "cloud_provider": "Azure",
            "service": "Activity Logs",
            "event_name": "StartVM",
            "event_category": "Compute",
            "user": "user1",
            "source_ip": "1.2.3.4",
            "action": "Start",
            "status": "Success",
            "raw_log": {},
        }
        results = [normalizer.normalize(parsed) for _ in range(10)]
        log_ids = {r.log_id for r in results}
        assert len(log_ids) == 10  # All unique

    def test_timestamp_parsing_iso(self, normalizer):
        parsed = {
            "timestamp": "2026-07-17T10:25:30+00:00",
            "cloud_provider": "AWS",
            "service": "CloudTrail",
            "event_name": "Test",
            "event_category": "Unknown",
            "user": "test",
            "source_ip": "0.0.0.0",
            "action": "Test",
            "status": "Success",
            "raw_log": {},
        }
        result = normalizer.normalize(parsed)
        assert result.timestamp.year == 2026
        assert result.timestamp.month == 7

    def test_batch_normalization(self, normalizer):
        parsed_logs = [
            {
                "timestamp": "2026-07-17T10:00:00Z",
                "cloud_provider": "AWS",
                "service": "CloudTrail",
                "event_name": f"Event{i}",
                "event_category": "Unknown",
                "user": "user1",
                "source_ip": "1.2.3.4",
                "action": "Test",
                "status": "Success",
                "raw_log": {},
            }
            for i in range(5)
        ]
        # Add one bad entry
        parsed_logs.append({"invalid": "data"})

        normalized, failures = normalizer.normalize_batch(parsed_logs)

        assert len(normalized) == 5
        assert len(failures) == 1
