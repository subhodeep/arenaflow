from typing import Any

from app.services.gemini.scalars import (
    first_value,
    normalize_carbon_impact,
    normalize_priority,
    optional_int,
    string_list,
)


def normalize_route_steps(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    return [step for item in items if (step := route_step_from_item(item)) is not None]


def route_step_from_item(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {"instruction": item, "accessibility_notes": [], "crowd_notes": []}
    if not isinstance(item, dict):
        return None
    instruction = first_value(
        item,
        ("instruction", "step", "summary", "description", "action"),
        "Proceed to the next waypoint.",
    )
    return {
        "instruction": str(instruction),
        "distance_meters": optional_int(first_value(item, ("distance_meters", "distance"))),
        "duration_minutes": optional_int(
            first_value(item, ("duration_minutes", "minutes", "duration"))
        ),
        "accessibility_notes": string_list(
            first_value(item, ("accessibility_notes", "accessibility"))
        ),
        "crowd_notes": string_list(first_value(item, ("crowd_notes", "crowd"))),
    }


def normalize_transport_options(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    return [option for item in items if (option := transport_option_from_item(item)) is not None]


def transport_option_from_item(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {
            "mode": "recommended",
            "summary": item,
            "carbon_impact": "unknown",
            "accessibility_notes": [],
        }
    if not isinstance(item, dict):
        return None
    return {
        "mode": str(first_value(item, ("mode", "type"), "recommended")),
        "summary": str(
            first_value(
                item,
                ("summary", "description", "recommendation", "mode"),
                "Recommended transport option.",
            )
        ),
        "estimated_minutes": optional_int(
            first_value(item, ("estimated_minutes", "minutes", "duration"))
        ),
        "carbon_impact": normalize_carbon_impact(
            str(first_value(item, ("carbon_impact", "carbon"), "unknown"))
        ),
        "accessibility_notes": string_list(
            first_value(item, ("accessibility_notes", "accessibility"))
        ),
    }


def normalize_action_cards(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    return [card for item in items if (card := action_card_from_item(item)) is not None]


def action_card_from_item(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {"title": item, "priority": "medium", "steps": [], "escalation_required": False}
    if not isinstance(item, dict):
        return None
    return {
        "title": str(first_value(item, ("title", "action", "summary"), "Recommended action")),
        "priority": normalize_priority(item.get("priority"), "medium"),
        "owner": str(item.get("owner")) if item.get("owner") is not None else None,
        "steps": string_list(first_value(item, ("steps", "next_steps"))),
        "escalation_required": bool(item.get("escalation_required", False)),
    }
