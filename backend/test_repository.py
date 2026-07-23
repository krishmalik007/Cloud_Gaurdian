from app.pipeline.incident_pipeline import incident_pipeline
from app.storage.incident_repository import incident_repository

event = {
    "provider": "AWS",
    "username": "krish",
    "event_name": "GetObject",
    "resource": "SensitiveBucket",
    "bytes_transferred": 7000000000,
    "audit_logging_enabled": False,
    "severity": "CRITICAL"
}

incident = incident_pipeline.process_event(event)

incident_repository.save_incident(incident)

print("=" * 80)
print("INCIDENT SAVED")
print("=" * 80)

print(incident["incident_id"])

stored = incident_repository.get_incident(
    incident["incident_id"]
)

print("\nRetrieved Incident")

print(stored["_source"])

print("\nRepository Test Passed")
