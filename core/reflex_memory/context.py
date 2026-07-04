from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "fixtures" / "reflex_memory"

ALLOWED_REVIEW_POSTURE_EFFECTS = {
    "surface_prior_stress",
    "require_source_reconciliation_context",
    "flag_boundary_language_risk",
    "mark_context_as_source_limited",
    "preserve_manual_review_attention",
    "add_chronology_reference",
    "require_proof_reference",
    "highlight_recurring_context_pattern",
}


class ReflexMemoryError(ValueError):
    """Raised when Reflex Memory fixture state violates v0.1 invariants."""


def load_reflex_memory_entry(filename: str = "reflex_memory_entry_source_state_conflict.json") -> dict[str, Any]:
    """Load a deterministic Reflex Memory v0.1 fixture entry.

    This loader is intentionally fixture-backed. It is not dynamic storage,
    autonomous detection, automatic memory mutation, or production persistence.
    """
    path = FIXTURE_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        entry = json.load(f)

    validate_reflex_memory_entry(entry)
    return entry


def validate_reflex_memory_entry(entry: dict[str, Any]) -> None:
    """Validate the non-authority invariants for Reflex Memory v0.1."""
    if entry.get("version") != "reflex_memory_v0_1":
        raise ReflexMemoryError("Reflex Memory entry must use version reflex_memory_v0_1.")

    if entry.get("status") != "accepted":
        raise ReflexMemoryError("Only accepted Reflex Memory entries may appear in API review context.")

    if entry.get("authority_effect") != "none":
        raise ReflexMemoryError("Reflex Memory authority_effect must be none.")

    if entry.get("review_posture_effect") not in ALLOWED_REVIEW_POSTURE_EFFECTS:
        raise ReflexMemoryError("Reflex Memory review_posture_effect is not allowed.")

    if not entry.get("source_chronology_event_ids"):
        raise ReflexMemoryError("Reflex Memory entry must reference source chronology.")

    statement = entry.get("non_authority_statement", "")
    if "does not approve" not in statement or "execute" not in statement:
        raise ReflexMemoryError("Reflex Memory entry must preserve non-authority statement.")


def build_reflex_memory_context() -> dict[str, Any]:
    """Build Reflex Memory context for API review-context output.

    The returned object is review context only. It does not approve, deny,
    grant authority, route, settle, sign, execute, or replace local authority.
    """
    entry = load_reflex_memory_entry()

    return {
        "present": True,
        "version": "reflex_memory_v0_1",
        "entries": [
            {
                "reflex_id": entry["reflex_id"],
                "source_chronology_event_ids": entry["source_chronology_event_ids"],
                "trigger_pattern": entry["trigger_pattern"],
                "review_posture_effect": entry["review_posture_effect"],
                "authority_effect": "none",
                "note": "Accepted governance memory indicates that source-state reconciliation context should be visible before local authority acts.",
            }
        ],
    }
