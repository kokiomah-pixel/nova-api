from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"

ALLOWED_DECISION_OUTCOMES = {"accepted", "rejected", "deferred", "review_only"}

README_TEXT = """# Manual Chronology Acceptance Decision

This is an offline manual chronology acceptance decision record.

It does not automatically ingest records into the Sharpe Nova OS operating chronology.

It does not mutate Reflex Memory.

It does not move files into chronology.

It does not represent market validation, production readiness, buyer validation, production audit infrastructure, or execution authority.

Local authority remains responsible for deciding what, if anything, is manually accepted into chronology.
"""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def create_manual_chronology_acceptance_decision(
    chronology_package_dir: Path,
    decision_output_dir: Path,
    decision_outcome: str,
    decision_rationale: str,
    reviewer: str | None = None,
) -> dict[str, Any]:
    chronology_package_dir = Path(chronology_package_dir)
    decision_output_dir = Path(decision_output_dir)

    if decision_outcome not in ALLOWED_DECISION_OUTCOMES:
        allowed = ", ".join(sorted(ALLOWED_DECISION_OUTCOMES))
        raise ValueError(
            f"Invalid decision_outcome: {decision_outcome}. "
            f"Allowed outcomes: {allowed}"
        )

    manifest_path = chronology_package_dir / "chronology_ingestion_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Required chronology package manifest missing: {manifest_path}"
        )

    source_manifest = read_json(manifest_path)

    classification = {
        "manual_chronology_acceptance_workflow": True,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "files_moved_to_chronology": False,
        "reflex_memory_mutated": False,
        "continuous_operation": False,
        "live_integration": False,
        "execution_capability": False,
        "market_validation": False,
        "production_readiness": False,
        "buyer_validation": False,
        "production_audit_infrastructure": False,
    }

    decision = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.5",
        "workflow_type": "manual_chronology_acceptance_workflow",
        "source_chronology_package_path": str(chronology_package_dir),
        "source_chronology_manifest_path": str(manifest_path),
        "decision_outcome": decision_outcome,
        "decision_rationale": decision_rationale,
        "reviewer": reviewer,
        "manual_review_completed": True,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "files_moved_to_chronology": False,
        "reflex_memory_mutated": False,
        "ready_for_automatic_ingestion": False,
        "classification": classification,
        "source_package_classification": source_manifest.get("classification", {}),
    }

    decision_path = decision_output_dir / "manual_chronology_acceptance_decision.json"
    readme_path = decision_output_dir / "README_MANUAL_ACCEPTANCE.md"

    write_json(decision_path, decision)
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(README_TEXT, encoding="utf-8")

    return decision
