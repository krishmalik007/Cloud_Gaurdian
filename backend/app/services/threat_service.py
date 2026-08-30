from app.storage.ioc_repository import ioc_repository


class ThreatService:
    """
    Threat Intelligence Service

    Uses IOC Management (OpenSearch)
    instead of hardcoded IOC lists.
    """

    # ------------------------------------
    # Search IOC
    # ------------------------------------
    def lookup(self, value: str):

        return ioc_repository.search_value(value)

    def check_ip(self, ip: str):
        ioc = self.lookup(ip)
        if ioc and ioc.get("enabled", True):
            return {
                "ioc_type": "IP",
                "value": ip,
                "malicious": True,
                "severity": ioc.get("severity", "MEDIUM"),
                "source": ioc.get("source", "MANUAL"),
                "description": ioc.get("description", "Registered malicious IP indicator."),
                "created_at": ioc.get("created_at"),
                "enabled": True
            }
        return {
            "ioc_type": "IP",
            "value": ip,
            "malicious": False,
            "severity": "LOW",
            "source": "DATABASE",
            "description": "No active threat indicators match this IP pattern.",
            "created_at": None,
            "enabled": False
        }

    def check_domain(self, domain: str):
        ioc = self.lookup(domain)
        if ioc and ioc.get("enabled", True):
            return {
                "ioc_type": "DOMAIN",
                "value": domain,
                "malicious": True,
                "severity": ioc.get("severity", "MEDIUM"),
                "source": ioc.get("source", "MANUAL"),
                "description": ioc.get("description", "Registered malicious domain indicator."),
                "created_at": ioc.get("created_at"),
                "enabled": True
            }
        return {
            "ioc_type": "DOMAIN",
            "value": domain,
            "malicious": False,
            "severity": "LOW",
            "source": "DATABASE",
            "description": "No active threat indicators match this domain pattern.",
            "created_at": None,
            "enabled": False
        }

    def check_username(self, username: str):
        ioc = self.lookup(username)
        if ioc and ioc.get("enabled", True):
            return {
                "ioc_type": "USERNAME",
                "value": username,
                "malicious": True,
                "severity": ioc.get("severity", "MEDIUM"),
                "source": ioc.get("source", "MANUAL"),
                "description": ioc.get("description", "Suspicious watchlist username."),
                "created_at": ioc.get("created_at"),
                "enabled": True
            }
        return {
            "ioc_type": "USERNAME",
            "value": username,
            "malicious": False,
            "severity": "LOW",
            "source": "DATABASE",
            "description": "No active watchlist records match this username.",
            "created_at": None,
            "enabled": False
        }

    # ------------------------------------
    # Analyze Log
    # ------------------------------------
    def analyze_log(
        self,
        normalized_log: dict
    ):

        indicators = []

        # -----------------------------
        # IP
        # -----------------------------
        ip = normalized_log.get("source_ip")

        if ip:

            ioc = self.lookup(ip)

            if ioc and ioc["enabled"]:

                indicators.append(
                    {
                        "type": "IP",
                        "value": ip,
                        "severity": ioc["severity"]
                    }
                )

        # -----------------------------
        # Username
        # -----------------------------
        username = normalized_log.get("username")

        if username:

            ioc = self.lookup(username)

            if ioc and ioc["enabled"]:

                indicators.append(
                    {
                        "type": "USERNAME",
                        "value": username,
                        "severity": ioc["severity"]
                    }
                )

        # -----------------------------
        # Domain
        # -----------------------------
        domain = normalized_log.get("domain")

        if domain:

            ioc = self.lookup(domain)

            if ioc and ioc["enabled"]:

                indicators.append(
                    {
                        "type": "DOMAIN",
                        "value": domain,
                        "severity": ioc["severity"]
                    }
                )

        normalized_log["ioc_matches"] = indicators

        score = 0
        tags = []

        for indicator in indicators:
            ind_type = indicator["type"]
            severity = indicator["severity"].upper()

            multiplier = 1.0
            if severity == "CRITICAL":
                multiplier = 1.0
            elif severity == "HIGH":
                multiplier = 0.8
            elif severity == "MEDIUM":
                multiplier = 0.5
            elif severity == "LOW" or severity == "INFO":
                multiplier = 0.2

            if ind_type == "IP":
                score += int(50 * multiplier)
                tags.append("MALICIOUS_IP")
            elif ind_type == "DOMAIN":
                score += int(40 * multiplier)
                tags.append("MALICIOUS_DOMAIN")
            elif ind_type == "USERNAME":
                score += int(20 * multiplier)
                tags.append("SUSPICIOUS_USERNAME")

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


threat_service = ThreatService()