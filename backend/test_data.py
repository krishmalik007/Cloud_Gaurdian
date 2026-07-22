from datetime import datetime, timedelta, UTC

from app.correlation.correlation_engine import correlation_engine


# ============================================================
# HELPER
# ============================================================

def print_alerts(event_no, alerts):

    print(f"\n---------- Event {event_no} ----------")

    if alerts:

        print(f"Alerts Generated ({len(alerts)}):")

        for alert in alerts:
            print(alert)

    else:

        print("No Alerts")


# ============================================================
# TEST 1
# LARGE DATA DOWNLOAD
# ============================================================

print("\n" + "=" * 80)
print("TEST 1 : LARGE DATA DOWNLOAD")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "DATA_DOWNLOAD",

    "size_mb": 750,

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 2
# SENSITIVE FILE ACCESS
# ============================================================

print("\n" + "=" * 80)
print("TEST 2 : SENSITIVE FILE ACCESS")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "SENSITIVE_FILE_ACCESS",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 3
# MULTIPLE STORAGE READS
# ============================================================

print("\n" + "=" * 80)
print("TEST 3 : MULTIPLE STORAGE READS")
print("=" * 80)

base_time = datetime.now(UTC)

for i in range(20):

    event = {

        "username": "krish",

        "provider": "AWS",

        "event_type": "STORAGE_READ",

        "timestamp": base_time + timedelta(seconds=i)

    }

    alerts = correlation_engine.process_event(event)

print_alerts(20, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 4
# DATA EXFILTRATION
# ============================================================

print("\n" + "=" * 80)
print("TEST 4 : DATA EXFILTRATION")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "DATA_EXFILTRATION",

    "size_mb": 2500,

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

# ============================================================
# TEST 5
# PUBLIC DATABASE SNAPSHOT
# ============================================================

print("\n" + "=" * 80)
print("TEST 5 : PUBLIC DATABASE SNAPSHOT")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "DATABASE_SNAPSHOT_PUBLIC",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 6
# MASS OBJECT DELETION
# ============================================================

print("\n" + "=" * 80)
print("TEST 6 : MASS OBJECT DELETION")
print("=" * 80)

base_time = datetime.now(UTC)

for i in range(25):

    event = {

        "username": "krish",

        "provider": "AWS",

        "event_type": "OBJECT_DELETED",

        "timestamp": base_time + timedelta(seconds=i)

    }

    alerts = correlation_engine.process_event(event)

print_alerts(25, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 7
# CROSS REGION COPY
# ============================================================

print("\n" + "=" * 80)
print("TEST 7 : CROSS REGION COPY")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "DATA_COPIED",

    "source_region": "ap-south-1",

    "destination_region": "eu-west-1",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 8
# MULTIPLE DATA EVENTS
# ============================================================

print("\n" + "=" * 80)
print("TEST 8 : MULTIPLE DATA EVENTS")
print("=" * 80)

base_time = datetime.now(UTC)

events = [

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "DATA_DOWNLOAD",

        "size_mb": 700,

        "timestamp": base_time

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "SENSITIVE_FILE_ACCESS",

        "timestamp": base_time + timedelta(minutes=2)

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "DATABASE_SNAPSHOT_PUBLIC",

        "timestamp": base_time + timedelta(minutes=4)

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "DATA_EXFILTRATION",

        "size_mb": 2000,

        "timestamp": base_time + timedelta(minutes=6)

    }

]

for i, event in enumerate(events, start=1):

    alerts = correlation_engine.process_event(event)

    print_alerts(i, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


print("\n" + "=" * 80)
print("ALL DATA RULE TESTS COMPLETED")
print("=" * 80)