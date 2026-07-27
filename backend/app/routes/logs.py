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
            resource=incident["incident_id"],
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
            detail=str(e)
        )