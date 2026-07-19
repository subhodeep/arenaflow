import pytest

from app.models.requests import AssistantChatRequest
from app.services.grounding_service import GroundingService


class FailingFirestoreRepository:
    async def get_venue(self, venue_id: str):
        raise RuntimeError("venue unavailable")

    async def get_event(self, event_id: str | None):
        return None

    async def get_crowd_zones(self, venue_id: str):
        return [{"zone_id": "gate-a", "density_score": 0.2}]

    async def get_active_incidents(self, venue_id: str):
        return []


class CrowdTrendsRepository:
    async def query_recent_crowd_trends(self, venue_id: str, event_id: str | None):
        return [{"zone_id": "gate-a", "avg_density": 0.2}]


class MapsRepository:
    async def context_for_request(self, request):
        return {"available": True, "mode": "test-map"}


@pytest.mark.asyncio
async def test_grounding_service_records_source_failures_and_continues():
    service = GroundingService(
        FailingFirestoreRepository(),
        CrowdTrendsRepository(),
        MapsRepository(),
    )
    request = AssistantChatRequest(venue_id="venue", event_id="event", message="hello")

    context = await service.build_context(request, include_maps=True)
    sources = {source.name: source for source in context.sources}

    assert sources["venue"].available is False
    assert sources["venue"].reason == "RuntimeError"
    assert sources["crowd_zones"].available is True
    assert sources["maps"].available is True
