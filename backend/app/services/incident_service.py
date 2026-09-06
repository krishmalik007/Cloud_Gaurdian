from datetime import datetime, UTC
from app.logger import logger
from app.storage.incident_repository import incident_repository
from app.services.audit_service import audit_service


class IncidentService:
    """
    Service responsible for incident management.
    """

    def get_all_incidents(self):
        logger.info("Fetching all incidents.")
        return incident_repository.get_all_incidents()

    def get_incident(self, incident_id: str):
        logger.info(f"Fetching incident: {incident_id}")
        return incident_repository.get_incident(incident_id)

    def delete_incident(self, incident_id: str):
        logger.info(f"Deleting incident: {incident_id}")
        return incident_repository.delete_incident(incident_id)
    def search_incidents(
        self,
        provider=None,
        risk_level=None,
        status=None,
        username=None,
        page=1,
        size=10,
        sort_by="created_at",
        sort_order="desc"
    ):
        logger.info("Searching incidents.")
        return incident_repository.search_incidents(
            provider=provider,
            risk_level=risk_level,
            status=status,
            username=username,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def update_status(self, incident_id: str, new_status: str, user: dict):
        logger.info(f"Updating status for incident {incident_id} to {new_status}")
        incident = incident_repository.get_incident(incident_id)
        
        if not incident:
            return None
            
        old_status = incident.get("status", "OPEN")
        incident["status"] = new_status
        incident["updated_at"] = datetime.now(UTC).isoformat()
        
        updated_incident = incident_repository.save_incident(incident)
        
        audit_service.create_log(
            user_id=user.get("user_id", "Unknown"),
            username=user.get("username", "Unknown"),
            action="UPDATE_INCIDENT_STATUS",
            resource=f"Incident:{incident_id} ({old_status}->{new_status})",
            status="SUCCESS"
        )
        
        return updated_incident
        
    def add_note(self, incident_id: str, note_text: str, user: dict):
        logger.info(f"Adding note to incident {incident_id}")
        incident = incident_repository.get_incident(incident_id)
        
        if not incident:
            return None
            
        if not incident.get("notes"):
            incident["notes"] = []
            
        note = {
            "note": note_text,
            "author": user.get("username", "Unknown"),
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        incident["notes"].append(note)
        incident["updated_at"] = datetime.now(UTC).isoformat()
        
        updated_incident = incident_repository.save_incident(incident)
        
        audit_service.create_log(
            user_id=user.get("user_id", "Unknown"),
            username=user.get("username", "Unknown"),
            action="ADD_INCIDENT_NOTE",
            resource=f"Incident:{incident_id}",
            status="SUCCESS"
        )
        
        return updated_incident


incident_service = IncidentService()