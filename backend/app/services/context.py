from typing import Any

from app.models.domain import GroundingContext


def context_as_dict(context: GroundingContext | dict[str, Any]) -> dict[str, Any]:
    if isinstance(context, GroundingContext):
        return context.model_dump(mode="json")
    return context
