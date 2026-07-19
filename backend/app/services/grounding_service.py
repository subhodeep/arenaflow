from typing import Any

from app.models.requests import BaseArenaRequest
from app.repositories.bigquery_repo import BigQueryRepository
from app.repositories.firestore_repo import FirestoreRepository
from app.services.maps_service import MapsService


class GroundingService:
    def __init__(self, firestore_repo: FirestoreRepository, bigquery_repo: BigQueryRepository, maps_service: MapsService):
        self.firestore_repo = firestore_repo
        self.bigquery_repo = bigquery_repo
        self.maps_service = maps_service

    async def build_context(self, request: BaseArenaRequest, include_maps: bool = False) -> dict[str, Any]:
        sources: list[dict[str, Any]] = []
        context: dict[str, Any] = {
            "venue_id": request.venue_id,
            "event_id": request.event_id,
            "language": request.language,
            "sources": sources,
        }

        await self._safe_add(sources, "venue", lambda: self.firestore_repo.get_venue(request.venue_id))
        await self._safe_add(sources, "event", lambda: self.firestore_repo.get_event(request.event_id))
        await self._safe_add(sources, "crowd_zones", lambda: self.firestore_repo.get_crowd_zones(request.venue_id))
        await self._safe_add(sources, "incidents", lambda: self.firestore_repo.get_active_incidents(request.venue_id))
        await self._safe_add(sources, "crowd_trends", lambda: self.bigquery_repo.query_recent_crowd_trends(request.venue_id, request.event_id))
        if include_maps:
            await self._safe_add(sources, "maps", lambda: self.maps_service.context_for_request(request))
        return context

    async def _safe_add(self, sources: list[dict[str, Any]], name: str, loader):
        try:
            data = await loader()
            sources.append({"name": name, "available": data is not None, "data": data, "reason": None if data is not None else "not_found"})
        except Exception as exc:
            sources.append({"name": name, "available": False, "reason": exc.__class__.__name__, "data": None})
