from app.alerts.alert_engine import alert_engine
from app.risk.risk_engine import risk_engine


def print_incident(incident):

    print("\n" + "=" * 80)
    print("SECURITY INCIDENT")
    print("=" * 80)

    print(f"Incident ID : {incident['incident_id']}")
    print(f"Status      : {incident['status']}")
    print(f"Priority    : {incident['priority']}")
    print(f"Risk Score  : {incident['risk_score']}")
    print(f"Risk Level  : {incident['risk_level']}")
    print(f"User        : {incident['username']}")
    print(f"Provider    : {incident['provider']}")
    print(f"Created At  : {incident['created_at']}")

    print("\nAlerts")

    for alert in incident["alerts"]:
        print(f"- {alert['alert_type']} ({alert['severity']})")


# ============================================================
# SAMPLE EVENT
# ============================================================

event = {

    "username": "krish",

    "provider": "AWS"

}


# ============================================================
# SAMPLE ALERTS
# ============================================================

alerts = [

    {

        "alert_type": "DATA_EXFILTRATION",

        "severity": "CRITICAL"

    },

    {

        "alert_type": "AUDIT_LOGGING_DISABLED",

        "severity": "CRITICAL"

    },

    {

        "alert_type": "IAM_PRIVILEGE_ESCALATION",

        "severity": "CRITICAL"

    }

]


# ============================================================
# CALCULATE RISK
# ============================================================

risk = risk_engine.calculate_risk(alerts)


# ============================================================
# CREATE INCIDENT
# ============================================================

incident = alert_engine.generate_incident(

    event,

    risk

)


print_incident(incident)


print("\n")
print("=" * 80)
print("ALERT ENGINE TEST PASSED")
print("=" * 80)
