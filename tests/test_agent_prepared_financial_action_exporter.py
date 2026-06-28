from __future__ import annotations

import json
from pathlib import Path

from nova.harnesses.agent_prepared_financial_action_review.exporter import (
    export_governance_records,
    safe_filename,
)


def test_safe_filename_normalizes_action_id():
    assert safe_filename("Action 001") == "action-001"
    assert safe_filename("Action/001!") == "action-001"
    assert safe_filename("ACTION_001") == "action_001"
    assert safe_filename("") == "unknown-action"
    assert safe_filename(None) == "unknown-action"


def test_export_governance_records_writes_expected_files(tmp_path: Path):
    batch_output = {
        "batch_id": "test-batch",
        "harness_version": "v0.2",
        "summary": {
            "total_files_seen": 2,
            "valid_records": 1,
            "input_errors": 1,
            "review_status_counts": {"constrained_review": 1},
            "reason_code_counts": {
                "retry_pressure_after_incomplete_confirmation": 1
            },
        },
        "results": [
            {
                "input_file": "retry.json",
                "action_id": "Retry Action 001",
                "review": {
                    "review_status": "constrained_review",
                    "boundary_log": {
                        "nova_executes": False,
                        "nova_approves": False,
                        "nova_denies": False,
                        "nova_blocks": False,
                        "nova_routes": False,
                        "nova_settles": False,
                        "nova_moves_capital": False,
                        "nova_selects_source": False,
                        "nova_resolves_conflict": False,
                        "nova_makes_final_decision": False,
                        "local_authority_decides": True,
                    },
                },
                "governance_record": {
                    "action_id": "Retry Action 001",
                    "review_status": "constrained_review",
                    "boundary_log": {
                        "nova_executes": False,
                        "nova_approves": False,
                        "nova_denies": False,
                        "nova_blocks": False,
                        "nova_routes": False,
                        "nova_settles": False,
                        "nova_moves_capital": False,
                        "nova_selects_source": False,
                        "nova_resolves_conflict": False,
                        "nova_makes_final_decision": False,
                        "local_authority_decides": True,
                    },
                    "classification": {
                        "market_validation": False,
                        "production_readiness": False,
                        "buyer_validation": False,
                    },
                },
            }
        ],
        "input_errors": [
            {
                "input_file": "malformed.json",
                "error_type": "schema_error",
                "message": "missing required field",
            }
        ],
    }

    manifest = export_governance_records(batch_output, tmp_path)

    assert (tmp_path / "batch_summary.json").exists()
    assert (tmp_path / "batch_results.json").exists()
    assert (tmp_path / "input_errors.json").exists()
    assert (tmp_path / "export_manifest.json").exists()
    assert (tmp_path / "governance_records" / "retry-action-001.json").exists()

    assert manifest["classification"]["offline_export"] is True
    assert manifest["classification"]["continuous_operation"] is False
    assert manifest["classification"]["live_integration"] is False
    assert manifest["classification"]["execution_capability"] is False
    assert manifest["classification"]["market_validation"] is False
    assert manifest["classification"]["production_readiness"] is False
    assert manifest["classification"]["buyer_validation"] is False
    assert manifest["governance_record_count"] == 1
    assert manifest["input_error_count"] == 1

    summary = json.loads((tmp_path / "batch_summary.json").read_text())
    assert summary["classification"]["offline_export"] is True
    assert summary["classification"]["continuous_operation"] is False
    assert summary["classification"]["execution_capability"] is False

    exported_record = json.loads(
        (tmp_path / "governance_records" / "retry-action-001.json").read_text()
    )
    assert exported_record["boundary_log"]["nova_executes"] is False
    assert exported_record["boundary_log"]["nova_selects_source"] is False
    assert exported_record["boundary_log"]["nova_resolves_conflict"] is False
    assert exported_record["boundary_log"]["local_authority_decides"] is True
