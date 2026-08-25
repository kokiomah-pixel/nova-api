from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import scripts.validate_gate4_private_synthetic_adapter as gate4_validator

from nova.harnesses.target_v2_private_synthetic_adapter import (
    CanonicalizationError,
    SyntheticAdapterError,
    TargetV2SyntheticAdapter,
    canonicalize_jcs,
    fixture_checksum_v0,
    normalize_declared_set,
    normalize_exact_decimal,
    normalize_timestamp,
)
from scripts.gate3_reference_semantics import canonicalize_jcs_profile
from scripts.validate_gate4_private_synthetic_adapter import (
    validate_implementation_source,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/target-v2/gate4/private_synthetic_adapter_v0_1.json"


def _base() -> dict:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))["base_request"]


def _adapter() -> TargetV2SyntheticAdapter:
    return TargetV2SyntheticAdapter(
        fingerprint_algorithm_qualification="fixture-only-checksum-v0",
        fingerprint_function=fixture_checksum_v0,
    )


def _add_second_source(request: dict, environment: str = "synthetic") -> None:
    request["evidence"]["sources"].append(
        {
            "source_id": "source-b",
            "source_version_or_digest": "fixture-version-2",
            "observed_at": "2030-01-01T11:59:20Z",
            "received_at": "2030-01-01T11:59:40Z",
            "record_source_type": environment,
        }
    )


def test_gate4_boundary_validator_passes() -> None:
    assert validate_repository() == []


def test_gate4_safety_validator_does_not_require_git_history(monkeypatch: pytest.MonkeyPatch) -> None:
    def inaccessible_history(*args: object, **kwargs: object) -> object:
        raise AssertionError("CI-portable safety validation must not inspect git history")

    monkeypatch.setattr(gate4_validator.subprocess, "run", inaccessible_history)
    assert validate_repository() == []


def test_external_action_and_proposal_identities_remain_distinct() -> None:
    result = _adapter().adapt(_base())
    reference = result.response["prepared_action_reference"]
    assert reference["action_id"] == "external-action-lineage-001"
    assert reference["proposal_version_identity"] == {
        "value": "external-proposal-version-001.1",
        "source_type": "external_institution_or_orchestrator",
        "establishes_action_lineage": False,
    }


def test_missing_action_id_means_lineage_is_unavailable_and_not_inferred() -> None:
    request = _base()
    request["prepared_action"].pop("action_id")
    result = _adapter().adapt(request)
    reference = result.response["prepared_action_reference"]
    assert "action_id" not in reference
    assert reference["proposal_version_identity"]["establishes_action_lineage"] is False


def test_Nova_derived_proposal_fingerprint_is_qualified_and_prepared_action_only() -> None:
    request = _base()
    request["prepared_action"].pop("proposal_version_id")
    result = _adapter().adapt(request)
    identity = result.response["prepared_action_reference"]["proposal_version_identity"]
    assert identity["source_type"] == "Nova_derived_proposal_fingerprint"
    assert identity["algorithm_qualification"] == "fixture-only-checksum-v0"
    assert identity["material_scope"] == "canonical_prepared_action_material_only"
    assert identity["establishes_action_lineage"] is False


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("complete", "complete"),
        ("partial", "partial"),
        ("conflicted", "conflicted"),
        ("unavailable", "unavailable"),
    ],
)
def test_all_review_completeness_states(mutation: str, expected: str) -> None:
    request = _base()
    if mutation == "partial":
        request["institution_context"]["relevant_constraints"] = []
    elif mutation == "conflicted":
        request["evidence"]["unresolved_source_conflicts"] = [
            {"conflict_id": "conflict-1", "variants": ["source-a", "source-b"]}
        ]
    elif mutation == "unavailable":
        request["review_profile"]["required_field_inventory_available"] = False
    assert _adapter().adapt(request).response["review_completeness"]["value"] == expected


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("current", "current"),
        ("uncertain", "uncertain"),
        ("stale", "stale"),
        ("superseded", "superseded"),
    ],
)
def test_all_temporal_context_states(mutation: str, expected: str) -> None:
    request = _base()
    if mutation == "uncertain":
        request["evidence"]["sources"][0]["observed_at"] = None
    elif mutation == "stale":
        request["evidence"]["sources"][0]["observed_at"] = "2030-01-01T11:00:00Z"
    elif mutation == "superseded":
        request["prepared_action"]["superseded_by_reference"] = "opaque-proposal-002"
    assert _adapter().adapt(request).response["context_state"]["value"] == expected


def test_missing_timestamp_never_becomes_current() -> None:
    request = _base()
    request["evidence"]["sources"][0]["observed_at"] = None
    result = _adapter().adapt(request).response
    assert result["context_state"]["value"] == "uncertain"
    assert result["source_state"]["value"] == "partial"


def test_source_conflict_preserves_variants_without_Nova_selected_winner() -> None:
    request = _base()
    request["evidence"]["unresolved_source_conflicts"] = [
        {"conflict_id": "conflict-1", "variants": ["source-a", "source-b"]}
    ]
    result = _adapter().adapt(request).response
    assert result["source_state"]["value"] == "conflicted"
    assert result["source_state"]["unresolved_source_conflicts"][0]["variants"] == ["source-a", "source-b"]
    assert "selected_winner" not in canonicalize_jcs(result).decode("utf-8")


def test_exact_financial_normalization_and_no_rounding() -> None:
    result = _adapter().adapt(_base())
    assert result.normalized_prepared_action_material["amount_or_scope"] == {
        "numeric_type": "monetary_amount",
        "asset_id": "fixture-USD",
        "coefficient": "123",
        "scale": 2,
    }
    assert normalize_exact_decimal(
        "1.2300", max_precision=8, max_scale=2, max_abs_exponent=4, max_input_characters=16
    ) == {"numeric_type": "decimal", "coefficient": "123", "scale": 2}
    with pytest.raises(CanonicalizationError):
        normalize_exact_decimal(
            "1.234", max_precision=8, max_scale=2, max_abs_exponent=4, max_input_characters=16
        )


def test_timestamp_rules_reject_unknown_offset_and_overprecision() -> None:
    assert normalize_timestamp("2030-01-01T01:02:03-05:00") == "2030-01-01T06:02:03.000000Z"
    with pytest.raises(CanonicalizationError):
        normalize_timestamp("2030-01-01T01:02:03-00:00")
    with pytest.raises(CanonicalizationError):
        normalize_timestamp("2030-01-01T01:02:03.1234567Z")


def test_jcs_key_order_unicode_and_gate3_oracle_agree() -> None:
    value = {"\ue000": "private", "\U00010000": "astral", "b": 2, "a": 1}
    independent = canonicalize_jcs(value)
    assert independent == canonicalize_jcs_profile(value)
    assert independent.startswith(b'{"a":1,"b":2,')
    assert canonicalize_jcs({"é": 1}) != canonicalize_jcs({"e\u0301": 1})


def test_source_set_order_is_invariant_and_exact_duplicates_collapse() -> None:
    first = _base()
    _add_second_source(first)
    second = copy.deepcopy(first)
    second["evidence"]["sources"].reverse()
    second["evidence"]["sources"].append(copy.deepcopy(second["evidence"]["sources"][0]))
    assert _adapter().adapt(first).canonical_semantic_material == _adapter().adapt(second).canonical_semantic_material


def test_primary_tuple_collision_rejects_instead_of_using_whole_item_order() -> None:
    left = {"reference_type": "prior_review", "reference_id": "same", "version_or_digest": "v1", "note": "a"}
    right = {"reference_type": "prior_review", "reference_id": "same", "version_or_digest": "v1", "note": "b"}
    with pytest.raises(CanonicalizationError, match="primary tuple"):
        normalize_declared_set(
            [right, left], tuple_fields=("reference_type", "reference_id", "version_or_digest")
        )


def test_null_and_absent_remain_distinct() -> None:
    assert canonicalize_jcs({"value": None}) != canonicalize_jcs({})
    request = _base()
    request["prepared_action"]["intended_time_window"].pop("end")
    with pytest.raises(SyntheticAdapterError):
        _adapter().adapt(request)


def test_synthetic_source_environment_is_preserved() -> None:
    request = _base()
    _add_second_source(request)
    result = _adapter().adapt(request).response
    assert result["record_source_type"]["value"] == "synthetic"
    assert {item["record_source_type"] for item in result["record_source_type"]["source_segmentation"]} == {
        "synthetic",
    }


@pytest.mark.parametrize("environment", ["production_like", "live", "mixed"])
def test_gate4_rejects_non_synthetic_record_source_type(environment: str) -> None:
    request = _base()
    request["evidence"]["sources"][0]["record_source_type"] = environment
    with pytest.raises(SyntheticAdapterError, match="accepts only record_source_type: synthetic"):
        _adapter().adapt(request)


def test_gate4_rejects_mixed_source_input() -> None:
    request = _base()
    _add_second_source(request, "production_like")
    with pytest.raises(SyntheticAdapterError, match="accepts only record_source_type: synthetic"):
        _adapter().adapt(request)


def test_G3_R03_mixed_semantics_remain_canonical_outside_gate4() -> None:
    contract = json.loads((ROOT / "specs/review_context_contract_v2.json").read_text(encoding="utf-8"))
    permitted = contract["response_model"]["record_source_type"]["permitted_values"]
    assert permitted == ["synthetic", "production_like", "live", "mixed"]


def test_empty_sources_do_not_invent_a_synthetic_environment() -> None:
    request = _base()
    request["evidence"]["sources"] = []
    with pytest.raises(SyntheticAdapterError, match="cannot be inferred"):
        _adapter().adapt(request)


def test_constraint_reference_cannot_smuggle_an_unapproved_semantic_field() -> None:
    request = _base()
    request["institution_context"]["relevant_constraints"][0]["unknown_scope"] = "must-not-hash"
    with pytest.raises(SyntheticAdapterError, match="approved opaque identity"):
        _adapter().adapt(request)


def test_profile_version_drives_deterministic_semantic_difference() -> None:
    first = _base()
    second = _base()
    second["review_profile"]["profile_version"] = "2"
    second["review_profile"]["profile_hash"] = "fixture-profile-hash-2"
    assert _adapter().adapt(first).canonical_semantic_material != _adapter().adapt(second).canonical_semantic_material


def test_chronology_and_memory_references_are_opaque_identity_only() -> None:
    response = _adapter().adapt(_base()).response["chronology_context"]
    assert response["prior_review_references"][0]["reference_id"] == "review-001"
    assert response["accepted_memory_references"][0]["reference_id"] == "memory-001"
    request = _base()
    request["institution_context"]["prior_review_references"][0]["policy_meaning"] = "do-not-interpret"
    with pytest.raises(SyntheticAdapterError, match="opaque identities"):
        _adapter().adapt(request)


def test_authority_handoff_and_boundary_are_constants() -> None:
    response = _adapter().adapt(_base()).response
    assert response["authority_handoff"] == {
        "decision_owner": "local_institutional_authority",
        "execution_owner": "external_system",
        "Nova_authority_effect": "none",
    }
    assert response["boundary"] == {
        "approval_effect": "none",
        "authorization_effect": "none",
        "execution_effect": "none",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("decision_status", "ALLOW"),
        ("decision_admission_record", {"status": "admitted"}),
        ("permission_budget", "fixture_value"),
        ("permission_budget_class", "fixture_class"),
        ("execution_posture", "fixture_posture"),
        ("recommended_action", "fixture_action"),
        ("adjusted_size", "10"),
        ("conditioned_size", "10"),
        ("halt_release_authority", "fixture_authority"),
        ("prevented_action", "fixture_action"),
        ("intervention_type", "fixture_intervention"),
    ],
)
def test_Legacy_v1_derivation_fields_fail_closed(field: str, value: object) -> None:
    request = _base()
    request[field] = value
    with pytest.raises(SyntheticAdapterError, match=f"prohibited Legacy v1 field.*{field}"):
        _adapter().adapt(request)


def test_Legacy_v1_outcome_changes_cannot_influence_target_v2_derivation() -> None:
    baseline = _adapter().adapt(_base()).canonical_semantic_material
    errors: list[str] = []
    for outcome in ("ALLOW", "DENY"):
        request = _base()
        request["decision_status"] = outcome
        with pytest.raises(SyntheticAdapterError) as caught:
            _adapter().adapt(request)
        errors.append(str(caught.value))
    assert errors[0] == errors[1]
    assert _adapter().adapt(_base()).canonical_semantic_material == baseline


def test_proof_inputs_select_no_production_algorithm_or_security_claim() -> None:
    inputs = _adapter().adapt(_base()).proof_envelope_inputs
    assert inputs["digest_algorithm_selection"] == "not_selected"
    assert inputs["signature_algorithm_selection"] == "not_selected"
    assert inputs["authority_effect"] == inputs["execution_effect"] == "none"
    assert isinstance(inputs["semantic_context_material"], bytes)


@pytest.mark.parametrize(
    "source",
    [
        "import fastapi",
        "import requests",
        "from app import app",
        "from scripts.gate3_reference_semantics import canonicalize_jcs_profile",
        "value = os.getenv('PRODUCTION_KEY')",
        "def write_reflex_memory(): pass",
    ],
)
def test_boundary_validator_rejects_forbidden_dependencies(source: str) -> None:
    assert validate_implementation_source(source)
