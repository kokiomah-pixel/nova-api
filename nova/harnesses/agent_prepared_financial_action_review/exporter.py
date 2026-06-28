from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"


def safe_filename(value: str | None) -> str:
    if not value:
        return "unknown-action"

    normalized = value.strip().lower().replace(" ", "-")
    safe = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    safe = re.sub(r"-+", "-", safe).strip("-")

    return safe or "unknown-action"


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def export_governance_records(
    batch_output: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    governance_dir = output_dir / "governance_records"

    classification = {
        "offline_export": True,
        "continuous_operation": False,
        "live_integration": False,
        "execution_capability": False,
        "market_validation": False,
        "production_readiness": False,
        "buyer_validation": False,
    }

    summary_payload = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.3",
        "export_type": "offline_governance_record_export",
        "classification": classification,
        "batch_id": batch_output.get("batch_id"),
        "source_harness_version": batch_output.get("harness_version"),
        "summary": batch_output.get("summary", {}),
    }

    results_payload = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.3",
        "export_type": "offline_batch_results_export",
        "classification": classification,
        "results": batch_output.get("results", []),
    }

    input_errors_payload = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.3",
        "export_type": "offline_input_errors_export",
        "classification": classification,
        "input_errors": batch_output.get("input_errors", []),
    }

    batch_summary_path = output_dir / "batch_summary.json"
    batch_results_path = output_dir / "batch_results.json"
    input_errors_path = output_dir / "input_errors.json"

    write_json(batch_summary_path, summary_payload)
    write_json(batch_results_path, results_payload)
    write_json(input_errors_path, input_errors_payload)

    files_written = [
        str(batch_summary_path),
        str(batch_results_path),
        str(input_errors_path),
    ]

    governance_record_count = 0

    for result in batch_output.get("results", []):
        action_id = result.get("action_id")
        governance_record = result.get("governance_record")

        if not isinstance(governance_record, dict):
            continue

        record_filename = f"{safe_filename(action_id)}.json"
        record_path = governance_dir / record_filename
        write_json(record_path, governance_record)
        files_written.append(str(record_path))
        governance_record_count += 1

    manifest_path = output_dir / "export_manifest.json"
    files_written.append(str(manifest_path))

    manifest = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.3",
        "export_type": "offline_governance_record_export",
        "classification": classification,
        "files_written": sorted(files_written),
        "governance_record_count": governance_record_count,
        "input_error_count": len(batch_output.get("input_errors", [])),
    }

    write_json(manifest_path, manifest)

    return manifest
