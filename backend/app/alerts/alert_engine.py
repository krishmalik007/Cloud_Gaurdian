import uuid
from datetime import datetime, UTC

from app.alerts.incident import Incident
from app.utils.redaction import redact_sensitive_data


class AlertEngine:

    """
    Converts generated alerts into a Security Incident.
    """

    def __init__(self):
        pass

    def generate_incident(self, event, risk_result):

        incident_id = self._generate_incident_id()
        
        # 1. Event Summary
        event_summary = {
            "event_name": event.get("event_name", "Unknown"),
            "region": event.get("region", "Unknown"),
            "source_ip": event.get("source_ip", "Unknown"),
            "timestamp": str(event.get("timestamp", ""))
        }
        
        # 2. XDR Intelligence
        risk_level = risk_result["level"]
        
        if risk_level in ["HIGH", "CRITICAL"]:
            attention = "REQUIRED"
            assessment = "Suspicious activity detected requiring analyst validation."
        elif risk_level == "MEDIUM":
            attention = "REVIEW RECOMMENDED"
            assessment = "Unusual activity detected that may warrant review."
        else:
            attention = "NOT REQUIRED"
            assessment = "Routine activity with no immediate security concern identified."

        incident = Incident(

            incident_id=incident_id,

            status="OPEN",

            priority=risk_level,

            risk_score=risk_result["score"],

            risk_level=risk_level,

            username=event.get("username", "Unknown"),

            provider=event.get("provider", "Unknown"),

            alerts=risk_result["alerts"],

            created_at=datetime.now(UTC).isoformat(),
            
            event_summary=event_summary,
            
            raw_log=redact_sensitive_data(event.get("raw_log")),
            
            analyst_attention=attention,
            
            xdr_assessment=assessment,
            
            notes=[],
            
            updated_at=datetime.now(UTC).isoformat()

        )

        return incident.to_dict()

    def _generate_incident_id(self):

        date = datetime.now(UTC).strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:8]

        incident_id = f"INC-{date}-{unique_suffix}"

        return incident_id


alert_engine = AlertEngine()