from datetime import timedelta

from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


def check(recent_events, current_event):
    """
    Executes all IAM correlation rules.
    """

    alerts = []

    alerts.extend(check_privilege_escalation(current_event))
    alerts.extend(check_new_admin_user(current_event))
    alerts.extend(check_root_account_usage(current_event))
    alerts.extend(check_mfa_disabled(current_event))
    alerts.extend(check_policy_changes(current_event))
    alerts.extend(check_access_key_created(current_event))
    alerts.extend(check_access_key_reactivated(current_event))
    alerts.extend(check_multiple_iam_changes(recent_events, current_event))

    return alerts


# ==========================================================
# RULE 1 : PRIVILEGE ESCALATION
# ==========================================================

def check_privilege_escalation(current_event):

    alerts = []

    admin_actions = {

        "ATTACH_ADMIN_POLICY",
        "ADD_TO_ADMIN_GROUP",
        "ASSUME_ADMIN_ROLE",
        "PRIVILEGE_ESCALATION"

    }

    event_type = current_event.get("event_type")
    is_priv_esc = event_type in admin_actions

    if not is_priv_esc:
        event_name = current_event.get("event_name")
        if event_name in {"AttachUserPolicy", "AttachRolePolicy", "AttachGroupPolicy"}:
            raw = current_event.get("raw_log", {}) if isinstance(current_event.get("raw_log"), dict) else current_event
            req_params = raw.get("requestParameters", {}) if isinstance(raw, dict) else {}
            if isinstance(req_params, dict):
                policy_arn = str(req_params.get("policyArn", ""))
                if "AdministratorAccess" in policy_arn:
                    is_priv_esc = True

    if not is_priv_esc:
        return alerts

    alerts.append(

        Alert(

            alert_type="IAM_PRIVILEGE_ESCALATION",

            severity=RULE_CONFIG["IAM_PRIVILEGE_ESCALATION"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Privilege escalation detected.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ==========================================================
# RULE 2 : NEW ADMIN USER
# ==========================================================

def check_new_admin_user(current_event):

    alerts = []

    if current_event.get("event_type") != "CREATE_ADMIN_USER":
        return alerts

    alerts.append(

        Alert(

            alert_type="NEW_ADMIN_USER",

            severity=RULE_CONFIG["NEW_ADMIN_USER"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="New administrator account created.",

            event=current_event

        ).to_dict()

    )

    return alerts

# ==========================================================
# RULE 3 : ROOT ACCOUNT USAGE
# ==========================================================

def check_root_account_usage(current_event):

    alerts = []

    event_type = current_event.get("event_type")
    is_root_login = event_type == "ROOT_LOGIN"

    if not is_root_login:
        event_name = current_event.get("event_name")
        raw = current_event.get("raw_log", {}) if isinstance(current_event.get("raw_log"), dict) else current_event
        user_identity = raw.get("userIdentity", {}) if isinstance(raw, dict) else {}
        is_root_identity = (
            user_identity.get("type") == "Root"
            or str(user_identity.get("arn", "")).endswith(":root")
            or current_event.get("username") == "root"
            or current_event.get("identity_type") == "Root"
        )
        is_login = (
            event_name == "ConsoleLogin"
            or event_type in {"AUTHENTICATION", "LOGIN", "LOGIN_SUCCESS"}
        )
        is_failed = event_type == "FAILED_LOGIN"
        if is_root_identity and is_login and not is_failed:
            is_root_login = True

    if not is_root_login:
        return alerts

    alerts.append(

        Alert(

            alert_type="ROOT_ACCOUNT_USAGE",

            severity=RULE_CONFIG["ROOT_ACCOUNT_USAGE"]["severity"],

            username=current_event.get("username") or "root",

            provider=current_event.get("provider", "AWS"),

            description="Root account usage detected.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ==========================================================
# RULE 4 : MFA DISABLED
# ==========================================================

def check_mfa_disabled(current_event):

    alerts = []

    if current_event.get("event_type") != "DISABLE_MFA":
        return alerts

    alerts.append(

        Alert(

            alert_type="MFA_DISABLED",

            severity=RULE_CONFIG["MFA_DISABLED"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Multi-Factor Authentication (MFA) has been disabled.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ==========================================================
# RULE 5 : IAM POLICY CHANGED
# ==========================================================

def check_policy_changes(current_event):

    alerts = []

    policy_events = {

        "CREATE_POLICY",
        "DELETE_POLICY",
        "UPDATE_POLICY",
        "ATTACH_POLICY",
        "DETACH_POLICY",
        "ATTACH_ADMIN_POLICY"

    }

    supported_aws_policy_events = {

        "CreatePolicy",
        "DeletePolicy",
        "CreatePolicyVersion",
        "SetDefaultPolicyVersion",
        "DeletePolicyVersion",
        "PutUserPolicy",
        "PutRolePolicy",
        "PutGroupPolicy",
        "DeleteUserPolicy",
        "DeleteRolePolicy",
        "DeleteGroupPolicy",
        "AttachUserPolicy",
        "AttachRolePolicy",
        "AttachGroupPolicy",
        "DetachUserPolicy",
        "DetachRolePolicy",
        "DetachGroupPolicy"

    }

    event_type = current_event.get("event_type")
    event_name = current_event.get("event_name")

    if event_type not in policy_events and event_name not in supported_aws_policy_events:
        return alerts

    alerts.append(

        Alert(

            alert_type="IAM_POLICY_CHANGED",

            severity=RULE_CONFIG["IAM_POLICY_CHANGED"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="IAM policy modification detected.",

            event=current_event

        ).to_dict()

    )

    return alerts

# ==========================================================
# RULE 6 : ACCESS KEY CREATED
# ==========================================================

def check_access_key_created(current_event):

    alerts = []

    if current_event.get("event_type") != "CREATE_ACCESS_KEY":
        return alerts

    alerts.append(

        Alert(

            alert_type="ACCESS_KEY_CREATED",

            severity=RULE_CONFIG["ACCESS_KEY_CREATED"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="New access key created.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ==========================================================
# RULE 7 : ACCESS KEY REACTIVATED
# ==========================================================

def check_access_key_reactivated(current_event):

    alerts = []

    if current_event.get("event_type") != "ACCESS_KEY_USED":
        return alerts

    inactive_days = current_event.get("inactive_days", 0)

    threshold = RULE_CONFIG["ACCESS_KEY_REACTIVATED"]["inactive_days"]

    if inactive_days < threshold:
        return alerts

    alerts.append(

        Alert(

            alert_type="ACCESS_KEY_REACTIVATED",

            severity=RULE_CONFIG["ACCESS_KEY_REACTIVATED"]["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description=f"Access key used after {inactive_days} days of inactivity.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ==========================================================
# RULE 8 : MULTIPLE IAM CHANGES
# ==========================================================

def check_multiple_iam_changes(recent_events, current_event):

    alerts = []

    iam_events = {

        "CREATE_USER",
        "DELETE_USER",
        "CREATE_ROLE",
        "DELETE_ROLE",
        "ATTACH_POLICY",
        "DETACH_POLICY",
        "CREATE_POLICY",
        "DELETE_POLICY",
        "UPDATE_POLICY",
        "CREATE_ACCESS_KEY",
        "DELETE_ACCESS_KEY",
        "DISABLE_MFA",
        "ENABLE_MFA",
        "ATTACH_ADMIN_POLICY",
        "ADD_TO_ADMIN_GROUP",
        "CREATE_ADMIN_USER"

    }

    config = RULE_CONFIG["MULTIPLE_IAM_CHANGES"]

    threshold = config["threshold"]

    window = timedelta(minutes=config["window_minutes"])

    current_time = current_event["timestamp"]

    count = 0
    matched_events = []

    for event in recent_events:

        if event.get("event_type") not in iam_events:
            continue

        if current_time - event["timestamp"] > window:
            continue

        count += 1
        matched_events.append(event)

    if count != threshold:
        return alerts

    alerts.append(

        Alert(

            alert_type="MULTIPLE_IAM_CHANGES",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description=f"{threshold} IAM changes detected within {config['window_minutes']} minutes.",

            event=current_event,
            
            related_events=matched_events

        ).to_dict()

    )

    return alerts