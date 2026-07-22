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
# PUBLIC BUCKET
# ============================================================

print("\n" + "=" * 80)
print("TEST 1 : PUBLIC BUCKET")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "PUBLIC_BUCKET_CREATED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 2
# SECURITY GROUP OPEN
# ============================================================

print("\n" + "=" * 80)
print("TEST 2 : SECURITY GROUP OPEN")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "SECURITY_GROUP_OPEN",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 3
# INSTANCE CREATED
# ============================================================

print("\n" + "=" * 80)
print("TEST 3 : INSTANCE CREATED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "INSTANCE_CREATED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 4
# INSTANCE TERMINATED
# ============================================================

print("\n" + "=" * 80)
print("TEST 4 : INSTANCE TERMINATED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "INSTANCE_TERMINATED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

# ============================================================
# TEST 5
# UNUSUAL REGION RESOURCE
# ============================================================

print("\n" + "=" * 80)
print("TEST 5 : UNUSUAL REGION RESOURCE")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "RESOURCE_CREATED",

    "region": "eu-central-1",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 6
# LOAD BALANCER DELETED
# ============================================================

print("\n" + "=" * 80)
print("TEST 6 : LOAD BALANCER DELETED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "LOAD_BALANCER_DELETED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 7
# PUBLIC SNAPSHOT
# ============================================================

print("\n" + "=" * 80)
print("TEST 7 : PUBLIC SNAPSHOT")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "SNAPSHOT_PUBLIC",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 8
# MULTIPLE RESOURCE DELETIONS
# ============================================================

print("\n" + "=" * 80)
print("TEST 8 : MULTIPLE RESOURCE DELETIONS")
print("=" * 80)

base_time = datetime.now(UTC)

events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "INSTANCE_TERMINATED",
        "timestamp": base_time
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOAD_BALANCER_DELETED",
        "timestamp": base_time + timedelta(minutes=2)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "BUCKET_DELETED",
        "timestamp": base_time + timedelta(minutes=4)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "DATABASE_DELETED",
        "timestamp": base_time + timedelta(minutes=6)
    }

]

for i, event in enumerate(events, start=1):

    alerts = correlation_engine.process_event(event)

    print_alerts(i, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


print("\n" + "=" * 80)
print("ALL RESOURCE RULE TESTS COMPLETED")
print("=" * 80)
