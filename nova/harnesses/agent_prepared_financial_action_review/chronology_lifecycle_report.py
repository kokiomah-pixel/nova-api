from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"

README_TEXT = """# Chronology Lifecycle Report

This is an offline chronology lifecycle report.

It reads a local chronology acceptance ledger and summarizes lifecycle state.

It does not move files into the Sharpe Nova OS operating chronology.

It does not automatically ingest records into chronology.

It does not mutate Reflex Memory.

It does not represent market validation, production readiness, buyer validation, production audit infrastructure, compliance reporting, audit reporting, or execution authority.

Local authority remains responsible for any future manual movement into chronology.
"""

BOUNDARY_EXPECTATIONS = {
    "files_moved_to_chronology": False,
    "automatic_file_movement": False,
    "automatic_chronology_ingestion": False,
    "automatic_reflex_memory_mutation": False,
    "reflex_memory_mutated": False,
    "manual_execution_required": True,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def summarize_chronology_acceptance_ledger(
    ledger_dir: Path,
    report_output_dir: Path,
    reviewer: str | None = None,
) -> dict[str, Any]:
    ledger_dir = Path(ledger_dir)
    report_output_dir = Path(report_output_dir)

    ledger_path = ledger_dir / "chronology_acceptance_ledger.json"
    if not ledger_path.exists():
        raise FileNotFoundError(
            f"Required chronology acceptance ledger missing: {ledger_path}"
        )

    ledger = read_json(ledger_path)
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Ledger entries field must be a list.")

    lifecycle_status_counts: Counter[str] = Counter()
    decision_outcome_counts: Counter[str] = Counter()
    package_paths: set[str] = set()
    decision_paths: set[str] = set()
    movement_plan_paths: set[str] = set()

    total_proposed_record_count = 0

    boundary_exceptions: list[dict[str, Any]] = []
    entries_claiming_files_moved = 0
    entries_claiming_automatic_file_movement = 0
    entries_claiming_automatic_ingestion = 0
    entries_claiming_automatic_reflex_mutation = 0
    entries_claiming_reflex_mutation = 0

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            boundary_exceptions.append(
                {
                    "entry_index": index,
                    "field": "entry",
                    "value": type(entry).__name__,
                    "expected": "dict",
                }
            )
            continue

        lifecycle_status = entry.get("lifecycle_status")
        if lifecycle_status is not None:
            lifecycle_status_counts[str(lifecycle_status)] += 1

        decision_outcome = entry.get("acceptance_decision_outcome")
        if decision_outcome is not None:
            decision_outcome_counts[str(decision_outcome)] += 1

        proposed_record_count = entry.get("proposed_record_count", 0)
        if isinstance(proposed_record_count, int):
            total_proposed_record_count += proposed_record_count

        package_path = entry.get("source_chronology_package_path")
        if package_path:
            package_paths.add(str(package_path))

        decision_path = entry.get("source_acceptance_decision_path")
        if decision_path:
            decision_paths.add(str(decision_path))

        movement_plan_path = entry.get("source_movement_plan_path")
        if movement_plan_path:
            movement_plan_paths.add(str(movement_plan_path))

        if entry.get("files_moved_to_chronology") is True:
            entries_claiming_files_moved += 1

        if entry.get("automatic_file_movement") is True:
            entries_claiming_automatic_file_movement += 1

        if entry.get("automatic_chronology_ingestion") is True:
            entries_claiming_automatic_ingestion += 1

        if entry.get("automatic_reflex_memory_mutation") is True:
            entries_claiming_automatic_reflex_mutation += 1

        if entry.get("reflex_memory_mutated") is True:
            entries_claiming_reflex_mutation += 1

        for field, expected_value in BOUNDARY_EXPECTATIONS.items():
            actual_value = entry.get(field)
            if actual_value is not expected_value:
                boundary_exceptions.append(
                    {
                        "entry_index": index,
                        "field": field,
                        "value": actual_value,
                        "expected": expected_value,
                    }
                )

    report_classification = {
        "chronology_lifecycle_report": True,
        "offline_report_only": True,
        "ledger_read_only": True,
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
        "audit_report": False,
        "compliance_report": False,
    }

    report = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.8",
        "workflow_type": "chronology_lifecycle_report",
        "source_ledger_path": str(ledger_path),
        "report_classification": report_classification,
        "summary": {
            "total_entries": len(entries),
            "lifecycle_status_counts": dict(sorted(lifecycle_status_counts.items())),
            "acceptance_decision_outcome_counts": dict(
                sorted(decision_outcome_counts.items())
            ),
            "total_proposed_record_count": total_proposed_record_count,
            "unique_source_chronology_package_paths": sorted(package_paths),
            "unique_source_acceptance_decision_paths": sorted(decision_paths),
            "unique_source_movement_plan_paths": sorted(movement_plan_paths),
            "entries_claiming_files_moved_to_chronology": entries_claiming_files_moved,
            "entries_claiming_automatic_file_movement": (
                entries_claiming_automatic_file_movement
            ),
            "entries_claiming_automatic_chronology_ingestion": (
                entries_claiming_automatic_ingestion
            ),
            "entries_claiming_automatic_reflex_memory_mutation": (
                entries_claiming_automatic_reflex_mutation
            ),
            "entries_claiming_reflex_memory_mutation": (
                entries_claiming_reflex_mutation
            ),
            "boundary_exception_count": len(boundary_exceptions),
            "boundary_exceptions": boundary_exceptions,
        },
        "reviewer": reviewer,
    }

    report_path = report_output_dir / "chronology_lifecycle_report.json"
    readme_path = report_output_dir / "README_CHRONOLOGY_LIFECYCLE_REPORT.md"

    write_json(report_path, report)
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(README_TEXT, encoding="utf-8")

    return report
