from __future__ import annotations

import json
from pathlib import Path

from nova.harnesses.agent_prepared_financial_action_review.batch_replay import (
    run_batch_replay,
)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def valid_base(**overrides):
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
    return base


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


def test_batch_replay_summarizes_valid_records_and_errors(tmp_path: Path):
    retry = tmp_path / "retry.json"
    stale = tmp_path / "stale.json"
    conflict = tmp_path / "conflict.json"
    normal = tmp_path / "normal.json"
    malformed = tmp_path / "malformed.json"

    write_json(
        retry,
        valid_base(
            action_id="retry",
            route_confirmed=False,
            confirmation_status="incomplete",
            retry_count=2,
            same_route_retry=True,
            authority_proximity="high",
        ),
    )
    write_json(
        stale,
        valid_base(
            action_id="stale",
            liquidity_source_age_minutes=14,
            expected_source_freshness_minutes=5,
            authority_proximity="high",
        ),
    )
    write_json(
        conflict,
        valid_base(
            action_id="conflict",
            source_conflict=True,
            source_conflict_description="Approved sources disagree.",
            authority_proximity="high",
        ),
    )
    write_json(normal, valid_base(action_id="normal"))
    write_json(malformed, {"agent_id": "missing-action-id"})

    output = run_batch_replay([retry, stale, conflict, normal, malformed])

    assert output["classification"]["offline_replay"] is True
    assert output["classification"]["continuous_operation"] is False
    assert output["classification"]["live_integration"] is False
    assert output["classification"]["execution_capability"] is False
    assert output["classification"]["market_validation"] is False
    assert output["classification"]["production_readiness"] is False
    assert output["classification"]["buyer_validation"] is False

    assert output["summary"]["total_files_seen"] == 5
    assert output["summary"]["valid_records"] == 4
    assert output["summary"]["input_errors"] == 1
    assert output["summary"]["review_status_counts"]["constrained_review"] == 3
    assert output["summary"]["review_status_counts"]["normal_review"] == 1
    assert (
        output["summary"]["reason_code_counts"][
            "retry_pressure_after_incomplete_confirmation"
        ]
        == 1
    )
    assert (
        output["summary"]["reason_code_counts"][
            "stale_liquidity_source_with_rising_authority_proximity"
        ]
        == 1
    )
    assert (
        output["summary"]["reason_code_counts"][
            "approved_source_disagreement_near_authority_handoff"
        ]
        == 1
    )
    assert output["summary"]["reason_code_counts"]["normal_context"] == 1

    for result in output["results"]:
        assert_boundary_safe(result["review"]["boundary_log"])
        assert_boundary_safe(result["governance_record"]["boundary_log"])

    assert output["input_errors"][0]["error_type"] == "schema_error"
