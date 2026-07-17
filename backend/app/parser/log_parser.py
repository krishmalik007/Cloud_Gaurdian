"""
Cloud Guardian — Log Parser Module.

Parses raw logs from AWS CloudTrail, AWS VPC Flow Logs, and Azure Activity Logs
into structured dictionaries ready for normalization.
"""

from typing import Any

from app.logger import logger


class LogParser:
    """
    Parses raw cloud provider logs into a structured intermediate format.
    Each parser method extracts relevant fields from the provider-specific schema.
    """

    # Mapping of AWS service sources to human-readable service names
    AWS_SERVICE_MAP: dict[str, str] = {
        "signin.amazonaws.com": "IAM",
        "iam.amazonaws.com": "IAM",
        "s3.amazonaws.com": "S3",
        "ec2.amazonaws.com": "EC2",
        "lambda.amazonaws.com": "Lambda",
        "rds.amazonaws.com": "RDS",
        "kms.amazonaws.com": "KMS",
        "sts.amazonaws.com": "STS",
        "cloudtrail.amazonaws.com": "CloudTrail",
    }

    # Event name to category mapping
    EVENT_CATEGORY_MAP: dict[str, str] = {
        "ConsoleLogin": "Authentication",
        "AssumeRole": "Authentication",
        "GetSessionToken": "Authentication",
        "CreateUser": "IAM",
        "DeleteUser": "IAM",
        "AttachUserPolicy": "IAM",
        "DetachUserPolicy": "IAM",
        "CreateAccessKey": "IAM",
        "DeleteAccessKey": "IAM",
        "PutBucketPolicy": "Storage",
        "DeleteBucket": "Storage",
        "GetObject": "Storage",
        "PutObject": "Storage",
        "RunInstances": "Compute",
        "TerminateInstances": "Compute",
        "StartInstances": "Compute",
        "StopInstances": "Compute",
        "AuthorizeSecurityGroupIngress": "Network",
        "RevokeSecurityGroupIngress": "Network",
        "CreateSecurityGroup": "Network",
        "DeleteSecurityGroup": "Network",
    }

    def parse_cloudtrail(self, raw_log: dict[str, Any]) -> dict[str, Any]:
        """
        Parse an AWS CloudTrail log event.

        Args:
            raw_log: Raw CloudTrail event dictionary.

        Returns:
            Structured dictionary with extracted fields.
        """
        try:
            user_identity = raw_log.get("userIdentity", {})
            username = (
                user_identity.get("userName")
                or user_identity.get("principalId", "")
                or user_identity.get("arn", "unknown")
            )

            event_name = raw_log.get("eventName", "Unknown")
            event_source = raw_log.get("eventSource", "")
            service = self.AWS_SERVICE_MAP.get(event_source, "CloudTrail")
            category = self.EVENT_CATEGORY_MAP.get(event_name, "Unknown")

            # Determine status from errorCode
            error_code = raw_log.get("errorCode")
            status = "Failure" if error_code else "Success"

            return {
                "timestamp": raw_log.get("eventTime", ""),
                "cloud_provider": "AWS",
                "service": service,
                "event_name": event_name,
                "event_category": category,
                "user": str(username),
                "source_ip": raw_log.get("sourceIPAddress", ""),
                "destination_ip": "",
                "resource": event_source,
                "action": event_name,
                "status": status,
                "region": raw_log.get("awsRegion", ""),
                "raw_log": raw_log,
            }
        except Exception as e:
            logger.error(f"Failed to parse CloudTrail log: {e}")
            raise ValueError(f"Invalid CloudTrail log format: {e}") from e

    def parse_vpc_flow(self, raw_log: dict[str, Any]) -> dict[str, Any]:
        """
        Parse an AWS VPC Flow Log record.

        Args:
            raw_log: Raw VPC Flow Log dictionary.

        Returns:
            Structured dictionary with extracted fields.
        """
        try:
            from datetime import datetime, timezone

            action = raw_log.get("action", "UNKNOWN")
            start_ts = raw_log.get("start", 0)

            timestamp = datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat() if start_ts else ""

            protocol_map = {6: "TCP", 17: "UDP", 1: "ICMP"}
            protocol = protocol_map.get(raw_log.get("protocol", 0), str(raw_log.get("protocol", "")))

            return {
                "timestamp": timestamp,
                "cloud_provider": "AWS",
                "service": "VPC Flow Logs",
                "event_name": f"FlowLog-{action}",
                "event_category": "Network",
                "user": raw_log.get("account_id", ""),
                "source_ip": raw_log.get("srcaddr", ""),
                "destination_ip": raw_log.get("dstaddr", ""),
                "resource": raw_log.get("interface_id", ""),
                "action": action,
                "status": "Success" if action == "ACCEPT" else "Failure",
                "region": "",
                "raw_log": raw_log,
                "_extra": {
                    "protocol": protocol,
                    "src_port": raw_log.get("srcport", 0),
                    "dst_port": raw_log.get("dstport", 0),
                    "packets": raw_log.get("packets", 0),
                    "bytes": raw_log.get("bytes", 0),
                },
            }
        except Exception as e:
            logger.error(f"Failed to parse VPC Flow log: {e}")
            raise ValueError(f"Invalid VPC Flow Log format: {e}") from e

    def parse_azure_activity(self, raw_log: dict[str, Any]) -> dict[str, Any]:
        """
        Parse an Azure Activity Log event.

        Args:
            raw_log: Raw Azure Activity Log dictionary.

        Returns:
            Structured dictionary with extracted fields.
        """
        try:
            operation = raw_log.get("operationName", {})
            op_value = operation.get("value", "") if isinstance(operation, dict) else str(operation)
            op_localized = operation.get("localizedValue", op_value) if isinstance(operation, dict) else str(operation)

            # Extract action from operation name (e.g., "Microsoft.Compute/virtualMachines/start/action" -> "start")
            parts = op_value.split("/")
            action = parts[-2] if len(parts) >= 2 and parts[-1] == "action" else parts[-1] if parts else op_value

            # Determine category from resource type
            category = "Unknown"
            if "virtualMachines" in op_value or "Compute" in op_value:
                category = "Compute"
            elif "networkSecurityGroups" in op_value or "Network" in op_value:
                category = "Network"
            elif "storageAccounts" in op_value or "Storage" in op_value:
                category = "Storage"
            elif "roleAssignments" in op_value or "Authorization" in op_value:
                category = "Authorization"

            result_type = raw_log.get("resultType", "Success")
            status = "Success" if result_type.lower() in ("success", "succeeded") else "Failure"

            return {
                "timestamp": raw_log.get("time", ""),
                "cloud_provider": "Azure",
                "service": "Azure Activity Logs",
                "event_name": op_localized,
                "event_category": category,
                "user": raw_log.get("caller", ""),
                "source_ip": raw_log.get("callerIpAddress", ""),
                "destination_ip": "",
                "resource": raw_log.get("resourceId", ""),
                "action": action,
                "status": status,
                "region": "",
                "raw_log": raw_log,
            }
        except Exception as e:
            logger.error(f"Failed to parse Azure Activity log: {e}")
            raise ValueError(f"Invalid Azure Activity Log format: {e}") from e

    def parse(self, log_type: str, raw_log: dict[str, Any]) -> dict[str, Any]:
        """
        Route a raw log to the correct parser based on log type.

        Args:
            log_type: One of 'cloudtrail', 'vpc_flow', 'azure_activity'.
            raw_log: The raw log dictionary.

        Returns:
            Parsed and structured dictionary.

        Raises:
            ValueError: If the log type is unsupported.
        """
        parsers = {
            "cloudtrail": self.parse_cloudtrail,
            "vpc_flow": self.parse_vpc_flow,
            "azure_activity": self.parse_azure_activity,
        }

        parser_fn = parsers.get(log_type.lower())
        if not parser_fn:
            raise ValueError(f"Unsupported log type: '{log_type}'. Supported: {list(parsers.keys())}")

        return parser_fn(raw_log)


# Singleton instance
log_parser = LogParser()
