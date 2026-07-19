from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.models.responses import RuntimeConfigResponse

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("", response_model=RuntimeConfigResponse)
async def runtime_config(settings: Settings = Depends(get_settings)) -> RuntimeConfigResponse:
    return RuntimeConfigResponse(
        environment=settings.environment,
        region=settings.gcp_region,
        gemini_model=settings.gemini_model,
        features={
            "assistant": True,
            "navigation": True,
            "accessibility": True,
            "transportation": True,
            "sustainability": True,
            "operations": True,
        },
    )
