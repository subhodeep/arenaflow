from typing import Any


def grounding_summary(context: dict[str, Any]) -> list[str]:
    sources = context.get("sources", []) if isinstance(context, dict) else []
    summary: list[str] = []
    for source in sources:
        if isinstance(source, dict):
            status = (
                "available"
                if source.get("available")
                else f"unavailable: {source.get('reason', 'unknown')}"
            )
            summary.append(f"{source.get('name', 'source')}: {status}")
    return summary
