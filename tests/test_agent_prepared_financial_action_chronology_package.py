from __future__ import annotations

import json
from pathlib import Path

from nova.harnesses.agent_prepared_financial_action_review.chronology_package import (
    build_chronology_ingestion_package,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_chronology_ingestion_package(tmp_path: Path):
    export_dir = tmp_path / "export"
    package_dir = tmp_path / "package"

    write_json(
        export_dir / "export_manifest.json",
        {
            "classification": {
                "offline_export": True,
                "continuous_operation": False,
                "execution_capability": False,
            },
            "governance_record_count": 1,
            "input_error_count": 1,
        },
    )
    write_json(
        export_dir / "batch_summary.json",
        {
            "classification": {
                "offline_export": True,
                "continuous_operation": False,
                "execution_capability": False,
            },
            "summary": {
                "total_files_seen": 2,
                "valid_records": 1,
                "input_errors": 1,
            },
        },
    )
    write_json(
        export_dir / "input_errors.json",
        {
            "input_errors": [
                {
                    "input_file": "malformed.json",
                    "error_type": "schema_error",
                    "message": "missing required field",
                }
            ]
        },
    )
    write_json(
        export_dir / "governance_records" / "record-001.json",
        {
            "action_id": "record-001",
            "boundary_log": {
                "nova_executes": False,
                "nova_selects_source": False,
                "nova_resolves_conflict": False,
                "local_authority_decides": True,
            },
            "classification": {
                "market_validation": False,
                "production_readiness": False,
                "buyer_validation": False,
            },
        },
    )

    manifest = build_chronology_ingestion_package(export_dir, package_dir)

    assert (package_dir / "chronology_ingestion_manifest.json").exists()
    assert (package_dir / "source_export_manifest.json").exists()
    assert (package_dir / "batch_summary.json").exists()
    assert (package_dir / "input_errors.json").exists()
    assert (package_dir / "README_CHRONOLOGY_INGESTION.md").exists()
    assert (package_dir / "governance_records" / "record-001.json").exists()

    assert manifest["classification"]["offline_chronology_package"] is True
    assert manifest["classification"]["automatic_chronology_ingestion"] is False
    assert manifest["classification"]["automatic_reflex_memory_mutation"] is False
    assert manifest["classification"]["continuous_operation"] is False
    assert manifest["classification"]["live_integration"] is False
    assert manifest["classification"]["execution_capability"] is False
    assert manifest["classification"]["market_validation"] is False
    assert manifest["classification"]["production_readiness"] is False
    assert manifest["classification"]["buyer_validation"] is False
    assert manifest["classification"]["production_audit_infrastructure"] is False
    assert manifest["manual_review_required"] is True
    assert manifest["ready_for_automatic_ingestion"] is False
    assert manifest["ready_for_reflex_memory_mutation"] is False
    assert manifest["governance_record_count"] == 1
    assert manifest["input_error_count"] == 1

    readme = (package_dir / "README_CHRONOLOGY_INGESTION.md").read_text()
    assert "not automatically ingested" in readme
    assert "does not mutate Reflex Memory" in readme
    assert "Local authority remains responsible" in readme

    copied_record = json.loads(
        (package_dir / "governance_records" / "record-001.json").read_text()
    )
    assert copied_record["boundary_log"]["nova_executes"] is False
    assert copied_record["boundary_log"]["nova_selects_source"] is False
    assert copied_record["boundary_log"]["nova_resolves_conflict"] is False
    assert copied_record["boundary_log"]["local_authority_decides"] is True
