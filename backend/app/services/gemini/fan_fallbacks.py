from typing import Any

from app.models.domain import RouteStep, TransportOption
from app.models.requests import (
    AccessibilityPlanRequest,
    AssistantChatRequest,
    SustainabilityAdviceRequest,
    TransportationOptionsRequest,
)
from app.models.responses import (
    AccessibilityPlanResponse,
    AssistantChatResponse,
    SustainabilityAdviceResponse,
    TransportationOptionsResponse,
)
from app.services.gemini.grounding import grounding_summary


def assistant_fallback(
    request: AssistantChatRequest, context: dict[str, Any]
) -> AssistantChatResponse:
    return AssistantChatResponse(
        language=request.language,
        answer=(
            "I can help with stadium navigation, accessibility, transportation, "
            "sustainability, and match-day operations. Live AI is temporarily unavailable, "
            "so please confirm urgent safety matters with venue staff."
        ),
        confidence="low",
        assumptions=["Gemini response unavailable or not configured."],
        safety_notes=[
            "For emergencies, contact venue staff or local emergency services immediately."
        ],
        grounding_summary=grounding_summary(context),
        suggested_actions=["Check nearby signage", "Ask the nearest volunteer for urgent support"],
    )


def accessibility_fallback(
    request: AccessibilityPlanRequest,
    context: dict[str, Any],
) -> AccessibilityPlanResponse:
    return AccessibilityPlanResponse(
        language=request.language,
        recommendation=(
            "Use signed accessible routes, confirm elevator availability with venue staff, "
            "and allow extra time for assistance points."
        ),
        confidence="low",
        assumptions=["Live AI plan unavailable; using accessibility-safe fallback."],
        safety_notes=["Ask venue accessibility staff for urgent or medical assistance."],
        grounding_summary=grounding_summary(context),
        assistance_points=["Nearest information desk", "Accessibility services desk"],
        route_steps=[
            RouteStep(
                instruction=(
                    "Follow accessible signage and avoid stairs unless staff confirms an "
                    "alternative is unavailable."
                )
            )
        ],
    )


def transportation_fallback(
    request: TransportationOptionsRequest,
    context: dict[str, Any],
) -> TransportationOptionsResponse:
    return TransportationOptionsResponse(
        language=request.language,
        recommendation=(
            "Prefer public transit or official shuttles when available, and use designated "
            "accessible pickup zones if accessible transport is needed."
        ),
        confidence="low",
        assumptions=["Live AI transport plan unavailable; using general transportation fallback."],
        safety_notes=[
            "Follow police, transit agency, and venue instructions during post-match egress."
        ],
        grounding_summary=grounding_summary(context),
        options=[
            TransportOption(
                mode="public_transit",
                summary="Use official transit routes and allow extra time around match start/end.",
                carbon_impact="low",
            )
        ],
    )


def sustainability_fallback(
    request: SustainabilityAdviceRequest,
    context: dict[str, Any],
) -> SustainabilityAdviceResponse:
    return SustainabilityAdviceResponse(
        language=request.language,
        recommendation=(
            "Use refill stations, sort waste by venue signage, and choose walking, shuttle, "
            "or transit routes where practical."
        ),
        confidence="low",
        assumptions=[
            "Live AI sustainability advice unavailable; using general sustainability fallback."
        ],
        safety_notes=[
            "Do not enter restricted operational areas to reach sustainability amenities."
        ],
        grounding_summary=grounding_summary(context),
        actions=[
            "Carry a reusable bottle",
            "Follow waste sorting signs",
            "Choose low-carbon transport when safe",
        ],
    )
