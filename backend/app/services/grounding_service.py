from collections.abc import Awaitable, Callable
from typing import Any

from app.models.domain import GroundingContext, GroundingSource
from app.models.requests import BaseArenaRequest
from app.repositories.protocols import CrowdTrendRepository, VenueDataRepository
from app.services.maps_service import MapsService

GroundingLoader = Callable[[], Awaitable[Any]]


class GroundingService:
    def __init__(
        self,
        firestore_repo: VenueDataRepository,
        bigquery_repo: CrowdTrendRepository,
        maps_service: MapsService,
    ):
        self.firestore_repo = firestore_repo
        self.bigquery_repo = bigquery_repo
        self.maps_service = maps_service

    async def build_context(
        self,
        request: BaseArenaRequest,
        include_maps: bool = False,
    ) -> GroundingContext:
        sources: list[GroundingSource] = []
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
            sources.append(await self._safe_source(name, loader))

        return GroundingContext(
            venue_id=request.venue_id,
            event_id=request.event_id,
            language=request.language,
            sources=sources,
        )

    async def _safe_source(self, name: str, loader: GroundingLoader) -> GroundingSource:
        try:
            data = await loader()
            return self._available_source(name, data)
        except Exception as exc:
            return GroundingSource(
                name=name,
                available=False,
                reason=exc.__class__.__name__,
                data=None,
            )

    def _available_source(self, name: str, data: Any) -> GroundingSource:
        return GroundingSource(
            name=name,
            available=data is not None,
            data=data,
            reason=None if data is not None else "not_found",
        )
