"""
Cloud Guardian — Correlation Engine Module.

Detects multi-event attack patterns by correlating normalized logs
across a configurable time window.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.logger import logger
from app.models.log_models import NormalizedLog


class CorrelationRule:
    """Defines a single correlation rule for detecting attack patterns."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        required_events: list[str],
        time_window_minutes: int = 15,
        min_occurrences: int = 1,
        group_by: str = "source_ip",
        severity_boost: int = 20,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.required_events = required_events
        self.time_window = timedelta(minutes=time_window_minutes)
        self.min_occurrences = min_occurrences
        self.group_by = group_by
        self.severity_boost = severity_boost


class CorrelationEngine:
    """
    Correlates normalized logs to detect multi-step attack patterns.

    Uses a sliding window approach grouped by source IP, user, or resource
    to find sequences of suspicious events.
    """

    def __init__(self):
        self._incident_counter: int = 0
        self._event_buffer: dict[str, list[NormalizedLog]] = defaultdict(list)
        self._rules: list[CorrelationRule] = self._load_default_rules()

    def _load_default_rules(self) -> list[CorrelationRule]:
        """Load the default set of correlation rules."""
        return [
            CorrelationRule(
                rule_id="RULE-001",
                name="Brute Force Login",
                description="Multiple failed login attempts from the same IP",
                required_events=["ConsoleLogin"],
                time_window_minutes=10,
                min_occurrences=5,
                group_by="source_ip",
                severity_boost=30,
            ),
            CorrelationRule(
                rule_id="RULE-002",
                name="Privilege Escalation",
                description="User creation followed by policy attachment",
                required_events=["CreateUser", "AttachUserPolicy"],
                time_window_minutes=30,
                group_by="user",
                severity_boost=25,
            ),
            CorrelationRule(
                rule_id="RULE-003",
                name="Data Exfiltration",
                description="Multiple S3 GetObject calls from unusual IP",
                required_events=["GetObject"],
                time_window_minutes=15,
                min_occurrences=50,
                group_by="source_ip",
                severity_boost=35,
            ),
            CorrelationRule(
                rule_id="RULE-004",
                name="Security Group Modification",
                description="Security group opened followed by new instances",
                required_events=["AuthorizeSecurityGroupIngress", "RunInstances"],
                time_window_minutes=60,
                group_by="user",
                severity_boost=20,
            ),
            CorrelationRule(
                rule_id="RULE-005",
                name="Credential Theft",
                description="Access key creation followed by cross-account activity",
                required_events=["CreateAccessKey", "AssumeRole"],
                time_window_minutes=30,
                group_by="user",
                severity_boost=30,
            ),
            CorrelationRule(
                rule_id="RULE-006",
                name="Network Scan (VPC Flow)",
                description="High volume of rejected connections from a single IP",
                required_events=["FlowLog-REJECT"],
                time_window_minutes=5,
                min_occurrences=100,
                group_by="source_ip",
                severity_boost=25,
            ),
        ]

    def _generate_incident_id(self) -> str:
        """Generate a unique incident ID."""
        self._incident_counter += 1
        now = datetime.now(timezone.utc)
        return f"INC-{now.strftime('%Y%m%d')}-{self._incident_counter:04d}"

    def _get_group_key(self, log: NormalizedLog, group_by: str) -> str:
        """Extract the grouping key from a log."""
        return getattr(log, group_by, "unknown")

    def add_event(self, log: NormalizedLog) -> None:
        """Add a normalized log to the event buffer for correlation."""
        # Buffer by source_ip and by user for different rule types
        self._event_buffer[f"ip:{log.source_ip}"].append(log)
        self._event_buffer[f"user:{log.user}"].append(log)

        # Prune old events (older than 1 hour)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        for key in list(self._event_buffer.keys()):
            self._event_buffer[key] = [
                e for e in self._event_buffer[key] if e.timestamp > cutoff
            ]
            if not self._event_buffer[key]:
                del self._event_buffer[key]

    def correlate(self, log: NormalizedLog) -> list[dict[str, Any]]:
        """
        Check a log against all correlation rules.

        Args:
            log: The newly ingested normalized log.

        Returns:
            List of triggered incident dictionaries.
        """
        self.add_event(log)
        incidents = []

        for rule in self._rules:
            group_key = f"{rule.group_by.replace('source_ip', 'ip').replace('user', 'user')}:{self._get_group_key(log, rule.group_by)}"
            events = self._event_buffer.get(group_key, [])

            # Filter to the rule's time window
            cutoff = log.timestamp - rule.time_window
            window_events = [e for e in events if e.timestamp >= cutoff]

            if rule.min_occurrences > 1:
                # Count-based rule (e.g., brute force)
                matching = [e for e in window_events if e.event_name in rule.required_events]

                # For brute-force style, also check for failure status
                if rule.rule_id == "RULE-001":
                    matching = [e for e in matching if e.status.value == "Failure"]

                if len(matching) >= rule.min_occurrences:
                    incident = {
                        "incident_id": self._generate_incident_id(),
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "description": rule.description,
                        "severity_boost": rule.severity_boost,
                        "matched_events": len(matching),
                        "group_key": group_key,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    incidents.append(incident)
                    logger.warning(
                        f"Correlation triggered: {rule.name} | "
                        f"{group_key} | {len(matching)} events"
                    )
            else:
                # Sequence-based rule (e.g., privilege escalation)
                event_names_in_window = {e.event_name for e in window_events}
                if all(req in event_names_in_window for req in rule.required_events):
                    incident = {
                        "incident_id": self._generate_incident_id(),
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "description": rule.description,
                        "severity_boost": rule.severity_boost,
                        "matched_events": len(window_events),
                        "group_key": group_key,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    incidents.append(incident)
                    logger.warning(
                        f"Correlation triggered: {rule.name} | "
                        f"{group_key} | events: {rule.required_events}"
                    )

        return incidents

    @property
    def rules(self) -> list[dict[str, Any]]:
        """Return all correlation rules as dictionaries."""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "required_events": r.required_events,
                "time_window_minutes": int(r.time_window.total_seconds() / 60),
                "min_occurrences": r.min_occurrences,
                "group_by": r.group_by,
            }
            for r in self._rules
        ]


# Singleton instance
correlation_engine = CorrelationEngine()
