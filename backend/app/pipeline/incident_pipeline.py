from app.logger import logger

from app.alerts.alert_engine import alert_engine
from app.correlation.correlation_engine import correlation_engine
from app.normalizer.factory import normalizer_factory
from app.risk.risk_engine import risk_engine
from app.services.threat_service import threat_service


class IncidentPipeline:
    """
    Cloud Guardian Event Processing Pipeline

    Processing Flow

    Raw Cloud Log
            │
            ▼
    Provider Detection
            │
            ▼
    Normalizer
            │
            ▼
    Threat Intelligence
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
        Process a raw cloud log into a security incident.
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
        # Step 3 : Threat Intelligence
        # --------------------------------------------------
        threat_result = threat_service.analyze_log(
            normalized_log
        )

        normalized_log["threat_score"] = threat_result["threat_score"]
        normalized_log["threat_level"] = threat_result["threat_level"]
        normalized_log["threat_tags"] = threat_result["threat_tags"]

        logger.info(
            f"Threat Score : {threat_result['threat_score']} | "
            f"Threat Level : {threat_result['threat_level']}"
        )

        # --------------------------------------------------
        # Step 4 : Correlation Engine
        # --------------------------------------------------
        alerts = correlation_engine.process_event(
            normalized_log
        )

        logger.info(f"Generated {len(alerts)} Alert(s)")

        # --------------------------------------------------
        # Step 5 : Risk Engine
        # --------------------------------------------------
        risk_result = risk_engine.calculate_risk(
                normalized_log,
                alerts
        )

        # Combine threat score with calculated risk
        risk_result["score"] += threat_result["threat_score"]

        if risk_result["score"] >= 90:
            risk_result["level"] = "CRITICAL"
        elif risk_result["score"] >= 70:
            risk_result["level"] = "HIGH"
        elif risk_result["score"] >= 40:
            risk_result["level"] = "MEDIUM"
        else:
            risk_result["level"] = "LOW"

        logger.info(
            f"Risk Score : {risk_result['score']} | "
            f"Risk Level : {risk_result['level']}"
        )

        # --------------------------------------------------
        # Step 6 : Alert Engine
        # --------------------------------------------------
        incident = alert_engine.generate_incident(
            normalized_log,
            risk_result
        )

        # Store Threat Intelligence inside incident
        incident["threat_score"] = threat_result["threat_score"]
        incident["threat_level"] = threat_result["threat_level"]
        incident["threat_tags"] = threat_result["threat_tags"]

        logger.info(
            f"Incident Created : {incident['incident_id']}"
        )

        logger.info("Incident Processing Completed")
        logger.info("=" * 60)

        return incident


incident_pipeline = IncidentPipeline()