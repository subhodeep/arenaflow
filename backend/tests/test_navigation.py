import pytest
from pydantic import ValidationError

from app.models.requests import NavigationRouteRequest
from app.services.venue_graph_service import VenueGraphService


class EmptyVenueGraphRepository:
    async def get_venue_graph(self, venue_id: str):
        return None


@pytest.mark.asyncio
async def test_venue_graph_service_returns_safe_fallback_without_graph():
    service = VenueGraphService(EmptyVenueGraphRepository())
    steps = await service.route("venue", "Gate A", "Section 120", ["step-free"])

    assert steps[0].instruction == "Follow venue signage from Gate A to Section 120."
    assert steps[0].accessibility_notes == ["step-free"]


def test_navigation_request_requires_origin_and_destination():
    with pytest.raises(ValidationError):
        NavigationRouteRequest(venue_id="venue", origin="", destination="Section 120")
