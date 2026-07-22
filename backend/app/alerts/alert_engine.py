from datetime import datetime, UTC

from app.alerts.incident import Incident


class AlertEngine:

    """
    Converts generated alerts into a Security Incident.
    """

    def __init__(self):

        self.incident_counter = 1

    def generate_incident(self, event, risk_result):

        incident_id = self._generate_incident_id()

        incident = Incident(

            incident_id=incident_id,

            status="OPEN",

            priority=risk_result["level"],

            risk_score=risk_result["score"],

            risk_level=risk_result["level"],

            username=event.get("username", "Unknown"),

            provider=event.get("provider", "Unknown"),

            alerts=risk_result["alerts"],

            created_at=datetime.now(UTC).isoformat()

        )

        return incident.to_dict()

    def _generate_incident_id(self):

        date = datetime.now(UTC).strftime("%Y%m%d")

        incident_id = f"INC-{date}-{self.incident_counter:05d}"

        self.incident_counter += 1

        return incident_id


alert_engine = AlertEngine()