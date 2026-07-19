import pytest

from app.core.config import Settings
from app.models.requests import AssistantChatRequest
from app.models.responses import AssistantChatResponse, OpsDecisionSupportResponse
from app.services.gemini_service import GeminiService


@pytest.mark.asyncio
async def test_gemini_fallback_without_project_id():
    service = GeminiService(Settings(ENVIRONMENT="local", PROJECT_ID=""))
    request = AssistantChatRequest(venue_id="venue", message="hello")
    response = await service.chat_assistant(request, {"sources": []})

    assert isinstance(response, AssistantChatResponse)
    assert response.confidence == "low"


def test_gemini_normalizes_loose_payload_into_response_model():
    service = GeminiService(Settings(ENVIRONMENT="local", PROJECT_ID=""))
    fallback = OpsDecisionSupportResponse(
        language="en",
        recommendation="fallback",
        confidence="low",
    )
    normalized = service._normalize_payload(
        {
            "summary": "Use overflow gates",
            "confidence": 0.9,
            "priority": "urgent",
            "actions": [{"title": "Open Gate D", "steps": ["Brief staff"]}],
        },
        OpsDecisionSupportResponse,
        fallback,
    )
    response = OpsDecisionSupportResponse.model_validate(normalized)

    assert response.recommendation == "Use overflow gates"
    assert response.confidence == "high"
    assert response.action_cards[0].priority == "medium"
    assert response.action_cards[0].title == "Open Gate D"
