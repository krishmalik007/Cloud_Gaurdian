"""
Cloud Guardian — Pydantic data models for normalized log schema.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    AWS = "AWS"
    AZURE = "Azure"


class EventCategory(str, Enum):
    """Event category classification."""
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    NETWORK = "Network"
    STORAGE = "Storage"
    COMPUTE = "Compute"
    IAM = "IAM"
    DATA = "Data"
    CONFIGURATION = "Configuration"
    UNKNOWN = "Unknown"


class Severity(str, Enum):
    """Event severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class EventStatus(str, Enum):
    """Event execution result."""
    SUCCESS = "Success"
    FAILURE = "Failure"


class NormalizedLog(BaseModel):
    """
    The core normalized log schema used across the entire Cloud Guardian pipeline.
    Every log — regardless of cloud provider — is converted to this format before
    being processed by the Correlation Engine, Risk Scoring Engine, and Alert Engine.
    """
    log_id: str = Field(..., description="Unique identifier for the log entry", examples=["LOG-10001"])
    timestamp: datetime = Field(..., description="Time when the event occurred")
    cloud_provider: CloudProvider = Field(..., description="Cloud provider (AWS or Azure)")
    service: str = Field(..., description="Cloud service generating the log", examples=["CloudTrail", "VPC Flow Logs"])
    event_name: str = Field(..., description="Name of the security event", examples=["ConsoleLogin", "CreateUser"])
    event_category: EventCategory = Field(
        default=EventCategory.UNKNOWN,
        description="Category of the event"
    )
    user: str = Field(..., description="Username or identity associated with the event")
    source_ip: str = Field(..., description="Source IP address", examples=["192.168.1.15"])
    destination_ip: str = Field(default="", description="Destination IP address (if applicable)")
    resource: str = Field(default="", description="Resource affected by the event")
    action: str = Field(..., description="Action performed", examples=["Login", "Create", "Delete"])
    status: EventStatus = Field(..., description="Success or Failure")
    severity: Severity = Field(default=Severity.LOW, description="Event severity level")
    region: str = Field(default="", description="Cloud region where the event occurred")
    risk_score: int = Field(default=0, ge=0, le=100, description="Risk score assigned by the Risk Engine")
    correlation_id: str = Field(default="", description="Incident ID generated after correlation")
    raw_log: dict[str, Any] = Field(default_factory=dict, description="Original cloud log without modification")

    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "LOG-10001",
                "timestamp": "2026-07-17T10:25:30Z",
                "cloud_provider": "AWS",
                "service": "CloudTrail",
                "event_name": "ConsoleLogin",
                "event_category": "Authentication",
                "user": "admin",
                "source_ip": "192.168.1.15",
                "destination_ip": "",
                "resource": "AWS Management Console",
                "action": "Login",
                "status": "Success",
                "severity": "Low",
                "region": "ap-south-1",
                "risk_score": 20,
                "correlation_id": "",
                "raw_log": {}
            }
        }


class RawAWSCloudTrailLog(BaseModel):
    """Schema for raw AWS CloudTrail log events."""
    eventVersion: str = Field(default="1.08")
    eventTime: str = Field(..., description="Timestamp of the event")
    eventSource: str = Field(..., description="AWS service source", examples=["signin.amazonaws.com"])
    eventName: str = Field(..., description="API action name", examples=["ConsoleLogin"])
    awsRegion: str = Field(..., description="AWS region")
    sourceIPAddress: str = Field(default="", description="Source IP address")
    userIdentity: dict[str, Any] = Field(default_factory=dict, description="User identity details")
    requestParameters: dict[str, Any] | None = Field(default=None)
    responseElements: dict[str, Any] | None = Field(default=None)
    errorCode: str | None = Field(default=None)
    errorMessage: str | None = Field(default=None)


class RawAWSVPCFlowLog(BaseModel):
    """Schema for raw AWS VPC Flow Log records."""
    version: int = Field(default=2)
    account_id: str = Field(default="")
    interface_id: str = Field(default="")
    srcaddr: str = Field(..., description="Source IP address")
    dstaddr: str = Field(..., description="Destination IP address")
    srcport: int = Field(..., description="Source port")
    dstport: int = Field(..., description="Destination port")
    protocol: int = Field(..., description="Protocol number (6=TCP, 17=UDP)")
    packets: int = Field(default=0)
    bytes: int = Field(default=0)
    start: int = Field(..., description="Unix timestamp of flow start")
    end: int = Field(..., description="Unix timestamp of flow end")
    action: str = Field(..., description="ACCEPT or REJECT")
    log_status: str = Field(default="OK")


class RawAzureActivityLog(BaseModel):
    """Schema for raw Azure Activity Log events."""
    time: str = Field(..., description="Timestamp of the event")
    resourceId: str = Field(default="", description="Azure resource ID")
    operationName: dict[str, str] = Field(..., description="Operation name with value and localizedValue")
    category: dict[str, str] = Field(default_factory=dict)
    resultType: str = Field(default="Success", description="Success or Failure")
    caller: str = Field(default="", description="Identity of the caller")
    callerIpAddress: str = Field(default="", description="Caller IP address")
    properties: dict[str, Any] = Field(default_factory=dict)


class LogIngestionRequest(BaseModel):
    """Request body for the log ingestion REST endpoint."""
    cloud_provider: CloudProvider = Field(..., description="Source cloud provider")
    log_type: str = Field(
        ...,
        description="Type of log being ingested",
        examples=["cloudtrail", "vpc_flow", "azure_activity"]
    )
    logs: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of raw log entries to ingest (max 1000 per request)"
    )


class LogIngestionResponse(BaseModel):
    """Response body for the log ingestion endpoint."""
    status: str = Field(..., description="Processing status")
    processed: int = Field(..., description="Number of logs successfully processed")
    failed: int = Field(default=0, description="Number of logs that failed processing")
    log_ids: list[str] = Field(default_factory=list, description="IDs of the processed logs")
