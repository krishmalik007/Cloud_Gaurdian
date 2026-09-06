from datetime import datetime
from typing import Optional, Literal
import json
from pydantic import BaseModel, Field, field_validator


class IncidentCreate(BaseModel):
    provider: str = Field(..., json_schema_extra={"example": "AWS"})
    eventName: str = Field(..., json_schema_extra={"example": "ConsoleLogin"})
    eventTime: datetime
    awsRegion: Optional[str] = None
    sourceIPAddress: Optional[str] = None
    userIdentity: dict

    @field_validator("userIdentity")
    @classmethod
    def validate_user_identity_size(cls, v: dict) -> dict:
        dumped = json.dumps(v)
        if len(dumped) > 8192:  # 8KB max
            raise ValueError("userIdentity payload too large")
        
        # Depth check
        def depth(d):
            if isinstance(d, dict):
                return 1 + (max(map(depth, d.values())) if d else 0)
            if isinstance(d, list):
                return 1 + (max(map(depth, d)) if d else 0)
            return 0
            
        if depth(v) > 10:
            raise ValueError("userIdentity payload too deep")
        return v


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
    event_summary: Optional[dict] = None
    raw_log: Optional[dict] = None
    analyst_attention: Optional[str] = "NOT REQUIRED"
    xdr_assessment: Optional[str] = "No immediate security concern identified."
    notes: Optional[list] = []
    updated_at: Optional[datetime] = None


class IncidentStatusUpdate(BaseModel):
    status: Literal["OPEN", "INVESTIGATING", "RESOLVED"] = Field(..., description="The new status of the incident")


class IncidentNoteCreate(BaseModel):
    note: str = Field(..., min_length=1, description="The content of the investigation note")


class IncidentNote(BaseModel):
    note: str
    author: str
    timestamp: datetime


class IncidentSearch(BaseModel):
    provider: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    username: Optional[str] = None
    page: int = 1
    size: int = 10