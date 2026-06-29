from __future__ import annotations

import json
from pathlib import Path

import pytest

from nova.harnesses.agent_prepared_financial_action_review.chronology_lifecycle_report import (
    summarize_chronology_acceptance_ledger,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def create_ledger_fixture(tmp_path: Path) -> Path:
    ledger_dir = tmp_path / "ledger"

    write_json(
        ledger_dir / "chronology_acceptance_ledger.json",
        {
            "formal_harness_name": "Agent-Prepared Financial Action Review Harness",
            "harness_version": "v0.7",
            "workflow_type": "chronology_acceptance_ledger",
            "ledger_classification": {
                "chronology_acceptance_ledger": True,
                "append_only_lifecycle_record": True,
                "manual_execution_required": True,
            },
            "entries": [
                {
                    "entry_type": "chronology_acceptance_lifecycle_entry",
                    "source_chronology_package_path": "/tmp/package",
                    "source_acceptance_decision_path": (
                        "/tmp/decision/manual_chronology_acceptance_decision.json"
                    ),
                    "source_movement_plan_path": (
                        "/tmp/movement/accepted_records_manual_movement_plan.json"
                    ),
                    "acceptance_decision_outcome": "accepted",
                    "acceptance_decision_rationale": (
                        "Accepted for later controlled movement."
                    ),
                    "lifecycle_status": "planned_for_manual_movement",
                    "reviewer": "local-authority-reviewer",
                    "proposed_record_count": 4,
                    "files_moved_to_chronology": False,
                    "automatic_file_movement": False,
                    "automatic_chronology_ingestion": False,
                    "automatic_reflex_memory_mutation": False,
                    "reflex_memory_mutated": False,
                    "manual_execution_required": True,
                },
                {
                    "entry_type": "chronology_acceptance_lifecycle_entry",
                    "source_chronology_package_path": "/tmp/package",
                    "source_acceptance_decision_path": (
                        "/tmp/decision/manual_chronology_acceptance_decision.json"
                    ),
                    "source_movement_plan_path": (
                        "/tmp/movement/accepted_records_manual_movement_plan.json"
                    ),
                    "acceptance_decision_outcome": "accepted",
                    "acceptance_decision_rationale": "Accepted lifecycle entry.",
                    "lifecycle_status": "accepted",
                    "reviewer": "local-authority-reviewer",
                    "proposed_record_count": 4,
                    "files_moved_to_chronology": False,
                    "automatic_file_movement": False,
                    "automatic_chronology_ingestion": False,
                    "automatic_reflex_memory_mutation": False,
                    "reflex_memory_mutated": False,
                    "manual_execution_required": True,
                },
            ],
        },
    )

    return ledger_dir


def test_summarize_chronology_acceptance_ledger(tmp_path: Path):
    ledger_dir = create_ledger_fixture(tmp_path)
    report_dir = tmp_path / "report"

    report = summarize_chronology_acceptance_ledger(
        ledger_dir=ledger_dir,
        report_output_dir=report_dir,
        reviewer="local-authority-reviewer",
    )

    assert (report_dir / "chronology_lifecycle_report.json").exists()
    assert (report_dir / "README_CHRONOLOGY_LIFECYCLE_REPORT.md").exists()

    assert report["workflow_type"] == "chronology_lifecycle_report"
    assert report["report_classification"]["chronology_lifecycle_report"] is True
    assert report["report_classification"]["offline_report_only"] is True
    assert report["report_classification"]["ledger_read_only"] is True
    assert report["report_classification"]["manual_execution_required"] is True
    assert report["report_classification"]["files_moved_to_chronology"] is False
    assert report["report_classification"]["automatic_file_movement"] is False
    assert report["report_classification"]["automatic_chronology_ingestion"] is False
    assert report["report_classification"]["automatic_reflex_memory_mutation"] is False
    assert report["report_classification"]["reflex_memory_mutated"] is False
    assert report["report_classification"]["continuous_operation"] is False
    assert report["report_classification"]["live_integration"] is False
    assert report["report_classification"]["execution_capability"] is False
    assert report["report_classification"]["market_validation"] is False
    assert report["report_classification"]["production_readiness"] is False
    assert report["report_classification"]["buyer_validation"] is False
    assert report["report_classification"]["production_audit_infrastructure"] is False
    assert report["report_classification"]["audit_report"] is False
    assert report["report_classification"]["compliance_report"] is False

    summary = report["summary"]
    assert summary["total_entries"] == 2
    assert summary["lifecycle_status_counts"] == {
        "accepted": 1,
        "planned_for_manual_movement": 1,
    }
    assert summary["acceptance_decision_outcome_counts"] == {"accepted": 2}
    assert summary["total_proposed_record_count"] == 8
    assert summary["unique_source_chronology_package_paths"] == ["/tmp/package"]
    assert summary["unique_source_acceptance_decision_paths"] == [
        "/tmp/decision/manual_chronology_acceptance_decision.json"
    ]
    assert summary["unique_source_movement_plan_paths"] == [
        "/tmp/movement/accepted_records_manual_movement_plan.json"
    ]
    assert summary["entries_claiming_files_moved_to_chronology"] == 0
    assert summary["entries_claiming_automatic_file_movement"] == 0
    assert summary["entries_claiming_automatic_chronology_ingestion"] == 0
    assert summary["entries_claiming_automatic_reflex_memory_mutation"] == 0
    assert summary["entries_claiming_reflex_memory_mutation"] == 0
    assert summary["boundary_exception_count"] == 0
    assert summary["boundary_exceptions"] == []

    readme = (report_dir / "README_CHRONOLOGY_LIFECYCLE_REPORT.md").read_text()
    assert "offline chronology lifecycle report" in readme
    assert "does not move files" in readme
    assert "does not automatically ingest" in readme
    assert "does not mutate Reflex Memory" in readme
    assert "production audit infrastructure" in readme
    assert "compliance reporting" in readme
    assert "audit reporting" in readme
    assert "Local authority remains responsible" in readme


def test_summarize_chronology_acceptance_ledger_reports_boundary_exceptions(
    tmp_path: Path,
):
    ledger_dir = tmp_path / "ledger"
    report_dir = tmp_path / "report"

    write_json(
        ledger_dir / "chronology_acceptance_ledger.json",
        {
            "entries": [
                {
                    "lifecycle_status": "accepted",
                    "acceptance_decision_outcome": "accepted",
                    "proposed_record_count": 1,
                    "files_moved_to_chronology": True,
                    "automatic_file_movement": False,
                    "automatic_chronology_ingestion": True,
                    "automatic_reflex_memory_mutation": False,
                    "reflex_memory_mutated": True,
                    "manual_execution_required": False,
                }
            ]
        },
    )

    report = summarize_chronology_acceptance_ledger(
        ledger_dir=ledger_dir,
        report_output_dir=report_dir,
    )

    summary = report["summary"]
    assert summary["entries_claiming_files_moved_to_chronology"] == 1
    assert summary["entries_claiming_automatic_chronology_ingestion"] == 1
    assert summary["entries_claiming_reflex_memory_mutation"] == 1
    assert summary["boundary_exception_count"] == 4

    fields = {exception["field"] for exception in summary["boundary_exceptions"]}
    assert "files_moved_to_chronology" in fields
    assert "automatic_chronology_ingestion" in fields
    assert "reflex_memory_mutated" in fields
    assert "manual_execution_required" in fields


def test_summarize_chronology_acceptance_ledger_requires_entries_list(
    tmp_path: Path,
):
    ledger_dir = tmp_path / "ledger"
    report_dir = tmp_path / "report"

    write_json(
        ledger_dir / "chronology_acceptance_ledger.json",
        {"entries": {"not": "a-list"}},
    )

    with pytest.raises(ValueError):
        summarize_chronology_acceptance_ledger(
            ledger_dir=ledger_dir,
            report_output_dir=report_dir,
        )


def test_summarize_chronology_acceptance_ledger_requires_ledger(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        summarize_chronology_acceptance_ledger(
            ledger_dir=tmp_path / "missing-ledger",
            report_output_dir=tmp_path / "report",
        )
