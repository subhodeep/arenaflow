from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service, get_grounding_service
from app.core.security import enforce_request_size, rate_limit
from app.models.requests import TransportationOptionsRequest
from app.models.responses import TransportationOptionsResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = APIRouter(
    prefix="/api/v1/transportation",
    tags=["transportation"],
    dependencies=[Depends(enforce_request_size), Depends(rate_limit)],
)


@router.post("/options", response_model=TransportationOptionsResponse)
async def options(
    request: TransportationOptionsRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
) -> TransportationOptionsResponse:
    context = await grounding.build_context(request, include_maps=True)
    return await gemini.generate_transportation_plan(request, context)
