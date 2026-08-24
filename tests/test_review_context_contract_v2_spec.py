from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "specs" / "review_context_contract_v2.json"


def _load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def _serialized(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _permitted_domain_values(value: Any) -> set[str]:
    values: set[str] = set()
    if isinstance(value, dict):
        permitted = value.get("permitted_values")
        if isinstance(permitted, list):
            values.update(item for item in permitted if isinstance(item, str))
        for child in value.values():
            values.update(_permitted_domain_values(child))
    elif isinstance(value, list):
        for child in value:
            values.update(_permitted_domain_values(child))
    return values


def test_specification_parses_and_is_design_only():
    spec = _load_spec()

    assert spec["name"] == "review_context_contract"
    assert spec["version"] == "design-v2.1"
    assert spec["interface_type"] == "proposed_response_contract"
    assert spec["implementation_status"] == "not_implemented"
    assert spec["implementation_gate"]["endpoint_exists"] is False
    assert spec["implementation_gate"]["approved_for_runtime_implementation"] is False


def test_external_authority_and_execution_effects_are_none():
    spec = _load_spec()

    assert spec["authority_model"] == "non_authority"
    assert spec["authority_effect"] == "none"
    assert spec["execution_effect"] == "none"
    assert spec["proof_semantics"]["authority_effect"] == "none"


def test_legacy_authority_fields_are_absent_from_response_model():
    spec = _load_spec()
    response_text = _serialized(spec["response_model"])
    prohibited = set(spec["prohibited_external_fields"])

    required_exclusions = {
        "decision_status",
        "decision_admission_record",
        "permission_budget",
        "permission_budget_class",
        "adjusted_size",
        "recommended_action",
    }
    assert required_exclusions <= prohibited
    for field in prohibited:
        assert f'"{field}"' not in response_text


def test_prohibited_status_values_are_absent_from_response_domain_enums():
    spec = _load_spec()
    domain_values = _permitted_domain_values(spec["response_model"])

    for value in spec["prohibited_external_values"]:
        assert value not in domain_values


def test_response_uses_descriptive_context_objects():
    spec = _load_spec()
    response = spec["response_model"]
    required_fields = set(response["required_fields"])

    assert {
        "context_state",
        "source_state",
        "constraint_context",
        "temporal_context",
        "contradiction_context",
        "review_completeness",
        "chronology_context",
        "authority_handoff",
        "reproducibility",
        "boundary",
    } <= required_fields
    assert response["context_state"]["permitted_values"] == [
        "current",
        "uncertain",
        "stale",
        "superseded",
    ]
    assert response["source_state"]["permitted_values"] == [
        "complete",
        "partial",
        "conflicted",
        "unavailable",
    ]


def test_versioned_review_profile_is_required_in_request_response_and_proof():
    spec = _load_spec()
    request = spec["request_model"]
    response = spec["response_model"]
    profile = request["review_profile"]

    assert "review_profile" in request["required_fields"]
    assert profile["required_fields"] == [
        "profile_id",
        "profile_version",
        "profile_owner",
        "required_context_fields",
        "profile_hash",
    ]
    assert profile["defines_completeness_requirements"] is True
    assert profile["selection_authority"] == "institution_approved_configuration"
    assert profile["Nova_invents_institution_requirements"] is False
    assert (
        profile["profile_change_may_change_completeness_without_evidence_change"]
        is True
    )
    assert "review_profile_reference" in response["required_fields"]
    assert response["review_profile_reference"]["required_fields"] == [
        "profile_id",
        "profile_version",
        "profile_owner",
        "profile_hash",
    ]
    assert {
        "review_profile_identity",
        "review_profile_hash",
    } <= set(spec["proof_semantics"]["verifies"])


def test_review_completeness_is_profile_relative_not_policy_satisfaction():
    completeness = _load_spec()["response_model"]["review_completeness"]

    assert completeness["semantic_owner"] == "target_v2_contract"
    assert completeness["precedence"] == [
        "unavailable",
        "conflicted",
        "partial",
        "complete",
    ]
    assert completeness["profile_may_redefine_enum_meaning_or_precedence"] is False
    assert "institutional_policy_satisfied" in completeness["does_not_mean"]


def test_contradiction_visibility_maps_to_required_descriptive_context():
    spec = _load_spec()
    request = spec["request_model"]
    response = spec["response_model"]
    contradiction = response["contradiction_context"]

    assert "contradiction_visibility" in request["requested_context_values"]
    assert request["requested_context_mapping"]["contradiction_visibility"] == (
        "review_context_response.contradiction_context"
    )
    assert "contradiction_context" in response["required_fields"]
    assert contradiction["required_fields"] == [
        "source_conflicts",
        "constraint_conflicts",
        "temporal_conflicts",
        "chronology_conflicts",
        "unresolved_questions",
    ]
    assert contradiction["descriptive_only"] is True
    assert contradiction["Nova_selects_winning_source"] is False
    assert contradiction["Nova_resolves_policy_dispute"] is False
    assert contradiction["empty_list_proves_no_external_conflict"] is False


def test_record_source_type_is_exact_and_proof_preserves_segmentation():
    spec = _load_spec()
    response = spec["response_model"]
    source_type = response["record_source_type"]

    assert "record_source_type" in response["required_fields"]
    assert source_type["permitted_values"] == [
        "synthetic",
        "production_like",
        "live",
        "mixed",
    ]
    assert source_type["semantics"]["mixed"] == (
        "more_than_one_evidence_environment_class_is_represented"
    )
    assert source_type["production_like_may_be_represented_as_live"] is False
    assert source_type["mixed_source_packet_segmentation_level"] == (
        "field_or_source_reference"
    )
    assert source_type["proof_preserves_source_segmentation"] is True
    assert source_type["signature_upgrades_evidence"] is False
    assert {
        "record_source_type",
        "source_segmentation",
    } <= set(spec["proof_semantics"]["verifies"])


def test_prepared_action_reference_is_opaque_and_does_not_embed_payload():
    reference = _load_spec()["response_model"]["prepared_action_reference"]

    assert reference["required_fields"] == [
        "reference_id",
        "proposal_version_identity",
        "reference_type",
        "payload_embedded",
    ]
    assert reference["optional_fields"] == ["action_id"]
    assert reference["reference_type"] == "opaque_external_reference"
    assert reference["payload_embedded"] is False
    assert reference["semantics"]["action_origin"] == "external_to_Nova"
    assert reference["semantics"]["Nova_owns_action"] is False
    assert reference["semantics"]["full_action_payload_required_in_response"] is False
    assert reference["semantics"]["sensitive_action_data_embedded_by_default"] is False
    assert reference["semantics"]["reference_grants_execution_authority"] is False
    identity = reference["semantics"]["identity_semantics"]
    assert identity["action_and_proposal_identity_distinct"] is True
    assert identity["proposal_version_identity"]["source_genesis_machine_visible"] is True
    assert identity["proposal_version_identity"]["establishes_action_lineage"] is False
    proposal_identity = reference["proposal_version_identity"]
    assert proposal_identity["required_fields"] == ["value", "source_type"]
    assert proposal_identity["conditional_fields"]["when_source_type_is_Nova_derived_proposal_fingerprint"] == {
        "algorithm_qualification": "required",
        "material_scope": "canonical_prepared_action_material_only",
    }


def test_reproducibility_preserves_profile_and_source_segmentation():
    required = set(
        _load_spec()["response_model"]["reproducibility"]["required_fields"]
    )

    assert {
        "review_profile_id",
        "review_profile_version",
        "review_profile_hash",
        "record_source_type",
        "source_segmentation",
    } <= required


def test_local_authority_and_external_execution_owner_are_declared():
    handoff = _load_spec()["response_model"]["authority_handoff"]

    assert handoff["decision_owner"] == "local_institutional_authority"
    assert handoff["execution_owner"] == "external_system"
    assert handoff["Nova_authority_effect"] == "none"


def test_response_boundary_has_no_approval_authorization_or_execution_effect():
    boundary = _load_spec()["response_model"]["boundary"]

    assert boundary == {
        "approval_effect": "none",
        "authorization_effect": "none",
        "execution_effect": "none",
    }


def test_proof_verifies_context_integrity_not_permission():
    proof = _load_spec()["proof_semantics"]

    assert proof["proof_type"] == "review_context_integrity"
    assert {
        "packet_integrity",
        "schema_identity",
        "source_reference_integrity",
        "reproducibility_inputs",
    } <= set(proof["verifies"])
    assert {
        "approval",
        "authorization",
        "execution_permission",
    } <= set(proof["does_not_verify"])


def test_internal_classification_cannot_be_external_permission_or_sole_source():
    boundary = _load_spec()["internal_classification_boundary"]

    assert boundary["may_exist"] is True
    assert boundary["may_be_exposed_as_external_permission"] is False
    assert boundary["may_directly_determine_local_execution"] is False
    assert boundary["public_packet_may_be_derived_solely_from_legacy_status"] is False
    assert boundary["may_be_used_to_construct_descriptive_context"] == (
        "only_with_field_level_mapping_review"
    )


def test_billing_is_disabled_outcome_independent_and_non_authority():
    billing = _load_spec()["billing_semantics"]

    assert billing["initial_state"] == "disabled"
    assert billing["outcome_dependent"] is False
    assert billing["status_dependent"] is False
    assert billing["payment_receipt_authority_effect"] == "none"
    assert {
        "approval",
        "authorization",
        "admission",
        "permission",
        "favorable_status",
        "execution_entitlement",
        "transaction_clearance",
    } <= set(billing["prohibited_billable_objects"])


def test_valid_incomplete_and_conflicted_context_use_http_200():
    semantics = _load_spec()["http_semantics"]

    assert semantics["valid_context_response"] == 200
    assert semantics["incomplete_context"] == 200
    assert semantics["conflicted_context"] == 200
    assert semantics["stale_context"] == 200
    assert semantics["unavailable_source_context"]["status"] == 200
    assert semantics["domain_state_changes_HTTP_status"] is False


def test_x402_is_outside_initial_v2_implementation():
    boundary = _load_spec()["x402_boundary"]

    assert boundary["public_surface"] == "disabled"
    assert boundary["production_reopening"] == "not_authorized"
    assert boundary["v2_integration"] == "not_part_of_initial_implementation"
    assert boundary["payment_authority_effect"] == "none"
