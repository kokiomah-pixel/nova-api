from __future__ import annotations

import json
from pathlib import Path

import pytest

from nova.harnesses.agent_prepared_financial_action_review.chronology_acceptance_ledger import (
    create_or_append_chronology_acceptance_ledger_entry,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def create_fixture_set(tmp_path: Path):
    package_dir = tmp_path / "package"
    decision_dir = tmp_path / "decision"
    movement_dir = tmp_path / "movement"
    ledger_dir = tmp_path / "ledger"

    write_json(
        package_dir / "chronology_ingestion_manifest.json",
        {
            "classification": {
                "offline_chronology_package": True,
                "automatic_chronology_ingestion": False,
                "automatic_reflex_memory_mutation": False,
            }
        },
    )

    write_json(
        decision_dir / "manual_chronology_acceptance_decision.json",
        {
            "decision_outcome": "accepted",
            "decision_rationale": "Accepted for later controlled manual movement.",
            "reviewer": "local-authority-reviewer",
            "classification": {
                "manual_chronology_acceptance_workflow": True,
                "automatic_chronology_ingestion": False,
                "automatic_reflex_memory_mutation": False,
            },
        },
    )

    write_json(
        movement_dir / "accepted_records_manual_movement_plan.json",
        {
            "reviewer": "local-authority-reviewer",
            "proposed_records": [
                {
                    "source_path": "/tmp/package/governance_records/record-001.json",
                    "proposed_destination_path": "/tmp/chronology/governance_records/record-001.json",
                    "movement_status": "not_moved",
                }
            ],
            "classification": {
                "accepted_records_manual_movement_plan": True,
                "manual_execution_required": True,
                "files_moved_to_chronology": False,
                "automatic_file_movement": False,
                "automatic_chronology_ingestion": False,
                "automatic_reflex_memory_mutation": False,
                "reflex_memory_mutated": False,
            },
        },
    )

    return package_dir, decision_dir, movement_dir, ledger_dir


def test_create_or_append_chronology_acceptance_ledger_entry(tmp_path: Path):
    package_dir, decision_dir, movement_dir, ledger_dir = create_fixture_set(tmp_path)

    ledger = create_or_append_chronology_acceptance_ledger_entry(
        chronology_package_dir=package_dir,
        acceptance_decision_dir=decision_dir,
        movement_plan_dir=movement_dir,
        ledger_output_dir=ledger_dir,
        reviewer="local-authority-reviewer",
    )

    assert (ledger_dir / "chronology_acceptance_ledger.json").exists()
    assert (ledger_dir / "README_CHRONOLOGY_ACCEPTANCE_LEDGER.md").exists()

    assert ledger["workflow_type"] == "chronology_acceptance_ledger"
    assert ledger["ledger_classification"]["chronology_acceptance_ledger"] is True
    assert ledger["ledger_classification"]["append_only_lifecycle_record"] is True
    assert ledger["ledger_classification"]["manual_execution_required"] is True
    assert ledger["ledger_classification"]["files_moved_to_chronology"] is False
    assert ledger["ledger_classification"]["automatic_file_movement"] is False
    assert ledger["ledger_classification"]["automatic_chronology_ingestion"] is False
    assert ledger["ledger_classification"]["automatic_reflex_memory_mutation"] is False
    assert ledger["ledger_classification"]["reflex_memory_mutated"] is False
    assert ledger["ledger_classification"]["continuous_operation"] is False
    assert ledger["ledger_classification"]["live_integration"] is False
    assert ledger["ledger_classification"]["execution_capability"] is False
    assert ledger["ledger_classification"]["market_validation"] is False
    assert ledger["ledger_classification"]["production_readiness"] is False
    assert ledger["ledger_classification"]["buyer_validation"] is False
    assert ledger["ledger_classification"]["production_audit_infrastructure"] is False

    assert len(ledger["entries"]) == 1
    entry = ledger["entries"][0]
    assert entry["entry_type"] == "chronology_acceptance_lifecycle_entry"
    assert entry["acceptance_decision_outcome"] == "accepted"
    assert entry["lifecycle_status"] == "planned_for_manual_movement"
    assert entry["proposed_record_count"] == 1
    assert entry["files_moved_to_chronology"] is False
    assert entry["automatic_file_movement"] is False
    assert entry["automatic_chronology_ingestion"] is False
    assert entry["automatic_reflex_memory_mutation"] is False
    assert entry["reflex_memory_mutated"] is False
    assert entry["manual_execution_required"] is True

    readme = (ledger_dir / "README_CHRONOLOGY_ACCEPTANCE_LEDGER.md").read_text()
    assert "offline chronology acceptance ledger" in readme
    assert "does not move files" in readme
    assert "does not automatically ingest" in readme
    assert "does not mutate Reflex Memory" in readme
    assert "Local authority remains responsible" in readme


def test_chronology_acceptance_ledger_appends_entries(tmp_path: Path):
    package_dir, decision_dir, movement_dir, ledger_dir = create_fixture_set(tmp_path)

    create_or_append_chronology_acceptance_ledger_entry(
        chronology_package_dir=package_dir,
        acceptance_decision_dir=decision_dir,
        movement_plan_dir=movement_dir,
        ledger_output_dir=ledger_dir,
    )

    ledger = create_or_append_chronology_acceptance_ledger_entry(
        chronology_package_dir=package_dir,
        acceptance_decision_dir=decision_dir,
        movement_plan_dir=movement_dir,
        ledger_output_dir=ledger_dir,
        lifecycle_status="accepted",
    )

    assert len(ledger["entries"]) == 2
    assert ledger["entries"][0]["lifecycle_status"] == "planned_for_manual_movement"
    assert ledger["entries"][1]["lifecycle_status"] == "accepted"


def test_chronology_acceptance_ledger_rejects_invalid_lifecycle_status(
    tmp_path: Path,
):
    package_dir, decision_dir, movement_dir, ledger_dir = create_fixture_set(tmp_path)

    with pytest.raises(ValueError):
        create_or_append_chronology_acceptance_ledger_entry(
            chronology_package_dir=package_dir,
            acceptance_decision_dir=decision_dir,
            movement_plan_dir=movement_dir,
            ledger_output_dir=ledger_dir,
            lifecycle_status="auto_ingested",
        )


def test_chronology_acceptance_ledger_rejects_bad_movement_classification(
    tmp_path: Path,
):
    package_dir, decision_dir, movement_dir, ledger_dir = create_fixture_set(tmp_path)

    write_json(
        movement_dir / "accepted_records_manual_movement_plan.json",
        {
            "classification": {
                "accepted_records_manual_movement_plan": True,
                "files_moved_to_chronology": True,
                "automatic_file_movement": False,
                "automatic_chronology_ingestion": False,
                "automatic_reflex_memory_mutation": False,
            },
            "proposed_records": [],
        },
    )

    with pytest.raises(ValueError):
        create_or_append_chronology_acceptance_ledger_entry(
            chronology_package_dir=package_dir,
            acceptance_decision_dir=decision_dir,
            movement_plan_dir=movement_dir,
            ledger_output_dir=ledger_dir,
        )
