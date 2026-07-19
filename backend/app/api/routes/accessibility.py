from fastapi import Depends

from app.api.deps import get_gemini_service, get_grounding_service
from app.api.router_factory import public_router
from app.models.requests import AccessibilityPlanRequest
from app.models.responses import AccessibilityPlanResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = public_router("/api/v1/accessibility", "accessibility")


@router.post("/plan", response_model=AccessibilityPlanResponse)
async def plan(
    request: AccessibilityPlanRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
) -> AccessibilityPlanResponse:
    context = await grounding.build_context(request, include_maps=True)
    return await gemini.generate_accessibility_plan(request, context)
