from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    provider: str = Field(..., example="AWS")
    eventName: str = Field(..., example="ConsoleLogin")
    eventTime: datetime
    awsRegion: Optional[str] = None
    sourceIPAddress: Optional[str] = None
    userIdentity: dict


class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    priority: str
    risk_score: int
    risk_level: str
    username: str
    provider: str
    alerts: list
    created_at: datetime


class IncidentSearch(BaseModel):
    provider: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    username: Optional[str] = None
    page: int = 1
    size: int = 10