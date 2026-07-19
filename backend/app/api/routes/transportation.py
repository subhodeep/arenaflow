from fastapi import Depends

from app.api.deps import get_gemini_service, get_grounding_service
from app.api.router_factory import public_router
from app.models.requests import TransportationOptionsRequest
from app.models.responses import TransportationOptionsResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = public_router("/api/v1/transportation", "transportation")


@router.post("/options", response_model=TransportationOptionsResponse)
async def options(
    request: TransportationOptionsRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
) -> TransportationOptionsResponse:
    context = await grounding.build_context(request, include_maps=True)
    return await gemini.generate_transportation_plan(request, context)
