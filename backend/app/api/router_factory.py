from fastapi import APIRouter, Depends

from app.core.security import enforce_request_size, rate_limit


def public_router(prefix: str, tag: str) -> APIRouter:
    return APIRouter(
        prefix=prefix,
        tags=[tag],
        dependencies=[Depends(enforce_request_size), Depends(rate_limit)],
    )
