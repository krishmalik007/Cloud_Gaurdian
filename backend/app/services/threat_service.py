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

        return indicators


threat_service = ThreatService()