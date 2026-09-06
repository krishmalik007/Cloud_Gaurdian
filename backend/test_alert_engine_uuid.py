import re
from app.alerts.alert_engine import AlertEngine

def test_incident_ids_are_unique():
    engine = AlertEngine()
    
    event = {"event_name": "TestEvent", "username": "testuser", "provider": "AWS"}
    risk_result = {"level": "HIGH", "score": 85, "alerts": []}
    
    id1 = engine._generate_incident_id()
    id2 = engine._generate_incident_id()
    
    assert id1 != id2

def test_incident_id_format():
    engine = AlertEngine()
    
    incident_id = engine._generate_incident_id()
    
    # Expected format: INC-YYYYMMDD-<8-char-hex>
    # e.g., INC-20260905-a7f3c921
    assert re.match(r"^INC-\d{8}-[a-f0-9]{8}$", incident_id)

def test_restarting_engine_does_not_reproduce_id():
    engine1 = AlertEngine()
    id1 = engine1._generate_incident_id()
    
    # Simulate a backend restart by reinitializing the engine
    engine2 = AlertEngine()
    id2 = engine2._generate_incident_id()
    
    assert id1 != id2
