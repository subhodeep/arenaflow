import os

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import require_staff
from app.main import app
from app.models.requests import AssistantChatRequest
from app.models.responses import AssistantChatResponse
from app.services.gemini_service import GeminiService


def test_health_endpoint():
    client = TestClient(app)
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_settings_reject_wildcard_in_prod():
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT='prod',
            PROJECT_ID='test-project',
            GCP_REGION='us-central1',
            ALLOWED_ORIGINS='*',
            STAFF_AUTH_ISSUER='https://issuer.example',
            STAFF_AUTH_AUDIENCE='arenaflow',
            STAFF_AUTH_JWKS_URL='https://issuer.example/.well-known/jwks.json',
        )


def test_request_validation():
    with pytest.raises(ValidationError):
        AssistantChatRequest(venue_id='', message='hello')


@pytest.mark.asyncio
async def test_staff_local_bypass():
    settings = Settings(ENVIRONMENT='local', ALLOW_LOCAL_STAFF_BYPASS=True)
    claims = await require_staff(None, settings)
    assert claims['sub'] == 'local-staff'


@pytest.mark.asyncio
async def test_gemini_fallback_without_project_id():
    service = GeminiService(Settings(ENVIRONMENT='local', PROJECT_ID=''))
    request = AssistantChatRequest(venue_id='venue', message='hello')
    response = await service.chat_assistant(request, {'sources': []})
    assert isinstance(response, AssistantChatResponse)
    assert response.confidence == 'low'
