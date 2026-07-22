from datetime import datetime, timedelta

from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


def check(recent_events, current_event):
    """
    Executes all Resource Correlation Rules.
    """

    alerts = []

    alerts.extend(
        check_public_bucket(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_security_group_open(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_instance_created(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_instance_terminated(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_unusual_region(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_load_balancer_deleted(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_public_snapshot(
            recent_events,
            current_event
        )
    )

    alerts.extend(
        check_multiple_resource_deletions(
            recent_events,
            current_event
        )
    )

    return alerts


# ============================================================
# RULE 1
# PUBLIC STORAGE BUCKET
# ============================================================

def check_public_bucket(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") not in (
        "PUBLIC_BUCKET_CREATED",
        "MAKE_BUCKET_PUBLIC"
    ):
        return alerts

    config = RULE_CONFIG["PUBLIC_BUCKET"]

    alerts.append(

        Alert(

            alert_type="PUBLIC_BUCKET",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Public storage bucket detected.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 2
# SECURITY GROUP OPEN
# ============================================================

def check_security_group_open(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "SECURITY_GROUP_OPEN":
        return alerts

    config = RULE_CONFIG["SECURITY_GROUP_OPEN"]

    alerts.append(

        Alert(

            alert_type="SECURITY_GROUP_OPEN",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Security Group opened to the Internet (0.0.0.0/0).",

            event=current_event

        ).to_dict()

    )

    return alerts

# ============================================================
# RULE 3
# INSTANCE CREATED
# ============================================================

def check_instance_created(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "INSTANCE_CREATED":
        return alerts

    config = RULE_CONFIG["INSTANCE_CREATED"]

    alerts.append(

        Alert(

            alert_type="INSTANCE_CREATED",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="New compute instance created.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 4
# INSTANCE TERMINATED
# ============================================================

def check_instance_terminated(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "INSTANCE_TERMINATED":
        return alerts

    config = RULE_CONFIG["INSTANCE_TERMINATED"]

    alerts.append(

        Alert(

            alert_type="INSTANCE_TERMINATED",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Compute instance terminated.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 5
# RESOURCE CREATED IN UNUSUAL REGION
# ============================================================

def check_unusual_region(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "RESOURCE_CREATED":
        return alerts

    config = RULE_CONFIG["UNUSUAL_REGION_RESOURCE"]

    allowed_regions = config["allowed_regions"]

    region = current_event.get("region")

    if region in allowed_regions:
        return alerts

    alerts.append(

        Alert(

            alert_type="UNUSUAL_REGION_RESOURCE",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description=(
                f"Resource created in unusual region: {region}."
            ),

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 6
# LOAD BALANCER DELETED
# ============================================================

def check_load_balancer_deleted(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "LOAD_BALANCER_DELETED":
        return alerts

    config = RULE_CONFIG["LOAD_BALANCER_DELETED"]

    alerts.append(

        Alert(

            alert_type="LOAD_BALANCER_DELETED",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Load Balancer deleted.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 7
# PUBLIC SNAPSHOT
# ============================================================

def check_public_snapshot(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "SNAPSHOT_PUBLIC":
        return alerts

    config = RULE_CONFIG["PUBLIC_SNAPSHOT"]

    alerts.append(

        Alert(

            alert_type="PUBLIC_SNAPSHOT",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Snapshot shared publicly.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 8
# MULTIPLE RESOURCE DELETIONS
# ============================================================

def check_multiple_resource_deletions(recent_events, current_event):

    alerts = []

    deletion_events = {

        "INSTANCE_TERMINATED",
        "LOAD_BALANCER_DELETED",
        "BUCKET_DELETED",
        "DATABASE_DELETED"

    }

    if current_event.get("event_type") not in deletion_events:
        return alerts

    config = RULE_CONFIG["MULTIPLE_RESOURCE_DELETIONS"]

    threshold = config["threshold"]

    window = timedelta(minutes=config["window_minutes"])

    current_time = current_event["timestamp"]

    deletion_count = 0

    for event in recent_events:

        if event.get("event_type") not in deletion_events:
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= window:
            deletion_count += 1

    if deletion_count >= threshold:

        alerts.append(

            Alert(

                alert_type="MULTIPLE_RESOURCE_DELETIONS",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=(
                    f"{deletion_count} resource deletions detected "
                    f"within {config['window_minutes']} minutes."
                ),

                event=current_event

            ).to_dict()

        )

    return alerts