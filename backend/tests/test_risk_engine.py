"""
Cloud Guardian — Unit Tests for Risk Scoring Engine.
"""

import pytest
from app.risk.risk_engine import RiskScoringEngine
from app.models.log_models import NormalizedLog, Severity, EventCategory, EventStatus, CloudProvider
from datetime import datetime, timezone


@pytest.fixture
def engine():
    return RiskScoringEngine()


def _make_log(**kwargs) -> NormalizedLog:
    """Helper to create a NormalizedLog with sensible defaults."""
    defaults = {
        "log_id": "LOG-TEST001",
        "timestamp": datetime.now(timezone.utc),
        "cloud_provider": CloudProvider.AWS,
        "service": "CloudTrail",
        "event_name": "ConsoleLogin",
        "event_category": EventCategory.AUTHENTICATION,
        "user": "testuser",
        "source_ip": "192.168.1.1",
        "action": "Login",
        "status": EventStatus.SUCCESS,
        "severity": Severity.LOW,
    }
    defaults.update(kwargs)
    return NormalizedLog(**defaults)


class TestRiskScoring:
    """Tests for the risk scoring engine."""

    def test_low_severity_low_score(self, engine):
        log = _make_log(
            event_name="GetObject",
            event_category=EventCategory.STORAGE,
            severity=Severity.LOW,
        )
        score = engine.score(log)
        assert 10 <= score <= 30

    def test_high_severity_high_score(self, engine):
        log = _make_log(
            event_name="DeleteUser",
            event_category=EventCategory.IAM,
            severity=Severity.HIGH,
        )
        score = engine.score(log)
        assert score >= 70

    def test_critical_severity_highest_score(self, engine):
        log = _make_log(
            event_name="DeleteBucket",
            event_category=EventCategory.STORAGE,
            severity=Severity.CRITICAL,
        )
        score = engine.score(log)
        assert score >= 85

    def test_failure_increases_score(self, engine):
        log_success = _make_log(status=EventStatus.SUCCESS)
        log_failure = _make_log(status=EventStatus.FAILURE)

        score_success = engine.score(log_success)
        score_failure = engine.score(log_failure)

        assert score_failure > score_success

    def test_failed_auth_bonus(self, engine):
        log = _make_log(
            event_category=EventCategory.AUTHENTICATION,
            status=EventStatus.FAILURE,
            severity=Severity.MEDIUM,
        )
        score = engine.score(log)
        # Should include auth failure bonus
        assert score >= 50

    def test_correlation_boost(self, engine):
        log = _make_log(severity=Severity.MEDIUM)

        base_score = engine.score(log, correlation_boost=0)
        boosted_score = engine.score(log, correlation_boost=30)

        assert boosted_score == base_score + 30

    def test_score_clamped_to_100(self, engine):
        log = _make_log(
            event_name="DeleteSecurityGroup",
            event_category=EventCategory.IAM,
            severity=Severity.CRITICAL,
            status=EventStatus.FAILURE,
        )
        # Even with a huge correlation boost, score should not exceed 100
        score = engine.score(log, correlation_boost=100)
        assert score <= 100

    def test_score_minimum_zero(self, engine):
        log = _make_log(severity=Severity.LOW)
        score = engine.score(log, correlation_boost=-500)
        assert score >= 0

    def test_batch_scoring(self, engine):
        logs = [
            _make_log(log_id=f"LOG-{i}", event_name="ConsoleLogin")
            for i in range(5)
        ]
        scored = engine.score_batch(logs)
        assert len(scored) == 5
        assert all(log.risk_score > 0 for log in scored)
