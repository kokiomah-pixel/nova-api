from core.reflex_memory.context import (
    build_reflex_memory_context,
    load_reflex_memory_entries,
)


def test_reflex_memory_loads_multiple_accepted_entries() -> None:
    entries = load_reflex_memory_entries()

    reflex_ids = {entry["reflex_id"] for entry in entries}

    assert "RM-0001" in reflex_ids
    assert "RM-0002" in reflex_ids
    assert "RM-0003" in reflex_ids


def test_reflex_memory_multi_scenario_entries_preserve_authority_effect_none() -> None:
    entries = load_reflex_memory_entries()

    for entry in entries:
        assert entry["status"] == "accepted"
        assert entry["authority_effect"] == "none"
        assert entry["source_chronology_event_ids"]
        assert "does not approve" in entry["non_authority_statement"]


def test_reflex_memory_context_exposes_multiple_review_posture_effects() -> None:
    context = build_reflex_memory_context()

    effects = {entry["review_posture_effect"] for entry in context["entries"]}

    assert "require_source_reconciliation_context" in effects
    assert "flag_boundary_language_risk" in effects
    assert "require_proof_reference" in effects


def test_reflex_memory_context_entries_are_review_context_only() -> None:
    context = build_reflex_memory_context()

    assert context["present"] is True
    assert context["version"] == "reflex_memory_v0_1"

    for entry in context["entries"]:
        assert entry["authority_effect"] == "none"
