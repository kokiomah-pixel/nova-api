from __future__ import annotations

import json
from pathlib import Path

import pytest

from nova.harnesses.agent_prepared_financial_action_review.chronology_acceptance import (
    create_manual_chronology_acceptance_decision,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_create_manual_chronology_acceptance_decision(tmp_path: Path):
    package_dir = tmp_path / "package"
    output_dir = tmp_path / "decision"

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

    decision = create_manual_chronology_acceptance_decision(
        chronology_package_dir=package_dir,
        decision_output_dir=output_dir,
        decision_outcome="accepted",
        decision_rationale="Manual review accepted this candidate package for later controlled chronology movement.",
        reviewer="local-authority-reviewer",
    )

    assert (output_dir / "manual_chronology_acceptance_decision.json").exists()
    assert (output_dir / "README_MANUAL_ACCEPTANCE.md").exists()

    assert decision["decision_outcome"] == "accepted"
    assert decision["reviewer"] == "local-authority-reviewer"
    assert decision["manual_review_completed"] is True
    assert decision["automatic_chronology_ingestion"] is False
    assert decision["automatic_reflex_memory_mutation"] is False
    assert decision["files_moved_to_chronology"] is False
    assert decision["reflex_memory_mutated"] is False
    assert decision["ready_for_automatic_ingestion"] is False

    assert decision["classification"]["manual_chronology_acceptance_workflow"] is True
    assert decision["classification"]["automatic_chronology_ingestion"] is False
    assert decision["classification"]["automatic_reflex_memory_mutation"] is False
    assert decision["classification"]["files_moved_to_chronology"] is False
    assert decision["classification"]["reflex_memory_mutated"] is False
    assert decision["classification"]["continuous_operation"] is False
    assert decision["classification"]["live_integration"] is False
    assert decision["classification"]["execution_capability"] is False
    assert decision["classification"]["market_validation"] is False
    assert decision["classification"]["production_readiness"] is False
    assert decision["classification"]["buyer_validation"] is False
    assert decision["classification"]["production_audit_infrastructure"] is False

    readme = (output_dir / "README_MANUAL_ACCEPTANCE.md").read_text()
    assert "does not automatically ingest" in readme
    assert "does not mutate Reflex Memory" in readme
    assert "does not move files into chronology" in readme
    assert "Local authority remains responsible" in readme


def test_reject_invalid_manual_chronology_acceptance_outcome(tmp_path: Path):
    package_dir = tmp_path / "package"
    output_dir = tmp_path / "decision"

    write_json(
        package_dir / "chronology_ingestion_manifest.json",
        {"classification": {}},
    )

    with pytest.raises(ValueError):
        create_manual_chronology_acceptance_decision(
            chronology_package_dir=package_dir,
            decision_output_dir=output_dir,
            decision_outcome="auto_accept",
            decision_rationale="Invalid automatic acceptance should not be allowed.",
        )
