from __future__ import annotations

from nova.harnesses.agent_prepared_financial_action_review import (
    AgentPreparedFinancialAction,
    build_governance_record,
    review_agent_prepared_action,
)


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


def make_action(**overrides):
    base = {
        "action_id": "test-action",
        "agent_id": "test-agent",
        "action_type": "material_financial_action",
        "materiality": "material",
        "route_confirmed": True,
        "confirmation_status": "complete",
        "retry_count": 0,
        "same_route_retry": False,
        "liquidity_source_age_minutes": 1,
        "expected_source_freshness_minutes": 5,
        "settlement_context": "normal",
        "source_conflict": False,
        "source_conflict_description": None,
        "venue_condition_summary": None,
        "authority_proximity": "low",
        "local_authority_context": "pending review",
    }
    base.update(overrides)
    return AgentPreparedFinancialAction.from_dict(base)


def assert_boundary_safe(boundary_log):
    assert boundary_log["nova_executes"] is False
    assert boundary_log["nova_approves"] is False
    assert boundary_log["nova_denies"] is False
    assert boundary_log["nova_blocks"] is False
    assert boundary_log["nova_routes"] is False
    assert boundary_log["nova_settles"] is False
    assert boundary_log["nova_moves_capital"] is False
    assert boundary_log["nova_selects_source"] is False
    assert boundary_log["nova_resolves_conflict"] is False
    assert boundary_log["nova_makes_final_decision"] is False
    assert boundary_log["local_authority_decides"] is True


def test_retry_pressure_produces_constrained_review():
    action = make_action(
        route_confirmed=False,
        confirmation_status="incomplete",
        retry_count=3,
        same_route_retry=True,
        authority_proximity="high",
    )
    review = review_agent_prepared_action(action)

    assert review.review_status == "constrained_review"
    assert "retry_pressure_after_incomplete_confirmation" in review.reason_codes
    assert_boundary_safe(review.boundary_log)


def test_stale_liquidity_produces_constrained_review():
    action = make_action(
        liquidity_source_age_minutes=14,
        expected_source_freshness_minutes=5,
        authority_proximity="high",
    )
    review = review_agent_prepared_action(action)

    assert review.review_status == "constrained_review"
    assert (
        "stale_liquidity_source_with_rising_authority_proximity"
        in review.reason_codes
    )
    assert_boundary_safe(review.boundary_log)


def test_source_conflict_produces_constrained_review_without_source_selection():
    action = make_action(
        source_conflict=True,
        source_conflict_description=(
            "Approved Source A reports venue available; Approved Source B reports "
            "venue degraded."
        ),
        venue_condition_summary="conflicting approved source reports",
        authority_proximity="high",
    )
    review = review_agent_prepared_action(action)

    assert review.review_status == "constrained_review"
    assert (
        "approved_source_disagreement_near_authority_handoff"
        in review.reason_codes
    )
    assert review.boundary_log["nova_selects_source"] is False
    assert review.boundary_log["nova_resolves_conflict"] is False
    assert_boundary_safe(review.boundary_log)


def test_normal_context_produces_normal_review_without_approval_language():
    action = make_action()
    review = review_agent_prepared_action(action)

    assert review.review_status == "normal_review"
    assert review.review_status not in FORBIDDEN_REVIEW_STATUSES
    assert "normal_context" in review.reason_codes
    assert_boundary_safe(review.boundary_log)


def test_governance_record_preserves_classification_boundaries():
    action = make_action(
        source_conflict=True,
        authority_proximity="high",
    )
    review = review_agent_prepared_action(action)
    record = build_governance_record(action, review)

    assert record["local_authority_decides"] is True
    assert record["classification"]["market_validation"] is False
    assert record["classification"]["production_readiness"] is False
    assert record["classification"]["buyer_validation"] is False
    assert record["classification"]["execution_system"] is False
    assert record["classification"]["treasury_agent"] is False
    assert record["classification"]["payment_router"] is False
    assert "execute" in record["what_nova_did_not_do"]
    assert "select_source" in record["what_nova_did_not_do"]
    assert "resolve_conflict" in record["what_nova_did_not_do"]
