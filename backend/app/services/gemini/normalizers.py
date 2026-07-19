from typing import Any, TypeVar

from pydantic import BaseModel

from app.services.gemini.scalars import (
    item_to_text,
    normalize_confidence,
    normalize_priority,
    optional_int,
    string_list,
)
from app.services.gemini.structured_normalizers import (
    normalize_action_cards,
    normalize_route_steps,
    normalize_transport_options,
)

ResponseT = TypeVar("ResponseT", bound=BaseModel)

LIST_FIELDS = (
    "assumptions",
    "safety_notes",
    "grounding_summary",
    "suggested_actions",
    "actions",
    "assistance_points",
    "alternatives",
)
PRIMARY_TEXT_KEYS = ("answer", "recommendation", "response", "message", "summary", "content")


class GeminiPayloadNormalizer:
    def normalize_payload(
        self,
        payload: Any,
        response_model: type[ResponseT],
        fallback: ResponseT,
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"answer": str(payload)}

        normalized = fallback.model_dump(mode="json")
        normalized.update(payload)
        primary_text = self.primary_text(payload)

        if response_model.__name__ == "AssistantChatResponse":
            normalized["answer"] = primary_text or fallback.answer
        elif "recommendation" in response_model.model_fields:
            normalized["recommendation"] = (
                primary_text
                or normalized.get("recommendation")
                or "ArenaFlow generated a recommendation."
            )

        normalized["language"] = str(payload.get("language") or normalized.get("language") or "en")
        normalized["confidence"] = normalize_confidence(
            payload.get("confidence"),
            normalized.get("confidence", "medium"),
        )
        normalized["priority"] = normalize_priority(
            payload.get("priority"),
            normalized.get("priority", "medium"),
        )
        normalize_text_lists(payload, normalized)
        normalize_structured_lists(payload, normalized)
        return normalized

    def primary_text(self, payload: dict[str, Any]) -> str | None:
        for key in PRIMARY_TEXT_KEYS:
            value = payload.get(key)
            if value is not None:
                return item_to_text(value)
        return None


def normalize_text_lists(payload: dict[str, Any], normalized: dict[str, Any]) -> None:
    for field_name in LIST_FIELDS:
        normalized[field_name] = string_list(payload.get(field_name)) or normalized.get(
            field_name, []
        )
    if "estimated_impact" in normalized and normalized.get("estimated_impact") is not None:
        normalized["estimated_impact"] = str(normalized["estimated_impact"])
    if "estimated_total_minutes" in normalized:
        normalized["estimated_total_minutes"] = optional_int(
            normalized.get("estimated_total_minutes")
        )


def normalize_structured_lists(payload: dict[str, Any], normalized: dict[str, Any]) -> None:
    if "route_steps" in normalized:
        normalized["route_steps"] = normalize_route_steps(
            payload.get("route_steps") or payload.get("steps") or normalized.get("route_steps")
        )
    if "options" in normalized:
        normalized["options"] = normalize_transport_options(
            payload.get("options") or payload.get("transport_options") or normalized.get("options")
        )
    if "action_cards" in normalized:
        normalized["action_cards"] = normalize_action_cards(
            payload.get("action_cards") or payload.get("actions") or normalized.get("action_cards")
        )
