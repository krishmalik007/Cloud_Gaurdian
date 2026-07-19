from app.logger import logger


class LogParser:
    """
    Parses raw cloud logs into a common format.
    """

    def parse(self, log_data: dict) -> dict:

        if not isinstance(log_data, dict):
            raise ValueError("Log must be a dictionary.")

        provider = log_data.get("provider", "Unknown")

        parsed_log = {
            "provider": provider,
            "username": log_data.get("username"),
            "event_name": log_data.get("eventName"),
            "source_ip": log_data.get("sourceIPAddress"),
            "event_time": log_data.get("eventTime"),
            "region": log_data.get("region")
        }

        logger.info(f"Parsed Log: {parsed_log}")

        return parsed_log


log_parser = LogParser()