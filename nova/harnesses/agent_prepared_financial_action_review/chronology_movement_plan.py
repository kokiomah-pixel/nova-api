from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"

README_TEXT = """# Accepted-Records Manual Movement Plan

This is an offline accepted-records manual movement plan.

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


def create_accepted_records_manual_movement_plan(
    chronology_package_dir: Path,
    acceptance_decision_dir: Path,
    movement_plan_output_dir: Path,
    proposed_chronology_root_path: Path,
    reviewer: str | None = None,
) -> dict[str, Any]:
    chronology_package_dir = Path(chronology_package_dir)
    acceptance_decision_dir = Path(acceptance_decision_dir)
    movement_plan_output_dir = Path(movement_plan_output_dir)
    proposed_chronology_root_path = Path(proposed_chronology_root_path)

    package_manifest_path = chronology_package_dir / "chronology_ingestion_manifest.json"
    governance_records_dir = chronology_package_dir / "governance_records"
    acceptance_decision_path = (
        acceptance_decision_dir / "manual_chronology_acceptance_decision.json"
    )

    if not package_manifest_path.exists():
        raise FileNotFoundError(
            f"Required chronology package manifest missing: {package_manifest_path}"
        )

    if not governance_records_dir.exists():
        raise FileNotFoundError(
            f"Required governance records directory missing: {governance_records_dir}"
        )

    if not acceptance_decision_path.exists():
        raise FileNotFoundError(
            f"Required manual acceptance decision missing: {acceptance_decision_path}"
        )

    package_manifest = read_json(package_manifest_path)
    acceptance_decision = read_json(acceptance_decision_path)

    decision_outcome = acceptance_decision.get("decision_outcome")
    if decision_outcome != "accepted":
        raise ValueError(
            "Manual movement plan requires decision_outcome='accepted'. "
            f"Found decision_outcome={decision_outcome!r}."
        )

    proposed_records = []
    for source_record in sorted(governance_records_dir.glob("*.json")):
        proposed_destination = (
            proposed_chronology_root_path / "governance_records" / source_record.name
        )
        proposed_records.append(
            {
                "source_path": str(source_record),
                "proposed_destination_path": str(proposed_destination),
                "movement_status": "not_moved",
            }
        )

    classification = {
        "accepted_records_manual_movement_plan": True,
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

    plan = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.6",
        "workflow_type": "accepted_records_manual_movement_plan",
        "source_chronology_package_path": str(chronology_package_dir),
        "source_acceptance_decision_path": str(acceptance_decision_path),
        "proposed_chronology_root_path": str(proposed_chronology_root_path),
        "acceptance_decision_outcome": decision_outcome,
        "acceptance_decision_rationale": acceptance_decision.get(
            "decision_rationale"
        ),
        "reviewer": reviewer
        if reviewer is not None
        else acceptance_decision.get("reviewer"),
        "manual_movement_plan_created": True,
        "files_moved_to_chronology": False,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "reflex_memory_mutated": False,
        "ready_for_automatic_ingestion": False,
        "manual_execution_required": True,
        "proposed_records": proposed_records,
        "classification": classification,
        "source_package_classification": package_manifest.get("classification", {}),
        "acceptance_decision_classification": acceptance_decision.get(
            "classification", {}
        ),
    }

    plan_path = movement_plan_output_dir / "accepted_records_manual_movement_plan.json"
    readme_path = movement_plan_output_dir / "README_MANUAL_MOVEMENT_PLAN.md"

    write_json(plan_path, plan)
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(README_TEXT, encoding="utf-8")

    return plan
