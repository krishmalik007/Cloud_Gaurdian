from datetime import timedelta

from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


def check(recent_events, current_event):

    alerts = []

    alerts.extend(check_audit_logging_disabled(current_event))
    alerts.extend(check_encryption_disabled(current_event))
    alerts.extend(check_mfa_enforcement_disabled(current_event))
    alerts.extend(check_weak_password_policy(current_event))
    alerts.extend(check_security_service_disabled(current_event))
    alerts.extend(check_backup_disabled(current_event))
    alerts.extend(check_retention_policy_changed(current_event))
    alerts.extend(
        check_multiple_configuration_changes(
            recent_events,
            current_event
        )
    )

    return alerts


def check_audit_logging_disabled(event):

    alerts = []

    if event.get("event_type") != "AUDIT_LOGGING_DISABLED":
        return alerts

    config = RULE_CONFIG["AUDIT_LOGGING_DISABLED"]

    alerts.append(

        Alert(

            alert_type="AUDIT_LOGGING_DISABLED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description="Cloud audit logging has been disabled.",

            event=event

        ).to_dict()

    )

    return alerts

def check_encryption_disabled(event):

    alerts = []

    if event.get("event_type") != "ENCRYPTION_DISABLED":
        return alerts

    config = RULE_CONFIG["ENCRYPTION_DISABLED"]

    alerts.append(

        Alert(

            alert_type="ENCRYPTION_DISABLED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description="Resource encryption has been disabled.",

            event=event

        ).to_dict()

    )

    return alerts

def check_mfa_enforcement_disabled(event):

    alerts = []

    if event.get("event_type") != "MFA_ENFORCEMENT_DISABLED":
        return alerts

    config = RULE_CONFIG["MFA_ENFORCEMENT_DISABLED"]

    alerts.append(

        Alert(

            alert_type="MFA_ENFORCEMENT_DISABLED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description="MFA enforcement has been disabled.",

            event=event

        ).to_dict()

    )

    return alerts


def check_weak_password_policy(event):

    alerts = []

    if event.get("event_type") != "PASSWORD_POLICY_CHANGED":
        return alerts

    config = RULE_CONFIG["WEAK_PASSWORD_POLICY"]

    minimum_length = event.get("minimum_length", 0)

    require_symbols = event.get("require_symbols", True)

    if (
        minimum_length >= config["minimum_length"]
        and require_symbols
    ):
        return alerts

    alerts.append(

        Alert(

            alert_type="WEAK_PASSWORD_POLICY",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description="Weak password policy detected.",

            event=event

        ).to_dict()

    )

    return alerts


def check_security_service_disabled(event):

    alerts = []

    if event.get("event_type") != "SECURITY_SERVICE_DISABLED":
        return alerts

    config = RULE_CONFIG["SECURITY_SERVICE_DISABLED"]

    service = event.get("service", "Unknown")

    alerts.append(

        Alert(

            alert_type="SECURITY_SERVICE_DISABLED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description=f"Security service '{service}' has been disabled.",

            event=event

        ).to_dict()

    )

    return alerts

def check_backup_disabled(event):

    alerts = []

    if event.get("event_type") != "BACKUP_DISABLED":
        return alerts

    config = RULE_CONFIG["BACKUP_DISABLED"]

    alerts.append(

        Alert(

            alert_type="BACKUP_DISABLED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description="Backup protection has been disabled.",

            event=event

        ).to_dict()

    )

    return alerts

def check_retention_policy_changed(event):

    alerts = []

    if event.get("event_type") != "RETENTION_POLICY_CHANGED":
        return alerts

    old_days = event.get("old_days", 0)
    new_days = event.get("new_days", 0)

    if new_days >= old_days:
        return alerts

    config = RULE_CONFIG["RETENTION_POLICY_CHANGED"]

    alerts.append(

        Alert(

            alert_type="RETENTION_POLICY_CHANGED",

            severity=config["severity"],

            username=event["username"],

            provider=event["provider"],

            description=(
                f"Log retention reduced from "
                f"{old_days} days to {new_days} days."
            ),

            event=event

        ).to_dict()

    )

    return alerts

def check_multiple_configuration_changes(recent_events, current_event):

    alerts = []

    config = RULE_CONFIG["MULTIPLE_CONFIGURATION_CHANGES"]

    monitored_events = {

        "AUDIT_LOGGING_DISABLED",

        "ENCRYPTION_DISABLED",

        "MFA_ENFORCEMENT_DISABLED",

        "PASSWORD_POLICY_CHANGED",

        "SECURITY_SERVICE_DISABLED",

        "BACKUP_DISABLED",

        "RETENTION_POLICY_CHANGED"

    }

    if current_event.get("event_type") not in monitored_events:
        return alerts

    window = timedelta(minutes=config["window_minutes"])

    count = sum(

        1

        for event in recent_events

        if (
            event.get("event_type") in monitored_events
            and event.get("username") == current_event.get("username")
            and (
                current_event["timestamp"] - event["timestamp"]
            ) <= window
        )

    )

    if count != config["threshold"]:
        return alerts

    alerts.append(

        Alert(

            alert_type="MULTIPLE_CONFIGURATION_CHANGES",

            severity=config["severity"],

            username=current_event["username"],

            provider=current_event["provider"],

            description=(
                f"{count} configuration changes detected "
                f"within {config['window_minutes']} minutes."
            ),

            event=current_event

        ).to_dict()

    )

    return alerts

