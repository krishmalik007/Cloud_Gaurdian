from app.normalizer.base import BaseNormalizer
from app.utils.log_sanitizer import redact_credentials


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
    ("iam.",        "AttachRolePolicy",                 "IAM"),
    ("iam.",        "DetachRolePolicy",                 "IAM"),
    ("iam.",        "AttachUserPolicy",                 "IAM"),
    ("iam.",        "DetachUserPolicy",                 "IAM"),
    ("iam.",        "AttachGroupPolicy",                "IAM"),
    ("iam.",        "DetachGroupPolicy",                "IAM"),
    ("iam.",        "PutRolePolicy",                    "IAM"),
    ("iam.",        "PutUserPolicy",                    "IAM"),
    ("iam.",        "PutGroupPolicy",                   "IAM"),
    ("iam.",        "DeleteRolePolicy",                 "IAM"),
    ("iam.",        "DeleteUserPolicy",                 "IAM"),
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
    ("iam.",        "CreatePolicy",                     "IAM"),
    ("iam.",        "DeletePolicy",                     "IAM"),
    ("iam.",        "CreatePolicyVersion",              "IAM"),
    ("iam.",        "SetDefaultPolicyVersion",          "IAM"),

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
    # MONITORING — CloudWatch metrics / alarms
    # ------------------------------------------------------------------
    ("monitoring.",     None,                           "MONITORING"),
    ("cloudwatch.",     None,                           "MONITORING"),
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

    def classify_aws_event(self, event_name: str, event_source: str) -> str:
        """
        Classify a CloudTrail event into a high-level event_type using the
        _AWS_EVENT_TYPE_RULES table above.

        Matching order:
        1. eventSource prefix AND exact eventName
        2. eventSource prefix only (eventName=None rule)
        Falls back to the inherited BaseNormalizer.classify_event() which
        uses regex on the event name, then finally to "UNKNOWN".
        """
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
    # Main normalizer
    # ------------------------------------------------------------------

    def normalize(self, log):

        if not isinstance(log, dict):
            raise ValueError("AWS log must be a dictionary.")

        # ------------------------------------------------------------------
        # username
        # From parser: log["username"] already resolved from userIdentity.
        # From raw CloudTrail: read userIdentity directly.
        # ------------------------------------------------------------------
        user_identity = log.get("userIdentity", {})
        if isinstance(user_identity, dict):
            username = (
                user_identity.get("userName")
                or user_identity.get("principalId")
            )
        else:
            username = None

        username = username or log.get("username")

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
        # event_source — used for classification; not stored in output
        # Pre-parsed path: raw_log.eventSource
        # Raw CloudTrail path: log.eventSource
        # ------------------------------------------------------------------
        raw = log.get("raw_log", log)
        event_source = ""
        if isinstance(raw, dict):
            event_source = raw.get("eventSource", "")
        if not event_source:
            event_source = log.get("eventSource", "")

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
        # Pre-parsed path: "region"   (already resolved from awsRegion)
        # Raw CloudTrail path: "awsRegion" then "region"
        # ------------------------------------------------------------------
        region = (
            log.get("region")
            or log.get("awsRegion")
        )

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
        # event_type classification
        # Uses AWS-specific lookup table first, inherited regex as fallback.
        # ------------------------------------------------------------------
        event_type = self.classify_aws_event(event_name, event_source)

        # ------------------------------------------------------------------
        # Build normalized log.
        # Store a sanitized version of the raw log so credentials from
        # responseElements.credentials are not persisted to OpenSearch.
        # ------------------------------------------------------------------
        source_raw = log.get("raw_log", log)
        sanitized_raw = redact_credentials(source_raw)

        normalized_log = {
            "provider": "AWS",
            "username": username,
            "event_name": event_name,
            "event_type": event_type,
            "resource": resource,
            "source_ip": source_ip,
            "region": region,
            "event_time": event_time,
            "raw_log": sanitized_raw,
        }

        return normalized_log


aws_normalizer = AWSNormalizer()