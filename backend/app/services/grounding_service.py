from collections.abc import Awaitable, Callable
from typing import Any

from app.models.requests import BaseArenaRequest
from app.repositories.bigquery_repo import BigQueryRepository
from app.repositories.firestore_repo import FirestoreRepository
from app.services.maps_service import MapsService

GroundingLoader = Callable[[], Awaitable[Any]]


class GroundingService:
    def __init__(
        self,
        firestore_repo: FirestoreRepository,
        bigquery_repo: BigQueryRepository,
        maps_service: MapsService,
    ):
        self.firestore_repo = firestore_repo
        self.bigquery_repo = bigquery_repo
        self.maps_service = maps_service

    async def build_context(
        self,
        request: BaseArenaRequest,
        include_maps: bool = False,
    ) -> dict[str, Any]:
        sources: list[dict[str, Any]] = []
        context: dict[str, Any] = {
            "venue_id": request.venue_id,
            "event_id": request.event_id,
            "language": request.language,
            "sources": sources,
        }

        loaders: list[tuple[str, GroundingLoader]] = [
            ("venue", lambda: self.firestore_repo.get_venue(request.venue_id)),
            ("event", lambda: self.firestore_repo.get_event(request.event_id)),
            ("crowd_zones", lambda: self.firestore_repo.get_crowd_zones(request.venue_id)),
            ("incidents", lambda: self.firestore_repo.get_active_incidents(request.venue_id)),
            (
                "crowd_trends",
                lambda: self.bigquery_repo.query_recent_crowd_trends(
                    request.venue_id,
                    request.event_id,
                ),
            ),
        ]
        if include_maps:
            loaders.append(("maps", lambda: self.maps_service.context_for_request(request)))

        for name, loader in loaders:
            await self._safe_add(sources, name, loader)
        return context

    async def _safe_add(
        self,
        sources: list[dict[str, Any]],
        name: str,
        loader: GroundingLoader,
    ) -> None:
        try:
            data = await loader()
            sources.append(self._available_source(name, data))
        except Exception as exc:
            sources.append(
                {"name": name, "available": False, "reason": exc.__class__.__name__, "data": None}
            )

    def _available_source(self, name: str, data: Any) -> dict[str, Any]:
        return {
            "name": name,
            "available": data is not None,
            "data": data,
            "reason": None if data is not None else "not_found",
        }
