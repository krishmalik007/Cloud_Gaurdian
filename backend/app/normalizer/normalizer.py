import re

from app.logger import logger


class LogNormalizer:
    """
    Generic Log Normalizer

    This normalizer accepts logs from different providers
    (AWS, Azure, GCP, Windows, Linux, etc.)
    and converts them into one standard format.
    """

    EVENT_RULES = {

        "LOGIN": [

            r"\blog.?in\b",
            r"\blogon\b",
            r"\bsign.?in\b",
            r"\bsign.?on\b",
            r"\bauth\b",
            r"\bauthentication\b",
            r"\bauthenticated\b",
            r"\bauthenticate\b",
            r"\bconsole.?login\b",
            r"\bssh\b",
            r"\baccepted password\b",
            r"\bsuccessful login\b",
            r"\blogin success\b",
            r"\buser login\b"

        ],

        "LOGOUT": [

            r"\blogout\b",
            r"\bsign.?out\b",
            r"\blog.?off\b"

        ],

        "CREATE": [

            r"\bcreate\b",
            r"\bcreated\b",
            r"\bcreation\b",
            r"\badd\b",
            r"\badded\b",
            r"\bprovision\b",
            r"\bnew\b"

        ],

        "DELETE": [

            r"\bdelete\b",
            r"\bdeleted\b",
            r"\bremove\b",
            r"\bremoved\b",
            r"\bterminate\b",
            r"\bdestroy\b"

        ],

        "UPDATE": [

            r"\bupdate\b",
            r"\bupdated\b",
            r"\bmodify\b",
            r"\bmodified\b",
            r"\bchange\b",
            r"\bedit\b",
            r"\bedited\b"

        ],

        "UPLOAD": [

            r"\bupload\b",
            r"\buploaded\b",
            r"\bput object\b"

        ],

        "DOWNLOAD": [

            r"\bdownload\b",
            r"\bdownloaded\b",
            r"\bfetch\b"

        ],

        "FAILED_LOGIN": [

            r"\bfailed login\b",
            r"\blogin failed\b",
            r"\binvalid password\b",
            r"\bauthentication failed\b",
            r"\baccess denied\b"

        ]

    }

    def detect_provider(self, log):
        """
        Detect cloud provider or operating system.
        """

        provider = (

            log.get("provider")
            or log.get("cloud")
            or log.get("vendor")
            or log.get("platform")
            or log.get("source")
            or "UNKNOWN"

        )

        return str(provider).strip().upper()

    def detect_event_name(self, log):
        """
        Find the primary event name.
        """

        return (

            log.get("event_name")
            or log.get("eventName")
            or log.get("operationName")
            or log.get("activity")
            or log.get("action")
            or "Unknown Event"

        )

    def build_search_text(self, log):
        """
        Combine multiple log fields into one searchable string.
        """

        searchable_fields = [

            "event_name",
            "eventName",
            "operationName",
            "activity",
            "action",
            "message",
            "description"

        ]

        values = []

        for field in searchable_fields:

            value = log.get(field)

            if value:
                values.append(str(value))

        return " ".join(values).lower().strip()

    def classify_event(self, search_text):
        """
        Detect standardized event type using regex.
        """

        for event_type, patterns in self.EVENT_RULES.items():

            for pattern in patterns:

                if re.search(pattern, search_text):
                    return event_type

        return "UNKNOWN"

    def build_normalized_log(
        self,
        log,
        provider,
        event_name,
        event_type
    ):
        """
        Build standardized log.
        """

        normalized_log = {

            "provider": provider,

            "username": (
                log.get("username")
                or log.get("user")
                or log.get("principal")
            ),

            "event_name": event_name,

            "event_type": event_type,

            "source_ip": (
                log.get("source_ip")
                or log.get("sourceIPAddress")
                or log.get("ip")
                or log.get("client_ip")
            ),

            "event_time": (
                log.get("event_time")
                or log.get("eventTime")
                or log.get("timestamp")
            ),

            "region": (
                log.get("region")
                or log.get("location")
            )

        }

        return normalized_log

    def normalize(self, parsed_log):
        """
        Main normalization function.
        """

        if not isinstance(parsed_log, dict):
            raise ValueError("Parsed log must be a dictionary.")

        provider = self.detect_provider(parsed_log)

        event_name = self.detect_event_name(parsed_log)

        search_text = self.build_search_text(parsed_log)

        event_type = self.classify_event(search_text)

        normalized_log = self.build_normalized_log(

            parsed_log,
            provider,
            event_name,
            event_type

        )

        logger.info(f"Normalized Log: {normalized_log}")

        return normalized_log


log_normalizer = LogNormalizer()