from fastapi import Depends

from app.api.deps import get_gemini_service, get_grounding_service, get_venue_graph_service
from app.api.router_factory import public_router
from app.models.domain import RouteStep
from app.models.requests import AccessibilityPlanRequest, NavigationRouteRequest
from app.models.responses import AccessibilityPlanResponse, NavigationRouteResponse
from app.services.context import context_as_dict
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.venue_graph_service import VenueGraphService

router = public_router("/api/v1/navigation", "navigation")


@router.post("/route", response_model=NavigationRouteResponse)
async def route(
    request: NavigationRouteRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    venue_graph: VenueGraphService = Depends(get_venue_graph_service),
) -> NavigationRouteResponse:
    context = await grounding.build_context(request, include_maps=True)
    steps = await venue_graph.route(
        request.venue_id,
        request.origin,
        request.destination,
        request.mobility_needs,
    )
    response = await gemini.generate_accessibility_plan(
        request=_to_accessibility_request(request),
        context=context_as_dict(context)
        | {"computed_route_steps": [step.model_dump() for step in steps]},
    )
    return _to_navigation_response(response, steps)


def _to_accessibility_request(request: NavigationRouteRequest) -> AccessibilityPlanRequest:
    return AccessibilityPlanRequest(
        venue_id=request.venue_id,
        event_id=request.event_id,
        language=request.language,
        origin=request.origin,
        destination=request.destination,
        needs=request.mobility_needs or ["general navigation"],
    )


def _to_navigation_response(
    response: AccessibilityPlanResponse,
    fallback_steps: list[RouteStep],
) -> NavigationRouteResponse:
    route_steps = response.route_steps or fallback_steps
    return NavigationRouteResponse(
        language=response.language,
        confidence=response.confidence,
        data_freshness=response.data_freshness,
        assumptions=response.assumptions,
        safety_notes=response.safety_notes,
        grounding_summary=response.grounding_summary,
        recommendation=response.recommendation,
        route_steps=route_steps,
        estimated_total_minutes=_total_minutes(route_steps),
    )


def _total_minutes(steps: list[RouteStep]) -> int | None:
    return sum(step.duration_minutes or 0 for step in steps) or None
