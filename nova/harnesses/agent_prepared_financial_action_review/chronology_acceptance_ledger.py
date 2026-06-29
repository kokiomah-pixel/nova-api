from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"

ALLOWED_LIFECYCLE_STATUSES = {
    "accepted",
    "planned_for_manual_movement",
    "deferred",
    "review_only",
    "rejected",
}

README_TEXT = """# Chronology Acceptance Ledger

This is an offline chronology acceptance ledger.

It records package lifecycle state across candidate packages, manual acceptance decisions, and manual movement plans.

It does not move files into the Sharpe Nova OS operating chronology.

It does not automatically ingest records into chronology.

It does not mutate Reflex Memory.

It does not represent market validation, production readiness, buyer validation, production audit infrastructure, or execution authority.

Local authority remains responsible for any future manual movement into chronology.
"""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def create_or_append_chronology_acceptance_ledger_entry(
    chronology_package_dir: Path,
    acceptance_decision_dir: Path,
    movement_plan_dir: Path,
    ledger_output_dir: Path,
    reviewer: str | None = None,
    lifecycle_status: str = "planned_for_manual_movement",
) -> dict[str, Any]:
    chronology_package_dir = Path(chronology_package_dir)
    acceptance_decision_dir = Path(acceptance_decision_dir)
    movement_plan_dir = Path(movement_plan_dir)
    ledger_output_dir = Path(ledger_output_dir)

    if lifecycle_status not in ALLOWED_LIFECYCLE_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_LIFECYCLE_STATUSES))
        raise ValueError(
            f"Invalid lifecycle_status: {lifecycle_status}. "
            f"Allowed statuses: {allowed}"
        )

    package_manifest_path = chronology_package_dir / "chronology_ingestion_manifest.json"
    acceptance_decision_path = (
        acceptance_decision_dir / "manual_chronology_acceptance_decision.json"
    )
    movement_plan_path = movement_plan_dir / "accepted_records_manual_movement_plan.json"

    if not package_manifest_path.exists():
        raise FileNotFoundError(
            f"Required chronology package manifest missing: {package_manifest_path}"
        )

    if not acceptance_decision_path.exists():
        raise FileNotFoundError(
            f"Required manual acceptance decision missing: {acceptance_decision_path}"
        )

    if not movement_plan_path.exists():
        raise FileNotFoundError(
            f"Required manual movement plan missing: {movement_plan_path}"
        )

    package_manifest = read_json(package_manifest_path)
    acceptance_decision = read_json(acceptance_decision_path)
    movement_plan = read_json(movement_plan_path)

    movement_classification = movement_plan.get("classification", {})
    required_movement_flags = {
        "accepted_records_manual_movement_plan": True,
        "files_moved_to_chronology": False,
        "automatic_file_movement": False,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
    }

    for key, expected_value in required_movement_flags.items():
        actual_value = movement_classification.get(key)
        if actual_value is not expected_value:
            raise ValueError(
                f"Movement plan classification guardrail failed for {key}: "
                f"expected {expected_value!r}, found {actual_value!r}."
            )

    ledger_classification = {
        "chronology_acceptance_ledger": True,
        "append_only_lifecycle_record": True,
        "manual_execution_required": True,
        "files_moved_to_chronology": False,
        "automatic_file_movement": False,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "reflex_memory_mutated": False,
        "continuous_operation": False,
        "live_integration": False,
        "execution_capability": False,
        "market_validation": False,
        "production_readiness": False,
        "buyer_validation": False,
        "production_audit_infrastructure": False,
    }

    proposed_records = movement_plan.get("proposed_records", [])

    entry = {
        "entry_type": "chronology_acceptance_lifecycle_entry",
        "source_chronology_package_path": str(chronology_package_dir),
        "source_acceptance_decision_path": str(acceptance_decision_path),
        "source_movement_plan_path": str(movement_plan_path),
        "acceptance_decision_outcome": acceptance_decision.get("decision_outcome"),
        "acceptance_decision_rationale": acceptance_decision.get("decision_rationale"),
        "lifecycle_status": lifecycle_status,
        "reviewer": reviewer
        if reviewer is not None
        else movement_plan.get("reviewer"),
        "proposed_record_count": len(proposed_records),
        "files_moved_to_chronology": False,
        "automatic_file_movement": False,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "reflex_memory_mutated": False,
        "manual_execution_required": True,
        "source_package_classification": package_manifest.get("classification", {}),
        "acceptance_decision_classification": acceptance_decision.get(
            "classification", {}
        ),
        "movement_plan_classification": movement_classification,
    }

    ledger_path = ledger_output_dir / "chronology_acceptance_ledger.json"
    readme_path = ledger_output_dir / "README_CHRONOLOGY_ACCEPTANCE_LEDGER.md"

    if ledger_path.exists():
        ledger = read_json(ledger_path)
        entries = ledger.setdefault("entries", [])
        if not isinstance(entries, list):
            raise ValueError("Existing ledger entries field must be a list.")
        entries.append(entry)
        ledger["ledger_classification"] = ledger_classification
    else:
        ledger = {
            "formal_harness_name": FORMAL_HARNESS_NAME,
            "harness_version": "v0.7",
            "workflow_type": "chronology_acceptance_ledger",
            "ledger_classification": ledger_classification,
            "entries": [entry],
        }

    write_json(ledger_path, ledger)
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(README_TEXT, encoding="utf-8")

    return ledger
