from app.logger import logger

from app.correlation.event_store import EventStore

from app.correlation.rules import (
    authentication_rules,
    iam_rules,
    resource_rules,
    data_rules,
    config_rules,
)


class CorrelationEngine:
    """
    Main Correlation Engine.

    Responsibilities:
    1. Receive normalized events.
    2. Store events using EventStore.
    3. Fetch recent events.
    4. Execute all rule modules.
    5. Return generated alerts.
    """

    def __init__(self):

        # Event Store manages timestamps and sliding window
        self.event_store = EventStore(window_minutes=10)

    def process_event(self, normalized_event):

        username = normalized_event.get("username", "UNKNOWN")

        # Store event
        self.event_store.add_event(normalized_event)

        logger.info(f"Stored event for user: {username}")

        # Fetch only recent events for this user
        recent_events = self.event_store.get_events(username)

        alerts = []

        # Authentication Rules
        alerts.extend(
            authentication_rules.check(
                recent_events,
                normalized_event
            )
        )

        # IAM Rules
        alerts.extend(
            iam_rules.check(
                recent_events,
                normalized_event
            )
        )

        # Resource Rules
        alerts.extend(
            resource_rules.check(
                recent_events,
                normalized_event
            )
        )

        # Data Security Rules
        alerts.extend(
            data_rules.check(
                recent_events,
                normalized_event
            )
        )

        # Configuration Rules
        alerts.extend(
            config_rules.check(
                recent_events,
                normalized_event
            )
        )

        logger.info(f"Generated {len(alerts)} alerts.")

        return alerts


correlation_engine = CorrelationEngine()