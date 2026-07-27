from fastapi import APIRouter, HTTPException

from app.logger import logger
from app.services.incident_service import incident_service

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.get("/")
async def get_all_incidents():
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    """
    Retrieve a single incident.
    """
    try:
        incident = incident_service.get_incident(incident_id)

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
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    """
    Delete an incident.
    """
    try:
        deleted = incident_service.delete_incident(incident_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        return {
            "success": True,
            "message": f"Incident '{incident_id}' deleted successfully."
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Failed to delete incident.")
        raise HTTPException(status_code=500, detail=str(e))