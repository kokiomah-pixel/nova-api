from __future__ import annotations

from .rules import (
    NORMAL_CONTEXT_REASON,
    RETRY_PRESSURE_REASON,
    SOURCE_CONFLICT_REASON,
    STALE_LIQUIDITY_REASON,
    has_approved_source_disagreement_near_authority_handoff,
    has_retry_pressure_after_incomplete_confirmation,
    has_stale_liquidity_source_with_rising_authority_proximity,
)
from .schema import AgentPreparedFinancialAction, ReviewOutput


BOUNDARY_LOG: dict[str, bool] = {
    "nova_executes": False,
    "nova_approves": False,
    "nova_denies": False,
    "nova_blocks": False,
    "nova_routes": False,
    "nova_settles": False,
    "nova_moves_capital": False,
    "nova_selects_source": False,
    "nova_resolves_conflict": False,
    "nova_makes_final_decision": False,
    "local_authority_decides": True,
}


SURFACE_SUMMARIES: dict[str, str] = {
    RETRY_PRESSURE_REASON: (
        "Retry pressure is rising while confirmation remains incomplete."
    ),
    STALE_LIQUIDITY_REASON: (
        "Liquidity source context is stale while the prepared action is approaching "
        "local authority review."
    ),
    SOURCE_CONFLICT_REASON: (
        "Approved sources disagree on a decision-relevant condition before local "
        "authority acts."
    ),
    NORMAL_CONTEXT_REASON: (
        "No constrained-review trigger detected from provided input."
    ),
}


FORBIDDEN_REVIEW_STATUSES = {
    "approved",
    "denied",
    "blocked",
    "rejected",
    "allowed",
    "permissioned",
    "executed",
    "routed",
    "settled",
}


def review_agent_prepared_action(
    action: AgentPreparedFinancialAction,
) -> ReviewOutput:
    reason_codes: list[str] = []

    if has_retry_pressure_after_incomplete_confirmation(action):
        reason_codes.append(RETRY_PRESSURE_REASON)

    if has_stale_liquidity_source_with_rising_authority_proximity(action):
        reason_codes.append(STALE_LIQUIDITY_REASON)

    if has_approved_source_disagreement_near_authority_handoff(action):
        reason_codes.append(SOURCE_CONFLICT_REASON)

    if reason_codes:
        review_status = "constrained_review"
    else:
        review_status = "normal_review"
        reason_codes.append(NORMAL_CONTEXT_REASON)

    if review_status in FORBIDDEN_REVIEW_STATUSES:
        raise ValueError(f"Forbidden review status emitted: {review_status}")

    reflex_memory_candidate = {
        "retain": True,
        "requires_review": True,
        "automatic_mutation": False,
        "candidate_triggers": reason_codes,
    }

    return ReviewOutput(
        action_id=action.action_id,
        review_status=review_status,
        reason_codes=reason_codes,
        nova_surface_summary=[SURFACE_SUMMARIES[reason] for reason in reason_codes],
        boundary_log=dict(BOUNDARY_LOG),
        local_authority_required=True,
        governance_record_candidate=True,
        reflex_memory_candidate=reflex_memory_candidate,
    )

