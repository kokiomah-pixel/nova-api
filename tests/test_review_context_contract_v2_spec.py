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


def test_specification_parses_and_is_design_only():
    spec = _load_spec()

    assert spec["name"] == "review_context_contract"
    assert spec["version"] == "design-v2"
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
    response_text = _serialized(spec["response_model"])

    for value in spec["prohibited_external_values"]:
        assert f'"{value}"' not in response_text


def test_response_uses_descriptive_context_objects():
    spec = _load_spec()
    response = spec["response_model"]
    required_fields = set(response["required_fields"])

    assert {
        "context_state",
        "source_state",
        "constraint_context",
        "temporal_context",
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
