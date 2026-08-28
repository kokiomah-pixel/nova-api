from __future__ import annotations

"""Accepted-state synchronization compatibility surface.

The legacy implementation is preserved verbatim in
``core.accepted_state_synchronization_legacy`` for historical fixtures and
pre-transfer reconstruction. After the explicit accepted-state authority
transfer, this module fails closed against treating the retained public
registry as current corporate accepted state.

This compatibility layer does not read the private repository directly and
cannot create accepted state, chronology, Reflex Memory, implementation
permission, production authority, payment authority, or capital authority.
"""

from pathlib import Path
from typing import Any, Mapping

import yaml

from core import accepted_state_synchronization_legacy as _legacy


# Preserve the historical module API, including constants used by older tests
# and bounded offline tooling. Projection-aware functions below intentionally
# override only the current-source interpretation.
for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)


AUTHORITY_TRANSFER_ACTIVATION_PATH = Path(
    "docs/governance/canonical-authority-transfer-activation-2026-08-28.yaml"
)
PUBLIC_PROJECTION_REPOSITORY = "nova-infrastructure-systems/sharpe-nova-os"
PRIVATE_CANONICAL_REPOSITORY = "nova-infrastructure-systems/nova-core"
PRIVATE_CANONICAL_REGISTRY_PATH = "governance/accepted-state/registry.yaml"


def authority_transfer_activation(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Resolve the already-authorized transfer marker without creating authority."""

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
            "authorization_reference": None,
        }

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    authority = payload.get("authority_state", {})
    evidence = payload.get("transfer_evidence", {})
    authorization = payload.get("authorization", {})
    effective = bool(
        payload.get("status") == "EFFECTIVE_REPOSITORY_VERIFIED"
        and authority.get("canonical_corporate_accepted_state_authority")
        == PRIVATE_CANONICAL_REPOSITORY
        and authority.get("canonical_private_registry_path")
        == PRIVATE_CANONICAL_REGISTRY_PATH
        and authority.get("public_repository_role")
        == "NON_AUTHORITATIVE_GOVERNED_PROJECTION"
        and authority.get("public_current_accepted_state_claim_use") == "prohibited"
        and evidence.get("private_effective_transfer_merge_commit")
        and evidence.get("public_projection_merge_commit")
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
        "private_effective_transfer_merge_commit": evidence.get(
            "private_effective_transfer_merge_commit"
        ),
        "private_completion_evidence_merge_commit": evidence.get(
            "private_completion_evidence_merge_commit"
        ),
        "public_projection_merge_commit": evidence.get("public_projection_merge_commit"),
        "authorization_reference": authorization.get("reference"),
    }


def resolve_registry_source(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    checkpoint_path: Path | None = None,
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    activation = authority_transfer_activation(repo_root)
    if not activation["effective"]:
        return _legacy.resolve_registry_source(
            repo_root,
            local_mirror_root=local_mirror_root,
            checkpoint_path=checkpoint_path,
            repository_state_override=repository_state_override,
        )

    historical = _legacy.resolve_registry_source(
        repo_root,
        local_mirror_root=local_mirror_root,
        checkpoint_path=checkpoint_path,
        repository_state_override=repository_state_override,
    )
    historical_registry_state = historical["registry_state"]
    selected_projection = historical_registry_state.get("selected_registry_path")
    if selected_projection is None and (repo_root / REGISTRY_PATH).exists():
        selected_projection = str(repo_root / REGISTRY_PATH)

    return {
        "source_resolution": {
            "local_runtime_root": historical["source_resolution"]["local_runtime_root"],
            "local_registry_absolute_path": historical["source_resolution"][
                "local_registry_absolute_path"
            ],
            "remote_repository": PRIVATE_CANONICAL_REPOSITORY,
            "remote_registry_commit": activation[
                "private_completion_evidence_merge_commit"
            ]
            or activation["private_effective_transfer_merge_commit"],
            "canonical_registry_path": PRIVATE_CANONICAL_REGISTRY_PATH,
            "projection_repository": PUBLIC_PROJECTION_REPOSITORY,
            "projection_registry_path": str(REGISTRY_PATH),
            "canonical_registry_standard": "private_repository_registry_after_explicit_transfer",
            "configured_registry_source": (
                f"{PRIVATE_CANONICAL_REPOSITORY}:{PRIVATE_CANONICAL_REGISTRY_PATH}"
            ),
            "source_selection_logic": (
                "require_private_canonical_registry_for_current_state; "
                "public_registry_is_historical_projection_only; "
                "do_not_substitute_public_checkout_or_mirror"
            ),
            "authority_transfer_effective": True,
            "authorization_reference": activation["authorization_reference"],
        },
        "repository_state": historical["repository_state"],
        "registry_operating_model": {
            "canonical_source": "private_repository_registry",
            "local_mirror_required": False,
            "read_mode": "historical_projection_only",
            "fallback_behavior": "bounded_public_projection_only",
            "local_mirror_authoritative": False,
        },
        "registry_state": {
            "canonical_source_state": "private_canonical_external_to_public_projection",
            "canonical_source_available": False,
            "canonical_commit": activation["private_completion_evidence_merge_commit"]
            or activation["private_effective_transfer_merge_commit"],
            "canonical_registry_path": PRIVATE_CANONICAL_REGISTRY_PATH,
            "selected_registry_path": selected_projection,
            "local_mirror_present": historical_registry_state.get(
                "local_mirror_present", False
            ),
            "local_mirror_commit": historical_registry_state.get("local_mirror_commit"),
            "local_mirror_in_sync": False,
            "mirror_lag_detected": False,
            "registry_schema_valid": historical_registry_state.get(
                "registry_schema_valid", False
            ),
            "registry_entry_count": historical_registry_state.get(
                "registry_entry_count", 0
            ),
            "authority_role": "historical_governed_projection_only",
        },
        "registry_ingestion": {
            "canonical_source_state": "private_canonical_external_to_public_projection",
            "checkout_commit": historical["registry_ingestion"].get("checkout_commit"),
            "canonical_main_commit": historical["registry_ingestion"].get(
                "canonical_main_commit"
            ),
            "checkout_is_canonical_main": historical["registry_ingestion"].get(
                "checkout_is_canonical_main", False
            ),
            "canonical_main_verified": historical["registry_ingestion"].get(
                "canonical_main_verified", False
            ),
            "canonical_registry_loaded": False,
            "canonical_source": "private_repository_registry",
            "canonical_repository": PRIVATE_CANONICAL_REPOSITORY,
            "canonical_commit": activation["private_completion_evidence_merge_commit"]
            or activation["private_effective_transfer_merge_commit"],
            "schema_valid": historical["registry_ingestion"].get(
                "registry_schema_valid", False
            ),
            "registry_schema_valid": historical["registry_ingestion"].get(
                "registry_schema_valid", False
            ),
            "current_accepted_state_claim_allowed": False,
            "projection_activation_effective": True,
            "mirror_status": "historical_only"
            if historical_registry_state.get("local_mirror_present")
            else "not_required",
            "checkpoint_status": historical["registry_ingestion"].get(
                "checkpoint_status", "missing"
            ),
            "contradictions_detected": False,
        },
        "registry_usage": {
            "allowed": "bounded_historical_context_only",
            "current_accepted_state_claim_allowed": False,
        },
        "accepted_state_delta": {
            "newly_accepted": "none",
            "stable_accepted_state": [],
            "checkpoint_path": historical["accepted_state_delta"]["checkpoint_path"],
        },
    }


def build_action_state(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not authority_transfer_activation(repo_root)["effective"]:
        return _legacy.build_action_state(
            repo_root,
            local_mirror_root=local_mirror_root,
            repository_state_override=repository_state_override,
        )
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


def synchronization_state(
    repo_root: Path = REPO_ROOT,
    *,
    local_mirror_root: Path | None = None,
    repository_state_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    activation = authority_transfer_activation(repo_root)
    if not activation["effective"]:
        return _legacy.synchronization_state(
            repo_root,
            local_mirror_root=local_mirror_root,
            repository_state_override=repository_state_override,
        )

    historical = _legacy.synchronization_state(
        repo_root,
        local_mirror_root=local_mirror_root,
        repository_state_override=repository_state_override,
    )
    resolution = resolve_registry_source(
        repo_root,
        local_mirror_root=local_mirror_root,
        repository_state_override=repository_state_override,
    )
    public_entry = _legacy.load_accepted_state_entry(repo_root)
    historical_repo = _legacy.classify_repo_movement_acceptance(public_entry)
    event_present = _legacy.chronology_event_present(repo_root)

    historical.update(
        {
            "operating_state": "historical_projection_only",
            "evidence_coverage": "bounded_historical_projection",
            "action_state": build_action_state(
                repo_root,
                local_mirror_root=local_mirror_root,
                repository_state_override=repository_state_override,
            ),
            "repository": {
                "current_repo_movement_reviewed": historical_repo[
                    "current_repo_movement_reviewed"
                ],
                "current_repo_movement_accepted": False,
                "accepted_remote_head": historical_repo["accepted_remote_head"],
                "rationale": (
                    "Public retained accepted-state material is historical governed "
                    "projection only; current corporate accepted-state authority "
                    "resides in nova-core."
                ),
            },
            "registry_source_resolution": resolution["source_resolution"],
            "repository_state": resolution["repository_state"],
            "registry_operating_model": resolution["registry_operating_model"],
            "registry_state": resolution["registry_state"],
            "Registry_ingestion": resolution["registry_ingestion"],
            "registry_usage": resolution["registry_usage"],
            "Accepted_state_delta": resolution["accepted_state_delta"],
            "authority_transfer": activation,
        }
    )
    historical["accepted_state_registry"].update(
        {
            "authority_role": "historical_governed_projection_only",
            "current_accepted_state_claim_allowed": False,
        }
    )
    historical["chronology"].update(
        {
            "canonical_event_required": False,
            "canonical_event_status": "historical_projection_preserved"
            if event_present
            else "historical_projection_absent",
            "authority_effect": "none",
        }
    )
    historical["durable_archive"]["authority_role"] = "historical_projection_evidence"
    return historical
