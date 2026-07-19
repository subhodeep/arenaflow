from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.domain import ActionCard, DataFreshness, RouteStep, TransportOption


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class BaseGeminiResponse(BaseModel):
    language: str = "en"
    confidence: Literal["low", "medium", "high"] = "medium"
    data_freshness: DataFreshness = Field(default_factory=DataFreshness)
    assumptions: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    grounding_summary: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    app_name: str
    app_version: str
    environment: str


class RuntimeConfigResponse(BaseModel):
    environment: str
    region: str
    gemini_model: str
    features: dict[str, bool]


class AssistantChatResponse(BaseGeminiResponse):
    answer: str
    suggested_actions: list[str] = Field(default_factory=list)


class NavigationRouteResponse(BaseGeminiResponse):
    recommendation: str
    route_steps: list[RouteStep] = Field(default_factory=list)
    estimated_total_minutes: int | None = None


class AccessibilityPlanResponse(BaseGeminiResponse):
    recommendation: str
    assistance_points: list[str] = Field(default_factory=list)
    route_steps: list[RouteStep] = Field(default_factory=list)


class TransportationOptionsResponse(BaseGeminiResponse):
    recommendation: str
    options: list[TransportOption] = Field(default_factory=list)


class SustainabilityAdviceResponse(BaseGeminiResponse):
    recommendation: str
    actions: list[str] = Field(default_factory=list)
    estimated_impact: str | None = None


class CrowdRecommendationResponse(BaseGeminiResponse):
    recommendation: str
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    action_cards: list[ActionCard] = Field(default_factory=list)


class OpsDecisionSupportResponse(BaseGeminiResponse):
    recommendation: str
    action_cards: list[ActionCard] = Field(default_factory=list)
    escalation_guidance: str | None = None
    alternatives: list[str] = Field(default_factory=list)


class OpsSnapshotResponse(BaseModel):
    status: Literal["accepted", "completed"]
    snapshot_id: str
    recommendation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
