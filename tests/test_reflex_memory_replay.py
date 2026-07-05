from core.reflex_memory.context import build_reflex_memory_context
from core.reflex_memory.replay import build_reflex_memory_replay


def test_reflex_memory_replay_reconstructs_all_context_entries() -> None:
    context = build_reflex_memory_context()
    replay = build_reflex_memory_replay()

    context_ids = {entry["reflex_id"] for entry in context["entries"]}
    replay_ids = {entry["reflex_id"] for entry in replay["entries"]}

    assert replay["status"] == "fixture_backed"
    assert replay["entry_count"] == len(context["entries"])
    assert replay_ids == context_ids


def test_reflex_memory_replay_traces_to_source_chronology_ids() -> None:
    replay = build_reflex_memory_replay()

    for entry in replay["entries"]:
        accepted = entry["accepted_entry"]

        assert accepted["source_chronology_event_ids"]
        assert accepted["authority_effect"] == "none"
        assert entry["trace_status"] == "reconstructed_from_fixture"


def test_reflex_memory_replay_preserves_non_authority_boundary() -> None:
    replay = build_reflex_memory_replay()

    assert "not approval" in replay["non_authority_statement"]
    assert "audit reporting" in replay["non_authority_statement"]

    for entry in replay["entries"]:
        assert entry["authority_effect"] == "none"
        assert entry["accepted_entry"]["authority_effect"] == "none"


def test_reflex_memory_replay_includes_expected_stress_types() -> None:
    replay = build_reflex_memory_replay()

    stress_types = {
        entry["accepted_entry"]["stress_type"]
        for entry in replay["entries"]
    }

    assert "source_integrity_risk" in stress_types
    assert "authority_boundary_risk" in stress_types
    assert "proof_lineage_incomplete" in stress_types
