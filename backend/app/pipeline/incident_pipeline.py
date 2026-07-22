from app.correlation.correlation_engine import correlation_engine
from app.risk.risk_engine import risk_engine
from app.alerts.alert_engine import alert_engine


class IncidentPipeline:
    """
    End-to-End Event Processing Pipeline

    Flow:
        Cloud Event
            ↓
        Correlation Engine
            ↓
        Risk Engine
            ↓
        Alert Engine
            ↓
        Security Incident
    """

    def process_event(self, event):
        # Step 1: Detect alerts
        alerts = correlation_engine.process_event(event)

        # Step 2: Calculate risk
        risk_result = risk_engine.calculate_risk(alerts)

        # Step 3: Generate incident
        incident = alert_engine.generate_incident(event, risk_result)

        return incident


incident_pipeline = IncidentPipeline()