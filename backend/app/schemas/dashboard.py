from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_incidents: int
    open_incidents: int
    closed_incidents: int
    high_risk: int
    medium_risk: int
    low_risk: int


class ProviderStats(BaseModel):
    provider: str
    count: int


class RiskDistribution(BaseModel):
    risk_level: str
    count: int