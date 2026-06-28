from __future__ import annotations

from .schema import AgentPreparedFinancialAction


RETRY_PRESSURE_REASON = "retry_pressure_after_incomplete_confirmation"
STALE_LIQUIDITY_REASON = "stale_liquidity_source_with_rising_authority_proximity"
SOURCE_CONFLICT_REASON = "approved_source_disagreement_near_authority_handoff"
NORMAL_CONTEXT_REASON = "normal_context"


def authority_is_near(action: AgentPreparedFinancialAction) -> bool:
    return action.authority_proximity in {"medium", "high"}


def has_retry_pressure_after_incomplete_confirmation(
    action: AgentPreparedFinancialAction,
) -> bool:
    return (
        action.confirmation_status == "incomplete"
        and action.retry_count > 0
        and action.same_route_retry
        and authority_is_near(action)
    )


def has_stale_liquidity_source_with_rising_authority_proximity(
    action: AgentPreparedFinancialAction,
) -> bool:
    return (
        action.liquidity_source_age_minutes
        > action.expected_source_freshness_minutes
        and authority_is_near(action)
    )


def has_approved_source_disagreement_near_authority_handoff(
    action: AgentPreparedFinancialAction,
) -> bool:
    return action.source_conflict and authority_is_near(action)

