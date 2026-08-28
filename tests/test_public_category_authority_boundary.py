from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATEGORY = REPO_ROOT / "CATEGORY.md"


def _category_text() -> str:
    return CATEGORY.read_text(encoding="utf-8")


def test_category_preserves_canonical_non_authority_boundary() -> None:
    text = _category_text()
    for line in (
        "Agent prepares an action.",
        "Nova structures review context.",
        "Local authority decides.",
        "External systems execute.",
        "Nova does not execute.",
    ):
        assert line in text


def test_category_rejects_nova_as_decision_authority() -> None:
    text = _category_text().lower()
    assert "nova determines whether capital should move" not in text
    assert "nova does not determine whether capital should move" in text
    assert "required input to authority\n!= authority" in text


def test_category_defines_local_authority_as_role_not_human_requirement() -> None:
    text = _category_text().lower()
    assert "local authority` is a role in the architecture" in text
    assert "human, committee" in text
    assert "separately authorized machine process" in text
    assert "nova does not decide who holds that authority" in text


def test_category_preserves_exact_proposal_binding() -> None:
    text = _category_text().lower()
    assert "exact-action binding" in text
    assert "exact proposal version" in text
    assert "proposal-version identity" in text


def test_category_does_not_reduce_reflex_memory_to_snapshot_logging() -> None:
    text = _category_text().lower()
    assert "reflex memory is not merely a snapshot" in text
    assert "accepted governance memory" in text
    assert "without creating decision authority" in text
