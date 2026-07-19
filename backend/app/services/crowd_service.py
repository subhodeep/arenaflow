from app.models.requests import CrowdRecommendationRequest
from app.models.responses import CrowdRecommendationResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService


class CrowdService:
    def __init__(self, grounding_service: GroundingService, gemini_service: GeminiService):
        self.grounding_service = grounding_service
        self.gemini_service = gemini_service

    async def recommend(self, request: CrowdRecommendationRequest) -> CrowdRecommendationResponse:
        context = await self.grounding_service.build_context(request)
        return await self.gemini_service.generate_crowd_recommendation(request, context)
