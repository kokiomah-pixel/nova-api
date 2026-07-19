"""Compile the bounded synthetic NSF review-state demonstration.

This module only structures supplied demo context.  It has no approval,
recommendation, routing, signing, settlement, or execution path.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEMO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = DEMO_ROOT / "demo_data"
SCHEMA_VERSION = "1.0"
DEMO_ID = "review-ready-before-execution"


def load_demo_data(data_root: Path = DATA_ROOT) -> dict[str, dict[str, Any]]:
    """Load the seven synthetic inputs used by this single-scenario demo."""
    filenames = {
        "request": "collateral_top_up_request.json",
        "source": "source_context.json",
        "classification": "classification_context.json",
        "constraints": "constraint_exposure_context.json",
        "chronology": "chronology_context.json",
        "contradictions": "contradiction_context.json",
        "proof_replay": "proof_replay_context.json",
    }
    return {
        name: json.loads((data_root / filename).read_text(encoding="utf-8"))
        for name, filename in filenames.items()
    }


def canonical_reproducibility_hash(data: dict[str, Any]) -> str:
    """Return a stable hash over the bounded, synthetic input package."""
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compile_review_state(
    data: dict[str, dict[str, Any]] | None = None,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Create review context while preserving unresolved conditions and authority."""
    data = load_demo_data() if data is None else data
    request = data["request"]
    source = data["source"]
    constraints = data["constraints"]
    chronology = data["chronology"]
    contradictions = data["contradictions"]
    reproducibility_hash = canonical_reproducibility_hash(data)

    stale_context = [
        item["source_id"]
        for item in source["sources"]
        if item.get("freshness") == "stale"
    ]
    missing_context = list(constraints["unresolved_constraints"])
    unresolved_questions = []
    if chronology.get("chronology_gap"):
        unresolved_questions.append(chronology["chronology_gap"])
    contradiction_flags = [
        contradiction["contradiction_id"]
        for contradiction in contradictions["contradictions"]
        if contradiction.get("resolution_status") == "unresolved"
    ]
    review_ready = not any(
        [missing_context, stale_context, contradiction_flags, unresolved_questions]
    )

    return {
        "review_state": {
            "schema_version": SCHEMA_VERSION,
            "demo_id": DEMO_ID,
            "generated_at": generated_at
            or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "action": {
                "action_type": request["action_type"],
                "account_reference": request["account_reference"],
                "asset": request["asset"],
                "proposed_amount_range": request["proposed_amount_range"],
                "prepared_by": request["prepared_by"],
                "operationally_executable": request["operationally_executable"],
            },
            "review_readiness": {
                "review_ready": review_ready,
                "readiness_meaning": "context_package_has_no_flagged_unresolved_conditions",
                "missing_context": missing_context,
                "stale_context": stale_context,
                "contradiction_flags": contradiction_flags,
                "unresolved_questions": unresolved_questions,
            },
            "context": {
                "collateral_position": source["collateral_position"],
                "source_data": {
                    "sources": source["sources"],
                    "provenance_complete": source["provenance_complete"],
                    "freshness_state": source["freshness_state"],
                },
                "classification": data["classification"],
                "constraints_and_exposure": constraints,
                "chronology": chronology,
                "contradictions": contradictions,
                "proof_or_replay": {
                    **data["proof_replay"],
                    "reproducibility_hash": reproducibility_hash,
                },
            },
            "authority_boundary": {
                "local_authority_required": True,
                "Nova_recommendation": False,
                "Nova_approval": False,
                "Nova_denial": False,
                "Nova_execution": False,
                "review_ready_does_not_equal_approved": True,
                "execution_effect": "none",
                "authority_effect": "none",
            },
            "NSF_research_surface": {
                "minimum_sufficient_context_question": "Which supplied context is materially necessary for review?",
                "temporal_coherence_question": "How should stale, late, or conflicting sources remain visible?",
                "contradiction_handling_question": "How can unresolved contradictions be preserved without false resolution?",
                "deterministic_reconstruction_question": "Can independent reviewers reconstruct a materially equivalent state?",
                "authority_boundary_question": "Do reviewers understand that local authority remains outside Nova?",
            },
        }
    }
