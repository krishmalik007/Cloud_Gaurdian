from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.permissions import require_role
from app.logger import logger
from app.services.audit_service import audit_service
from app.services.incident_service import incident_service
from app.schemas.incident import IncidentStatusUpdate, IncidentNoteCreate

# Whitelist of allowed sort fields for incident search
ALLOWED_SORT_FIELDS = Literal["created_at", "risk_score", "status", "provider", "username"]
ALLOWED_SORT_ORDERS = Literal["asc", "desc"]

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


# --------------------------------------------------
# Get All Incidents
# --------------------------------------------------
@router.get("/")
async def get_all_incidents(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve all incidents.
    """

    try:

        incidents = incident_service.get_all_incidents()

        return {
            "success": True,
            "count": len(incidents),
            "incidents": incidents
        }

    except Exception as e:

        logger.exception("Failed to fetch incidents.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


# --------------------------------------------------
# Search Incidents
# --------------------------------------------------
@router.get("/search")
async def search_incidents(
    provider: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: ALLOWED_SORT_FIELDS = Query("created_at"),
    sort_order: ALLOWED_SORT_ORDERS = Query("desc"),
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Search incidents using filters.
    """

    try:

        return incident_service.search_incidents(
            provider=provider,
            risk_level=risk_level,
            status=status,
            username=username,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )

    except Exception as e:

        logger.exception("Incident search failed.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


# --------------------------------------------------
# Get Incident
# --------------------------------------------------
@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve a single incident.
    """

    try:

        incident = incident_service.get_incident(
            incident_id
        )

        if not incident:

            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        return incident

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to fetch incident.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


# --------------------------------------------------
# Delete Incident
# --------------------------------------------------
@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: str,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Delete an incident.

    Accessible by:
    - ADMIN
    """

    try:

        deleted = incident_service.delete_incident(
            incident_id
        )

        if not deleted:

            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        # ----------------------------------------
        # Audit Log
        # ----------------------------------------
        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="DELETE_INCIDENT",
            resource=incident_id,
            status="SUCCESS"
        )

        return {
            "success": True,
            "message": f"Incident '{incident_id}' deleted successfully."
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to delete incident.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


# --------------------------------------------------
# Update Incident Status
# --------------------------------------------------
@router.put("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status_update: IncidentStatusUpdate,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Update incident status.
    """
    try:
        updated_incident = incident_service.update_status(
            incident_id,
            status_update.status,
            current_user
        )

        if not updated_incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        return updated_incident

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update incident status.")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )


# --------------------------------------------------
# Add Investigation Note
# --------------------------------------------------
@router.post("/{incident_id}/notes")
async def add_incident_note(
    incident_id: str,
    note: IncidentNoteCreate,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Add a note to an incident.
    """
    try:
        updated_incident = incident_service.add_note(
            incident_id,
            note.note,
            current_user
        )

        if not updated_incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        return updated_incident

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to add incident note.")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred."
        )