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

    def to_dict(self):

        return asdict(self)