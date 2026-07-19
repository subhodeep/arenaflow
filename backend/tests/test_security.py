import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.core.security import enforce_request_size, parse_roles, rate_limit, require_staff


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
