from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("agent_files/state/accepted-state-registry.yaml")
REGISTRY_CHECKPOINT_PATH = Path("agent_files/state/accepted-state-checkpoint.yaml")
ARCHIVE_RECORD_PATH = Path("archive/governance/architect-data-operations-stage-a-acceptance-2026-07-17.yaml")
CHRONOLOGY_PATH = Path("chronology/governance/governance-events.jsonl")
REGISTRY_SCHEMA_PATH = Path("schemas/accepted-state-registry.schema.json")
ACCEPTED_STATE_ID = "architect_data_operations_stage_a_policy_2026_07_17"
CHRONOLOGY_EVENT_ID = "GOV-20260717-STAGE-A-GOVERNANCE-INFRA-ACCEPTED"

ACTION_TYPES = {
    "none",
    "registry_synchronization",
    "chronology_write",
    "archive_write",
    "repo_review",
    "source_acquisition",
    "Architect_policy_decision",
    "contradiction_resolution",
    "external_validation",
}
BLOCKING_STATES = {
    "non_blocking",
    "blocks_state_acceptance",
    "blocks_Architect_decision",
    "blocks_external_claim",
    "blocks_production_claim",
}


def _read_yaml(path: Path) -> Mapping[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, Mapping) else {}


def _write_yaml_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(yaml.safe_dump(dict(payload), sort_keys=False), encoding="utf-8")
    temporary.replace(path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def sha256_path(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(repo_root: Path = REPO_ROOT) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _validate_registry_schema(path: Path, repo_root: Path = REPO_ROOT) -> bool:
    if not path.exists():
        return False
    registry = _read_yaml(path)
    schema_path = repo_root / REGISTRY_SCHEMA_PATH
    if not schema_path.exists():
        schema_path = REPO_ROOT / REGISTRY_SCHEMA_PATH
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return not list(validator.iter_errors(registry))


def _registry_entry_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    registry = _read_yaml(path)
    return [
        entry["accepted_state_id"]
        for entry in registry.get("entries", [])
        if isinstance(entry, Mapping) and "accepted_state_id" in entry
    ]


def _load_checkpoint(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    checkpoint = _read_yaml(path).get("accepted_state_checkpoint", {})
    return checkpoint if isinstance(checkpoint, Mapping) else {}


def accepted_state_delta(
    *,
    registry_path: Path,
    checkpoint_path: Path,
) -> dict[str, Any]:
    entry_ids = _registry_entry_ids(registry_path)
    acknowledged = set(_load_checkpoint(checkpoint_path).get("latest_acknowledged_entry_ids", []))
    newly_accepted = [entry_id for entry_id in entry_ids if entry_id not in acknowledged]
    return {
        "newly_accepted": newly_accepted,
        "stable_accepted_state": [entry_id for entry_id in entry_ids if entry_id in acknowledged],
        "checkpoint_path": str(checkpoint_path),
    }


def resolve_registry_source(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    checkpoint_path: Path | None = None,
) -> dict[str, Any]:
    canonical_path = repo_root / REGISTRY_PATH
    mirror_path = local_mirror_root / REGISTRY_PATH if local_mirror_root else None
    mirror_metadata_path = (
        local_mirror_root / "agent_files/state/accepted-state-registry.mirror-metadata.yaml"
        if local_mirror_root
        else None
    )
    checkpoint = checkpoint_path or repo_root / REGISTRY_CHECKPOINT_PATH

    canonical_available = canonical_path.exists()
    canonical_schema_valid = _validate_registry_schema(canonical_path, repo_root) if canonical_available else False
    canonical_commit = git_commit(repo_root) if canonical_available else None
    canonical_hash = sha256_path(canonical_path)

    mirror_present = bool(mirror_path and mirror_path.exists())
    mirror_schema_valid = _validate_registry_schema(mirror_path, repo_root) if mirror_present and mirror_path else False
    mirror_hash = sha256_path(mirror_path) if mirror_path else None
    mirror_metadata = _read_yaml(mirror_metadata_path).get("mirror_metadata", {}) if mirror_metadata_path and mirror_metadata_path.exists() else {}
    mirror_commit = mirror_metadata.get("canonical_commit")
    canonical_ids = _registry_entry_ids(canonical_path)
    mirror_ids = _registry_entry_ids(mirror_path) if mirror_path else []
    mirror_in_sync = bool(
        canonical_available
        and mirror_present
        and mirror_schema_valid
        and mirror_hash == canonical_hash
        and (not mirror_commit or mirror_commit == canonical_commit)
    )
    mirror_lag = bool(canonical_available and mirror_present and not mirror_in_sync)

    if canonical_available and canonical_schema_valid:
        selected_path = canonical_path
        registry_usage = {
            "allowed": "current_accepted_state",
            "current_accepted_state_claim_allowed": True,
        }
    elif mirror_present:
        selected_path = mirror_path
        registry_usage = {
            "allowed": "bounded_historical_context_only",
            "current_accepted_state_claim_allowed": False,
        }
    else:
        selected_path = None
        registry_usage = {
            "allowed": "source_unavailable",
            "current_accepted_state_claim_allowed": False,
        }

    delta = (
        accepted_state_delta(registry_path=canonical_path, checkpoint_path=checkpoint)
        if canonical_available and canonical_schema_valid
        else {"newly_accepted": [], "stable_accepted_state": [], "checkpoint_path": str(checkpoint)}
    )

    return {
        "source_resolution": {
            "local_runtime_root": str(repo_root.resolve()),
            "local_registry_absolute_path": str(canonical_path.resolve()),
            "remote_repository": "kokiomah-pixel/sharpe-nova-os",
            "remote_registry_commit": canonical_commit,
            "canonical_registry_standard": "repository_main_unless_governing_standard_designates_external_store",
            "configured_registry_source": "repository_checkout",
            "source_selection_logic": "prefer_valid_repository_registry; do_not_silently_fallback_to_stale_mirror; stale_mirror_is_historical_only",
        },
        "registry_operating_model": {
            "canonical_source": "repository_main",
            "local_mirror_required": False,
            "read_mode": "read_only",
            "fallback_behavior": "source_unavailable",
            "local_mirror_authoritative": False,
        },
        "registry_state": {
            "canonical_source_available": canonical_available and canonical_schema_valid,
            "canonical_commit": canonical_commit,
            "canonical_registry_path": str(canonical_path),
            "selected_registry_path": str(selected_path) if selected_path else None,
            "local_mirror_present": mirror_present,
            "local_mirror_commit": mirror_commit,
            "local_mirror_in_sync": mirror_in_sync,
            "mirror_lag_detected": mirror_lag,
            "registry_schema_valid": canonical_schema_valid if canonical_available else mirror_schema_valid,
            "registry_entry_count": len(canonical_ids if canonical_available and canonical_schema_valid else mirror_ids),
        },
        "registry_ingestion": {
            "canonical_registry_loaded": canonical_available and canonical_schema_valid,
            "canonical_source": "repository_main",
            "canonical_commit": canonical_commit,
            "schema_valid": canonical_schema_valid,
            "mirror_status": "not_required"
            if not mirror_present
            else ("in_sync" if mirror_in_sync else "lag_detected"),
            "contradictions_detected": False,
        },
        "registry_usage": registry_usage,
        "accepted_state_delta": {
            "newly_accepted": delta["newly_accepted"] or "none",
            "stable_accepted_state": delta["stable_accepted_state"],
            "checkpoint_path": delta["checkpoint_path"],
        },
    }


def refresh_local_mirror(
    *,
    canonical_registry_path: Path,
    mirror_registry_path: Path,
    metadata_path: Path,
    canonical_repository: str,
    canonical_commit: str,
    synchronized_at: str,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    if not _validate_registry_schema(canonical_registry_path, REPO_ROOT):
        return {
            "sync_status": "failed_schema_validation",
            "mirror_preserved": mirror_registry_path.exists(),
        }
    mirror_registry_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = mirror_registry_path.with_suffix(mirror_registry_path.suffix + ".tmp")
    temporary.write_bytes(canonical_registry_path.read_bytes())
    temporary.replace(mirror_registry_path)
    metadata = {
        "mirror_metadata": {
            "canonical_repository": canonical_repository,
            "canonical_commit": canonical_commit,
            "synchronized_at": synchronized_at,
            "registry_content_hash": sha256_path(mirror_registry_path),
            "schema_version": schema_version,
            "sync_status": "in_sync",
        }
    }
    _write_yaml_atomic(metadata_path, metadata)
    return {
        "sync_status": "in_sync",
        "mirror_preserved": False,
        "registry_content_hash": metadata["mirror_metadata"]["registry_content_hash"],
    }


def load_accepted_state_entry(repo_root: Path = REPO_ROOT) -> dict[str, Any] | None:
    path = repo_root / REGISTRY_PATH
    if not path.exists():
        return None
    registry = _read_yaml(path)
    for entry in registry.get("entries", []):
        if isinstance(entry, Mapping) and entry.get("accepted_state_id") == ACCEPTED_STATE_ID:
            return dict(entry)
    return None


def chronology_event_present(repo_root: Path = REPO_ROOT) -> bool:
    return any(
        event.get("event_id") == CHRONOLOGY_EVENT_ID
        for event in _read_jsonl(repo_root / CHRONOLOGY_PATH)
    )


def load_archive_record(repo_root: Path = REPO_ROOT) -> dict[str, Any] | None:
    path = repo_root / ARCHIVE_RECORD_PATH
    if not path.exists():
        return None
    return dict(_read_yaml(path))


def classify_repo_movement_acceptance(entry: Mapping[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {
            "current_repo_movement_reviewed": False,
            "current_repo_movement_accepted": False,
            "accepted_remote_head": None,
            "rationale": "No accepted-state registry entry was found.",
        }
    review = entry.get("review_authority", {})
    reviewed = bool(review.get("Architect_reviewed") or review.get("CCO_reviewed"))
    accepted = (
        reviewed
        and entry.get("classification", {}).get("status") == "accepted"
        and entry.get("contradiction_state") == "none"
        and entry.get("classification", {}).get("scope") == "bounded_stage_a"
    )
    return {
        "current_repo_movement_reviewed": reviewed,
        "current_repo_movement_accepted": accepted,
        "accepted_remote_head": entry.get("source", {})
        .get("merge_commits", {})
        .get("runtime_evidence_policy"),
        "rationale": "Reviewed repository movement has an accepted bounded claim boundary."
        if accepted
        else "Repository movement is not accepted solely because it is merged.",
    }


def archive_external_dependency_required(record: Mapping[str, Any] | None) -> bool:
    if not record:
        return True
    completion = record.get("completion", {})
    return completion.get("status") in {
        "pending_external_write",
        "destination_unavailable",
        "written_receipt_pending",
    }


def build_action_state(repo_root: Path = REPO_ROOT, *, local_mirror_root: Path | None = None) -> dict[str, Any]:
    registry_resolution = resolve_registry_source(repo_root, local_mirror_root=local_mirror_root)
    registry_state = registry_resolution["registry_state"]
    registry_usage = registry_resolution["registry_usage"]
    entry = load_accepted_state_entry(repo_root)
    event_written = chronology_event_present(repo_root)
    archive_record = load_archive_record(repo_root)
    archive_status = (
        archive_record.get("completion", {}).get("status") if archive_record else "pending_external_write"
    )

    assigned_to: list[str] = []
    action_type = "none"
    system_required = False
    external_required = False
    rationale: list[str] = []

    if registry_state["mirror_lag_detected"]:
        system_required = True
        action_type = "registry_synchronization"
        assigned_to.append("accepted_state_registry_writer")
        rationale.append("Non-authoritative accepted-state mirror lags the canonical repository registry.")
    if not registry_usage["current_accepted_state_claim_allowed"]:
        system_required = True
        action_type = "source_acquisition" if action_type == "none" else action_type
        assigned_to.append("accepted_state_registry_reader")
        rationale.append("Canonical accepted-state registry source is unavailable for current-state claims.")
    if not entry:
        system_required = True
        action_type = "registry_synchronization"
        assigned_to.append("accepted_state_registry_writer")
        rationale.append("Reviewed repository movement has not been written to the accepted-state registry.")
    if not event_written:
        system_required = True
        if action_type == "none":
            action_type = "chronology_write"
        assigned_to.append("Chronology_Agent")
        rationale.append("Canonical governance-infrastructure chronology event is not written.")
    if archive_status != "completed_and_verified":
        system_required = True
        if action_type == "none":
            action_type = "archive_write"
        external_required = archive_external_dependency_required(archive_record)
        assigned_to.append("archive_writer")
        rationale.append("Durable archive completion is not externally verified.")

    if not system_required:
        rationale.append("Stage_A_governance_state_synchronized_and_archive_receipt_verified")

    return {
        "system_maintenance_action_required": system_required,
        "Architect_decision_required": False,
        "external_dependency_action_required": external_required,
        "assigned_to": sorted(set(assigned_to)),
        "action_type": action_type,
        "blocking_state": "non_blocking"
        if not external_required
        else "blocks_external_claim",
        "rationale": " ".join(rationale),
    }


def synchronization_state(repo_root: Path = REPO_ROOT, *, local_mirror_root: Path | None = None) -> dict[str, Any]:
    registry_resolution = resolve_registry_source(repo_root, local_mirror_root=local_mirror_root)
    entry = load_accepted_state_entry(repo_root)
    archive_record = load_archive_record(repo_root)
    event_written = chronology_event_present(repo_root)
    archive_completion = archive_record.get("completion", {}) if archive_record else {}
    repo_movement = classify_repo_movement_acceptance(entry)
    return {
        "operating_state": "bounded_infrastructure_accepted"
        if repo_movement["current_repo_movement_accepted"]
        else "source_incomplete",
        "evidence_coverage": "source_incomplete",
        "contradiction_detected": False,
        "action_state": build_action_state(repo_root, local_mirror_root=local_mirror_root),
        "repository": repo_movement,
        "accepted_state_registry": {
            "path": str(REGISTRY_PATH),
            "updated": entry is not None,
            "accepted_entry_id": ACCEPTED_STATE_ID if entry else None,
            "schema_valid": registry_resolution["registry_state"]["registry_schema_valid"],
            "duplicate_entry_created": False,
        },
        "registry_source_resolution": registry_resolution["source_resolution"],
        "registry_operating_model": registry_resolution["registry_operating_model"],
        "registry_state": registry_resolution["registry_state"],
        "Registry_ingestion": registry_resolution["registry_ingestion"],
        "registry_usage": registry_resolution["registry_usage"],
        "Accepted_state_delta": registry_resolution["accepted_state_delta"],
        "chronology": {
            "store": str(CHRONOLOGY_PATH),
            "canonical_event_required": not event_written,
            "canonical_event_status": "written" if event_written else "pending",
            "event_id": CHRONOLOGY_EVENT_ID,
        },
        "durable_archive": {
            "record_path": str(ARCHIVE_RECORD_PATH),
            "status": archive_completion.get("status", "pending_external_write"),
            "archive_reference": archive_completion.get("receipt_or_reference"),
            "verified": archive_completion.get("status") == "completed_and_verified",
        },
        "runtime_evidence": {
            "Stage_A_policy_and_ingestion_path": "validated",
            "Stage_A_live_operation": "not_established",
            "Stage_B": "locked",
            "production_health_claim": "prohibited",
        },
    }
