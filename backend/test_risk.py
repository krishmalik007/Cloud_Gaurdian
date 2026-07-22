from app.risk.risk_engine import risk_engine


def print_result(test_name, result):

    print("\n" + "=" * 80)
    print(test_name)
    print("=" * 80)

    print(f"Risk Score : {result['score']}")
    print(f"Risk Level : {result['level']}")
    print(f"Alert Count: {result['alert_count']}")

    print("\nAlerts:")

    if result["alerts"]:

        for alert in result["alerts"]:
            print(alert)

    else:
        print("No Alerts")


# ============================================================
# TEST 1
# LOW RISK
# ============================================================

alerts = [

    {
        "alert_type": "BUSINESS_HOURS_LOGIN"
    }

]

result = risk_engine.calculate_risk(alerts)

print_result("TEST 1 : LOW RISK", result)


# ============================================================
# TEST 2
# MEDIUM RISK
# ============================================================

alerts = [

    {
        "alert_type": "BUSINESS_HOURS_LOGIN"
    },

    {
        "alert_type": "MULTIPLE_FAILED_LOGINS"
    }

]

result = risk_engine.calculate_risk(alerts)

print_result("TEST 2 : MEDIUM RISK", result)


# ============================================================
# TEST 3
# HIGH RISK
# ============================================================

alerts = [

    {
        "alert_type": "BRUTE_FORCE"
    },

    {
        "alert_type": "MULTIPLE_IP_LOGIN"
    },

    {
        "alert_type": "PUBLIC_BUCKET"
    }

]

result = risk_engine.calculate_risk(alerts)

print_result("TEST 3 : HIGH RISK", result)


# ============================================================
# TEST 4
# CRITICAL RISK
# ============================================================

alerts = [

    {
        "alert_type": "DATA_EXFILTRATION"
    },

    {
        "alert_type": "AUDIT_LOGGING_DISABLED"
    },

    {
        "alert_type": "IAM_PRIVILEGE_ESCALATION"
    }

]

result = risk_engine.calculate_risk(alerts)

print_result("TEST 4 : CRITICAL RISK", result)


# ============================================================
# TEST 5
# EMPTY ALERT LIST
# ============================================================

alerts = []

result = risk_engine.calculate_risk(alerts)

print_result("TEST 5 : EMPTY ALERT LIST", result)


# ============================================================
# TEST 6
# UNKNOWN ALERT TYPE
# ============================================================

alerts = [

    {
        "alert_type": "UNKNOWN_ALERT"
    }

]

result = risk_engine.calculate_risk(alerts)

print_result("TEST 6 : UNKNOWN ALERT", result)


print("\n")
print("=" * 80)
print("ALL RISK ENGINE TESTS PASSED")
print("=" * 80)