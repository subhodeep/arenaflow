from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables only."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="ArenaFlow", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    project_id: str = Field(default="", validation_alias="PROJECT_ID")
    gcp_region: str = Field(default="us-central1", validation_alias="GCP_REGION")
    environment: Literal["local", "dev", "stage", "prod"] = Field(
        default="local",
        validation_alias="ENVIRONMENT",
    )

    gemini_model: str = Field(default="gemini-2.5-pro", validation_alias="GEMINI_MODEL")
    gemini_location: str = Field(default="global", validation_alias="GEMINI_LOCATION")
    gemini_use_vertex_ai: bool = Field(default=True, validation_alias="GEMINI_USE_VERTEX_AI")

    allowed_origins: str = Field(
        default="http://localhost:5173",
        validation_alias="ALLOWED_ORIGINS",
    )
    firestore_database_id: str = Field(
        default="(default)",
        validation_alias="FIRESTORE_DATABASE_ID",
    )
    bigquery_dataset: str = Field(default="arenaflow_local", validation_alias="BIGQUERY_DATASET")
    pubsub_topic_operations: str = Field(
        default="arenaflow-local-operations",
        validation_alias="PUBSUB_TOPIC_OPERATIONS",
    )
    pubsub_topic_crowd: str = Field(
        default="arenaflow-local-crowd",
        validation_alias="PUBSUB_TOPIC_CROWD",
    )
    pubsub_topic_sustainability: str = Field(
        default="arenaflow-local-sustainability",
        validation_alias="PUBSUB_TOPIC_SUSTAINABILITY",
    )

    rate_limit_requests_per_minute: int = Field(
        default=60,
        validation_alias="RATE_LIMIT_REQUESTS_PER_MINUTE",
    )
    max_request_bytes: int = Field(default=1_048_576, validation_alias="MAX_REQUEST_BYTES")

    staff_auth_issuer: str | None = Field(default=None, validation_alias="STAFF_AUTH_ISSUER")
    staff_auth_audience: str | None = Field(default=None, validation_alias="STAFF_AUTH_AUDIENCE")
    staff_auth_jwks_url: str | None = Field(default=None, validation_alias="STAFF_AUTH_JWKS_URL")
    allow_local_staff_bypass: bool = Field(
        default=False,
        validation_alias="ALLOW_LOCAL_STAFF_BYPASS",
    )
    scheduler_service_account_email: str | None = Field(
        default=None,
        validation_alias="SCHEDULER_SERVICE_ACCOUNT_EMAIL",
    )

    maps_api_server_key_secret_name: str | None = Field(
        default=None,
        validation_alias="MAPS_API_SERVER_KEY_SECRET_NAME",
    )
    maps_server_api_key: str | None = Field(default=None, validation_alias="MAPS_SERVER_API_KEY")

    collection_venues: str = Field(default="venues", validation_alias="COLLECTION_VENUES")
    collection_venue_graphs: str = Field(
        default="venue_graphs",
        validation_alias="COLLECTION_VENUE_GRAPHS",
    )
    collection_events: str = Field(default="events", validation_alias="COLLECTION_EVENTS")
    collection_crowd_zones: str = Field(
        default="crowd_zones",
        validation_alias="COLLECTION_CROWD_ZONES",
    )
    collection_incidents: str = Field(
        default="incidents",
        validation_alias="COLLECTION_INCIDENTS",
    )
    collection_assistant_sessions: str = Field(
        default="assistant_sessions",
        validation_alias="COLLECTION_ASSISTANT_SESSIONS",
    )
    collection_ops_snapshots: str = Field(
        default="ops_snapshots",
        validation_alias="COLLECTION_OPS_SNAPSHOTS",
    )

    @field_validator("allowed_origins")
    @classmethod
    def validate_allowed_origins_format(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("ALLOWED_ORIGINS must contain at least one origin")
        return ",".join(origins)

    @model_validator(mode="after")
    def validate_deployed_settings(self) -> "Settings":
        if self.environment not in {"local", "dev"} and not self.project_id:
            raise ValueError("PROJECT_ID is required outside local/dev environments")
        if self.environment not in {"local", "dev"} and "*" in self.allowed_origins_list:
            raise ValueError("Wildcard CORS origins are forbidden outside local/dev environments")
        if self.environment not in {"local", "dev"} and not self.gemini_use_vertex_ai:
            raise ValueError("GEMINI_USE_VERTEX_AI must remain enabled for ADC-based Gemini access")
        if self.environment not in {"local", "dev"}:
            auth_values = [
                self.staff_auth_issuer,
                self.staff_auth_audience,
                self.staff_auth_jwks_url,
            ]
            if not all(auth_values):
                raise ValueError(
                    "Staff auth issuer, audience, and JWKS URL are required in stage/prod"
                )
        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def collections(self) -> dict[str, str]:
        return {
            "venues": self.collection_venues,
            "venue_graphs": self.collection_venue_graphs,
            "events": self.collection_events,
            "crowd_zones": self.collection_crowd_zones,
            "incidents": self.collection_incidents,
            "assistant_sessions": self.collection_assistant_sessions,
            "ops_snapshots": self.collection_ops_snapshots,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
