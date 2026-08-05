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