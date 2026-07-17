"""
Cloud Guardian — Log Normalizer Module.

Converts parsed log dictionaries into validated NormalizedLog Pydantic models,
assigning unique log IDs and default severity.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.logger import logger
from app.models.log_models import (
    CloudProvider,
    EventCategory,
    EventStatus,
    NormalizedLog,
    Severity,
)


class LogNormalizer:
    """
    Normalizes parsed log dictionaries into the standard NormalizedLog schema.
    Handles type coercion, ID generation, and fallback defaults.
    """

    # Default severity per event category
    CATEGORY_SEVERITY: dict[str, Severity] = {
        "Authentication": Severity.MEDIUM,
        "Authorization": Severity.HIGH,
        "IAM": Severity.HIGH,
        "Network": Severity.MEDIUM,
        "Storage": Severity.MEDIUM,
        "Compute": Severity.LOW,
        "Data": Severity.MEDIUM,
        "Configuration": Severity.MEDIUM,
        "Unknown": Severity.LOW,
    }

    # Events that always get elevated severity
    HIGH_SEVERITY_EVENTS: set[str] = {
        "DeleteUser",
        "DeleteBucket",
        "AttachUserPolicy",
        "CreateAccessKey",
        "AuthorizeSecurityGroupIngress",
        "TerminateInstances",
    }

    CRITICAL_SEVERITY_EVENTS: set[str] = {
        "DeleteSecurityGroup",
        "PutBucketPolicy",
    }

    @staticmethod
    def _generate_log_id() -> str:
        """Generate a unique log ID."""
        return f"LOG-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def _parse_timestamp(ts_value: Any) -> datetime:
        """Parse a timestamp string into a datetime object."""
        if isinstance(ts_value, datetime):
            return ts_value

        if isinstance(ts_value, str) and ts_value:
            # Try ISO format first
            try:
                return datetime.fromisoformat(ts_value.replace("Z", "+00:00"))
            except ValueError:
                pass

            # Try common formats
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(ts_value, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

        # Fallback to current time
        return datetime.now(timezone.utc)

    def _determine_severity(self, event_name: str, category: str, status: str) -> Severity:
        """Determine event severity based on event name, category, and status."""
        if event_name in self.CRITICAL_SEVERITY_EVENTS:
            return Severity.CRITICAL
        if event_name in self.HIGH_SEVERITY_EVENTS:
            return Severity.HIGH

        base_severity = self.CATEGORY_SEVERITY.get(category, Severity.LOW)

        # Failed auth events are always elevated
        if category == "Authentication" and status == "Failure":
            return Severity.HIGH

        return base_severity

    def normalize(self, parsed_log: dict[str, Any]) -> NormalizedLog:
        """
        Convert a parsed log dictionary into a NormalizedLog model.

        Args:
            parsed_log: Dictionary from the LogParser output.

        Returns:
            Validated NormalizedLog instance.

        Raises:
            ValueError: If the log data fails validation.
        """
        try:
            event_name = parsed_log.get("event_name", "Unknown")
            category = parsed_log.get("event_category", "Unknown")
            status = parsed_log.get("status", "Success")
            severity = self._determine_severity(event_name, category, status)

            # Map string values to enums safely
            cloud_provider = CloudProvider(parsed_log.get("cloud_provider", "AWS"))
            event_category = EventCategory(category) if category in EventCategory.__members__.values() else EventCategory.UNKNOWN
            event_status = EventStatus(status) if status in ("Success", "Failure") else EventStatus.SUCCESS

            normalized = NormalizedLog(
                log_id=self._generate_log_id(),
                timestamp=self._parse_timestamp(parsed_log.get("timestamp")),
                cloud_provider=cloud_provider,
                service=parsed_log.get("service", "Unknown"),
                event_name=event_name,
                event_category=event_category,
                user=parsed_log.get("user", "unknown"),
                source_ip=parsed_log.get("source_ip", ""),
                destination_ip=parsed_log.get("destination_ip", ""),
                resource=parsed_log.get("resource", ""),
                action=parsed_log.get("action", event_name),
                status=event_status,
                severity=severity,
                region=parsed_log.get("region", ""),
                risk_score=0,  # Will be set by RiskScoringEngine
                correlation_id="",  # Will be set by CorrelationEngine
                raw_log=parsed_log.get("raw_log", {}),
            )

            logger.debug(f"Normalized log: {normalized.log_id} | {event_name} | {severity.value}")
            return normalized

        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            raise ValueError(f"Failed to normalize log: {e}") from e

    def normalize_batch(self, parsed_logs: list[dict[str, Any]]) -> tuple[list[NormalizedLog], list[dict]]:
        """
        Normalize a batch of parsed logs.

        Args:
            parsed_logs: List of parsed log dictionaries.

        Returns:
            Tuple of (successful normalizations, failed entries with errors).
        """
        normalized = []
        failures = []

        for i, parsed_log in enumerate(parsed_logs):
            try:
                normalized.append(self.normalize(parsed_log))
            except Exception as e:
                failures.append({"index": i, "error": str(e), "log": parsed_log})
                logger.warning(f"Skipping log at index {i}: {e}")

        logger.info(f"Batch normalization: {len(normalized)} success, {len(failures)} failures")
        return normalized, failures


# Singleton instance
log_normalizer = LogNormalizer()
