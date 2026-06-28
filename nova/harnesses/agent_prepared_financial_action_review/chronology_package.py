from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"

README_TEXT = """# Chronology Ingestion Candidate Package

This package is an offline chronology-ingestion candidate package.

It is not automatically ingested into the Sharpe Nova OS operating chronology.

It does not mutate Reflex Memory.

It does not represent market validation, production readiness, buyer validation, production audit infrastructure, or execution authority.

Local authority remains responsible for deciding what, if anything, is accepted into chronology.
"""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def copy_file(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def build_chronology_ingestion_package(
    export_dir: Path,
    package_dir: Path,
) -> dict[str, Any]:
    export_dir = Path(export_dir)
    package_dir = Path(package_dir)

    export_manifest_path = export_dir / "export_manifest.json"
    batch_summary_path = export_dir / "batch_summary.json"
    input_errors_path = export_dir / "input_errors.json"
    governance_records_dir = export_dir / "governance_records"

    required_paths = [
        export_manifest_path,
        batch_summary_path,
        input_errors_path,
        governance_records_dir,
    ]

    for required_path in required_paths:
        if not required_path.exists():
            raise FileNotFoundError(f"Required export artifact missing: {required_path}")

    export_manifest = read_json(export_manifest_path)
    input_errors_payload = read_json(input_errors_path)
    governance_record_files = sorted(governance_records_dir.glob("*.json"))

    classification = {
        "offline_chronology_package": True,
        "automatic_chronology_ingestion": False,
        "automatic_reflex_memory_mutation": False,
        "continuous_operation": False,
        "live_integration": False,
        "execution_capability": False,
        "market_validation": False,
        "production_readiness": False,
        "buyer_validation": False,
        "production_audit_infrastructure": False,
    }

    files_written: list[str] = []

    files_written.append(
        copy_file(export_manifest_path, package_dir / "source_export_manifest.json")
    )
    files_written.append(copy_file(batch_summary_path, package_dir / "batch_summary.json"))
    files_written.append(copy_file(input_errors_path, package_dir / "input_errors.json"))

    package_governance_dir = package_dir / "governance_records"
    for source_record in governance_record_files:
        files_written.append(
            copy_file(source_record, package_governance_dir / source_record.name)
        )

    readme_path = package_dir / "README_CHRONOLOGY_INGESTION.md"
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(README_TEXT, encoding="utf-8")
    files_written.append(str(readme_path))

    manifest_path = package_dir / "chronology_ingestion_manifest.json"
    files_written.append(str(manifest_path))

    manifest = {
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "harness_version": "v0.4",
        "package_type": "offline_chronology_ingestion_package",
        "source_export_manifest_path": str(export_manifest_path),
        "classification": classification,
        "files_written": sorted(files_written),
        "governance_record_count": len(governance_record_files),
        "input_error_count": len(input_errors_payload.get("input_errors", [])),
        "manual_review_required": True,
        "ready_for_automatic_ingestion": False,
        "ready_for_reflex_memory_mutation": False,
        "source_export_classification": export_manifest.get("classification", {}),
    }

    write_json(manifest_path, manifest)

    return manifest
