from datetime import datetime, timedelta, timezone

from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


def _parse_event_timestamp(event) -> datetime:
    """
    Safely extract and normalize the timestamp from an event dictionary.
    Handles datetime objects (with or without tzinfo) and ISO string timestamps.
    Falls back to current UTC time.
    """
    if not isinstance(event, dict):
        return datetime.now(timezone.utc)
    ts = event.get("timestamp") or event.get("event_time")
    if isinstance(ts, datetime):
        return ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return datetime.now(timezone.utc)


def check(recent_events, current_event):
    """
    Executes all Authentication Correlation Rules.
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


# ============================================================
# RULE 1
# MULTIPLE FAILED LOGIN
# ============================================================

def check_multiple_failed_logins(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    config = RULE_CONFIG["MULTIPLE_FAILED_LOGINS"]

    threshold = config["threshold"]
    window = timedelta(minutes=config["window_minutes"])

    current_time = _parse_event_timestamp(current_event)

    failed_count = 0
    matched_events = []

    for event in recent_events:

        if event.get("event_type") != "FAILED_LOGIN":
            continue

        event_time = _parse_event_timestamp(event)

        if event_time is None:
            continue

        if current_time - event_time <= window:
            failed_count += 1
            matched_events.append(event)

    if failed_count == threshold:

        alerts.append(

            Alert(
                alert_type="MULTIPLE_FAILED_LOGINS",
                severity=config["severity"],
                username=current_event["username"],
                provider=current_event.get("provider"),
                description=(
                    f"{failed_count} failed login attempts "
                    f"detected within {config['window_minutes']} minutes."
                ),
                event=current_event,
                related_events=matched_events
            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 2
# BRUTE FORCE
# ============================================================

def check_brute_force(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "FAILED_LOGIN":
        return alerts

    config = RULE_CONFIG["BRUTE_FORCE"]

    threshold = config["threshold"]
    window = timedelta(minutes=config["window_minutes"])

    current_time = _parse_event_timestamp(current_event)

    failed_count = 0
    matched_events = []

    for event in recent_events:

        if event.get("event_type") != "FAILED_LOGIN":
            continue

        event_time = _parse_event_timestamp(event)

        if event_time is None:
            continue

        if current_time - event_time <= window:
            failed_count += 1
            matched_events.append(event)

    if failed_count == threshold:

        alerts.append(

            Alert(
                alert_type="BRUTE_FORCE",
                severity=config["severity"],
                username=current_event["username"],
                provider=current_event.get("provider"),
                description=(
                    f"{failed_count} failed login attempts "
                    f"detected within {config['window_minutes']} minutes."
                ),
                event=current_event,
                related_events=matched_events
            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 3
# MULTIPLE IP LOGIN
# ============================================================

def check_multiple_ips(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    config = RULE_CONFIG["MULTIPLE_IP_LOGIN"]

    threshold = config["threshold"]
    window = timedelta(minutes=config["window_minutes"])

    current_time = _parse_event_timestamp(current_event)

    unique_ips = set()

    for event in recent_events:

        if event.get("event_type") != "LOGIN_SUCCESS":
            continue

        event_time = _parse_event_timestamp(event)

        if event_time is None:
            continue

        if current_time - event_time > window:
            continue

        ip = event.get("source_ip")

        if ip:
            unique_ips.add(ip)

    current_ip = current_event.get("source_ip")

    if current_ip:
        unique_ips.add(current_ip)

    if len(unique_ips) == threshold:

        alerts.append(

            Alert(
                alert_type="MULTIPLE_IP_LOGIN",
                severity=config["severity"],
                username=current_event["username"],
                provider=current_event.get("provider"),
                description=(
                    f"User logged in from "
                    f"{len(unique_ips)} unique IP addresses "
                    f"within {config['window_minutes']} minutes."
                ),
                event=current_event
            ).to_dict()

        )

    return alerts

    # ============================================================
# RULE 4
# BUSINESS HOURS LOGIN
# ============================================================

def check_business_hours(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    config = RULE_CONFIG["BUSINESS_HOURS_LOGIN"]

    start_hour = config["start_hour"]
    end_hour = config["end_hour"]

    current_time = _parse_event_timestamp(current_event)

    if current_time.hour < start_hour or current_time.hour >= end_hour:

        alerts.append(

            Alert(
                alert_type="BUSINESS_HOURS_LOGIN",
                severity=config["severity"],
                username=current_event.get("username"),
                provider=current_event.get("provider"),
                description=(
                    f"Login detected outside business hours "
                    f"({start_hour}:00 - {end_hour}:00)."
                ),
                event=current_event
            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 5
# CONCURRENT LOGIN
# ============================================================

def check_concurrent_login(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    config = RULE_CONFIG["CONCURRENT_LOGIN"]

    current_ip = current_event.get("source_ip")

    if current_ip is None:
        return alerts

    current_time = _parse_event_timestamp(current_event)

    window = timedelta(minutes=config["window_minutes"])

    for event in recent_events:

        # Ignore the current event itself
        if event is current_event:
            continue

        if event.get("event_type") != "LOGIN_SUCCESS":
            continue

        previous_ip = event.get("source_ip")

        if previous_ip is None:
            continue

        # Same IP is not concurrent
        if previous_ip == current_ip:
            continue

        event_time = _parse_event_timestamp(event)

        if event_time is None:
            continue

        if current_time - event_time > window:
            continue

        alerts.append(

            Alert(
                alert_type="CONCURRENT_LOGIN",
                severity=config["severity"],
                username=current_event["username"],
                provider=current_event.get("provider"),
                description=(
                    "Concurrent login detected from "
                    f"{previous_ip} and {current_ip} "
                    "within one minute."
                ),
                event=current_event
            ).to_dict()

        )

        break

    return alerts


# ============================================================
# RULE 6
# DISABLED USER LOGIN
# ============================================================

def check_disabled_user(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    if current_event.get("user_status") != "DISABLED":
        return alerts

    config = RULE_CONFIG["DISABLED_USER_LOGIN"]

    alerts.append(

        Alert(
            alert_type="DISABLED_USER_LOGIN",
            severity=config["severity"],
            username=current_event.get("username"),
            provider=current_event.get("provider"),
            description="Disabled user successfully logged in.",
            event=current_event
        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 7
# SERVICE ACCOUNT LOGIN
# ============================================================

def check_service_account(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    if current_event.get("account_type") != "SERVICE":
        return alerts

    config = RULE_CONFIG["SERVICE_ACCOUNT_LOGIN"]

    alerts.append(

        Alert(
            alert_type="SERVICE_ACCOUNT_LOGIN",
            severity=config["severity"],
            username=current_event.get("username"),
            provider=current_event.get("provider"),
            description="Interactive login detected for service account.",
            event=current_event
        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 8
# MULTIPLE CLOUD PROVIDER LOGIN
# ============================================================

def check_multiple_provider_login(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOGIN_SUCCESS":
        return alerts

    config = RULE_CONFIG["MULTIPLE_PROVIDER_LOGIN"]

    current_time = _parse_event_timestamp(current_event)

    window = timedelta(minutes=config["window_minutes"])

    providers = set()

    for event in recent_events:

        if event.get("event_type") != "LOGIN_SUCCESS":
            continue

        event_time = _parse_event_timestamp(event)

        if event_time is None:
            continue

        if current_time - event_time > window:
            continue

        provider = event.get("provider")

        if provider:
            providers.add(provider)

    current_provider = current_event.get("provider")

    if current_provider:
        providers.add(current_provider)

    if len(providers) >= config["threshold"]:

        alerts.append(

            Alert(
                alert_type="MULTIPLE_PROVIDER_LOGIN",
                severity=config["severity"],
                username=current_event.get("username"),
                provider=current_provider,
                description=(
                    f"User authenticated from "
                    f"{len(providers)} cloud providers "
                    f"within {config['window_minutes']} minutes."
                ),
                event=current_event
            ).to_dict()

        )

    return alerts