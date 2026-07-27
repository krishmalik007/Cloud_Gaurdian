from app.logger import logger

from app.normalizer.factory import normalizer_factory
from app.correlation.correlation_engine import correlation_engine
from app.risk.risk_engine import risk_engine
from app.alerts.alert_engine import alert_engine


class IncidentPipeline:
    """
    Cloud Guardian Event Processing Pipeline

    Processing Flow:

        Raw Cloud Log
                │
                ▼
        Provider Detection
                │
                ▼
        Normalizer Factory
                │
                ▼
        AWS / Azure / GCP Normalizer
                │
                ▼
        Correlation Engine
                │
                ▼
        Risk Engine
                │
                ▼
        Alert Engine
                │
                ▼
        Security Incident
    """

    def process_event(self, raw_log: dict) -> dict:
        """
        Process a raw cloud log and generate a security incident.
        """

        logger.info("=" * 60)
        logger.info("Starting Incident Processing Pipeline")

        # --------------------------------------------------
        # Step 1 : Detect Cloud Provider
        # --------------------------------------------------
        provider = raw_log.get("provider", "").upper()

        logger.info(f"Detected Provider : {provider}")

        # --------------------------------------------------
        # Step 2 : Normalize Log
        # --------------------------------------------------
        normalizer = normalizer_factory.get_normalizer(provider)

        normalized_log = normalizer.normalize(raw_log)

        logger.info("Log Normalization Completed")

        # --------------------------------------------------
        # Step 3 : Correlation Engine
        # --------------------------------------------------
        alerts = correlation_engine.process_event(normalized_log)

        logger.info(f"Generated {len(alerts)} Alert(s)")

        # --------------------------------------------------
        # Step 4 : Risk Engine
        # --------------------------------------------------
        risk_result = risk_engine.calculate_risk(alerts)

        logger.info(
            f"Risk Score : {risk_result['score']} | "
            f"Risk Level : {risk_result['level']}"
        )

        # --------------------------------------------------
        # Step 5 : Alert Engine
        # --------------------------------------------------
        incident = alert_engine.generate_incident(
            normalized_log,
            risk_result
        )

        logger.info(f"Incident Created : {incident['incident_id']}")

        logger.info("Incident Processing Completed")
        logger.info("=" * 60)

        return incident


incident_pipeline = IncidentPipeline()