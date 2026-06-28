from __future__ import annotations

from typing import Any

from .schema import AgentPreparedFinancialAction, ReviewOutput


def build_governance_record(
    action: AgentPreparedFinancialAction,
    review: ReviewOutput,
) -> dict[str, Any]:
    return {
        "record_type": (
            "agent_prepared_financial_action_review_harness_governance_record"
        ),
        "harness_version": "v0.1",
        "formal_harness_name": "Agent-Prepared Financial Action Review Harness",
        "action_id": action.action_id,
        "agent_id": action.agent_id,
        "review_status": review.review_status,
        "reason_codes": review.reason_codes,
        "what_nova_surfaced": review.nova_surface_summary,
        "what_nova_did_not_do": [
            "approve",
            "deny",
            "block",
            "execute",
            "route",
            "settle",
            "move_capital",
            "select_source",
            "resolve_conflict",
            "make_final_decision",
        ],
        "local_authority_decides": True,
        "boundary_log": review.boundary_log,
        "reflex_memory_candidate": review.reflex_memory_candidate,
        "classification": {
            "market_validation": False,
            "production_readiness": False,
            "buyer_validation": False,
            "execution_system": False,
            "treasury_agent": False,
            "payment_router": False,
        },
    }

