from pathlib import Path

import yaml

from core.accepted_state_synchronization import (
    AUTHORITY_TRANSFER_ACTIVATION_PATH,
    PRIVATE_CANONICAL_REGISTRY_PATH,
    PRIVATE_CANONICAL_REPOSITORY,
    PUBLIC_PROJECTION_REPOSITORY,
    authority_transfer_activation,
    build_action_state,
    resolve_registry_source,
    synchronization_state,
)


def test_public_projection_activation_is_effective_and_exact() -> None:
    activation = authority_transfer_activation()

    assert activation["effective"] is True
    assert activation["status"] == "EFFECTIVE_REPOSITORY_VERIFIED"
    assert activation["canonical_repository"] == PRIVATE_CANONICAL_REPOSITORY
    assert activation["canonical_registry_path"] == PRIVATE_CANONICAL_REGISTRY_PATH
    assert activation["authorization_reference"] == (
        "ARCHITECT-AUTH-CANONICAL-TRANSFER-2026-08-28-B3FB1A8-F50BC42"
    )


def test_activation_marker_preserves_non_authorizations() -> None:
    marker = yaml.safe_load(Path(AUTHORITY_TRANSFER_ACTIVATION_PATH).read_text(encoding="utf-8"))

    assert marker["non_authorizations"] == {
        "public_runtime_deletion": False,
        "chronology": False,
        "Reflex_Memory_acceptance": False,
        "payment_or_settlement": False,
        "institutional_Gate_5": False,
        "production_runtime_change": False,
        "capital_movement": False,
    }
    assert marker["state_separation"] == {
        "repository_governance_surface_changed": True,
        "canonical_corporate_state_changed": True,
        "cross_agent_current_use_set_changed": False,
    }


def test_public_registry_cannot_make_current_corporate_accepted_state_claim() -> None:
    state = resolve_registry_source()

    assert state["source_resolution"]["remote_repository"] == PRIVATE_CANONICAL_REPOSITORY
    assert state["source_resolution"]["projection_repository"] == PUBLIC_PROJECTION_REPOSITORY
    assert state["registry_state"]["canonical_source_state"] == (
        "private_canonical_external_to_public_projection"
    )
    assert state["registry_state"]["authority_role"] == "historical_governed_projection_only"
    assert state["registry_usage"]["allowed"] == "bounded_historical_context_only"
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is False
    assert state["registry_ingestion"]["canonical_registry_loaded"] is False


def test_public_compatibility_surface_cannot_request_state_or_chronology_mutation() -> None:
    action = build_action_state()

    assert action["system_maintenance_action_required"] is False
    assert action["Architect_decision_required"] is False
    assert action["external_dependency_action_required"] is False
    assert action["assigned_to"] == []
    assert action["action_type"] == "none"
    assert action["blocking_state"] == "non_blocking"
    assert "nova-core" in action["rationale"]


def test_public_synchronization_state_is_historical_projection_only() -> None:
    state = synchronization_state()

    assert state["operating_state"] == "historical_projection_only"
    assert state["evidence_coverage"] == "bounded_historical_projection"
    assert state["repository"]["current_repo_movement_accepted"] is False
    assert state["accepted_state_registry"]["authority_role"] == (
        "historical_governed_projection_only"
    )
    assert state["accepted_state_registry"]["current_accepted_state_claim_allowed"] is False
    assert state["chronology"]["canonical_event_required"] is False
    assert state["chronology"]["authority_effect"] == "none"


def test_active_public_entry_surfaces_do_not_claim_corporate_authority() -> None:
    current_state = Path("CURRENT_STATE.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    start_here = Path("docs/start-here.md").read_text(encoding="utf-8")

    for text in (current_state, readme, start_here):
        assert "nova-infrastructure-systems/nova-core" in text
        assert "governed public" in text.lower() or "governed external projection" in text.lower()

    assert "transfer_status: PENDING_ARCHITECT_ACCEPTANCE" not in current_state
    assert "Read the authoritative current-state summary" not in readme
    assert "See the authoritative [Current State]" not in start_here
