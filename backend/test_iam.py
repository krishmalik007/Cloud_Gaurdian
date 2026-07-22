from datetime import datetime, timedelta, UTC   

from app.correlation.correlation_engine import correlation_engine


def run_test(test_name, events):
    """
    Runs an IAM correlation test and prints generated alerts.
    """

    print("\n" + "=" * 80)
    print(test_name)
    print("=" * 80)

    for i, event in enumerate(events, start=1):

        alerts = correlation_engine.process_event(event)

        print(f"\n---------- Event {i} ----------")

        if alerts:

            print(f"Alerts Generated ({len(alerts)}):")

            for alert in alerts:
                print(alert)

        else:

            print("No Alerts")

    print("\nClearing Event Store...\n")

    correlation_engine.event_store.clear()


# ==========================================================
# TEST 1 : PRIVILEGE ESCALATION
# ==========================================================

privilege_escalation_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "ATTACH_ADMIN_POLICY",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 2 : NEW ADMIN USER
# ==========================================================

new_admin_events = [

    {
        "username": "newadmin",
        "provider": "AWS",
        "event_type": "CREATE_ADMIN_USER",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 3 : ROOT ACCOUNT USAGE
# ==========================================================

root_login_events = [

    {
        "username": "root",
        "provider": "AWS",
        "event_type": "ROOT_LOGIN",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 4 : MFA DISABLED
# ==========================================================

mfa_disabled_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "DISABLE_MFA",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 5 : IAM POLICY CHANGED
# ==========================================================

policy_change_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "UPDATE_POLICY",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 6 : ACCESS KEY CREATED
# ==========================================================

access_key_created_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "CREATE_ACCESS_KEY",
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 7 : ACCESS KEY REACTIVATED
# ==========================================================

access_key_reactivated_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "ACCESS_KEY_USED",
        "inactive_days": 120,
        "timestamp": datetime.now(UTC)
    }

]


# ==========================================================
# TEST 8 : MULTIPLE IAM CHANGES
#
# Expected:
# Event 4 -> MULTIPLE_IAM_CHANGES
# ==========================================================

base_time = datetime(2026, 7, 22, 10, 0, 0)

multiple_iam_change_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "CREATE_USER",
        "timestamp": base_time
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "ATTACH_POLICY",
        "timestamp": base_time + timedelta(minutes=2)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "CREATE_ACCESS_KEY",
        "timestamp": base_time + timedelta(minutes=4)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "DISABLE_MFA",
        "timestamp": base_time + timedelta(minutes=6)
    }

]


# ==========================================================
# RUN ALL TESTS
# ==========================================================

if __name__ == "__main__":

    run_test(
        "TEST 1 : PRIVILEGE ESCALATION",
        privilege_escalation_events
    )

    run_test(
        "TEST 2 : NEW ADMIN USER",
        new_admin_events
    )

    run_test(
        "TEST 3 : ROOT ACCOUNT USAGE",
        root_login_events
    )

    run_test(
        "TEST 4 : MFA DISABLED",
        mfa_disabled_events
    )

    run_test(
        "TEST 5 : IAM POLICY CHANGED",
        policy_change_events
    )

    run_test(
        "TEST 6 : ACCESS KEY CREATED",
        access_key_created_events
    )

    run_test(
        "TEST 7 : ACCESS KEY REACTIVATED",
        access_key_reactivated_events
    )

    run_test(
        "TEST 8 : MULTIPLE IAM CHANGES",
        multiple_iam_change_events
    )

    print("\n" + "=" * 80)
    print("ALL IAM RULE TESTS COMPLETED")
    print("=" * 80)