from __future__ import annotations

import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from review_state_compiler import compile_review_state, load_demo_data  # noqa: E402


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


def test_nsf_research_surface_fields_present():
    state = _state()
    assert len(state["NSF_research_surface"]) == 5
    assert len(state["context"]["proof_or_replay"]["reproducibility_hash"]) == 64
