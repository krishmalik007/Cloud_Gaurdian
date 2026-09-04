from app.logger import logger

from app.pipeline.incident_pipeline import incident_pipeline
from app.storage.incident_repository import incident_repository
from app.services.websocket_manager import ws_manager


class LogProcessor:
    """
    Cloud Guardian Log Processing Service

    Flow:

    Raw Log
        ↓
    Incident Pipeline
        ↓
    Incident Repository
        ↓
    Return Incident
    """

    def process_log(self, raw_log: dict) -> dict:

        logger.info("=" * 60)
        logger.info("Starting Log Processing Service")

        # Process raw log through the pipeline
        incident = incident_pipeline.process_event(raw_log)

        # Save incident in OpenSearch
        try:
            incident_repository.save_incident(incident)
            logger.info(
                f"Incident {incident['incident_id']} stored successfully."
            )
        except Exception as e:
            logger.error(f"Failed to save incident {incident.get('incident_id')}: {e}")
            raise e

        # Construct a dashboard-safe payload, strictly excluding raw logs and credentials
        safe_incident_data = {
            "incident_id": incident.get("incident_id"),
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