from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DataFreshness(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sources: list[str] = Field(default_factory=list)
    stale_sources: list[str] = Field(default_factory=list)


class GroundingSource(BaseModel):
    name: str
    available: bool
    reason: str | None = None
    data: dict[str, Any] | list[Any] | None = None


class GroundingContext(BaseModel):
    venue_id: str | None = None
    event_id: str | None = None
    language: str = "en"
    sources: list[GroundingSource] = Field(default_factory=list)
    data_freshness: DataFreshness = Field(default_factory=DataFreshness)


class RouteStep(BaseModel):
    instruction: str
    distance_meters: int | None = None
    duration_minutes: int | None = None
    accessibility_notes: list[str] = Field(default_factory=list)
    crowd_notes: list[str] = Field(default_factory=list)


class ActionCard(BaseModel):
    title: str
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    owner: str | None = None
    steps: list[str] = Field(default_factory=list)
    escalation_required: bool = False


class TransportOption(BaseModel):
    mode: str
    summary: str
    estimated_minutes: int | None = None
    carbon_impact: Literal["low", "medium", "high", "unknown"] = "unknown"
    accessibility_notes: list[str] = Field(default_factory=list)


class SustainabilityMetric(BaseModel):
    name: str
    value: str
    trend: Literal["improving", "stable", "worsening", "unknown"] = "unknown"
