from app.logger import logger
from app.storage.incident_repository import incident_repository


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


incident_service = IncidentService()