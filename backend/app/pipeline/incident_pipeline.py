from datetime import datetime, timezone
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
    Incident Evaluation (_should_generate_incident)
       ├── True  → Alert Engine → Security Incident
       └── False → Informational / Operational Event Record
    """

    def _should_generate_incident(
        self,
        normalized_log: dict,
        risk_result: dict,
        threat_result: dict,
        alerts: list
    ) -> bool:
        """
        Determine whether an incoming cloud event should be elevated to a security incident.
        Separates routine/operational cloud events from true security incidents.
        """
        # 1. Operational / Integration health errors are operational health events, not security incidents
        if normalized_log.get("is_operational_health"):
            logger.info(
                f"Event {normalized_log.get('event_id')} classified as OPERATIONAL_HEALTH "
                f"({normalized_log.get('operational_issue')}). Suppressing security incident creation."
            )
            return False

        # 2. Correlation alerts: multi-event correlation or security violations detected
        if alerts and len(alerts) > 0:
            return True

        # 3. Threat intelligence: matched known malicious IP, domain, or watchlist user
        if threat_result.get("threat_score", 0) > 0 or len(normalized_log.get("ioc_matches", [])) > 0:
            return True

        # 4. Explicit high-severity security event types
        if normalized_log.get("event_type") in [
            "BRUTE_FORCE",
            "ANOMALY",
            "MALWARE_DETECTED",
            "PRIVILEGE_ESCALATION",
            "UNAUTHORIZED_ACCESS",
        ]:
            return True

        # 5. Meaningful risk score threshold (score >= 40 indicates elevated risk)
        if risk_result.get("score", 0) >= 40:
            return True

        # 6. Routine AWS service activity (e.g. ResourceExplorer, EventBridge, read-only queries)
        if normalized_log.get("is_service_activity"):
            logger.info(
                f"Event {normalized_log.get('event_id')} is routine AWS service activity "
                f"({normalized_log.get('service_context')}). Indexed as informational event."
            )
            return False

        # 7. Otherwise, routine single event with low/zero risk score (e.g. routine AssumeRole, GetCallerIdentity, Describe*)
        return False

    def process_event(self, raw_log: dict) -> dict:
        """
        Process a raw cloud log into a normalized event or security incident.
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
        # Step 6 : Incident Evaluation & Alert Engine
        # --------------------------------------------------
        is_incident = self._should_generate_incident(
            normalized_log,
            risk_result,
            threat_result,
            alerts
        )

        if is_incident:
            incident = alert_engine.generate_incident(
                normalized_log,
                risk_result
            )
            incident["is_incident"] = True
            incident["threat_score"] = threat_result["threat_score"]
            incident["threat_level"] = threat_result["threat_level"]
            incident["threat_tags"] = threat_result["threat_tags"]
            incident["event_category"] = normalized_log.get("event_category", "SECURITY")
            incident["event_id"] = normalized_log.get("event_id")
            incident["event_name"] = normalized_log.get("event_name", "Unknown")
            incident["region"] = normalized_log.get("region", "Unknown")
            incident["source_ip"] = normalized_log.get("source_ip", "Unknown")
            raw_ts = normalized_log.get("timestamp") or normalized_log.get("event_time")
            incident["timestamp"] = (
                raw_ts.isoformat() if isinstance(raw_ts, datetime) else str(raw_ts or incident.get("created_at"))
            )
            incident["event_time"] = normalized_log.get("event_time")
            incident["is_service_activity"] = normalized_log.get("is_service_activity", False)
            incident["is_operational_health"] = normalized_log.get("is_operational_health", False)
            incident["operational_issue"] = normalized_log.get("operational_issue", "")

            logger.info(f"Security Incident Created : {incident['incident_id']}")
            logger.info("Incident Processing Completed")
            logger.info("=" * 60)
            return incident
        else:
            event_id = normalized_log.get("event_id")
            status = "OPERATIONAL_HEALTH" if normalized_log.get("is_operational_health") else "INFORMATIONAL"
            category = normalized_log.get("event_category", "INFORMATIONAL")
            raw_ts = normalized_log.get("timestamp") or normalized_log.get("event_time")
            iso_ts = raw_ts.isoformat() if isinstance(raw_ts, datetime) else str(raw_ts or "")

            non_incident_event = {
                "is_incident": False,
                "incident_id": None,
                "event_id": event_id,
                "status": status,
                "priority": risk_result["level"],
                "risk_score": risk_result["score"],
                "risk_level": risk_result["level"],
                "username": normalized_log.get("username", "Unknown"),
                "provider": normalized_log.get("provider", "AWS"),
                "event_name": normalized_log.get("event_name", "Unknown"),
                "event_type": normalized_log.get("event_type", "UNKNOWN"),
                "event_category": category,
                "region": normalized_log.get("region", "Unknown"),
                "source_ip": normalized_log.get("source_ip", "Unknown"),
                "timestamp": iso_ts or datetime.now(timezone.utc).isoformat(),
                "event_time": normalized_log.get("event_time"),
                "is_service_activity": normalized_log.get("is_service_activity", False),
                "service_context": normalized_log.get("service_context", ""),
                "is_operational_health": normalized_log.get("is_operational_health", False),
                "operational_issue": normalized_log.get("operational_issue", ""),
                "is_read_only": normalized_log.get("is_read_only", False),
                "alerts": alerts,
                "threat_score": threat_result["threat_score"],
                "threat_level": threat_result["threat_level"],
                "threat_tags": threat_result["threat_tags"],
                "analyst_attention": "NOT REQUIRED",
                "xdr_assessment": "Routine activity with no immediate security concern identified." if not normalized_log.get("is_operational_health") else "Operational health event requiring operator attention.",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "event_summary": {
                    "event_name": normalized_log.get("event_name", "Unknown"),
                    "region": normalized_log.get("region", "Unknown"),
                    "source_ip": normalized_log.get("source_ip", "Unknown"),
                    "timestamp": iso_ts or str(normalized_log.get("event_time", "")),
                    "event_id": str(event_id or "")
                },
                "raw_log": normalized_log.get("raw_log")
            }

            logger.info(
                f"Event {event_id} evaluated as non-incident ({category}, risk={risk_result['score']}). "
                "Indexed as event without security incident."
            )
            logger.info("Incident Processing Completed")
            logger.info("=" * 60)
            return non_incident_event


incident_pipeline = IncidentPipeline()