import time
from collections import defaultdict, deque
from typing import Annotated, Any

import httpx
import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token

from app.core.config import Settings, get_settings

security_scheme = HTTPBearer(auto_error=False)
_ALLOWED_STAFF_ROLES = {"arenaflow_staff", "arenaflow_ops", "arenaflow_admin"}
_RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
_JWKS_CACHE: dict[str, Any] = {"expires_at": 0.0, "keys": None}


def parse_roles(claims: dict[str, Any]) -> set[str]:
    roles: set[str] = set()
    raw_roles = claims.get("roles") or claims.get("role") or claims.get("groups") or []
    if isinstance(raw_roles, str):
        roles.add(raw_roles)
    elif isinstance(raw_roles, list):
        roles.update(str(role) for role in raw_roles)
    for role in _ALLOWED_STAFF_ROLES:
        if claims.get(role) is True:
            roles.add(role)
    return roles


async def fetch_jwks(settings: Settings) -> dict[str, Any]:
    now = time.time()
    if _JWKS_CACHE["keys"] and _JWKS_CACHE["expires_at"] > now:
        return _JWKS_CACHE["keys"]
    if not settings.staff_auth_jwks_url:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Staff JWKS URL is not configured",
        )
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(settings.staff_auth_jwks_url)
        response.raise_for_status()
        jwks = response.json()
    _JWKS_CACHE["keys"] = jwks
    _JWKS_CACHE["expires_at"] = now + 300
    return jwks


async def validate_staff_token(token: str, settings: Settings) -> dict[str, Any]:
    jwks = await fetch_jwks(settings)
    header = jwt.get_unverified_header(token)
    key = next(
        (
            candidate
            for candidate in jwks.get("keys", [])
            if candidate.get("kid") == header.get("kid")
        ),
        None,
    )
    if not key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown staff token key")
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[header.get("alg", "RS256")],
            audience=settings.staff_auth_audience,
            issuer=settings.staff_auth_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid staff token") from exc
    roles = parse_roles(claims)
    if not roles.intersection(_ALLOWED_STAFF_ROLES):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff role is required")
    return claims


async def require_staff(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    if settings.environment == "local" and settings.allow_local_staff_bypass:
        return {"sub": "local-staff", "roles": ["arenaflow_admin"]}
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer token is required")
    return await validate_staff_token(credentials.credentials, settings)


async def require_scheduler_or_staff(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    if settings.environment == "local" and settings.allow_local_staff_bypass:
        return {"sub": "local-scheduler", "roles": ["arenaflow_admin"]}
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer token is required")

    token = credentials.credentials
    try:
        audience = str(request.base_url).rstrip("/")
        claims = id_token.verify_oauth2_token(
            token,
            google_auth_requests.Request(),
            audience=audience,
        )
        expected_email = settings.scheduler_service_account_email
        if expected_email and claims.get("email") == expected_email:
            return claims
    except Exception:
        pass
    return await validate_staff_token(token, settings)


async def enforce_request_size(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    content_length: Annotated[str | None, Header(alias="content-length")] = None,
) -> None:
    if content_length is None:
        return
    try:
        request_bytes = int(content_length)
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Content-Length must be an integer",
        ) from exc
    if request_bytes > settings.max_request_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Request body is too large")


async def rate_limit(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    window_seconds = 60
    now = time.time()
    client = request.client.host if request.client else "unknown"
    key = f"{client}:{request.url.path}"
    bucket = _RATE_BUCKETS[key]
    while bucket and bucket[0] < now - window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_requests_per_minute:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
    bucket.append(now)
