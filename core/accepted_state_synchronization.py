from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("agent_files/state/accepted-state-registry.yaml")
ARCHIVE_RECORD_PATH = Path("archive/governance/architect-data-operations-stage-a-acceptance-2026-07-17.yaml")
CHRONOLOGY_PATH = Path("chronology/governance/governance-events.jsonl")
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


def build_action_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
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
        rationale.append("Registry, chronology, and local archive record are synchronized.")

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


def synchronization_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
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
        "action_state": build_action_state(repo_root),
        "repository": repo_movement,
        "accepted_state_registry": {
            "path": str(REGISTRY_PATH),
            "updated": entry is not None,
            "accepted_entry_id": ACCEPTED_STATE_ID if entry else None,
            "schema_valid": entry is not None,
            "duplicate_entry_created": False,
        },
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
