from typing import Protocol

from app.models.types import JsonObject


class VenueDataRepository(Protocol):
    async def get_venue(self, venue_id: str) -> JsonObject | None: ...

    async def get_event(self, event_id: str | None) -> JsonObject | None: ...

    async def get_crowd_zones(self, venue_id: str) -> list[JsonObject]: ...

    async def get_active_incidents(self, venue_id: str) -> list[JsonObject]: ...

    async def get_venue_graph(self, venue_id: str) -> JsonObject | None: ...


class CrowdTrendRepository(Protocol):
    async def query_recent_crowd_trends(
        self,
        venue_id: str,
        event_id: str | None,
    ) -> list[JsonObject]: ...


class EventPublisher(Protocol):
    async def publish_operations_event(self, event: JsonObject) -> str: ...

    async def publish_sustainability_event(self, event: JsonObject) -> str: ...
