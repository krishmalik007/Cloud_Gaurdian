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

print("\n" + "=" * 80)
print("TEST 1 : AUDIT LOGGING DISABLED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "AUDIT_LOGGING_DISABLED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

print("\n" + "=" * 80)
print("TEST 2 : ENCRYPTION DISABLED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "ENCRYPTION_DISABLED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

print("\n" + "=" * 80)
print("TEST 3 : MFA ENFORCEMENT DISABLED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "MFA_ENFORCEMENT_DISABLED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

print("\n" + "=" * 80)
print("TEST 4 : WEAK PASSWORD POLICY")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "PASSWORD_POLICY_CHANGED",

    "minimum_length": 8,

    "require_symbols": False,

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()



# ============================================================
# TEST 5
# SECURITY SERVICE DISABLED
# ============================================================

print("\n" + "=" * 80)
print("TEST 5 : SECURITY SERVICE DISABLED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "SECURITY_SERVICE_DISABLED",

    "service": "GuardDuty",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()

# ============================================================
# TEST 6
# BACKUP DISABLED
# ============================================================

print("\n" + "=" * 80)
print("TEST 6 : BACKUP DISABLED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "BACKUP_DISABLED",

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 7
# RETENTION POLICY CHANGED
# ============================================================

print("\n" + "=" * 80)
print("TEST 7 : RETENTION POLICY CHANGED")
print("=" * 80)

event = {

    "username": "krish",

    "provider": "AWS",

    "event_type": "RETENTION_POLICY_CHANGED",

    "old_days": 365,

    "new_days": 90,

    "timestamp": datetime.now(UTC)

}

alerts = correlation_engine.process_event(event)

print_alerts(1, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


# ============================================================
# TEST 8
# MULTIPLE CONFIGURATION CHANGES
# ============================================================

print("\n" + "=" * 80)
print("TEST 8 : MULTIPLE CONFIGURATION CHANGES")
print("=" * 80)

base_time = datetime.now(UTC)

events = [

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "AUDIT_LOGGING_DISABLED",

        "timestamp": base_time

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "ENCRYPTION_DISABLED",

        "timestamp": base_time + timedelta(minutes=2)

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "MFA_ENFORCEMENT_DISABLED",

        "timestamp": base_time + timedelta(minutes=4)

    },

    {

        "username": "krish",

        "provider": "AWS",

        "event_type": "BACKUP_DISABLED",

        "timestamp": base_time + timedelta(minutes=6)

    }

]

for i, event in enumerate(events, start=1):

    alerts = correlation_engine.process_event(event)

    print_alerts(i, alerts)

print("\nClearing Event Store...\n")

correlation_engine.event_store.clear()


print("\n" + "=" * 80)
print("ALL CONFIGURATION RULE TESTS COMPLETED")
print("=" * 80)