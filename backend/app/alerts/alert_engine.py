import hashlib
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

        stable_id = event.get("event_id") or event.get("eventID")
        event_time = event.get("event_time") or event.get("timestamp")
        incident_id = self._generate_incident_id(stable_id, event_time)
        
        # 1. Event Summary
        event_summary = {
            "event_name": event.get("event_name", "Unknown"),
            "region": event.get("region", "Unknown"),
            "source_ip": event.get("source_ip", "Unknown"),
            "timestamp": str(event.get("timestamp", "")),
            "event_id": str(stable_id) if stable_id else ""
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

    def _generate_incident_id(self, stable_id=None, event_time=None):

        date_str = None
        if event_time and isinstance(event_time, str):
            clean_ts = event_time.replace("-", "")[:8]
            if len(clean_ts) == 8 and clean_ts.isdigit():
                date_str = clean_ts
        if not date_str:
            date_str = datetime.now(UTC).strftime("%Y%m%d")

        if stable_id:
            unique_suffix = hashlib.sha256(str(stable_id).encode("utf-8")).hexdigest()[:8]
        else:
            unique_suffix = uuid.uuid4().hex[:8]

        incident_id = f"INC-{date_str}-{unique_suffix}"

        return incident_id


alert_engine = AlertEngine()