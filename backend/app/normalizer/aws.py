from typing import Optional
from app.normalizer.base import BaseNormalizer
from app.utils.redaction import redact_sensitive_data


# ---------------------------------------------------------------------------
# AWS CloudTrail event classification table
#
# Maps (eventSource prefix, eventName) → event_type.
#
# Rules are evaluated in ORDER.  The first match wins.
# eventSource is matched as a prefix of the actual source string
# (e.g. "sts." matches "sts.amazonaws.com").
# eventName is matched exactly (case-sensitive, as CloudTrail provides it).
#
# Use None for eventSource to match any source for that eventName.
# Use None for eventName to match all events from that source.
# ---------------------------------------------------------------------------

_AWS_EVENT_TYPE_RULES = [

    # ------------------------------------------------------------------
    # AUTHENTICATION — credential / session operations
    # ------------------------------------------------------------------
    ("sts.",        "AssumeRole",                       "AUTHENTICATION"),
    ("sts.",        "AssumeRoleWithSAML",               "AUTHENTICATION"),
    ("sts.",        "AssumeRoleWithWebIdentity",        "AUTHENTICATION"),
    ("sts.",        "GetSessionToken",                  "AUTHENTICATION"),
    ("sts.",        "GetFederationToken",               "AUTHENTICATION"),
    ("signin.",     "ConsoleLogin",                     "AUTHENTICATION"),
    (None,          "ConsoleLogin",                     "AUTHENTICATION"),

    # ------------------------------------------------------------------
    # IAM — identity and access management changes
    # ------------------------------------------------------------------
    ("iam.",        "CreateUser",                       "IAM"),
    ("iam.",        "DeleteUser",                       "IAM"),
    ("iam.",        "UpdateUser",                       "IAM"),
    ("iam.",        "CreateRole",                       "IAM"),
    ("iam.",        "DeleteRole",                       "IAM"),
    ("iam.",        "UpdateRole",                       "IAM"),
    ("iam.",        "AttachRolePolicy",                 "ATTACH_POLICY"),
    ("iam.",        "DetachRolePolicy",                 "DETACH_POLICY"),
    ("iam.",        "AttachUserPolicy",                 "ATTACH_POLICY"),
    ("iam.",        "DetachUserPolicy",                 "DETACH_POLICY"),
    ("iam.",        "AttachGroupPolicy",                "ATTACH_POLICY"),
    ("iam.",        "DetachGroupPolicy",                "DETACH_POLICY"),
    ("iam.",        "PutRolePolicy",                    "UPDATE_POLICY"),
    ("iam.",        "PutUserPolicy",                    "UPDATE_POLICY"),
    ("iam.",        "PutGroupPolicy",                   "UPDATE_POLICY"),
    ("iam.",        "DeleteRolePolicy",                 "DELETE_POLICY"),
    ("iam.",        "DeleteUserPolicy",                 "DELETE_POLICY"),
    ("iam.",        "DeleteGroupPolicy",                "DELETE_POLICY"),
    ("iam.",        "CreateAccessKey",                  "IAM"),
    ("iam.",        "DeleteAccessKey",                  "IAM"),
    ("iam.",        "UpdateAccessKey",                  "IAM"),
    ("iam.",        "CreateLoginProfile",               "IAM"),
    ("iam.",        "DeleteLoginProfile",               "IAM"),
    ("iam.",        "UpdateLoginProfile",               "IAM"),
    ("iam.",        "EnableMFADevice",                  "IAM"),
    ("iam.",        "DeactivateMFADevice",              "IAM"),
    ("iam.",        "CreateGroup",                      "IAM"),
    ("iam.",        "DeleteGroup",                      "IAM"),
    ("iam.",        "AddUserToGroup",                   "IAM"),
    ("iam.",        "RemoveUserFromGroup",              "IAM"),
    ("iam.",        "CreatePolicy",                     "CREATE_POLICY"),
    ("iam.",        "DeletePolicy",                     "DELETE_POLICY"),
    ("iam.",        "CreatePolicyVersion",              "UPDATE_POLICY"),
    ("iam.",        "SetDefaultPolicyVersion",          "UPDATE_POLICY"),
    ("iam.",        "DeletePolicyVersion",              "DELETE_POLICY"),

    # ------------------------------------------------------------------
    # COMPUTE — EC2 / Lambda / ECS instance lifecycle
    # ------------------------------------------------------------------
    ("ec2.",        "RunInstances",                     "COMPUTE"),
    ("ec2.",        "TerminateInstances",               "COMPUTE"),
    ("ec2.",        "StartInstances",                   "COMPUTE"),
    ("ec2.",        "StopInstances",                    "COMPUTE"),
    ("ec2.",        "RebootInstances",                  "COMPUTE"),
    ("ec2.",        "CreateImage",                      "COMPUTE"),
    ("ec2.",        "DeregisterImage",                  "COMPUTE"),
    ("lambda.",     None,                               "COMPUTE"),
    ("ecs.",        None,                               "COMPUTE"),

    # ------------------------------------------------------------------
    # STORAGE — S3 / EBS / EFS
    # ------------------------------------------------------------------
    ("s3.",         "CreateBucket",                     "STORAGE"),
    ("s3.",         "DeleteBucket",                     "STORAGE"),
    ("s3.",         "PutBucketPolicy",                  "STORAGE"),
    ("s3.",         "DeleteBucketPolicy",               "STORAGE"),
    ("s3.",         "PutBucketAcl",                     "STORAGE"),
    ("s3.",         "PutObject",                        "STORAGE"),
    ("s3.",         "DeleteObject",                     "STORAGE"),
    ("s3.",         "GetObject",                        "STORAGE"),
    ("ec2.",        "CreateVolume",                     "STORAGE"),
    ("ec2.",        "DeleteVolume",                     "STORAGE"),
    ("ec2.",        "CreateSnapshot",                   "STORAGE"),
    ("ec2.",        "DeleteSnapshot",                   "STORAGE"),
    ("ec2.",        "ModifySnapshotAttribute",          "STORAGE"),

    # ------------------------------------------------------------------
    # NETWORK — VPC / security groups / routing
    # ------------------------------------------------------------------
    ("ec2.",        "CreateSecurityGroup",              "NETWORK"),
    ("ec2.",        "DeleteSecurityGroup",              "NETWORK"),
    ("ec2.",        "AuthorizeSecurityGroupIngress",    "NETWORK"),
    ("ec2.",        "RevokeSecurityGroupIngress",       "NETWORK"),
    ("ec2.",        "AuthorizeSecurityGroupEgress",     "NETWORK"),
    ("ec2.",        "RevokeSecurityGroupEgress",        "NETWORK"),
    ("ec2.",        "CreateVpc",                        "NETWORK"),
    ("ec2.",        "DeleteVpc",                        "NETWORK"),
    ("ec2.",        "CreateSubnet",                     "NETWORK"),
    ("ec2.",        "DeleteSubnet",                     "NETWORK"),
    ("ec2.",        "CreateInternetGateway",            "NETWORK"),
    ("ec2.",        "AttachInternetGateway",            "NETWORK"),
    ("ec2.",        "CreateRouteTable",                 "NETWORK"),
    ("ec2.",        "CreateRoute",                      "NETWORK"),
    ("elasticloadbalancing.", None,                     "NETWORK"),

    # ------------------------------------------------------------------
    # DATABASE — RDS / DynamoDB / ElastiCache
    # ------------------------------------------------------------------
    ("rds.",        "CreateDBInstance",                 "DATABASE"),
    ("rds.",        "DeleteDBInstance",                 "DATABASE"),
    ("rds.",        "ModifyDBInstance",                 "DATABASE"),
    ("rds.",        "CreateDBSnapshot",                 "DATABASE"),
    ("rds.",        "DeleteDBSnapshot",                 "DATABASE"),
    ("rds.",        "RestoreDBInstanceFromDBSnapshot",  "DATABASE"),
    ("rds.",        "ModifyDBSnapshotAttribute",        "DATABASE"),
    ("dynamodb.",   None,                               "DATABASE"),
    ("elasticache.", None,                              "DATABASE"),

    # ------------------------------------------------------------------
    # SECURITY — GuardDuty / SecurityHub / Macie / Inspector
    # ------------------------------------------------------------------
    ("guardduty.",      None,                           "SECURITY"),
    ("securityhub.",    None,                           "SECURITY"),
    ("macie2.",         None,                           "SECURITY"),
    ("inspector2.",     None,                           "SECURITY"),
    ("access-analyzer.", None,                          "SECURITY"),
    ("waf.",            None,                           "SECURITY"),
    ("wafv2.",          None,                           "SECURITY"),
    ("shield.",         None,                           "SECURITY"),
    ("kms.",        "DisableKey",                       "SECURITY"),
    ("kms.",        "ScheduleKeyDeletion",              "SECURITY"),
    ("kms.",        "DisableKeyRotation",               "SECURITY"),

    # ------------------------------------------------------------------
    # LOGGING — CloudTrail / CloudWatch Logs
    # ------------------------------------------------------------------
    ("cloudtrail.",     "CreateTrail",                  "LOGGING"),
    ("cloudtrail.",     "DeleteTrail",                  "LOGGING"),
    ("cloudtrail.",     "UpdateTrail",                  "LOGGING"),
    ("cloudtrail.",     "StartLogging",                 "LOGGING"),
    ("cloudtrail.",     "StopLogging",                  "LOGGING"),
    ("cloudtrail.",     "PutEventSelectors",            "LOGGING"),
    ("logs.",           None,                           "LOGGING"),

    # ------------------------------------------------------------------
    # MONITORING — CloudWatch metrics / alarms / notifications
    # ------------------------------------------------------------------
    ("monitoring.",     None,                           "MONITORING"),
    ("cloudwatch.",     None,                           "MONITORING"),
    ("notifications.",  None,                           "MONITORING"),
]


class AWSNormalizer(BaseNormalizer):
    """
    Normalizer for AWS logs such as:
    - CloudTrail (received via SQS/EventBridge or /logs/ API)
    - GuardDuty
    - IAM
    - S3

    Accepts both:
    1. Raw CloudTrail event dicts (from the /logs/ API route)
       Fields: eventName, awsRegion, sourceIPAddress, eventTime, userIdentity
    2. Pre-parsed dicts (from the Kafka consumer path via LogParser)
       Fields: event_name, region, source_ip, event_time, username, raw_log
    """

    # ------------------------------------------------------------------
    # AWS-specific event classification
    # ------------------------------------------------------------------

    def classify_aws_event(
        self,
        event_name: str,
        event_source: str,
        error_message: str = "",
        response_elements: dict = None,
        error_code: str = "",
        user_identity: dict = None,
    ) -> str:
        """
        Classify a CloudTrail event into a high-level event_type using the
        _AWS_EVENT_TYPE_RULES table above.

        Matching order:
        1. Failed authentication / login indicators for ConsoleLogin -> FAILED_LOGIN
        2. Root user ConsoleLogin -> ROOT_LOGIN
        3. eventSource prefix AND exact eventName
        4. eventSource prefix only (eventName=None rule)
        Falls back to the inherited BaseNormalizer.classify_event() which
        uses regex on the event name, then finally to "UNKNOWN".
        """
        # Handle ConsoleLogin failure check before static table mapping
        if event_name == "ConsoleLogin":
            resp = response_elements if isinstance(response_elements, dict) else {}
            err_msg_lower = (error_message or "").lower()
            err_code_lower = (error_code or "").lower()
            if (
                "fail" in err_msg_lower
                or "fail" in err_code_lower
                or resp.get("ConsoleLogin") == "Failure"
                or bool(error_message)
                or bool(error_code)
            ):
                return "FAILED_LOGIN"

            user_id_dict = user_identity if isinstance(user_identity, dict) else {}
            if user_id_dict.get("type") == "Root" or str(user_id_dict.get("arn", "")).endswith(":root"):
                return "ROOT_LOGIN"

        source_lower = (event_source or "").lower()
        for source_prefix, rule_event_name, event_type in _AWS_EVENT_TYPE_RULES:
            # Check source prefix (None means match any source)
            if source_prefix is not None:
                if not source_lower.startswith(source_prefix):
                    continue
            # Check event name (None means match any event from this source)
            if rule_event_name is not None:
                if event_name != rule_event_name:
                    continue
            return event_type

        # Fall back to the inherited regex-based classifier on the event name
        search_text = self.build_search_text({
            "eventName": event_name,
            "message": str(event_name),
        })
        return self.classify_event(search_text)

    # ------------------------------------------------------------------
    # AWS Region Resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_region_from_s3_key(key: str) -> Optional[str]:
        if not key:
            return None
        parts = key.split("/")
        for i, part in enumerate(parts):
            if part == "CloudTrail" and i + 1 < len(parts):
                candidate = parts[i + 1]
                if candidate and not candidate.isdigit() and len(candidate) >= 4:
                    return candidate
        return None

    @classmethod
    def resolve_aws_region(cls, log: dict, raw: dict) -> Optional[str]:
        """
        Preserve the actual AWS region from the event payload or metadata.
        Supports standard CloudTrail 'awsRegion', aliases ('region', 'aws_region'),
        nested EventBridge 'detail' structures, EventBridge envelope 'eventbridge_region',
        and S3 regional key partition paths.
        Distinguishes genuinely absent regions (returns None) from normalization defects.
        Never fabricates a default region like ap-south-1.
        """
        raw_dict = raw if isinstance(raw, dict) else {}
        log_dict = log if isinstance(log, dict) else {}
        detail_dict = raw_dict.get("detail") if isinstance(raw_dict.get("detail"), dict) else {}
        if not detail_dict and isinstance(log_dict.get("detail"), dict):
            detail_dict = log_dict.get("detail")

        candidates = [
            log_dict.get("region"),
            log_dict.get("awsRegion"),
            log_dict.get("aws_region"),
            raw_dict.get("awsRegion"),
            raw_dict.get("aws_region"),
            raw_dict.get("region"),
            detail_dict.get("awsRegion"),
            detail_dict.get("aws_region"),
            detail_dict.get("region"),
            raw_dict.get("eventbridge_region"),
            log_dict.get("eventbridge_region"),
        ]
        for c in candidates:
            if c is not None:
                val = str(c).strip()
                if val and val.lower() not in {"none", "null", "unknown", ""}:
                    return val

        # Check S3 key partition if present
        s3_key = raw_dict.get("s3_key") or log_dict.get("s3_key")
        if s3_key:
            region_from_key = cls._extract_region_from_s3_key(str(s3_key))
            if region_from_key:
                return region_from_key

        return None

    # ------------------------------------------------------------------
    # Main normalizer
    # ------------------------------------------------------------------

    def normalize(self, log):

        if not isinstance(log, dict):
            raise ValueError("AWS log must be a dictionary.")

        raw = log.get("raw_log", log)

        # ------------------------------------------------------------------
        # username
        # From parser: log["username"] already resolved from userIdentity.
        # From raw CloudTrail: read userIdentity directly.
        # Fallback to additionalEventData for failed console sign-ins.
        # ------------------------------------------------------------------
        user_identity = log.get("userIdentity", {})
        if not user_identity and isinstance(raw, dict):
            user_identity = raw.get("userIdentity", {})
        if isinstance(user_identity, dict):
            if user_identity.get("type") == "Root":
                username = user_identity.get("userName") or "root"
            else:
                username = (
                    user_identity.get("userName")
                    or user_identity.get("principalId")
                )
        else:
            username = None

        username = username or log.get("username")

        if not username and isinstance(raw, dict):
            add_data = raw.get("additionalEventData")
            if isinstance(add_data, dict):
                username = add_data.get("userName") or add_data.get("UserName")

        # ------------------------------------------------------------------
        # event_name
        # Pre-parsed path: "event_name"
        # Raw CloudTrail path: "eventName"
        # ------------------------------------------------------------------
        event_name = (
            log.get("event_name")
            or log.get("eventName")
            or "Unknown Event"
        )

        # ------------------------------------------------------------------
        # event_source & error indicators
        # Pre-parsed path: raw_log.eventSource / errorMessage / responseElements
        # Raw CloudTrail path: log.eventSource / errorMessage / responseElements
        # ------------------------------------------------------------------
        event_source = ""
        if isinstance(raw, dict):
            event_source = raw.get("eventSource", "")
        if not event_source:
            event_source = log.get("eventSource", "")

        error_message = ""
        if isinstance(raw, dict):
            error_message = raw.get("errorMessage") or ""
        if not error_message:
            error_message = log.get("errorMessage") or ""

        error_code = ""
        if isinstance(raw, dict):
            error_code = raw.get("errorCode") or ""
        if not error_code:
            error_code = log.get("errorCode") or ""

        response_elements = None
        if isinstance(raw, dict):
            response_elements = raw.get("responseElements")
        if response_elements is None and isinstance(log, dict):
            response_elements = log.get("responseElements")

        # ------------------------------------------------------------------
        # source_ip
        # Pre-parsed path: "source_ip"
        # Raw CloudTrail path: "sourceIPAddress"
        # ------------------------------------------------------------------
        source_ip = (
            log.get("source_ip")
            or log.get("sourceIPAddress")
        )

        # ------------------------------------------------------------------
        # region
        # Fully resolved across all aliases, payloads, and key partitions
        # ------------------------------------------------------------------
        region = self.resolve_aws_region(log, raw)

        # ------------------------------------------------------------------
        # event_time
        # Pre-parsed path: "event_time"
        # Raw CloudTrail path: "eventTime"
        # ------------------------------------------------------------------
        event_time = (
            log.get("event_time")
            or log.get("eventTime")
        )

        # ------------------------------------------------------------------
        # event_id
        # CloudTrail standard field: "eventID"
        # ------------------------------------------------------------------
        event_id = (
            log.get("event_id")
            or log.get("eventID")
            or (raw.get("eventID") if isinstance(raw, dict) else None)
        )

        # ------------------------------------------------------------------
        # resource — from CloudTrail resources list
        # ------------------------------------------------------------------
        resource = None
        resources = raw.get("resources") if isinstance(raw, dict) else None

        if isinstance(resources, list) and resources:
            first = resources[0]
            if isinstance(first, dict):
                resource = (
                    first.get("ARN")
                    or first.get("resourceName")
                )

        # ------------------------------------------------------------------
        # Contextual AWS Service Activity & Operational Health Evaluation
        # ------------------------------------------------------------------
        user_identity_dict = user_identity if isinstance(user_identity, dict) else {}
        invoked_by = user_identity_dict.get("invokedBy", "")
        user_arn = user_identity_dict.get("arn", "")
        session_context = user_identity_dict.get("sessionContext", {}) if isinstance(user_identity_dict, dict) else {}
        session_issuer = session_context.get("sessionIssuer", {}) if isinstance(session_context, dict) else {}
        issuer_arn = session_issuer.get("arn", "") if isinstance(session_issuer, dict) else ""
        request_params = (raw.get("requestParameters") if isinstance(raw, dict) else None) or (log.get("requestParameters") if isinstance(log, dict) else None) or {}
        role_arn = request_params.get("roleArn", "") if isinstance(request_params, dict) else ""
        read_only = bool((raw.get("readOnly") if isinstance(raw, dict) else False) or log.get("readOnly", False))

        # ------------------------------------------------------------------
        # event_type classification
        # Uses AWS-specific lookup table first, inherited regex as fallback.
        # ------------------------------------------------------------------
        event_type = self.classify_aws_event(
            event_name=event_name,
            event_source=event_source,
            error_message=error_message,
            response_elements=response_elements,
            error_code=error_code,
            user_identity=user_identity_dict,
        )

        if event_name in {"AttachUserPolicy", "AttachRolePolicy", "AttachGroupPolicy"}:
            policy_arn = str(request_params.get("policyArn", ""))
            if "AdministratorAccess" in policy_arn:
                event_type = "ATTACH_ADMIN_POLICY"

        is_operational_health = False
        operational_issue = ""
        is_service_activity = False
        service_context = ""

        # 1. Operational / Integration-Health errors (e.g. GuardDuty missing subscription)
        if error_code == "SubscriptionRequiredException":
            is_operational_health = True
            event_type = "INTEGRATION_HEALTH"
            operational_issue = f"Service '{event_source or 'AWS'}' subscription required in region '{region}'."

        # 2. AWS Resource Explorer service-linked role and discovery operations
        elif (
            "AWSServiceRoleForResourceExplorer" in user_arn
            or "AWSServiceRoleForResourceExplorer" in role_arn
            or "AWSServiceRoleForResourceExplorer" in issuer_arn
            or invoked_by == "resource-explorer-2.amazonaws.com"
        ):
            is_service_activity = True
            service_context = "AWSServiceRoleForResourceExplorer"

        # 3. Amazon EventBridge SQS invocation role
        elif (
            "Amazon_EventBridge_Invoke_Sqs" in role_arn
            or "Amazon_EventBridge_Invoke_Sqs" in user_arn
            or invoked_by == "events.amazonaws.com"
        ):
            is_service_activity = True
            service_context = "Amazon_EventBridge_Invoke_Sqs"

        # 4. Routine read-only administrative inspection queries
        elif read_only and event_name in [
            "ListClusters", "DescribeCanaries", "ListDetectors",
            "ListResources", "ListManagedNotificationEvents"
        ]:
            is_service_activity = True
            service_context = "AWS_READ_ONLY_DISCOVERY"

        elif invoked_by.endswith(".amazonaws.com") or user_identity_dict.get("type") == "AWSService":
            is_service_activity = True
            service_context = invoked_by or "AWSService"

        if is_operational_health:
            event_category = "OPERATIONAL_HEALTH"
        elif is_service_activity:
            event_category = "INFORMATIONAL"
        else:
            event_category = "SECURITY"

        # ------------------------------------------------------------------
        # Build normalized log.
        # Store a sanitized version of the raw log so credentials from
        # responseElements.credentials are not persisted to OpenSearch.
        # ------------------------------------------------------------------
        source_raw = log.get("raw_log", log)
        sanitized_raw = redact_sensitive_data(source_raw)

        normalized_log = {
            "provider": "AWS",
            "username": username,
            "event_name": event_name,
            "event_type": event_type,
            "identity_type": user_identity_dict.get("type") if isinstance(user_identity_dict, dict) else None,
            "resource": resource,
            "source_ip": source_ip,
            "region": region,
            "event_time": event_time,
            "timestamp": event_time,
            "event_id": event_id,
            "is_service_activity": is_service_activity,
            "service_context": service_context,
            "is_read_only": read_only,
            "is_operational_health": is_operational_health,
            "operational_issue": operational_issue,
            "event_category": event_category,
            "raw_log": sanitized_raw,
        }

        return normalized_log


aws_normalizer = AWSNormalizer()