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
AUTHORITY_TRANSFER_ACTIVATION_PATH = Path(
    "docs/governance/canonical-authority-transfer-activation-2026-08-28.yaml"
)
PUBLIC_PROJECTION_REPOSITORY = "nova-infrastructure-systems/sharpe-nova-os"
PRIVATE_CANONICAL_REPOSITORY = "nova-infrastructure-systems/nova-core"
PRIVATE_CANONICAL_REGISTRY_PATH = "governance/accepted-state/registry.yaml"
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


def _read_yaml_text(text: str) -> Mapping[str, Any]:
    payload = yaml.safe_load(text)
    return payload if isinstance(payload, Mapping) else {}


def _read_yaml(path: Path) -> Mapping[str, Any]:
    return _read_yaml_text(path.read_text(encoding="utf-8"))


def _write_yaml_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(yaml.safe_dump(dict(payload), sort_keys=False), encoding="utf-8")
    temporary.replace(path)


def authority_transfer_activation(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Resolve the public projection activation without creating authority.

    The activation marker records an already-effected, separately authorized
    repository transition. Its presence only changes how this public
    compatibility module may interpret retained public accepted-state files.
    """

    path = repo_root / AUTHORITY_TRANSFER_ACTIVATION_PATH
    if not path.exists():
        return {
            "effective": False,
            "status": "not_present",
            "canonical_repository": PUBLIC_PROJECTION_REPOSITORY,
            "canonical_registry_path": str(REGISTRY_PATH),
            "private_effective_transfer_merge_commit": None,
            "private_completion_evidence_merge_commit": None,
            "public_projection_merge_commit": None,
        }

    payload = _read_yaml(path)
    authority_state = payload.get("authority_state", {})
    transfer_evidence = payload.get("transfer_evidence", {})
    if not isinstance(authority_state, Mapping):
        authority_state = {}
    if not isinstance(transfer_evidence, Mapping):
        transfer_evidence = {}

    effective = bool(
        payload.get("status") == "EFFECTIVE_REPOSITORY_VERIFIED"
        and authority_state.get("canonical_corporate_accepted_state_authority")
        == PRIVATE_CANONICAL_REPOSITORY
        and authority_state.get("canonical_private_registry_path")
        == PRIVATE_CANONICAL_REGISTRY_PATH
        and authority_state.get("public_repository_role")
        == "NON_AUTHORITATIVE_GOVERNED_PROJECTION"
        and authority_state.get("public_current_accepted_state_claim_use") == "prohibited"
        and transfer_evidence.get("private_effective_transfer_merge_commit")
        and transfer_evidence.get("public_projection_merge_commit")
    )

    return {
        "effective": effective,
        "status": payload.get("status"),
        "canonical_repository": PRIVATE_CANONICAL_REPOSITORY
        if effective
        else PUBLIC_PROJECTION_REPOSITORY,
        "canonical_registry_path": PRIVATE_CANONICAL_REGISTRY_PATH
        if effective
        else str(REGISTRY_PATH),
        "private_effective_transfer_merge_commit": transfer_evidence.get(
            "private_effective_transfer_merge_commit"
        ),
        "private_completion_evidence_merge_commit": transfer_evidence.get(
            "private_completion_evidence_merge_commit"
        ),
        "public_projection_merge_commit": transfer_evidence.get(
            "public_projection_merge_commit"
        ),
        "authorization_reference": payload.get("authorization", {}).get("reference")
        if isinstance(payload.get("authorization", {}), Mapping)
        else None,
    }


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


def sha256_text(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def git_ref_commit(repo_root: Path = REPO_ROOT, ref: str = "HEAD") -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def git_commit(repo_root: Path = REPO_ROOT) -> str | None:
    return git_ref_commit(repo_root, "HEAD")


def git_file_text(repo_root: Path, ref: str, path: Path) -> str | None:
    completed = _run_git(repo_root, ["show", f"{ref}:{path.as_posix()}"])
    if completed.returncode != 0:
        return None
    return completed.stdout


def resolve_repository_state(
    repo_root: Path = REPO_ROOT,
    *,
    override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if override is not None:
        checkout_commit = override.get("checkout_commit")
        canonical_main_commit = override.get("canonical_main_commit")
        canonical_main_verified = bool(override.get("canonical_main_verified"))
        return {
            "checkout_commit": checkout_commit,
            "canonical_main_commit": canonical_main_commit if canonical_main_verified else None,
            "checkout_is_canonical_main": bool(
                checkout_commit and canonical_main_commit and checkout_commit == canonical_main_commit
            ),
            "canonical_main_verified": canonical_main_verified,
        }

    checkout_commit = git_ref_commit(repo_root, "HEAD")
    canonical_main_commit = git_ref_commit(repo_root, "origin/main")
    canonical_main_verified = canonical_main_commit is not None
    return {
        "checkout_commit": checkout_commit,
        "canonical_main_commit": canonical_main_commit if canonical_main_verified else None,
        "checkout_is_canonical_main": bool(
            checkout_commit and canonical_main_commit and checkout_commit == canonical_main_commit
        ),
        "canonical_main_verified": canonical_main_verified,
    }


def _registry_schema(repo_root: Path = REPO_ROOT) -> Mapping[str, Any]:
    schema_path = repo_root / REGISTRY_SCHEMA_PATH
    if not schema_path.exists():
        schema_path = REPO_ROOT / REGISTRY_SCHEMA_PATH
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate_registry_payload(registry: Mapping[str, Any], repo_root: Path = REPO_ROOT) -> bool:
    schema = _registry_schema(repo_root)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return not list(validator.iter_errors(registry))


def _validate_registry_schema(path: Path, repo_root: Path = REPO_ROOT) -> bool:
    if not path.exists():
        return False
    return _validate_registry_payload(_read_yaml(path), repo_root)


def _registry_entry_ids_from_registry(registry: Mapping[str, Any]) -> list[str]:
    return [
        entry["accepted_state_id"]
        for entry in registry.get("entries", [])
        if isinstance(entry, Mapping) and "accepted_state_id" in entry
    ]


def _registry_entry_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    return _registry_entry_ids_from_registry(_read_yaml(path))


def _registry_from_text(text: str | None) -> Mapping[str, Any] | None:
    if text is None:
        return None
    registry = _read_yaml_text(text)
    return registry if registry else None


def _accepted_state_entry_from_registry(registry: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if registry is None:
        return None
    for entry in registry.get("entries", []):
        if isinstance(entry, Mapping) and entry.get("accepted_state_id") == ACCEPTED_STATE_ID:
            return dict(entry)
    return None


def _canonical_registry_for_state(
    repo_root: Path,
    repository_state: Mapping[str, Any],
    *,
    repository_state_override: Mapping[str, Any] | None = None,
) -> Mapping[str, Any] | None:
    if authority_transfer_activation(repo_root)["effective"]:
        return None
    if not repository_state.get("canonical_main_verified"):
        return None
    text = (
        (repo_root / REGISTRY_PATH).read_text(encoding="utf-8")
        if repository_state_override is not None and (repo_root / REGISTRY_PATH).exists()
        else git_file_text(repo_root, "origin/main", REGISTRY_PATH)
    )
    registry = _registry_from_text(text)
    if registry is None or not _validate_registry_payload(registry, repo_root):
        return None
    return registry


def _load_checkpoint(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    checkpoint = _read_yaml(path).get("accepted_state_checkpoint", {})
    return checkpoint if isinstance(checkpoint, Mapping) else {}


def accepted_state_delta(
    *,
    registry_path: Path | None = None,
    registry: Mapping[str, Any] | None = None,
    checkpoint_path: Path,
) -> dict[str, Any]:
    entry_ids = _registry_entry_ids_from_registry(registry) if registry is not None else _registry_entry_ids(registry_path)  # type: ignore[arg-type]
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
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    checkout_registry_path = repo_root / REGISTRY_PATH
    mirror_path = local_mirror_root / REGISTRY_PATH if local_mirror_root else None
    mirror_metadata_path = (
        local_mirror_root / "agent_files/state/accepted-state-registry.mirror-metadata.yaml"
        if local_mirror_root
        else None
    )
    checkpoint = checkpoint_path or repo_root / REGISTRY_CHECKPOINT_PATH
    repository_state = resolve_repository_state(repo_root, override=repository_state_override)
    checkout_commit = repository_state["checkout_commit"]
    canonical_main_commit = repository_state["canonical_main_commit"]
    canonical_main_verified = repository_state["canonical_main_verified"]
    checkout_is_canonical_main = repository_state["checkout_is_canonical_main"]
    activation = authority_transfer_activation(repo_root)
    projection_effective = bool(activation["effective"])

    checkout_available = checkout_registry_path.exists()
    checkout_schema_valid = _validate_registry_schema(checkout_registry_path, repo_root) if checkout_available else False
    checkout_hash = sha256_path(checkout_registry_path)

    if projection_effective:
        canonical_text = None
        canonical_registry = None
        canonical_schema_valid = False
        canonical_hash = None
        canonical_available = False
    else:
        canonical_text = (
            checkout_registry_path.read_text(encoding="utf-8")
            if canonical_main_verified and repository_state_override is not None and checkout_available
            else git_file_text(repo_root, "origin/main", REGISTRY_PATH)
            if canonical_main_verified
            else None
        )
        canonical_registry = _registry_from_text(canonical_text)
        canonical_schema_valid = bool(
            canonical_registry is not None and _validate_registry_payload(canonical_registry, repo_root)
        )
        canonical_hash = sha256_text(canonical_text)
        canonical_available = canonical_main_verified and canonical_schema_valid

    mirror_present = bool(mirror_path and mirror_path.exists())
    mirror_schema_valid = _validate_registry_schema(mirror_path, repo_root) if mirror_present and mirror_path else False
    mirror_hash = sha256_path(mirror_path) if mirror_path else None
    mirror_metadata = _read_yaml(mirror_metadata_path).get("mirror_metadata", {}) if mirror_metadata_path and mirror_metadata_path.exists() else {}
    mirror_commit = mirror_metadata.get("canonical_commit")
    canonical_ids = (
        _registry_entry_ids_from_registry(canonical_registry)
        if canonical_registry is not None
        else []
    )
    projection_ids = _registry_entry_ids(checkout_registry_path) if checkout_available else []
    mirror_ids = _registry_entry_ids(mirror_path) if mirror_path else []

    if projection_effective:
        mirror_in_sync = False
        mirror_lag = False
    else:
        mirror_in_sync = bool(
            canonical_available
            and mirror_present
            and mirror_schema_valid
            and mirror_hash == canonical_hash
            and (not mirror_commit or mirror_commit == canonical_main_commit)
        )
        mirror_lag = bool(canonical_available and mirror_present and not mirror_in_sync)

    if projection_effective:
        canonical_source_state = "private_canonical_external_to_public_projection"
        selected_path = (
            checkout_registry_path
            if checkout_available and checkout_schema_valid
            else mirror_path
            if mirror_present and mirror_schema_valid
            else None
        )
        registry_usage = {
            "allowed": "bounded_historical_context_only",
            "current_accepted_state_claim_allowed": False,
        }
    elif canonical_available:
        canonical_source_state = "verified_repository_main"
        selected_path = checkout_registry_path
        registry_usage = {
            "allowed": "current_accepted_state",
            "current_accepted_state_claim_allowed": True,
        }
    elif checkout_available and checkout_schema_valid:
        canonical_source_state = "unverified_repository_checkout"
        selected_path = checkout_registry_path
        registry_usage = {
            "allowed": "bounded_checkout_context",
            "current_accepted_state_claim_allowed": False,
        }
    elif mirror_present:
        canonical_source_state = "non_authoritative_local_mirror"
        selected_path = mirror_path
        registry_usage = {
            "allowed": "bounded_historical_context_only",
            "current_accepted_state_claim_allowed": False,
        }
    else:
        canonical_source_state = "source_unavailable"
        selected_path = None
        registry_usage = {
            "allowed": "source_unavailable",
            "current_accepted_state_claim_allowed": False,
        }

    delta = (
        {"newly_accepted": [], "stable_accepted_state": [], "checkpoint_path": str(checkpoint)}
        if projection_effective
        else accepted_state_delta(registry=canonical_registry, checkpoint_path=checkpoint)
        if canonical_available and canonical_registry is not None
        else {"newly_accepted": [], "stable_accepted_state": [], "checkpoint_path": str(checkpoint)}
    )

    canonical_repository = (
        PRIVATE_CANONICAL_REPOSITORY if projection_effective else PUBLIC_PROJECTION_REPOSITORY
    )
    canonical_registry_path = (
        PRIVATE_CANONICAL_REGISTRY_PATH if projection_effective else str(checkout_registry_path)
    )
    canonical_commit = (
        activation["private_completion_evidence_merge_commit"]
        or activation["private_effective_transfer_merge_commit"]
        if projection_effective
        else canonical_main_commit
    )

    return {
        "source_resolution": {
            "local_runtime_root": str(repo_root.resolve()),
            "local_registry_absolute_path": str(checkout_registry_path.resolve()),
            "remote_repository": canonical_repository,
            "remote_registry_commit": canonical_commit,
            "canonical_registry_path": canonical_registry_path,
            "projection_repository": PUBLIC_PROJECTION_REPOSITORY,
            "projection_registry_path": str(REGISTRY_PATH),
            "canonical_registry_standard": "private_repository_registry_after_explicit_transfer"
            if projection_effective
            else "repository_main_unless_governing_standard_designates_external_store",
            "configured_registry_source": (
                f"{PRIVATE_CANONICAL_REPOSITORY}:{PRIVATE_CANONICAL_REGISTRY_PATH}"
                if projection_effective
                else "origin/main"
                if canonical_available
                else "repository_checkout"
            ),
            "source_selection_logic": (
                "require_private_canonical_registry_for_current_state; public_registry_is_historical_projection_only; do_not_substitute_public_checkout_or_mirror"
                if projection_effective
                else "prefer_verified_origin_main_registry; feature_branch_checkout_is_not_canonical_main; stale_mirror_is_historical_only"
            ),
            "authority_transfer_effective": projection_effective,
            "authorization_reference": activation.get("authorization_reference"),
        },
        "repository_state": repository_state,
        "registry_operating_model": {
            "canonical_source": "private_repository_registry"
            if projection_effective
            else "repository_main",
            "local_mirror_required": False,
            "read_mode": "historical_projection_only"
            if projection_effective
            else "read_only",
            "fallback_behavior": "bounded_public_projection_only"
            if projection_effective
            else "source_unavailable",
            "local_mirror_authoritative": False,
        },
        "registry_state": {
            "canonical_source_state": canonical_source_state,
            "canonical_source_available": canonical_available,
            "canonical_commit": canonical_commit,
            "canonical_registry_path": canonical_registry_path,
            "selected_registry_path": str(selected_path) if selected_path else None,
            "projection_registry_path": str(checkout_registry_path),
            "projection_registry_content_hash": checkout_hash,
            "local_mirror_present": mirror_present,
            "local_mirror_commit": mirror_commit,
            "local_mirror_in_sync": mirror_in_sync,
            "mirror_lag_detected": mirror_lag,
            "registry_schema_valid": (
                checkout_schema_valid
                if projection_effective and checkout_available
                else canonical_schema_valid
                if canonical_available
                else checkout_schema_valid
                if checkout_available
                else mirror_schema_valid
            ),
            "registry_entry_count": (
                len(projection_ids)
                if projection_effective
                else len(canonical_ids if canonical_available and canonical_registry is not None else mirror_ids)
            ),
            "authority_role": "historical_governed_projection_only"
            if projection_effective
            else "candidate_current_source",
        },
        "registry_ingestion": {
            "canonical_source_state": canonical_source_state,
            "checkout_commit": checkout_commit,
            "canonical_main_commit": canonical_main_commit,
            "checkout_is_canonical_main": checkout_is_canonical_main,
            "canonical_main_verified": canonical_main_verified,
            "canonical_registry_loaded": canonical_available,
            "canonical_source": "private_repository_registry"
            if projection_effective
            else "repository_main",
            "canonical_repository": canonical_repository,
            "canonical_commit": canonical_commit,
            "schema_valid": (
                checkout_schema_valid
                if projection_effective
                else canonical_schema_valid
                if canonical_available
                else checkout_schema_valid
            ),
            "registry_schema_valid": (
                checkout_schema_valid
                if projection_effective
                else canonical_schema_valid
                if canonical_available
                else checkout_schema_valid
            ),
            "current_accepted_state_claim_allowed": registry_usage[
                "current_accepted_state_claim_allowed"
            ],
            "projection_activation_effective": projection_effective,
            "mirror_status": "historical_only"
            if projection_effective and mirror_present
            else "not_required"
            if not mirror_present
            else ("in_sync" if mirror_in_sync else "lag_detected"),
            "checkpoint_status": "available" if checkpoint.exists() else "missing",
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


def advance_accepted_state_checkpoint(
    *,
    registry: Mapping[str, Any],
    checkpoint_path: Path,
    canonical_main_commit: str | None,
    canonical_main_verified: bool,
    observed_at: str,
    successful_daily_run: bool,
    acknowledge_entry_ids: list[str] | None = None,
) -> dict[str, Any]:
    if not successful_daily_run:
        return {"advanced": False, "status": "failed_daily_run_does_not_advance"}
    if not canonical_main_verified or not canonical_main_commit:
        return {"advanced": False, "status": "canonical_main_not_verified"}
    if not _validate_registry_payload(registry, REPO_ROOT):
        return {"advanced": False, "status": "registry_schema_invalid"}

    registry_ids = set(_registry_entry_ids_from_registry(registry))
    requested_ids = set(acknowledge_entry_ids or registry_ids)
    unknown = sorted(requested_ids - registry_ids)
    if unknown:
        raise ValueError(f"Checkpoint cannot acknowledge unknown accepted_state_id: {','.join(unknown)}")

    existing = _load_checkpoint(checkpoint_path)
    acknowledged = sorted(set(existing.get("latest_acknowledged_entry_ids", [])) | requested_ids)
    payload = {
        "accepted_state_checkpoint": {
            "schema_version": "1.0.0",
            "checkpoint_type": "observation_cursor",
            "storage_model": {
                "committed_file_role": "bootstrap_or_fixture",
                "runtime_checkpoint_role": "mutable_observation_cursor",
                "runtime_checkpoint_authoritative": False,
            },
            "checkpoint_rules": {
                "authority_effect": "none",
                "execution_effect": "none",
                "independent_governance_claims": False,
                "may_acknowledge_only_ids_present_in_verified_canonical_registry": True,
                "advancement_requires_successful_daily_run": True,
                "advancement_occurs_after_brief_generation": True,
                "failed_run_does_not_advance": True,
            },
            "canonical_registry_commit": canonical_main_commit,
            "latest_acknowledged_entry_ids": acknowledged,
            "observed_at": observed_at,
            "authority_effect": "none",
            "execution_effect": "none",
            "independent_governance_claims": False,
        }
    }
    _write_yaml_atomic(checkpoint_path, payload)
    return {
        "advanced": True,
        "status": "advanced",
        "acknowledged_entry_ids": acknowledged,
        "canonical_registry_commit": canonical_main_commit,
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


def build_action_state(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    activation = authority_transfer_activation(repo_root)
    if activation["effective"]:
        return {
            "system_maintenance_action_required": False,
            "Architect_decision_required": False,
            "external_dependency_action_required": False,
            "assigned_to": [],
            "action_type": "none",
            "blocking_state": "non_blocking",
            "rationale": (
                "Public repository is a non-authoritative governed projection; "
                "current accepted-state maintenance belongs to nova-core and this "
                "compatibility surface cannot request accepted-state or chronology mutation."
            ),
        }

    registry_resolution = resolve_registry_source(
        repo_root,
        local_mirror_root=local_mirror_root,
        repository_state_override=repository_state_override,
    )
    registry_state = registry_resolution["registry_state"]
    registry_usage = registry_resolution["registry_usage"]
    canonical_registry = _canonical_registry_for_state(
        repo_root,
        registry_resolution["repository_state"],
        repository_state_override=repository_state_override,
    )
    entry = _accepted_state_entry_from_registry(canonical_registry)
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


def synchronization_state(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    activation = authority_transfer_activation(repo_root)
    projection_effective = bool(activation["effective"])
    registry_resolution = resolve_registry_source(
        repo_root,
        local_mirror_root=local_mirror_root,
        repository_state_override=repository_state_override,
    )
    canonical_registry = _canonical_registry_for_state(
        repo_root,
        registry_resolution["repository_state"],
        repository_state_override=repository_state_override,
    )
    entry = _accepted_state_entry_from_registry(canonical_registry)
    projection_entry = load_accepted_state_entry(repo_root)
    archive_record = load_archive_record(repo_root)
    event_written = chronology_event_present(repo_root)
    archive_completion = archive_record.get("completion", {}) if archive_record else {}
    repo_movement = classify_repo_movement_acceptance(entry)

    if projection_effective:
        historical = classify_repo_movement_acceptance(projection_entry)
        repo_movement = {
            "current_repo_movement_reviewed": historical["current_repo_movement_reviewed"],
            "current_repo_movement_accepted": False,
            "accepted_remote_head": historical["accepted_remote_head"],
            "rationale": (
                "Public retained accepted-state material is historical governed projection only; "
                "current corporate accepted-state authority resides in nova-core."
            ),
        }

    projected_entry_present = projection_entry is not None if projection_effective else entry is not None

    return {
        "operating_state": "historical_projection_only"
        if projection_effective
        else "bounded_infrastructure_accepted"
        if repo_movement["current_repo_movement_accepted"]
        else "source_incomplete",
        "evidence_coverage": "bounded_historical_projection"
        if projection_effective
        else "source_incomplete",
        "contradiction_detected": False,
        "action_state": build_action_state(
            repo_root,
            local_mirror_root=local_mirror_root,
            repository_state_override=repository_state_override,
        ),
        "repository": repo_movement,
        "accepted_state_registry": {
            "path": str(REGISTRY_PATH),
            "updated": projected_entry_present,
            "accepted_entry_id": ACCEPTED_STATE_ID if projected_entry_present else None,
            "schema_valid": registry_resolution["registry_state"]["registry_schema_valid"],
            "duplicate_entry_created": False,
            "authority_role": "historical_governed_projection_only"
            if projection_effective
            else "repository_registry",
            "current_accepted_state_claim_allowed": registry_resolution["registry_usage"][
                "current_accepted_state_claim_allowed"
            ],
        },
        "registry_source_resolution": registry_resolution["source_resolution"],
        "repository_state": registry_resolution["repository_state"],
        "registry_operating_model": registry_resolution["registry_operating_model"],
        "registry_state": registry_resolution["registry_state"],
        "Registry_ingestion": registry_resolution["registry_ingestion"],
        "registry_usage": registry_resolution["registry_usage"],
        "Accepted_state_delta": registry_resolution["accepted_state_delta"],
        "chronology": {
            "store": str(CHRONOLOGY_PATH),
            "canonical_event_required": False if projection_effective else not event_written,
            "canonical_event_status": "historical_projection_preserved"
            if projection_effective and event_written
            else "historical_projection_absent"
            if projection_effective
            else "written"
            if event_written
            else "pending",
            "event_id": CHRONOLOGY_EVENT_ID,
            "authority_effect": "none",
        },
        "durable_archive": {
            "record_path": str(ARCHIVE_RECORD_PATH),
            "status": archive_completion.get("status", "pending_external_write"),
            "archive_reference": archive_completion.get("receipt_or_reference"),
            "verified": archive_completion.get("status") == "completed_and_verified",
            "authority_role": "historical_projection_evidence"
            if projection_effective
            else "governed_archive_evidence",
        },
        "runtime_evidence": {
            "Stage_A_policy_and_ingestion_path": "validated",
            "Stage_A_live_operation": "not_established",
            "Stage_B": "locked",
            "production_health_claim": "prohibited",
        },
        "authority_transfer": activation,
    }
