from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.permissions import require_role
from app.logger import logger
from app.services.event_service import event_service

ALLOWED_EVENT_SORT_FIELDS = Literal[
    "timestamp", "ingested_at", "risk_score", "status", "provider", "username", "event_name"
]
ALLOWED_EVENT_SORT_ORDERS = Literal["asc", "desc"]

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.get("/")
@router.get("/search")
async def search_events(
    provider: Optional[str] = Query(None, description="Cloud provider filter (e.g. AWS, Azure, GCP)"),
    risk_level: Optional[str] = Query(None, description="Risk level filter (e.g. LOW, MEDIUM, HIGH, CRITICAL)"),
    status: Optional[str] = Query(None, description="Event status (e.g. INFORMATIONAL, OPEN, RESOLVED)"),
    username: Optional[str] = Query(None, description="IAM username or principal"),
    event_name: Optional[str] = Query(None, description="AWS/Cloud API event name (e.g. GetCallerIdentity)"),
    event_type: Optional[str] = Query(None, description="Event classification type (e.g. AUTHENTICATION, FAILED_LOGIN, UPDATE_POLICY)"),
    region: Optional[str] = Query(None, description="AWS region (e.g. ap-south-1)"),
    is_incident: Optional[bool] = Query(None, description="Filter for incident-generating events vs routine events"),
    search: Optional[str] = Query(None, description="Free text search query across event fields"),
    start_date: Optional[str] = Query(None, description="Start timestamp (ISO 8601)"),
    end_date: Optional[str] = Query(None, description="End timestamp (ISO 8601)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=500, description="Page size"),
    sort_by: ALLOWED_EVENT_SORT_FIELDS = Query("timestamp", description="Sort field"),
    sort_order: ALLOWED_EVENT_SORT_ORDERS = Query("desc", description="Sort order"),
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Search and paginate cloud events from the OpenSearch `events` index.
    Accessible by ADMIN and ANALYST.
    """
    try:
        return event_service.search_events(
            provider=provider,
            risk_level=risk_level,
            status=status,
            username=username,
            event_name=event_name,
            event_type=event_type,
            region=region,
            is_incident=is_incident,
            search=search,
            start_date=start_date,
            end_date=end_date,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        logger.exception(f"Event search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve cloud events from OpenSearch."
        )


@router.get("/stats")
async def get_event_stats(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve aggregated cloud event statistics (totals, informational vs incident, providers).
    Accessible by ADMIN and ANALYST.
    """
    try:
        return event_service.get_stats()
    except Exception as e:
        logger.exception(f"Failed to fetch event statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch event statistics from OpenSearch."
        )


@router.get("/{event_id}")
async def get_event_by_id(
    event_id: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve an individual cloud event by its unique ID from the `events` index.
    Accessible by ADMIN and ANALYST.
    """
    try:
        event = event_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail=f"Event '{event_id}' not found."
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch event '{event_id}': {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch event from OpenSearch."
        )
