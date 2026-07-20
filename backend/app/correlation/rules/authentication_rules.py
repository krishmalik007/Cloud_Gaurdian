from app.correlation.alerts import Alert
from datetime import datetime, timedelta
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

    Generates an alert if the configured threshold of failed
    login attempts occurs within the configured time window.
    """

    alerts = []

    # Only process FAILED_LOGIN events
    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    username = current_event.get("username")

    config = RULE_CONFIG["MULTIPLE_FAILED_LOGINS"]
    threshold = config["threshold"]
    severity = config["severity"]
    window_minutes = config["window_minutes"]

    current_time = current_event.get("timestamp", datetime.utcnow())

    failed_login_count = 0

    for event in recent_events:

        if event.get("event_type") != "FAILED_LOGIN":
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= timedelta(minutes=window_minutes):
            failed_login_count += 1

    # Trigger only once when threshold is reached
    if failed_login_count == threshold:

        alert = Alert(
            alert_type="MULTIPLE_FAILED_LOGINS",
            severity=severity,
            username=username,
            provider=current_event.get("provider"),
            description=(
                f"{failed_login_count} failed login attempts "
                f"detected within {window_minutes} minutes."
            ),
            event=current_event
        )

        alerts.append(alert.to_dict())

    return alerts


def check_brute_force(recent_events, current_event):
    """
    Detects brute-force login attacks.

    Generates an alert if the configured threshold of failed
    login attempts occurs within the configured time window.
    """

    alerts = []

    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    config = RULE_CONFIG["BRUTE_FORCE"]

    threshold = config["threshold"]
    severity = config["severity"]
    window_minutes = config["window_minutes"]

    current_time = current_event.get("timestamp", datetime.utcnow())

    failed_login_count = 0

    for event in recent_events:

        if event.get("event_type") != "FAILED_LOGIN":
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= timedelta(minutes=window_minutes):
            failed_login_count += 1

    # Trigger only once when threshold is reached
    if failed_login_count == threshold:

        alert = Alert(
            alert_type="BRUTE_FORCE",
            severity=severity,
            username=current_event.get("username"),
            provider=current_event.get("provider"),
            description=(
                f"{failed_login_count} failed login attempts detected "
                f"within {window_minutes} minutes."
            ),
            event=current_event
        )

        alerts.append(alert.to_dict())

    return alerts


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