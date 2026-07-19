from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


def check(recent_events, current_event):
    """
    Runs all authentication correlation rules.

    Parameters:
        recent_events : List containing recent events for the current user.
        current_event : Newly received normalized event.

    Returns:
        List of generated alerts.
    """

    alerts = []

    alerts.extend(
        check_multiple_failed_logins(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_brute_force(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_multiple_ips(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_business_hours(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_concurrent_login(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_disabled_user(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_service_account(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_multiple_provider_login(
            recent_events,
            current_event
        )
    )

    return alerts


def check_multiple_failed_logins(recent_events, current_event):
    """
    Detects multiple failed login attempts.

    Generates an alert if a user has 5 or more failed logins
    within the configured sliding time window.
    """

    alerts = []

    # Only process FAILED_LOGIN events
    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    username = current_event.get("username")

    config = RULE_CONFIG["MULTIPLE_FAILED_LOGINS"]
    threshold = config["threshold"]
    severity = config["severity"]

    failed_login_count = 0

    # Count failed logins in recent events
    for event in recent_events:

        if event.get("event_type") == "FAILED_LOGIN":
            failed_login_count += 1

    # Generate alert
    if failed_login_count >= threshold :

        alert = Alert(
            alert_type="MULTIPLE_FAILED_LOGINS",
            severity=severity,
            username=username,
            provider=current_event.get("provider"),
            description=f"{failed_login_count} failed login attempts detected within correlation window.",
            event=current_event
        )

        alerts.append(alert.to_dict())

    return alerts


def check_brute_force(recent_events, current_event):
    return []


def check_multiple_ips(recent_events, current_event):
    return []


def check_business_hours(recent_events, current_event):
    return []


def check_concurrent_login(recent_events, current_event):
    return []


def check_disabled_user(recent_events, current_event):
    return []


def check_service_account(recent_events, current_event):
    return []


def check_multiple_provider_login(recent_events, current_event):
    return []