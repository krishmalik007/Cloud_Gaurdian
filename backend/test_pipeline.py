from app.pipeline.incident_pipeline import incident_pipeline

event = {
    "provider": "AWS",
    "username": "krish",
    "event_name": "GetObject",
    "resource": "SensitiveBucket",
    "bytes_transferred": 6000000000,
    "audit_logging_enabled": False,
    "severity": "CRITICAL"
}

incident = incident_pipeline.process_event(event)

print("=" * 80)
print("PIPELINE TEST")
print("=" * 80)

print(f"Incident ID : {incident['incident_id']}")
print(f"Status      : {incident['status']}")
print(f"Priority    : {incident['priority']}")
print(f"Risk Score  : {incident['risk_score']}")
print(f"Risk Level  : {incident['risk_level']}")
print(f"User        : {incident['username']}")
print(f"Provider    : {incident['provider']}")

print("\nAlerts")
for alert in incident["alerts"]:
    print(f"- {alert['alert_type']} ({alert['severity']})")

print("\n" + "=" * 80)
print("PIPELINE TEST PASSED")
print("=" * 80)
