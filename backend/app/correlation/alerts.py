from datetime import datetime, UTC


class Alert:
    """
    Represents a security alert generated
    by the Correlation Engine.
    """

    def __init__(
        self,
        alert_type,
        severity,
        username,
        provider,
        description,
        event,
        related_events=None
    ):

        self.alert_type = alert_type

        self.severity = severity

        self.username = username

        self.provider = provider

        self.description = description

        self.event = event

        self.related_events = related_events or []

        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self):

        return {

            "alert_type": self.alert_type,

            "severity": self.severity,

            "username": self.username,

            "provider": self.provider,

            "description": self.description,

            "timestamp": self.timestamp,

            "event": self.event,
            
            "related_events": self.related_events

        }