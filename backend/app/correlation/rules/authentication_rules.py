from app.correlation.alerts import Alert


def check(event_memory, current_event):
    """
    Runs all authentication correlation rules.

    Parameters:
        event_memory : Dictionary containing previous events
        current_event : Newly received normalized event

    Returns:
        List of generated alerts.
    """

    alerts = []

    alerts.extend(
        check_multiple_failed_logins(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_brute_force(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_multiple_ips(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_business_hours(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_concurrent_login(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_disabled_user(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_service_account(
            event_memory,
            current_event
        )
    )

    alerts.extend(
        check_multiple_provider_login(
            event_memory,
            current_event
        )
    )

    return alerts


def check_multiple_failed_logins(event_memory, current_event):
    """
    Detects multiple failed login attempts.
    Generates an alert if a user has 5 or more failed logins.
    """

    alerts = []

    # Check if current event is FAILED_LOGIN
    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    username = current_event.get("username")

    user_events = event_memory.get(username, [])

    failed_login_count = 0

    # Count failed logins
    for event in user_events:

        if event.get("event_type") == "FAILED_LOGIN":
            failed_login_count += 1

    # Generate alert
    if failed_login_count >= 5:

        alert = Alert(

            alert_type="MULTIPLE_FAILED_LOGINS",

            severity="MEDIUM",

            username=username,

            provider=current_event.get("provider"),

            description=f"{failed_login_count} failed login attempts detected.",

            event=current_event

        )

        alerts.append(alert.to_dict())

    return alerts


def check_brute_force(event_memory, current_event):
    return []


def check_multiple_ips(event_memory, current_event):
    return []


def check_business_hours(event_memory, current_event):
    return []


def check_concurrent_login(event_memory, current_event):
    return []


def check_disabled_user(event_memory, current_event):
    return []


def check_service_account(event_memory, current_event):
    return []


def check_multiple_provider_login(event_memory, current_event):
    return []