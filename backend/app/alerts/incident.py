from dataclasses import dataclass, asdict
from datetime import datetime, UTC


@dataclass
class Incident:

    incident_id: str

    status: str

    priority: str

    risk_score: int

    risk_level: str

    username: str

    provider: str

    alerts: list

    created_at: str
    
    event_summary: dict = None
    
    raw_log: dict = None
    
    analyst_attention: str = "NOT REQUIRED"
    
    xdr_assessment: str = "No immediate security concern identified."
    
    notes: list = None
    
    updated_at: str = None

    def to_dict(self):

        return asdict(self)