from app.normalizer.base import BaseNormalizer


class GCPNormalizer(BaseNormalizer):
    """
    Normalizer for Google Cloud Audit Logs.
    """

    def normalize(self, log):

        if not isinstance(log, dict):
            raise ValueError("GCP log must be a dictionary.")

        payload = log.get("protoPayload", {})

        auth = payload.get("authenticationInfo", {})

        username = (
            auth.get("principalEmail")
            or log.get("username")
        )

        event_name = (
            payload.get("methodName")
            or "Unknown Event"
        )

        resource = (
            payload.get("resourceName")
            or log.get("resourceName")
        )

        source_ip = (
            payload.get("callerIp")
            or log.get("source_ip")
        )

        region = (
            log.get("resourceLocation")
            or log.get("location")
        )

        event_time = (
            log.get("timestamp")
            or log.get("receiveTimestamp")
        )

        search_text = self.build_search_text({

            "eventName": event_name,
            "message": str(log)

        })

        event_type = self.classify_event(search_text)

        return {

            "provider": "GCP",

            "username": username,

            "event_name": event_name,

            "event_type": event_type,

            "resource": resource,

            "source_ip": source_ip,

            "region": region,

            "event_time": event_time,

            "raw_log": log

        }


gcp_normalizer = GCPNormalizer()