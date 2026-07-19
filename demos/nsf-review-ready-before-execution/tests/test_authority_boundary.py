from __future__ import annotations

import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from review_state_compiler import compile_review_state  # noqa: E402


def _boundary():
    return compile_review_state(generated_at="2026-07-19T12:00:00Z")["review_state"]["authority_boundary"]


def test_authority_boundary_fields_are_false():
    boundary = _boundary()
    assert boundary["Nova_recommendation"] is False
    assert boundary["Nova_approval"] is False
    assert boundary["Nova_denial"] is False
    assert boundary["Nova_execution"] is False
    assert boundary["review_ready_does_not_equal_approved"] is True


def test_execution_and_authority_effects_are_none():
    boundary = _boundary()
    assert boundary["execution_effect"] == "none"
    assert boundary["authority_effect"] == "none"


def test_no_recommendation_approval_or_execution_command_generated():
    state = compile_review_state(generated_at="2026-07-19T12:00:00Z")["review_state"]
    assert "recommendation" not in state
    assert "approval" not in state
    assert "execution_command" not in state
    assert "routing_instruction" not in state
    assert "signing_instruction" not in state
    assert "settlement_instruction" not in state
