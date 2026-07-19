from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service, get_grounding_service, get_venue_graph_service
from app.core.security import enforce_request_size, rate_limit
from app.models.requests import AccessibilityPlanRequest, NavigationRouteRequest
from app.models.responses import NavigationRouteResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.venue_graph_service import VenueGraphService

router = APIRouter(prefix="/api/v1/navigation", tags=["navigation"], dependencies=[Depends(enforce_request_size), Depends(rate_limit)])


@router.post("/route", response_model=NavigationRouteResponse)
async def route(
    request: NavigationRouteRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    venue_graph: VenueGraphService = Depends(get_venue_graph_service),
) -> NavigationRouteResponse:
    context = await grounding.build_context(request, include_maps=True)
    steps = await venue_graph.route(request.venue_id, request.origin, request.destination, request.mobility_needs)
    assistant_request = request.model_copy(update={})
    fallback_context = context | {"computed_route_steps": [step.model_dump() for step in steps]}
    response = await gemini.generate_accessibility_plan(
        request=AccessibilityPlanRequest(
            venue_id=assistant_request.venue_id,
            event_id=assistant_request.event_id,
            language=assistant_request.language,
            origin=assistant_request.origin,
            destination=assistant_request.destination,
            needs=assistant_request.mobility_needs or ["general navigation"],
        ),
        context=fallback_context,
    )
    return NavigationRouteResponse(
        language=response.language,
        confidence=response.confidence,
        data_freshness=response.data_freshness,
        assumptions=response.assumptions,
        safety_notes=response.safety_notes,
        grounding_summary=response.grounding_summary,
        recommendation=response.recommendation,
        route_steps=response.route_steps or steps,
        estimated_total_minutes=sum(step.duration_minutes or 0 for step in (response.route_steps or steps)) or None,
    )
