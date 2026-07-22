from datetime import timedelta

from app.correlation.alerts import Alert
from app.correlation.rule_config import RULE_CONFIG


# ============================================================
# MAIN CHECK FUNCTION
# ============================================================

def check(recent_events, current_event):

    alerts = []

    alerts.extend(check_large_data_download(recent_events, current_event))
    alerts.extend(check_sensitive_file_access(recent_events, current_event))
    alerts.extend(check_multiple_storage_reads(recent_events, current_event))
    alerts.extend(check_data_exfiltration(recent_events, current_event))
    alerts.extend(check_public_database_snapshot(recent_events, current_event))
    alerts.extend(check_mass_object_deletion(recent_events, current_event))
    alerts.extend(check_cross_region_copy(recent_events, current_event))
    alerts.extend(check_multiple_data_events(recent_events, current_event))

    return alerts


# ============================================================
# RULE 1
# LARGE DATA DOWNLOAD
# ============================================================

def check_large_data_download(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "DATA_DOWNLOAD":
        return alerts

    config = RULE_CONFIG["DATA_DOWNLOAD"]

    downloaded_mb = current_event.get("size_mb", 0)

    if downloaded_mb >= config["threshold_mb"]:

        alerts.append(

            Alert(

                alert_type="LARGE_DATA_DOWNLOAD",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=f"Large data download detected ({downloaded_mb} MB).",

                event=current_event

            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 2
# SENSITIVE FILE ACCESS
# ============================================================

def check_sensitive_file_access(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "SENSITIVE_FILE_ACCESS":
        return alerts

    config = RULE_CONFIG["SENSITIVE_FILE_ACCESS"]

    alerts.append(

        Alert(

            alert_type="SENSITIVE_FILE_ACCESS",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Sensitive file accessed.",

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 3
# MULTIPLE STORAGE READS
# ============================================================

def check_multiple_storage_reads(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "STORAGE_READ":
        return alerts

    config = RULE_CONFIG["MULTIPLE_STORAGE_READS"]

    threshold = config["threshold"]

    window = timedelta(minutes=config["window_minutes"])

    current_time = current_event["timestamp"]

    read_count = 0

    for event in recent_events:

        if event.get("event_type") != "STORAGE_READ":
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= window:
            read_count += 1

    if read_count >= threshold:

        alerts.append(

            Alert(

                alert_type="MULTIPLE_STORAGE_READS",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=f"{read_count} storage read operations detected within {config['window_minutes']} minutes.",

                event=current_event

            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 4
# DATA EXFILTRATION
# ============================================================

def check_data_exfiltration(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "DATA_EXFILTRATION":
        return alerts

    config = RULE_CONFIG["DATA_EXFILTRATION"]

    transferred_mb = current_event.get("size_mb", 0)

    if transferred_mb >= config["threshold_mb"]:

        alerts.append(

            Alert(

                alert_type="DATA_EXFILTRATION",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=f"Potential data exfiltration detected ({transferred_mb} MB transferred).",

                event=current_event

            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 5
# PUBLIC DATABASE SNAPSHOT
# ============================================================

def check_public_database_snapshot(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "DATABASE_SNAPSHOT_PUBLIC":
        return alerts

    config = RULE_CONFIG["PUBLIC_DATABASE_SNAPSHOT"]

    alerts.append(

        Alert(

            alert_type="PUBLIC_DATABASE_SNAPSHOT",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description="Database snapshot exposed publicly.",

            event=current_event

        ).to_dict()

    )

    return alerts

# ============================================================
# RULE 6
# MASS OBJECT DELETION
# ============================================================

def check_mass_object_deletion(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "OBJECT_DELETED":
        return alerts

    config = RULE_CONFIG["MASS_OBJECT_DELETION"]

    threshold = config["threshold"]

    window = timedelta(minutes=config["window_minutes"])

    current_time = current_event["timestamp"]

    delete_count = 0

    for event in recent_events:

        if event.get("event_type") != "OBJECT_DELETED":
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= window:
            delete_count += 1

    if delete_count == threshold:

        alerts.append(

            Alert(

                alert_type="MASS_OBJECT_DELETION",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=(
                    f"{delete_count} objects deleted within "
                    f"{config['window_minutes']} minutes."
                ),

                event=current_event

            ).to_dict()

        )

    return alerts


# ============================================================
# RULE 7
# CROSS REGION COPY
# ============================================================

def check_cross_region_copy(recent_events, current_event):

    alerts = []

    if current_event.get("event_type") != "DATA_COPIED":
        return alerts

    source_region = current_event.get("source_region")
    destination_region = current_event.get("destination_region")

    if source_region == destination_region:
        return alerts

    config = RULE_CONFIG["CROSS_REGION_COPY"]

    alerts.append(

        Alert(

            alert_type="CROSS_REGION_COPY",

            severity=config["severity"],

            username=current_event.get("username"),

            provider=current_event.get("provider"),

            description=(
                f"Data copied from {source_region} "
                f"to {destination_region}."
            ),

            event=current_event

        ).to_dict()

    )

    return alerts


# ============================================================
# RULE 8
# MULTIPLE DATA EVENTS
# ============================================================

def check_multiple_data_events(recent_events, current_event):

    alerts = []

    monitored_events = {

        "DATA_DOWNLOAD",
        "DATA_EXFILTRATION",
        "SENSITIVE_FILE_ACCESS",
        "DATABASE_SNAPSHOT_PUBLIC",
        "OBJECT_DELETED",
        "DATA_COPIED"

    }

    if current_event.get("event_type") not in monitored_events:
        return alerts

    config = RULE_CONFIG["MULTIPLE_DATA_EVENTS"]

    threshold = config["threshold"]

    window = timedelta(minutes=config["window_minutes"])

    current_time = current_event["timestamp"]

    event_count = 0

    for event in recent_events:

        if event.get("event_type") not in monitored_events:
            continue

        event_time = event.get("timestamp")

        if event_time is None:
            continue

        if current_time - event_time <= window:
            event_count += 1

    if event_count == threshold:

        alerts.append(

            Alert(

                alert_type="MULTIPLE_DATA_EVENTS",

                severity=config["severity"],

                username=current_event.get("username"),

                provider=current_event.get("provider"),

                description=(
                    f"{event_count} sensitive data events detected "
                    f"within {config['window_minutes']} minutes."
                ),

                event=current_event

            ).to_dict()

        )

    return alerts