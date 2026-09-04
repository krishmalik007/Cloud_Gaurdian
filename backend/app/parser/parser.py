from app.logger import logger


class LogParser:
    """
    Parses raw cloud logs into a common intermediate format.

    Handles both the existing /logs/ API format and real CloudTrail events
    received through the SQS/EventBridge integration.

    CloudTrail field mapping:
        eventName        -> event_name
        sourceIPAddress  -> source_ip
        eventTime        -> event_time
        awsRegion        -> region   (CloudTrail uses awsRegion, not region)
        userIdentity     -> username (extracted from userName or principalId)
    """

    def parse(self, log_data: dict) -> dict:

        if not isinstance(log_data, dict):
            raise ValueError("Log must be a dictionary.")

        provider = log_data.get("provider", "Unknown")

        # Extract username from userIdentity (CloudTrail) or flat "username" field
        user_identity = log_data.get("userIdentity", {})
        if isinstance(user_identity, dict):
            username = (
                user_identity.get("userName")
                or user_identity.get("principalId")
            )
        else:
            username = None
        username = username or log_data.get("username")

        # region: CloudTrail uses "awsRegion"; fallback to "region"
        region = log_data.get("awsRegion") or log_data.get("region")

        parsed_log = {
            "provider": provider,
            "username": username,
            "event_name": log_data.get("eventName"),
            "source_ip": log_data.get("sourceIPAddress"),
            "event_time": log_data.get("eventTime"),
            "region": region,
            # Carry the full original log through so the normalizer
            # has access to all fields (resources, userIdentity, etc.)
            "raw_log": log_data,
        }

        logger.info(f"Parsed Log: {parsed_log.get('event_name')} | "
                    f"Provider: {provider} | Region: {region}")

        return parsed_log


log_parser = LogParser()