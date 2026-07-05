import pytest

from core.reflex_memory import (
    ReflexMemoryError,
    build_reflex_memory_context,
    load_reflex_memory_entries,
    validate_reflex_memory_entry,
)


def test_build_reflex_memory_context_is_review_context_only() -> None:
    context = build_reflex_memory_context()

    assert context["present"] is True
    assert context["version"] == "reflex_memory_v0_1"

    by_id = {entry["reflex_id"]: entry for entry in context["entries"]}

    assert by_id["RM-0001"]["authority_effect"] == "none"
    assert by_id["RM-0001"]["review_posture_effect"] == "require_source_reconciliation_context"


def test_load_reflex_memory_entries_preserves_single_entry_selection() -> None:
    entries = load_reflex_memory_entries(["reflex_memory_entry_source_state_conflict.json"])

    assert [entry["reflex_id"] for entry in entries] == ["RM-0001"]


def test_reflex_memory_rejects_non_accepted_entry() -> None:
    entry = {
        "version": "reflex_memory_v0_1",
        "status": "candidate",
        "authority_effect": "none",
        "review_posture_effect": "require_source_reconciliation_context",
        "source_chronology_event_ids": ["CHR-2026-07-03-001"],
        "non_authority_statement": "This does not approve, deny, authorize, block, route, settle, sign, execute, or replace local authority.",
    }

    with pytest.raises(ReflexMemoryError):
        validate_reflex_memory_entry(entry)


def test_reflex_memory_rejects_authority_effect() -> None:
    entry = {
        "version": "reflex_memory_v0_1",
        "status": "accepted",
        "authority_effect": "approve_action",
        "review_posture_effect": "require_source_reconciliation_context",
        "source_chronology_event_ids": ["CHR-2026-07-03-001"],
        "non_authority_statement": "This does not approve, deny, authorize, block, route, settle, sign, execute, or replace local authority.",
    }

    with pytest.raises(ReflexMemoryError):
        validate_reflex_memory_entry(entry)


def test_reflex_memory_rejects_missing_source_chronology() -> None:
    entry = {
        "version": "reflex_memory_v0_1",
        "status": "accepted",
        "authority_effect": "none",
        "review_posture_effect": "require_source_reconciliation_context",
        "source_chronology_event_ids": [],
        "non_authority_statement": "This does not approve, deny, authorize, block, route, settle, sign, execute, or replace local authority.",
    }

    with pytest.raises(ReflexMemoryError):
        validate_reflex_memory_entry(entry)
