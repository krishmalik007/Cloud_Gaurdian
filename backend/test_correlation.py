from datetime import datetime

from app.correlation.correlation_engine import correlation_engine


def run_test(test_name, events):
    """
    Runs a correlation test and prints generated alerts.
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
# TEST 1 : FAILED LOGIN RULES
#
# Expected:
# Event 5  -> MULTIPLE_FAILED_LOGINS
# Event 10 -> BRUTE_FORCE
# ==========================================================

failed_login_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "FAILED_LOGIN"
    }

]


# ==========================================================
# TEST 2 : LOGIN SUCCESS RULES
#
# Expected:
#
# Event 1
#   BUSINESS_HOURS_LOGIN
#
# Event 2
#   BUSINESS_HOURS_LOGIN
#   CONCURRENT_LOGIN
#
# Event 3
#   BUSINESS_HOURS_LOGIN
#   CONCURRENT_LOGIN
#   MULTIPLE_IP_LOGIN
# ==========================================================

login_success_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "source_ip": "192.168.1.10",
        "timestamp": datetime(2026, 7, 22, 2, 0, 0)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "source_ip": "192.168.1.11",
        "timestamp": datetime(2026, 7, 22, 2, 0, 20)
    },

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "source_ip": "192.168.1.12",
        "timestamp": datetime(2026, 7, 22, 2, 0, 40)
    }

]


# ==========================================================
# TEST 3 : DISABLED USER LOGIN
#
# Expected:
#
# Event 1
#   DISABLED_USER_LOGIN
# ==========================================================

disabled_user_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "user_status": "DISABLED",
        "source_ip": "10.0.0.10",
        "timestamp": datetime.utcnow()
    }

]


# ==========================================================
# TEST 4 : SERVICE ACCOUNT LOGIN
#
# Expected:
#
# Event 1
#   SERVICE_ACCOUNT_LOGIN
# ==========================================================

service_account_events = [

    {
        "username": "backup-service",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "account_type": "SERVICE",
        "source_ip": "10.0.0.20",
        "timestamp": datetime.utcnow()
    }

]


# ==========================================================
# TEST 5 : MULTIPLE PROVIDER LOGIN
#
# Expected:
#
# Event 2
#   MULTIPLE_PROVIDER_LOGIN
# ==========================================================

multiple_provider_events = [

    {
        "username": "krish",
        "provider": "AWS",
        "event_type": "LOGIN_SUCCESS",
        "source_ip": "192.168.1.10",
        "timestamp": datetime(2026, 7, 22, 10, 0, 0)
    },

    {
        "username": "krish",
        "provider": "Azure",
        "event_type": "LOGIN_SUCCESS",
        "source_ip": "192.168.1.11",
        "timestamp": datetime(2026, 7, 22, 10, 2, 0)
    }

]


# ==========================================================
# RUN ALL TESTS
# ==========================================================

if __name__ == "__main__":

    run_test(
        "TEST 1 : FAILED LOGIN RULES",
        failed_login_events
    )

    run_test(
        "TEST 2 : LOGIN SUCCESS RULES",
        login_success_events
    )

    run_test(
        "TEST 3 : DISABLED USER LOGIN",
        disabled_user_events
    )

    run_test(
        "TEST 4 : SERVICE ACCOUNT LOGIN",
        service_account_events
    )

    run_test(
        "TEST 5 : MULTIPLE PROVIDER LOGIN",
        multiple_provider_events
    )

    print("\n" + "=" * 80)
    print("ALL AUTHENTICATION RULE TESTS COMPLETED")
    print("=" * 80)