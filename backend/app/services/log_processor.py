from app.logger import logger

from app.pipeline.incident_pipeline import incident_pipeline
from app.storage.incident_repository import incident_repository


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
        incident_repository.save_incident(incident)

        logger.info(
            f"Incident {incident['incident_id']} stored successfully."
        )

        logger.info("Log Processing Completed")
        logger.info("=" * 60)

        return incident


log_processor = LogProcessor()