from app.logger import logger
from app.storage.incident_repository import incident_repository


class DashboardService:
    """
    Dashboard Analytics Service
    """

    def get_summary(self):
        logger.info("Fetching dashboard summary.")
        return incident_repository.get_dashboard_summary()

    def get_provider_stats(self):
        logger.info("Fetching provider statistics.")
        return incident_repository.get_provider_stats()

    def get_risk_distribution(self):
        logger.info("Fetching risk distribution.")
        return incident_repository.get_risk_distribution()

    def get_recent_incidents(self, limit: int = 10):
        logger.info(f"Fetching {limit} recent incidents.")
        return incident_repository.get_recent_incidents(limit)

    def get_active_analysts_count(self):
        from app.storage.session_repository import session_repository
        logger.info("Fetching active analyst sessions count.")
        count = session_repository.count_active_analyst_users()
        return {"count": count}

dashboard_service = DashboardService()