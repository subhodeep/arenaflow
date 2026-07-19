import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import enforce_request_size, parse_roles, rate_limit, require_staff
from app.main import app
from app.models.requests import AssistantChatRequest, NavigationRouteRequest
from app.models.responses import AssistantChatResponse, OpsDecisionSupportResponse
from app.services.gemini_service import GeminiService
from app.services.grounding_service import GroundingService
from app.services.venue_graph_service import VenueGraphService


class FailingFirestoreRepository:
    async def get_venue(self, venue_id: str):
        raise RuntimeError("venue unavailable")

    async def get_event(self, event_id: str | None):
        return None

    async def get_crowd_zones(self, venue_id: str):
        return [{"zone_id": "gate-a", "density_score": 0.2}]

    async def get_active_incidents(self, venue_id: str):
        return []


class CrowdTrendsRepository:
    async def query_recent_crowd_trends(self, venue_id: str, event_id: str | None):
        return [{"zone_id": "gate-a", "avg_density": 0.2}]


class MapsRepository:
    async def context_for_request(self, request):
        return {"available": True, "mode": "test-map"}


class EmptyVenueGraphRepository:
    async def get_venue_graph(self, venue_id: str):
        return None


def test_health_endpoint_includes_security_headers():
    client = TestClient(app)
    response = client.get("/healthz", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "test-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_validation_errors_use_consistent_error_shape():
    client = TestClient(app)
    response = client.post("/api/v1/assistant/chat", json={"venue_id": "", "message": "hello"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["request_id"]


def test_settings_reject_wildcard_in_prod():
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="prod",
            PROJECT_ID="test-project",
            GCP_REGION="us-central1",
            ALLOWED_ORIGINS="*",
            STAFF_AUTH_ISSUER="https://issuer.example",
            STAFF_AUTH_AUDIENCE="arenaflow",
            STAFF_AUTH_JWKS_URL="https://issuer.example/.well-known/jwks.json",
        )


def test_settings_normalize_allowed_origins():
    settings = Settings(ALLOWED_ORIGINS=" https://a.example,https://b.example ")

    assert settings.allowed_origins == "https://a.example,https://b.example"
    assert settings.allowed_origins_list == ["https://a.example", "https://b.example"]


def test_request_validation_and_normalization():
    with pytest.raises(ValidationError):
        AssistantChatRequest(venue_id="", message="hello")

    request = AssistantChatRequest(venue_id="venue", message="hello", language=" ES ")
    assert request.language == "es"


def test_parse_roles_accepts_multiple_claim_shapes():
    roles = parse_roles(
        {
            "roles": ["arenaflow_staff", "guest"],
            "arenaflow_admin": True,
        }
    )

    assert roles == {"arenaflow_staff", "guest", "arenaflow_admin"}


@pytest.mark.asyncio
async def test_staff_local_bypass():
    settings = Settings(ENVIRONMENT="local", ALLOW_LOCAL_STAFF_BYPASS=True)
    claims = await require_staff(None, settings)

    assert claims["sub"] == "local-staff"


@pytest.mark.asyncio
async def test_staff_requires_bearer_token_without_local_bypass():
    settings = Settings(ENVIRONMENT="local", ALLOW_LOCAL_STAFF_BYPASS=False)

    with pytest.raises(HTTPException) as exc_info:
        await require_staff(None, settings)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_enforce_request_size_rejects_large_or_malformed_content_length():
    settings = Settings(MAX_REQUEST_BYTES=4)

    with pytest.raises(HTTPException) as too_large:
        await enforce_request_size(object(), settings, "5")
    assert too_large.value.status_code == 413

    with pytest.raises(HTTPException) as malformed:
        await enforce_request_size(object(), settings, "not-an-int")
    assert malformed.value.status_code == 400


@pytest.mark.asyncio
async def test_rate_limit_enforces_per_path_window():
    settings = Settings(RATE_LIMIT_REQUESTS_PER_MINUTE=1)
    request = type(
        "Request",
        (),
        {
            "client": type("Client", (), {"host": "rate-test"})(),
            "url": type("Url", (), {"path": "/test-rate-limit"})(),
        },
    )()

    await rate_limit(request, settings)
    with pytest.raises(HTTPException) as exc_info:
        await rate_limit(request, settings)

    assert exc_info.value.status_code == 429


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


@pytest.mark.asyncio
async def test_grounding_service_records_source_failures_and_continues():
    service = GroundingService(
        FailingFirestoreRepository(),
        CrowdTrendsRepository(),
        MapsRepository(),
    )
    request = AssistantChatRequest(venue_id="venue", event_id="event", message="hello")

    context = await service.build_context(request, include_maps=True)
    sources = {source["name"]: source for source in context["sources"]}

    assert sources["venue"]["available"] is False
    assert sources["venue"]["reason"] == "RuntimeError"
    assert sources["crowd_zones"]["available"] is True
    assert sources["maps"]["available"] is True


@pytest.mark.asyncio
async def test_venue_graph_service_returns_safe_fallback_without_graph():
    service = VenueGraphService(EmptyVenueGraphRepository())
    steps = await service.route("venue", "Gate A", "Section 120", ["step-free"])

    assert steps[0].instruction == "Follow venue signage from Gate A to Section 120."
    assert steps[0].accessibility_notes == ["step-free"]


def test_navigation_request_requires_origin_and_destination():
    with pytest.raises(ValidationError):
        NavigationRouteRequest(venue_id="venue", origin="", destination="Section 120")
