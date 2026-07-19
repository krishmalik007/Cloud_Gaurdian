from collections import defaultdict

from app.logger import logger

# Rule modules
from app.correlation.rules import authentication_rules
from app.correlation.rules import iam_rules
from app.correlation.rules import resource_rules
from app.correlation.rules import data_rules
from app.correlation.rules import config_rules


class CorrelationEngine:
    """
    Main Correlation Engine.

    Responsibilities:
    1. Store recent events
    2. Execute correlation rules
    3. Collect alerts
    """

    def __init__(self):
        """
        Store events grouped by username.
        """

        self.event_memory = defaultdict(list)

    def process_event(self, normalized_event):
        """
        Process one normalized event.

        Returns:
            List of generated alerts.
        """

        username = normalized_event.get("username", "UNKNOWN")

        # Store event in memory
        self.event_memory[username].append(normalized_event)

        logger.info(
            f"Stored event for user: {username}"
        )

        alerts = []

        # Authentication rules
        alerts.extend(
            authentication_rules.check(
                self.event_memory,
                normalized_event
            )
        )

        # IAM rules
        alerts.extend(
            iam_rules.check(
                self.event_memory,
                normalized_event
            )
        )

        # Resource rules
        alerts.extend(
            resource_rules.check(
                self.event_memory,
                normalized_event
            )
        )

        # Data rules
        alerts.extend(
            data_rules.check(
                self.event_memory,
                normalized_event
            )
        )

        # Configuration rules
        alerts.extend(
            config_rules.check(
                self.event_memory,
                normalized_event
            )
        )

        logger.info(
            f"Generated {len(alerts)} alerts."
        )

        return alerts


correlation_engine = CorrelationEngine()