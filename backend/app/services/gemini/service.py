from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.config import Settings
from app.models.requests import (
    AccessibilityPlanRequest,
    AssistantChatRequest,
    CrowdRecommendationRequest,
    OpsDecisionSupportRequest,
    SustainabilityAdviceRequest,
    TransportationOptionsRequest,
)
from app.models.responses import (
    AccessibilityPlanResponse,
    AssistantChatResponse,
    CrowdRecommendationResponse,
    OpsDecisionSupportResponse,
    SustainabilityAdviceResponse,
    TransportationOptionsResponse,
)
from app.services.context import context_as_dict
from app.services.gemini.fallbacks import (
    accessibility_fallback,
    assistant_fallback,
    crowd_fallback,
    ops_fallback,
    sustainability_fallback,
    transportation_fallback,
)
from app.services.gemini.generator import GeminiJsonGenerator
from app.services.gemini.prompts import base_prompt

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class GeminiService:
    def __init__(self, settings: Settings):
        self.generator = GeminiJsonGenerator(settings)

    @property
    def client(self) -> Any | None:
        return self.generator.client

    async def _generate_json(
        self,
        prompt: str,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> ResponseT:
        return await self.generator.generate(prompt, response_model, fallback)

    def _normalize_payload(
        self,
        payload: Any,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> dict[str, Any]:
        return self.generator.normalize_payload(payload, response_model, fallback)

    async def chat_assistant(
        self,
        request: AssistantChatRequest,
        context: Any,
    ) -> AssistantChatResponse:
        return await self._run(
            task="Answer a fan or staff question in the requested language.",
            request=request,
            context=context,
            response_model=AssistantChatResponse,
            fallback_factory=assistant_fallback,
        )

    async def summarize_incident(
        self,
        request: OpsDecisionSupportRequest,
        context: Any,
    ) -> OpsDecisionSupportResponse:
        return await self.generate_ops_decision_support(request, context)

    async def generate_crowd_recommendation(
        self,
        request: CrowdRecommendationRequest,
        context: Any,
    ) -> CrowdRecommendationResponse:
        return await self._run(
            task="Generate crowd management recommendations for staff.",
            request=request,
            context=context,
            response_model=CrowdRecommendationResponse,
            fallback_factory=crowd_fallback,
        )

    async def generate_accessibility_plan(
        self,
        request: AccessibilityPlanRequest,
        context: Any,
    ) -> AccessibilityPlanResponse:
        return await self._run(
            task="Create an accessibility support plan.",
            request=request,
            context=context,
            response_model=AccessibilityPlanResponse,
            fallback_factory=accessibility_fallback,
        )

    async def generate_transportation_plan(
        self,
        request: TransportationOptionsRequest,
        context: Any,
    ) -> TransportationOptionsResponse:
        return await self._run(
            task="Recommend transportation options.",
            request=request,
            context=context,
            response_model=TransportationOptionsResponse,
            fallback_factory=transportation_fallback,
        )

    async def generate_sustainability_advice(
        self,
        request: SustainabilityAdviceRequest,
        context: Any,
    ) -> SustainabilityAdviceResponse:
        return await self._run(
            task="Give sustainability advice.",
            request=request,
            context=context,
            response_model=SustainabilityAdviceResponse,
            fallback_factory=sustainability_fallback,
        )

    async def generate_ops_decision_support(
        self,
        request: OpsDecisionSupportRequest,
        context: Any,
    ) -> OpsDecisionSupportResponse:
        return await self._run(
            task="Generate real-time operational decision support.",
            request=request,
            context=context,
            response_model=OpsDecisionSupportResponse,
            fallback_factory=ops_fallback,
        )

    async def _run(
        self,
        task: str,
        request: BaseModel,
        context: Any,
        response_model: type[ResponseT],
        fallback_factory,
    ) -> ResponseT:
        context_dict = context_as_dict(context)
        fallback = fallback_factory(request, context_dict)
        return await self._generate_json(
            base_prompt(task, request, context_dict),
            response_model,
            fallback,
        )
