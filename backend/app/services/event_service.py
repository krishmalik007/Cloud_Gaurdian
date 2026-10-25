from typing import Optional
from app.logger import logger
from app.storage.event_repository import event_repository


class EventService:
    """
    Service responsible for querying, searching, and managing cloud events
    stored in the OpenSearch `events` index.
    """

    def get_all_events(self, limit: int = 100) -> list:
        logger.info(f"Fetching {limit} recent cloud events.")
        return event_repository.get_all_events(limit=limit)

    def get_event(self, event_id: str) -> Optional[dict]:
        logger.info(f"Fetching cloud event: {event_id}")
        return event_repository.get_event(event_id)

    def search_events(
        self,
        provider: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        username: Optional[str] = None,
        event_name: Optional[str] = None,
        event_type: Optional[str] = None,
        region: Optional[str] = None,
        is_incident: Optional[bool] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> dict:
        logger.info(
            f"Searching cloud events. Provider: {provider} | Status: {status} | "
            f"Risk: {risk_level} | Type: {event_type} | Page: {page} | Size: {size}"
        )
        return event_repository.search_events(
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

    def get_stats(self) -> dict:
        logger.info("Fetching cloud event statistics.")
        return event_repository.get_event_stats()

    def count_events(self) -> int:
        return event_repository.count_events()


event_service = EventService()
