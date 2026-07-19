from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service, get_grounding_service
from app.core.security import enforce_request_size, rate_limit, require_staff
from app.models.requests import CrowdRecommendationRequest
from app.models.responses import CrowdRecommendationResponse
from app.services.crowd_service import CrowdService
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = APIRouter(prefix="/api/v1/crowd", tags=["crowd"], dependencies=[Depends(enforce_request_size), Depends(rate_limit), Depends(require_staff)])


@router.post("/recommendation", response_model=CrowdRecommendationResponse)
async def recommendation(
    request: CrowdRecommendationRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
) -> CrowdRecommendationResponse:
    service = CrowdService(grounding, gemini)
    return await service.recommend(request)
