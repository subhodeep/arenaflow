from contextlib import suppress
from uuid import uuid4

from app.models.requests import OpsDecisionSupportRequest, OpsSnapshotRequest
from app.models.responses import OpsDecisionSupportResponse, OpsSnapshotResponse
from app.repositories.firestore_repo import FirestoreRepository
from app.repositories.pubsub_repo import PubSubRepository
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService


class OpsIntelService:
    def __init__(
        self,
        grounding_service: GroundingService,
        gemini_service: GeminiService,
        firestore_repo: FirestoreRepository,
        pubsub_repo: PubSubRepository,
    ):
        self.grounding_service = grounding_service
        self.gemini_service = gemini_service
        self.firestore_repo = firestore_repo
        self.pubsub_repo = pubsub_repo

    async def decision_support(
        self,
        request: OpsDecisionSupportRequest,
    ) -> OpsDecisionSupportResponse:
        context = await self.grounding_service.build_context(
            request,
            include_maps=request.include_transportation,
        )
        response = await self.gemini_service.generate_ops_decision_support(request, context)
        with suppress(Exception):
            await self.pubsub_repo.publish_operations_event(
                {
                    "type": "ops_decision_support",
                    "venue_id": request.venue_id,
                    "event_id": request.event_id,
                    "priority": "generated",
                }
            )
        return response

    async def snapshot(self, request: OpsSnapshotRequest) -> OpsSnapshotResponse:
        snapshot_id = str(uuid4())
        decision_request = OpsDecisionSupportRequest(
            venue_id=request.venue_id,
            event_id=request.event_id,
            language=request.language,
            situation=f"Generate operational snapshot from source {request.source}.",
        )
        context = await self.grounding_service.build_context(request, include_maps=True)
        response = await self.gemini_service.generate_ops_decision_support(
            decision_request, context
        )
        with suppress(Exception):
            await self.firestore_repo.write_ops_snapshot(
                {
                    "id": snapshot_id,
                    "venue_id": request.venue_id,
                    "event_id": request.event_id,
                    "source": request.source,
                    "recommendation": response.recommendation,
                    "response": response.model_dump(mode="json"),
                }
            )
        return OpsSnapshotResponse(
            status="completed",
            snapshot_id=snapshot_id,
            recommendation=response.recommendation,
        )
