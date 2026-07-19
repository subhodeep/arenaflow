from fastapi import APIRouter, Depends

from app.api.deps import (
    get_firestore_repo,
    get_gemini_service,
    get_grounding_service,
    get_pubsub_repo,
)
from app.core.security import (
    enforce_request_size,
    rate_limit,
    require_scheduler_or_staff,
    require_staff,
)
from app.models.requests import OpsDecisionSupportRequest, OpsSnapshotRequest
from app.models.responses import OpsDecisionSupportResponse, OpsSnapshotResponse
from app.repositories.firestore_repo import FirestoreRepository
from app.repositories.pubsub_repo import PubSubRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.ops_intel_service import OpsIntelService

router = APIRouter(
    prefix="/api/v1/ops",
    tags=["operations"],
    dependencies=[Depends(enforce_request_size), Depends(rate_limit)],
)


@router.post(
    "/decision-support",
    response_model=OpsDecisionSupportResponse,
    dependencies=[Depends(require_staff)],
)
async def decision_support(
    request: OpsDecisionSupportRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    firestore: FirestoreRepository = Depends(get_firestore_repo),
    pubsub: PubSubRepository = Depends(get_pubsub_repo),
) -> OpsDecisionSupportResponse:
    service = OpsIntelService(grounding, gemini, firestore, pubsub)
    return await service.decision_support(request)


@router.post(
    "/snapshot",
    response_model=OpsSnapshotResponse,
    dependencies=[Depends(require_scheduler_or_staff)],
)
async def snapshot(
    request: OpsSnapshotRequest,
    grounding: GroundingService = Depends(get_grounding_service),
    gemini: GeminiService = Depends(get_gemini_service),
    firestore: FirestoreRepository = Depends(get_firestore_repo),
    pubsub: PubSubRepository = Depends(get_pubsub_repo),
) -> OpsSnapshotResponse:
    service = OpsIntelService(grounding, gemini, firestore, pubsub)
    return await service.snapshot(request)
