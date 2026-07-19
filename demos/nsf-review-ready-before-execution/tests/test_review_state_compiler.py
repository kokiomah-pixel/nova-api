from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from review_state_compiler import (  # noqa: E402
    canonical_reproducibility_hash,
    compile_review_state,
    load_demo_data,
)


def _state():
    return compile_review_state(generated_at="2026-07-19T12:00:00Z")["review_state"]


def test_synthetic_request_can_be_loaded():
    request = load_demo_data()["request"]
    assert request["action_type"] == "collateral_top_up_request"
    assert request["account_reference"].startswith("SYNTHETIC-")


def test_review_state_object_contains_required_fields():
    state = _state()
    assert {"action", "review_readiness", "context", "authority_boundary", "NSF_research_surface"} <= set(state)
    assert state["action"]["operationally_executable"] is True
    assert state["review_readiness"]["review_ready"] is False


def test_stale_source_is_flagged():
    state = _state()
    assert "synthetic_collateral_ledger_snapshot" in state["review_readiness"]["stale_context"]


def test_missing_constraint_context_is_flagged():
    state = _state()
    assert "institutional_collateral_limit" in state["review_readiness"]["missing_context"]


def test_contradiction_fixture_is_loaded_and_unresolved_contradiction_is_flagged():
    data = load_demo_data()
    contradiction = data["contradictions"]["contradictions"][0]
    state = _state()
    assert contradiction["Nova_resolution"] == "none"
    assert contradiction["contradiction_id"] in state["review_readiness"]["contradiction_flags"]


def test_contradiction_is_preserved_without_resolution_or_winning_source():
    contradiction = _state()["context"]["contradictions"]["contradictions"][0]
    assert contradiction["resolution_status"] == "unresolved"
    assert contradiction["Nova_resolution"] == "none"
    assert set(contradiction) == {
        "contradiction_id", "field", "source_a", "source_b", "resolution_status", "Nova_resolution"
    }


def test_default_demo_is_not_review_ready():
    assert _state()["review_readiness"]["review_ready"] is False


def test_clean_control_can_be_review_ready_without_authority_effect():
    data = deepcopy(load_demo_data())
    data["source"]["sources"][0]["freshness"] = "current"
    data["source"]["collateral_position"]["freshness"] = "current"
    data["source"]["freshness_state"] = "current"
    data["constraints"]["unresolved_constraints"] = []
    data["chronology"]["chronology_gap"] = None
    data["contradictions"]["contradictions"] = []

    state = compile_review_state(data, generated_at="2026-07-19T12:00:00Z")["review_state"]
    assert state["review_readiness"]["review_ready"] is True
    assert state["review_readiness"]["readiness_meaning"] == "context_package_has_no_flagged_unresolved_conditions"
    assert state["authority_boundary"]["review_ready_does_not_equal_approved"] is True
    assert state["authority_boundary"]["Nova_approval"] is False
    assert state["authority_boundary"]["Nova_execution"] is False
    assert state["authority_boundary"]["authority_effect"] == "none"
    assert state["authority_boundary"]["execution_effect"] == "none"


def test_nsf_research_surface_fields_present():
    state = _state()
    assert len(state["NSF_research_surface"]) == 5
    assert len(state["context"]["proof_or_replay"]["reproducibility_hash"]) == 64


def test_reproducibility_hash_is_computed_stable_and_changes_with_input():
    data = load_demo_data()
    first = canonical_reproducibility_hash(data)
    second = canonical_reproducibility_hash(deepcopy(data))
    changed = deepcopy(data)
    changed["request"]["asset"] = "SYNTH-EUR"

    state = _state()
    assert first == second == state["context"]["proof_or_replay"]["reproducibility_hash"]
    assert canonical_reproducibility_hash(changed) != first
    assert state["context"]["proof_or_replay"]["hash_generation"] == "computed_by_demo_compiler"
