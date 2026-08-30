from app.logger import logger


class RiskEngine:
    """
    Risk Scoring Engine

    Calculates incident severity based on:
    - Correlation alerts
    - IOC matches
    """

    def calculate_risk(self, normalized_log: dict | list, alerts: list = None):
        if isinstance(normalized_log, list):
            alerts = normalized_log
            normalized_log = {}
        if alerts is None:
            alerts = []

        score = 0

        # --------------------------------
        # Alert-based scoring
        # --------------------------------
        score += len(alerts) * 10

        # --------------------------------
        # IOC-based scoring
        # --------------------------------
        for ioc in normalized_log.get("ioc_matches", []):

            severity = ioc["severity"].upper()

            if severity == "LOW":
                score += 10

            elif severity == "MEDIUM":
                score += 25

            elif severity == "HIGH":
                score += 50

            elif severity == "CRITICAL":
                score += 75

        # --------------------------------
        # Cap Score
        # --------------------------------
        score = min(score, 100)

        # --------------------------------
        # Risk Level
        # --------------------------------
        if score >= 80:
            level = "CRITICAL"

        elif score >= 60:
            level = "HIGH"

        elif score >= 30:
            level = "MEDIUM"

        else:
            level = "LOW"

        logger.info(
            f"Risk Score={score} Level={level}"
        )

        return {
            "score": score,
            "level": level,
            "alert_count": len(alerts),
            "alerts": alerts
        }


risk_engine = RiskEngine()