from contextlib import suppress

from app.models.requests import SustainabilityAdviceRequest
from app.models.responses import SustainabilityAdviceResponse
from app.repositories.pubsub_repo import PubSubRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService


class SustainabilityService:
    def __init__(
        self,
        grounding_service: GroundingService,
        gemini_service: GeminiService,
        pubsub_repo: PubSubRepository,
    ):
        self.grounding_service = grounding_service
        self.gemini_service = gemini_service
        self.pubsub_repo = pubsub_repo

    async def advise(self, request: SustainabilityAdviceRequest) -> SustainabilityAdviceResponse:
        context = await self.grounding_service.build_context(request, include_maps=True)
        response = await self.gemini_service.generate_sustainability_advice(request, context)
        with suppress(Exception):
            await self.pubsub_repo.publish_sustainability_event(
                {
                    "type": "sustainability_advice",
                    "venue_id": request.venue_id,
                    "event_id": request.event_id,
                    "intent": request.intent,
                }
            )
        return response
