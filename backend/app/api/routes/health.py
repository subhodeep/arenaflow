from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.models.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(app_name=settings.app_name, app_version=settings.app_version, environment=settings.environment)
