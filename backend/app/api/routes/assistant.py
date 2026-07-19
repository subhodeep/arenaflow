from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.api.deps import get_firestore_repo, get_gemini_service, get_grounding_service
from app.core.security import enforce_request_size, rate_limit
from app.models.requests import AssistantChatRequest
from app.models.responses import AssistantChatResponse
from app.repositories.firestore_repo import FirestoreRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"], dependencies=[Depends(enforce_request_size), Depends(rate_limit)])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(
    request: AssistantChatRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    firestore: FirestoreRepository = Depends(get_firestore_repo),
) -> AssistantChatResponse:
    context = await grounding.build_context(request, include_maps=True)
    response = await gemini.chat_assistant(request, context)
    try:
        await firestore.write_assistant_audit({
            "session_id": request.session_id,
            "venue_id": request.venue_id,
            "event_id": request.event_id,
            "user_type": request.user_type,
            "language": request.language,
            "created_at": datetime.now(timezone.utc),
            "confidence": response.confidence,
        })
    except Exception:
        # Assistant availability should not depend on analytics/audit persistence.
        pass
    return response
