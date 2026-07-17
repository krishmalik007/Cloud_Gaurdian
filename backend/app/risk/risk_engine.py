"""
Cloud Guardian — Risk Scoring Engine Module.

Evaluates normalized logs and assigns a risk score (0-100) based on
event type, category, severity, status, context, and correlation results.
"""

from app.logger import logger
from app.models.log_models import NormalizedLog, Severity


class RiskScoringEngine:
    """
    Assigns risk scores to normalized log events.

    Scoring is based on multiple weighted factors:
    - Base severity score
    - Event category weight
    - Status modifier (failure events score higher)
    - Specific event risk bonuses
    - Correlation boost from the Correlation Engine
    """

    # Base score by severity level
    SEVERITY_SCORES: dict[Severity, int] = {
        Severity.LOW: 10,
        Severity.MEDIUM: 30,
        Severity.HIGH: 60,
        Severity.CRITICAL: 85,
    }

    # Additional weight by event category
    CATEGORY_WEIGHTS: dict[str, int] = {
        "Authentication": 10,
        "Authorization": 15,
        "IAM": 20,
        "Network": 10,
        "Storage": 10,
        "Compute": 5,
        "Data": 10,
        "Configuration": 15,
        "Unknown": 0,
    }

    # Specific high-risk events with fixed bonus scores
    HIGH_RISK_EVENTS: dict[str, int] = {
        "DeleteUser": 15,
        "DeleteBucket": 20,
        "CreateAccessKey": 15,
        "AttachUserPolicy": 15,
        "PutBucketPolicy": 20,
        "AuthorizeSecurityGroupIngress": 15,
        "TerminateInstances": 10,
        "DeleteSecurityGroup": 20,
        "ConsoleLogin": 5,  # Baseline for login events
        "AssumeRole": 10,
    }

    def score(self, log: NormalizedLog, correlation_boost: int = 0) -> int:
        """
        Calculate the risk score for a normalized log.

        Args:
            log: The normalized log event.
            correlation_boost: Additional score from correlation engine matches.

        Returns:
            Risk score between 0 and 100.
        """
        # 1. Base severity score
        base_score = self.SEVERITY_SCORES.get(log.severity, 10)

        # 2. Category weight
        category_weight = self.CATEGORY_WEIGHTS.get(log.event_category.value, 0)

        # 3. Status modifier — failures are inherently more suspicious
        status_modifier = 10 if log.status.value == "Failure" else 0

        # 4. Specific event risk bonus
        event_bonus = self.HIGH_RISK_EVENTS.get(log.event_name, 0)

        # 5. Failed authentication gets extra weight (brute force indicator)
        auth_failure_bonus = 0
        if log.event_category.value == "Authentication" and log.status.value == "Failure":
            auth_failure_bonus = 15

        # 6. Sum up and add correlation boost
        total = base_score + category_weight + status_modifier + event_bonus + auth_failure_bonus + correlation_boost

        # 7. Clamp to 0-100
        risk_score = max(0, min(100, total))

        logger.debug(
            f"Risk scored: {log.log_id} | event={log.event_name} | "
            f"base={base_score} + cat={category_weight} + status={status_modifier} + "
            f"event={event_bonus} + auth_fail={auth_failure_bonus} + corr={correlation_boost} "
            f"= {risk_score}"
        )

        return risk_score

    def score_batch(self, logs: list[NormalizedLog], correlation_boosts: dict[str, int] | None = None) -> list[NormalizedLog]:
        """
        Score a batch of normalized logs.

        Args:
            logs: List of normalized log events.
            correlation_boosts: Optional mapping of log_id -> correlation boost score.

        Returns:
            List of logs with updated risk_score field.
        """
        boosts = correlation_boosts or {}
        scored = []

        for log in logs:
            boost = boosts.get(log.log_id, 0)
            log.risk_score = self.score(log, correlation_boost=boost)
            scored.append(log)

        logger.info(f"Batch risk scoring: {len(scored)} logs scored")
        return scored


# Singleton instance
risk_scoring_engine = RiskScoringEngine()
