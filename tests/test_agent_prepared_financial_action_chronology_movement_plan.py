from __future__ import annotations

import json
from pathlib import Path

import pytest

from nova.harnesses.agent_prepared_financial_action_review.chronology_movement_plan import (
    create_accepted_records_manual_movement_plan,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_create_accepted_records_manual_movement_plan(tmp_path: Path):
    package_dir = tmp_path / "package"
    decision_dir = tmp_path / "decision"
    output_dir = tmp_path / "movement_plan"
    proposed_root = tmp_path / "operating_chronology"

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
        package_dir / "governance_records" / "record-001.json",
        {
            "action_id": "record-001",
            "boundary_log": {
                "nova_executes": False,
                "local_authority_decides": True,
            },
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

    plan = create_accepted_records_manual_movement_plan(
        chronology_package_dir=package_dir,
        acceptance_decision_dir=decision_dir,
        movement_plan_output_dir=output_dir,
        proposed_chronology_root_path=proposed_root,
    )

    assert (output_dir / "accepted_records_manual_movement_plan.json").exists()
    assert (output_dir / "README_MANUAL_MOVEMENT_PLAN.md").exists()

    assert plan["workflow_type"] == "accepted_records_manual_movement_plan"
    assert plan["acceptance_decision_outcome"] == "accepted"
    assert plan["manual_movement_plan_created"] is True
    assert plan["files_moved_to_chronology"] is False
    assert plan["automatic_chronology_ingestion"] is False
    assert plan["automatic_reflex_memory_mutation"] is False
    assert plan["reflex_memory_mutated"] is False
    assert plan["ready_for_automatic_ingestion"] is False
    assert plan["manual_execution_required"] is True

    assert len(plan["proposed_records"]) == 1
    assert plan["proposed_records"][0]["movement_status"] == "not_moved"
    assert plan["proposed_records"][0]["source_path"].endswith("record-001.json")
    assert plan["proposed_records"][0]["proposed_destination_path"].endswith(
        "governance_records/record-001.json"
    )

    assert plan["classification"]["accepted_records_manual_movement_plan"] is True
    assert plan["classification"]["manual_execution_required"] is True
    assert plan["classification"]["files_moved_to_chronology"] is False
    assert plan["classification"]["automatic_file_movement"] is False
    assert plan["classification"]["automatic_chronology_ingestion"] is False
    assert plan["classification"]["automatic_reflex_memory_mutation"] is False
    assert plan["classification"]["reflex_memory_mutated"] is False
    assert plan["classification"]["continuous_operation"] is False
    assert plan["classification"]["live_integration"] is False
    assert plan["classification"]["execution_capability"] is False
    assert plan["classification"]["market_validation"] is False
    assert plan["classification"]["production_readiness"] is False
    assert plan["classification"]["buyer_validation"] is False
    assert plan["classification"]["production_audit_infrastructure"] is False

    readme = (output_dir / "README_MANUAL_MOVEMENT_PLAN.md").read_text()
    assert "does not move files" in readme
    assert "does not automatically ingest" in readme
    assert "does not mutate Reflex Memory" in readme
    assert "Local authority remains responsible" in readme


def test_reject_non_accepted_decision_for_manual_movement_plan(tmp_path: Path):
    package_dir = tmp_path / "package"
    decision_dir = tmp_path / "decision"
    output_dir = tmp_path / "movement_plan"
    proposed_root = tmp_path / "operating_chronology"

    write_json(package_dir / "chronology_ingestion_manifest.json", {"classification": {}})
    (package_dir / "governance_records").mkdir(parents=True)

    write_json(
        decision_dir / "manual_chronology_acceptance_decision.json",
        {
            "decision_outcome": "deferred",
            "decision_rationale": "Not accepted yet.",
            "classification": {},
        },
    )

    with pytest.raises(ValueError):
        create_accepted_records_manual_movement_plan(
            chronology_package_dir=package_dir,
            acceptance_decision_dir=decision_dir,
            movement_plan_output_dir=output_dir,
            proposed_chronology_root_path=proposed_root,
        )
