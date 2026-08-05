from app.threat_intelligence.ioc_database import (
    MALICIOUS_IPS,
    MALICIOUS_DOMAINS,
    SUSPICIOUS_USERS
)


class ThreatEngine:
    """
    Threat Intelligence Engine

    Checks incoming logs against known Indicators of Compromise (IOCs).
    """

    def analyze(self, log: dict):

        tags = []
        score = 0

        # -----------------------------
        # Source IP Check
        # -----------------------------
        ip = log.get("source_ip")

        if ip and ip in MALICIOUS_IPS:
            tags.append("MALICIOUS_IP")
            score += 50

        # -----------------------------
        # Domain Check
        # -----------------------------
        domain = log.get("domain")

        if domain and domain in MALICIOUS_DOMAINS:
            tags.append("MALICIOUS_DOMAIN")
            score += 40

        # -----------------------------
        # Username Check
        # -----------------------------
        username = log.get("username")

        if username and username.lower() in {
            user.lower() for user in SUSPICIOUS_USERS
        }:
            tags.append("SUSPICIOUS_USERNAME")
            score += 20

        # -----------------------------
        # Determine Threat Level
        # -----------------------------
        if score >= 80:
            level = "CRITICAL"
        elif score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        elif score > 0:
            level = "LOW"
        else:
            level = "NONE"

        return {
            "threat_score": score,
            "threat_level": level,
            "threat_tags": tags
        }


threat_engine = ThreatEngine()