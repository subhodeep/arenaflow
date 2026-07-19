from typing import Any

CONFIDENCE_VALUES = {"low", "medium", "high"}
PRIORITY_VALUES = {"low", "medium", "high", "critical"}
PRIORITY_ALIASES = {"urgent": "critical", "severe": "critical", "normal": "medium"}
CARBON_VALUES = {"low", "medium", "high", "unknown"}
TEXT_KEYS = (
    "title",
    "summary",
    "instruction",
    "recommendation",
    "action",
    "step",
    "description",
    "name",
)


def normalize_confidence(value: Any, default: Any = "medium") -> str:
    if value in CONFIDENCE_VALUES:
        return str(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in CONFIDENCE_VALUES:
            return lowered
        try:
            value = float(lowered)
        except ValueError:
            return default if default in CONFIDENCE_VALUES else "medium"
    if isinstance(value, int | float):
        if value >= 0.8:
            return "high"
        if value >= 0.45:
            return "medium"
        return "low"
    return default if default in CONFIDENCE_VALUES else "medium"


def normalize_priority(value: Any, default: Any = "medium") -> str:
    if value in PRIORITY_VALUES:
        return str(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in PRIORITY_ALIASES:
            return PRIORITY_ALIASES[lowered]
        if lowered in PRIORITY_VALUES:
            return lowered
    if isinstance(value, int | float):
        if value >= 0.9:
            return "critical"
        if value >= 0.7:
            return "high"
        if value >= 0.4:
            return "medium"
        return "low"
    return default if default in PRIORITY_VALUES else "medium"


def normalize_carbon_impact(value: str) -> str:
    carbon = value.lower()
    return carbon if carbon in CARBON_VALUES else "unknown"


def optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item_to_text(item) for item in value if item is not None]
    if isinstance(value, str):
        return [value]
    return [str(value)]


def item_to_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in TEXT_KEYS:
            if item.get(key):
                return str(item[key])
    return str(item)


def first_value(
    payload: dict[str, Any],
    keys: tuple[str, ...],
    default: Any = None,
) -> Any:
    return next((payload[key] for key in keys if payload.get(key) is not None), default)
