from typing import Literal

from pydantic import BaseModel, Field, field_validator


class BaseArenaRequest(BaseModel):
    venue_id: str = Field(min_length=1, max_length=120)
    event_id: str | None = Field(default=None, max_length=120)
    language: str = Field(default="en", min_length=2, max_length=10)

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        return value.strip().lower()


class AssistantChatRequest(BaseArenaRequest):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=120)
    user_type: Literal["fan", "volunteer", "staff", "organizer"] = "fan"
    location_hint: str | None = Field(default=None, max_length=250)
    accessibility_needs: list[str] = Field(default_factory=list, max_length=12)


class NavigationRouteRequest(BaseArenaRequest):
    origin: str = Field(min_length=1, max_length=250)
    destination: str = Field(min_length=1, max_length=250)
    mobility_needs: list[str] = Field(default_factory=list, max_length=12)
    avoid_crowds: bool = True


class AccessibilityPlanRequest(BaseArenaRequest):
    origin: str | None = Field(default=None, max_length=250)
    destination: str | None = Field(default=None, max_length=250)
    needs: list[str] = Field(default_factory=list, min_length=1, max_length=16)
    companion_count: int = Field(default=0, ge=0, le=10)


class TransportationOptionsRequest(BaseArenaRequest):
    origin_address: str = Field(min_length=1, max_length=500)
    arrival_target: str | None = Field(default=None, max_length=80)
    departure_context: Literal["pre_match", "post_match", "general"] = "general"
    needs_accessible_transport: bool = False


class SustainabilityAdviceRequest(BaseArenaRequest):
    location: str | None = Field(default=None, max_length=250)
    intent: Literal["route", "waste", "water", "food", "energy", "general"] = "general"
    preferences: list[str] = Field(default_factory=list, max_length=12)


class CrowdRecommendationRequest(BaseArenaRequest):
    zone_id: str | None = Field(default=None, max_length=120)
    signal_summary: str = Field(min_length=1, max_length=3000)
    severity: Literal["low", "medium", "high", "critical"] = "medium"


class OpsDecisionSupportRequest(BaseArenaRequest):
    situation: str = Field(min_length=1, max_length=5000)
    decision_window_minutes: int = Field(default=15, ge=1, le=240)
    include_sustainability: bool = True
    include_transportation: bool = True


class OpsSnapshotRequest(BaseArenaRequest):
    source: str = Field(default="manual", max_length=80)
