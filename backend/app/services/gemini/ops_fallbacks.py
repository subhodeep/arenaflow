from typing import Any

from app.models.domain import ActionCard
from app.models.requests import CrowdRecommendationRequest, OpsDecisionSupportRequest
from app.models.responses import CrowdRecommendationResponse, OpsDecisionSupportResponse
from app.services.gemini.grounding import grounding_summary


def crowd_fallback(
    request: CrowdRecommendationRequest,
    context: dict[str, Any],
) -> CrowdRecommendationResponse:
    return CrowdRecommendationResponse(
        language=request.language,
        recommendation=(
            "Monitor the affected zone, dispatch a staff observer, and prepare nearby "
            "overflow routes if density continues rising."
        ),
        confidence="low",
        priority=request.severity,
        assumptions=[
            "Live AI recommendation unavailable; using conservative crowd-management fallback."
        ],
        safety_notes=[
            "Escalate immediately if crowd movement becomes unsafe or emergency access is blocked."
        ],
        grounding_summary=grounding_summary(context),
        action_cards=[
            ActionCard(
                title="Verify crowd pressure",
                priority=request.severity,
                steps=[
                    "Send staff observer",
                    "Confirm exits remain clear",
                    "Report status to venue command",
                ],
            )
        ],
    )


def ops_fallback(
    request: OpsDecisionSupportRequest,
    context: dict[str, Any],
) -> OpsDecisionSupportResponse:
    return OpsDecisionSupportResponse(
        language=request.language,
        recommendation=(
            "Stabilize the situation by confirming facts, assigning an owner, protecting "
            "accessible and emergency routes, and escalating to venue command "
            "if severity increases."
        ),
        confidence="low",
        assumptions=[
            "Live AI decision support unavailable; using conservative operational fallback."
        ],
        safety_notes=[
            "Escalate life-safety issues immediately and follow official command procedures."
        ],
        grounding_summary=grounding_summary(context),
        action_cards=[
            ActionCard(
                title="Confirm and triage",
                priority="high",
                escalation_required=True,
                steps=[
                    "Validate latest field report",
                    "Assign incident owner",
                    "Share update with command center",
                ],
            )
        ],
        escalation_guidance=(
            "Escalate to venue command for safety, security, medical, or blocked-egress concerns."
        ),
        alternatives=[
            "Hold current flow and monitor",
            "Open overflow route after staff confirmation",
            "Send multilingual volunteer support",
        ],
    )
