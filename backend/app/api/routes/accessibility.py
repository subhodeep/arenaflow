from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service, get_grounding_service
from app.core.security import enforce_request_size, rate_limit
from app.models.requests import AccessibilityPlanRequest
from app.models.responses import AccessibilityPlanResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = APIRouter(
    prefix="/api/v1/accessibility",
    tags=["accessibility"],
    dependencies=[Depends(enforce_request_size), Depends(rate_limit)],
)


@router.post("/plan", response_model=AccessibilityPlanResponse)
async def plan(
    request: AccessibilityPlanRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
) -> AccessibilityPlanResponse:
    context = await grounding.build_context(request, include_maps=True)
    return await gemini.generate_accessibility_plan(request, context)
