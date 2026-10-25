from fastapi import APIRouter, Depends, HTTPException

from app.auth.permissions import require_role
from app.logger import logger
from app.schemas.incident import IncidentCreate
from app.services.audit_service import audit_service
from app.services.log_processor import log_processor

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.post("/")
async def process_cloud_log(
    raw_log: IncidentCreate,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Process an incoming cloud log.

    Supported Providers:
    - AWS
    - Azure
    - GCP

    Accessible by:
    - ADMIN
    - ANALYST
    """

    try:

        logger.info(
            f"User '{current_user['username']}' submitted a new cloud log."
        )

        incident = log_processor.process_log(
            raw_log.model_dump()
        )

        # -----------------------------
        # Audit Log
        # -----------------------------
        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="UPLOAD_LOG",
            resource=str(incident.get("incident_id") or incident.get("event_id") or "EVENT"),
            status="SUCCESS"
        )

        return {
            "success": True,
            "message": "Log processed successfully.",
            "processed_by": current_user["username"],
            "incident": incident
        }

    except Exception as e:

        logger.exception("Error while processing cloud log.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


@router.get("/")
@router.get("/search")
async def list_cloud_logs(
    provider: str = None,
    risk_level: str = None,
    status: str = None,
    username: str = None,
    event_name: str = None,
    region: str = None,
    is_incident: bool = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    size: int = 10,
    sort_by: str = "timestamp",
    sort_order: str = "desc",
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve and search processed cloud events / logs from OpenSearch.
    Accessible by ADMIN and ANALYST.
    """
    try:
        from app.services.event_service import event_service
        return event_service.search_events(
            provider=provider,
            risk_level=risk_level,
            status=status,
            username=username,
            event_name=event_name,
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
        logger.exception("Failed to retrieve cloud logs.")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )