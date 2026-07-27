from app.normalizer.base import BaseNormalizer


class AWSNormalizer(BaseNormalizer):
    """
    Normalizer for AWS logs such as:
    - CloudTrail
    - GuardDuty
    - IAM
    - S3
    """

    def normalize(self, log):

        if not isinstance(log, dict):
            raise ValueError("AWS log must be a dictionary.")

        username = (
            log.get("userIdentity", {})
               .get("userName")
            or log.get("userIdentity", {})
                  .get("principalId")
            or log.get("username")
        )

        event_name = (
            log.get("eventName")
            or "Unknown Event"
        )

        source_ip = (
            log.get("sourceIPAddress")
            or log.get("source_ip")
        )

        region = (
            log.get("awsRegion")
            or log.get("region")
        )

        event_time = (
            log.get("eventTime")
            or log.get("event_time")
        )

        resource = None

        resources = log.get("resources")

        if isinstance(resources, list) and resources:

            first = resources[0]

            if isinstance(first, dict):
                resource = (
                    first.get("ARN")
                    or first.get("resourceName")
                )

        search_text = self.build_search_text({

            "eventName": event_name,

            "message": str(log)

        })

        event_type = self.classify_event(search_text)

        normalized_log = {

            "provider": "AWS",

            "username": username,

            "event_name": event_name,

            "event_type": event_type,

            "resource": resource,

            "source_ip": source_ip,

            "region": region,

            "event_time": event_time,

            "raw_log": log

        }

        return normalized_log


aws_normalizer = AWSNormalizer()