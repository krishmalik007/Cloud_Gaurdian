from app.normalizer.base import BaseNormalizer


class AzureNormalizer(BaseNormalizer):
    """
    Normalizer for Azure Activity Logs,
    Azure Sign-In Logs and Microsoft Defender alerts.
    """

    def normalize(self, log):

        if not isinstance(log, dict):
            raise ValueError("Azure log must be a dictionary.")

        identity = log.get("identity", {})
        claims = identity.get("claims", {})

        username = (
            claims.get("name")
            or claims.get("upn")
            or log.get("caller")
            or log.get("username")
        )

        operation = log.get("operationName")

        if isinstance(operation, dict):
            event_name = (
                operation.get("value")
                or operation.get("localizedValue")
            )
        else:
            event_name = operation

        event_name = event_name or "Unknown Event"

        source_ip = (
            log.get("callerIpAddress")
            or log.get("ipAddress")
            or log.get("source_ip")
        )

        region = (
            log.get("resourceLocation")
            or log.get("location")
        )

        event_time = (
            log.get("eventTimestamp")
            or log.get("time")
            or log.get("timestamp")
        )

        resource = (
            log.get("resourceId")
            or log.get("resourceGroupName")
        )

        search_text = self.build_search_text({

            "operationName": event_name,
            "message": str(log)

        })

        event_type = self.classify_event(search_text)

        return {

            "provider": "AZURE",

            "username": username,

            "event_name": event_name,

            "event_type": event_type,

            "resource": resource,

            "source_ip": source_ip,

            "region": region,

            "event_time": event_time,

            "raw_log": log

        }


azure_normalizer = AzureNormalizer()