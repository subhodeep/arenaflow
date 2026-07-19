import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.models.requests import AssistantChatRequest


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
