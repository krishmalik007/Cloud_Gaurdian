from app.logger import logger

from app.pipeline.incident_pipeline import incident_pipeline
from app.storage.incident_repository import incident_repository
from app.storage.event_repository import event_repository
from app.services.websocket_manager import ws_manager


class LogProcessor:
    """
    Cloud Guardian Log Processing Service

    Flow:
    Raw Log
        ↓
    Incident Pipeline (Normalize, Threat Intel, Correlation, Risk Scoring, Incident Classification)
        ↓
    Event Repository (ALWAYS store & index event in OpenSearch `events` index)
        ↓
    Is Security Incident?
       ├── NO  → Return non-incident event record (no incident saved, no WS broadcast)
       └── YES → Deduplicate & Save in `incidents` repository → Broadcast WS notification
    """

    def process_log(self, raw_log: dict) -> dict:

        logger.info("=" * 60)
        logger.info("Starting Log Processing Service")

        # 1. Process raw log through the pipeline
        output = incident_pipeline.process_event(raw_log)

        # 2. ALWAYS index and store the event in OpenSearch events repository
        try:
            event_repository.save_event(output)
            logger.info(f"Event {output.get('event_id')} indexed in events repository.")
        except Exception as e:
            logger.warning(f"Failed to index event in event_repository: {e}")

        # 3. Check if this event warrants a security incident
        is_incident = output.get("is_incident")
        # Backwards compatibility: if is_incident is None but incident_id exists, treat as incident
        if is_incident is None:
            is_incident = bool(output.get("incident_id"))

        if not is_incident:
            logger.info(
                f"Event {output.get('event_id')} recorded as {output.get('status', 'INFORMATIONAL')}. "
                "No security incident generated or broadcasted."
            )
            logger.info("Log Processing Completed")
            logger.info("=" * 60)
            return output

        # 4. For true security incidents: deduplicate at incident persistence boundary
        incident = output
        incident_id = incident.get("incident_id")

        existing = incident_repository.get_incident(incident_id)
        if existing:
            logger.info(
                f"Incident {incident_id} already exists in repository. "
                "Skipping duplicate persistence and notification."
            )
            return existing

        # 5. Save incident in OpenSearch
        try:
            incident_repository.save_incident(incident)
            logger.info(
                f"Incident {incident['incident_id']} stored successfully."
            )
        except Exception as e:
            logger.error(f"Failed to save incident {incident.get('incident_id')}: {e}")
            raise e

        # 6. Extract event name and title for notifications
        event_name = (
            incident.get("event_summary", {}).get("event_name")
            or incident.get("event_name")
            or raw_log.get("eventName")
            or raw_log.get("event_name")
            or "CloudEvent"
        )
        title = incident.get("title") or f"{event_name} Activity"

        # Construct a dashboard-safe payload, strictly excluding raw logs and credentials
        safe_incident_data = {
            "incident_id": incident.get("incident_id"),
            "title": title,
            "event_name": event_name,
            "status": incident.get("status"),
            "priority": incident.get("priority"),
            "risk_score": incident.get("risk_score"),
            "risk_level": incident.get("risk_level"),
            "username": incident.get("username"),
            "provider": incident.get("provider"),
            "created_at": incident.get("created_at"),
            "threat_score": incident.get("threat_score"),
            "threat_level": incident.get("threat_level"),
            "threat_tags": incident.get("threat_tags", [])
        }

        # Safely broadcast to WebSockets; failure here MUST NOT affect the pipeline
        try:
            ws_manager.broadcast_sync({
                "type": "incident_created",
                "timestamp": incident.get("created_at"),
                "data": safe_incident_data
            })
        except Exception as e:
            logger.error(f"WebSocket broadcast failed: {e}")

        logger.info("Log Processing Completed")
        logger.info("=" * 60)

        return incident


log_processor = LogProcessor()