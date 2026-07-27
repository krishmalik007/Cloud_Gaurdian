from typing import Optional

from pydantic import BaseModel, Field


class IncidentSearchQuery(BaseModel):
    provider: Optional[str] = Field(default=None)
    risk_level: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)

    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

    sort_by: str = "created_at"
    sort_order: str = "desc"