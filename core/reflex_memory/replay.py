from __future__ import annotations

from typing import Any

from core.reflex_memory.context import build_reflex_memory_context, load_reflex_memory_entries


def build_reflex_memory_replay() -> dict[str, Any]:
    """Build a fixture-backed replay artifact for Reflex Memory v0.1.

    This replay traces API review context back to accepted Reflex Memory entries
    and source chronology references.

    It is not an audit report, compliance review, execution authorization,
    approval, denial, routing, settlement, signing, wallet control, agent
    supervision, or local authority replacement.
    """
    context = build_reflex_memory_context()
    accepted_entries = load_reflex_memory_entries()
    accepted_by_id = {entry["reflex_id"]: entry for entry in accepted_entries}

    replay_entries = []

    for context_entry in context["entries"]:
        reflex_id = context_entry["reflex_id"]
        accepted_entry = accepted_by_id[reflex_id]

        replay_entries.append(
            {
                "reflex_id": reflex_id,
                "context_entry": context_entry,
                "accepted_entry": {
                    "status": accepted_entry["status"],
                    "source_chronology_event_ids": accepted_entry[
                        "source_chronology_event_ids"
                    ],
                    "trigger_pattern": accepted_entry["trigger_pattern"],
                    "stress_type": accepted_entry["stress_type"],
                    "review_posture_effect": accepted_entry["review_posture_effect"],
                    "authority_effect": accepted_entry["authority_effect"],
                    "evidence_refs": accepted_entry["evidence_refs"],
                },
                "trace_status": "reconstructed_from_fixture",
                "authority_effect": "none",
            }
        )

    return {
        "replay_type": "reflex_memory_v0_1_fixture_replay",
        "status": "fixture_backed",
        "context_version": context["version"],
        "entry_count": len(replay_entries),
        "entries": replay_entries,
        "non_authority_statement": (
            "This replay artifact reconstructs Reflex Memory context from deterministic "
            "fixtures only. It is not approval, denial, authorization, blocking, routing, "
            "settlement, signing, execution, compliance review, audit reporting, wallet "
            "control, agent supervision, or local authority replacement."
        ),
    }
