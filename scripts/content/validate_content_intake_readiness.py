#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.content.validate_post_record import validate_post_record
    from scripts.content.validation_common import (
        ROOT,
        ContentValidationError,
        find_mapping,
        run_cli,
    )
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from validate_post_record import validate_post_record  # type: ignore[no-redef]
    from validation_common import (  # type: ignore[no-redef]
        ROOT,
        ContentValidationError,
        find_mapping,
        run_cli,
    )


DEFAULT_ROOT = ROOT


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContentValidationError(f"{path} must contain a YAML mapping")
    return payload


def validate_content_intake_readiness(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    root = root.resolve()
    content_root = root / "docs/content"
    passed: list[str] = []
    failed: list[str] = []

    def require(name: str, condition: bool, detail: str) -> None:
        if condition:
            passed.append(name)
        else:
            failed.append(f"{name}: {detail}")

    production_os = find_mapping(content_root / "content-production-os.md", "document")
    require(
        "Content_Production_OS.status_is_authoritative",
        production_os.get("status") == "authoritative",
        "document.status must be authoritative",
    )
    require(
        "Content_Production_OS.repository_status_is_merged",
        production_os.get("repository_status") == "merged",
        "document.repository_status must be merged",
    )
    require(
        "Content_Production_OS.canonical_version_is_1_0_0",
        str(production_os.get("version")) == "1.0.0",
        "document.version must be 1.0.0",
    )

    daily_state = find_mapping(
        content_root / "daily-coherence-content-operating-contract.md",
        "content_system_state",
    )
    require(
        "Daily_Coherence.repository_status_is_merged",
        daily_state.get("repository_status") == "merged",
        "repository_status must be merged",
    )
    require(
        "Daily_Coherence.operating_status_is_initialized",
        daily_state.get("operating_status") == "initialized",
        "operating_status must be initialized",
    )
    require(
        "Daily_Coherence.content_intake_status_is_ready",
        daily_state.get("content_intake_status") == "ready",
        "content_intake_status must be ready",
    )

    current_payload = _load_yaml(content_root / "content-current-state.yaml")
    current = current_payload.get("content_current_state")
    if not isinstance(current, dict):
        raise ContentValidationError("content-current-state.yaml requires content_current_state")
    intake = current.get("content_intake")
    if not isinstance(intake, dict):
        intake = {}
    require(
        "current_state.intake_status_is_ready",
        intake.get("status") == "ready",
        "content_intake.status must be ready",
    )
    require(
        "current_state.intake_surface_is_Content_Production_Engine",
        intake.get("intake_surface") == "Content_Production_Engine",
        "content_intake.intake_surface must be Content_Production_Engine",
    )
    require(
        "current_state.persistence_mode_is_bounded_VS_Code_repository_update",
        intake.get("persistence_mode") == "bounded_VS_Code_repository_update",
        "content_intake.persistence_mode must preserve the bounded VS Code handoff",
    )
    require(
        "current_state.automatic_repository_write_is_false",
        intake.get("automatic_repository_write") is False,
        "content_intake.automatic_repository_write must be false",
    )
    active_experiments = current.get("active_experiments")
    require(
        "current_state.active_experiments_is_empty",
        active_experiments == [],
        "active_experiments must remain empty",
    )
    require(
        "current_state.canonical_content_OS_version_is_1_0_0",
        str(current.get("canonical_content_OS_version")) == "1.0.0",
        "canonical_content_OS_version must be 1.0.0",
    )

    required_artifacts = {
        "artifacts.August_intake_protocol_exists": content_root
        / "content-production-engine-august-intake-protocol.md",
        "artifacts.post_record_template_exists": content_root / "templates/post-record-template.yaml",
        "artifacts.performance_ledger_exists": content_root
        / "performance/content-performance-ledger.csv",
        "artifacts.audience_ledger_exists": content_root
        / "performance/audience-engagement-ledger.csv",
    }
    for name, path in required_artifacts.items():
        require(name, path.is_file(), f"required artifact is missing: {path}")

    template_path = content_root / "templates/post-record-template.yaml"
    try:
        post_result = validate_post_record(template_path, allow_template_placeholders=True)
        template_valid = post_result.get("status") == "passed"
    except (ContentValidationError, OSError):
        template_valid = False
    require(
        "post_validation.post_record_template_validator_passes",
        template_valid,
        "post record template structural validation failed",
    )

    bridge_paths = {
        "bridge_boundary.automated_ingestion_script_absent": root
        / "scripts/content/ingest_content_evidence.py",
        "bridge_boundary.automated_evidence_store_absent": root
        / "scripts/content/content_evidence_store.py",
    }
    for name, path in bridge_paths.items():
        require(name, not path.exists(), f"automated bridge path must remain absent: {path}")
    intake_dir = content_root / "intake"
    receipt_dir = content_root / "receipts"
    require(
        "bridge_boundary.intake_receipt_directory_absent",
        not intake_dir.exists() and not receipt_dir.exists(),
        "automated intake and receipt directories must remain absent",
    )

    if failed:
        raise ContentValidationError("content intake readiness failed: " + "; ".join(failed))

    return {
        "content_intake_readiness": {
            "overall_status": "ready_for_Architect_input",
            "intake_surface": "Content_Production_Engine",
            "cohort": "August_2026_LinkedIn_posts",
            "persistence_mode": "bounded_VS_Code_repository_update",
            "automatic_repository_write": False,
            "controlled_experiments_active": len(active_experiments),
            "automated_ingestion_bridge_present": False,
            "checks_passed": len(passed),
            "check_names": passed,
            "checks_failed": [],
        }
    }


if __name__ == "__main__":
    run_cli(validate_content_intake_readiness, DEFAULT_ROOT)
