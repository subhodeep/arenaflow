from fastapi import Depends

from app.api.deps import get_gemini_service, get_grounding_service, get_pubsub_repo
from app.api.router_factory import public_router
from app.models.requests import SustainabilityAdviceRequest
from app.models.responses import SustainabilityAdviceResponse
from app.repositories.pubsub_repo import PubSubRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.sustainability_service import SustainabilityService

router = public_router("/api/v1/sustainability", "sustainability")


@router.post("/advice", response_model=SustainabilityAdviceResponse)
async def advice(
    request: SustainabilityAdviceRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    pubsub: PubSubRepository = Depends(get_pubsub_repo),
) -> SustainabilityAdviceResponse:
    service = SustainabilityService(grounding, gemini, pubsub)
    return await service.advise(request)
