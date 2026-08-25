from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

from scripts.gate3_reference_semantics import (
    ReferenceSemanticsError,
    build_digest_evidence,
    canonicalize_jcs_profile,
    derive_record_source_type,
    evaluate_review_completeness,
    normalize_exact_decimal,
    normalize_monetary_amount,
    normalize_semantic_array,
    normalize_timestamp,
    normalize_timestamp_window,
    resolve_prepared_action_identity,
    verify_semantic_identity_continuity,
)
from scripts.validate_target_v2_contract_revision import (
    ALL_GAPS,
    BRANCH_RELATIVE_LIFECYCLE_MARKERS,
    FORBIDDEN_RESPONSE_SHAPES,
    INCORPORATED_REFINEMENTS,
    PERSISTENT_LIFECYCLE_ARTIFACTS,
    UNAPPROVED_REFINEMENTS,
    UNAPPROVED_SORT_FIELD_DEPENDENCIES,
    validate_repository,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MACHINE_CONTRACT = REPO_ROOT / "specs/review_context_contract_v2.json"
HUMAN_CONTRACT = REPO_ROOT / "docs/architecture/external-review-context-contract-v2.md"
DERIVATION_SPEC = REPO_ROOT / "specs/review_context_field_derivation_v0_1.json"
GAP_REGISTER = REPO_ROOT / "specs/review_context_contract_gaps_v0_1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_revision_validator_passes() -> None:
    assert validate_repository() == []


def test_human_and_machine_contract_versions_match_design_v2_1() -> None:
    contract = _load(MACHINE_CONTRACT)
    human = HUMAN_CONTRACT.read_text(encoding="utf-8")

    assert contract["version"] == "design-v2.1"
    assert set(re.findall(r"version:\s*(design-v[^\s]+)", human)) == {"design-v2.1"}
    assert contract["implementation_status"] == "not_implemented"
    assert contract["runtime_implemented"] is False


def test_incorporated_refinement_set_is_exact_and_other_21_remain_unapproved() -> None:
    contract = _load(MACHINE_CONTRACT)
    gaps = _load(GAP_REGISTER)
    by_id = {record["id"]: record for record in gaps["contract_refinements"]}

    assert set(contract["incorporated_Gate_3_refinements"]) == INCORPORATED_REFINEMENTS
    assert len(by_id) == 26
    assert set(by_id) == ALL_GAPS
    assert len(UNAPPROVED_REFINEMENTS) == 21
    for gap_id in UNAPPROVED_REFINEMENTS:
        assert by_id[gap_id]["requires_CCO_review"] is True
        assert by_id[gap_id]["requires_Architect_review"] is True
        assert "contract_revision_target" not in by_id[gap_id]


def test_r01_distinguishes_external_action_lineage_from_exact_proposal_identity() -> None:
    fingerprint = lambda material: f"fixture:{len(material)}:{sum(material)}"
    v1 = resolve_prepared_action_identity(
        prepared_action={"amount": "1.00"},
        action_id=None,
        external_proposal_version_id=None,
        fingerprint_algorithm="fixture-only-a",
        fingerprint_function=fingerprint,
    )
    v2 = resolve_prepared_action_identity(
        prepared_action={"amount": "2.00"},
        action_id=None,
        external_proposal_version_id=None,
        fingerprint_algorithm="fixture-only-a",
        fingerprint_function=fingerprint,
    )

    assert v1["action_id"] == v2["action_id"] == {
        "value": None,
        "source": "unavailable",
        "lineage": "unavailable",
    }
    assert v1["same_action_inference_permitted"] is False
    assert v2["same_action_inference_permitted"] is False
    assert v1["proposal_version_identity"]["value"] != v2["proposal_version_identity"]["value"]
    assert v1["proposal_version_identity"]["source_type"] == "Nova_derived_proposal_fingerprint"
    assert v1["proposal_version_identity"]["algorithm_qualification"] == "fixture-only-a"
    assert v1["proposal_version_identity"]["material_scope"] == "canonical_prepared_action_material_only"
    assert v1["proposal_version_identity"]["establishes_action_lineage"] is False


def test_r01_external_identity_is_preserved_without_content_derivation() -> None:
    resolved = resolve_prepared_action_identity(
        prepared_action={"mutable": "content"},
        action_id="external-action-7",
        external_proposal_version_id="external-proposal-7.2",
    )

    assert resolved["action_id"]["source"] == "external_institution_or_orchestrator"
    assert resolved["action_id"]["value"] == "external-action-7"
    assert resolved["proposal_version_identity"] == {
        "value": "external-proposal-7.2",
        "source_type": "external_institution_or_orchestrator",
        "establishes_action_lineage": False,
    }
    assert resolved["same_action_inference_permitted"] is True


@pytest.mark.parametrize(
    ("segments", "expected"),
    [
        (["synthetic", "live"], "mixed"),
        (["production_like", "live"], "mixed"),
        (["live", "live"], "live"),
        (["production_like", "production_like"], "production_like"),
    ],
)
def test_r03_mixed_source_semantics_do_not_rank_or_promote(segments: list[str], expected: str) -> None:
    assert derive_record_source_type(segments) == expected


def test_r08_contract_precedence_is_executable_and_profile_cannot_redefine_it() -> None:
    common = {
        "required_field_inventory_available": True,
        "explicit_unresolved_required_context": [],
        "profile_allows_explicit_unresolved": True,
        "all_required_dimensions_represented": True,
    }
    assert evaluate_review_completeness(
        profile_available=False,
        unresolved_material_conflicts=["conflict"],
        missing_or_unavailable_required_context=["missing"],
        **common,
    ) == "unavailable"
    assert evaluate_review_completeness(
        profile_available=True,
        unresolved_material_conflicts=["conflict"],
        missing_or_unavailable_required_context=["missing"],
        **common,
    ) == "conflicted"
    assert evaluate_review_completeness(
        profile_available=True,
        unresolved_material_conflicts=[],
        missing_or_unavailable_required_context=["missing"],
        **common,
    ) == "partial"
    assert evaluate_review_completeness(
        profile_available=True,
        unresolved_material_conflicts=[],
        missing_or_unavailable_required_context=[],
        **common,
    ) == "complete"
    contract = _load(MACHINE_CONTRACT)["response_model"]["review_completeness"]
    assert contract["profile_may_redefine_enum_meaning_or_precedence"] is False
    assert set(contract["complete_does_not_mean"]) == {
        "policy_satisfied",
        "safe",
        "permitted",
        "approved",
        "executable",
    }
    assert {"institutional_policy_satisfied", "transaction_permitted", "action_executable"} <= set(contract["does_not_mean"])


def test_r11_generic_decimal_trims_before_scale_bound_without_rounding() -> None:
    assert normalize_exact_decimal(
        "1.2300",
        max_precision=8,
        max_scale=2,
        max_abs_exponent=8,
        max_input_characters=32,
    ) == {"numeric_type": "decimal", "coefficient": "123", "scale": 2}
    assert normalize_exact_decimal(
        "-0.000",
        max_precision=8,
        max_scale=3,
        max_abs_exponent=8,
        max_input_characters=32,
    ) == {"numeric_type": "decimal", "coefficient": "0", "scale": 0}
    with pytest.raises(ReferenceSemanticsError):
        normalize_exact_decimal(
            "1.234",
            max_precision=8,
            max_scale=2,
            max_abs_exponent=8,
            max_input_characters=32,
        )


def test_r11_fixed_scale_money_preserves_scale_and_rejects_rounding() -> None:
    assert normalize_monetary_amount(
        "1.2",
        asset_id="USD",
        scale=2,
        max_precision=8,
        max_scale=2,
        max_abs_exponent=8,
        max_input_characters=32,
    ) == {"numeric_type": "monetary_amount", "asset_id": "USD", "coefficient": "120", "scale": 2}
    with pytest.raises(ReferenceSemanticsError):
        normalize_monetary_amount(
            "1.234",
            asset_id="USD",
            scale=2,
            max_precision=8,
            max_scale=2,
            max_abs_exponent=8,
            max_input_characters=32,
        )


def test_r11_timestamps_and_window_boundaries_normalize_without_silent_unknown_offset() -> None:
    assert normalize_timestamp("2026-08-24T07:08:09-05:00") == "2026-08-24T12:08:09.000000Z"
    assert normalize_timestamp_window(
        {"start": "2026-08-24T07:08:09.1-05:00", "end": "2026-08-24T13:00:00Z"},
        boundary_fields=["start", "end"],
        precision=6,
    ) == {
        "start": "2026-08-24T12:08:09.100000Z",
        "end": "2026-08-24T13:00:00.000000Z",
    }
    with pytest.raises(ReferenceSemanticsError):
        normalize_timestamp("2026-08-24T12:00:00-00:00")


def test_r11_semantic_arrays_and_null_absence_are_explicit() -> None:
    left = [{"source_id": "b"}, {"source_id": "a"}, {"source_id": "a"}]
    right = list(reversed(left))
    source_sort = _load(MACHINE_CONTRACT)["canonicalization_semantics"]["semantic_arrays"]["sort_tuple_profiles"]["source_reference_sort"]
    assert normalize_semantic_array(left, semantics="set", sort_tuple=source_sort, identity_key="source_id") == normalize_semantic_array(
        right, semantics="set", sort_tuple=source_sort, identity_key="source_id"
    )
    with pytest.raises(ReferenceSemanticsError):
        normalize_semantic_array(left, semantics="undeclared", identity_key="source_id")
    assert canonicalize_jcs_profile({"value": None}) != canonicalize_jcs_profile({})


def test_r11_declared_type_tuples_drive_order_before_jcs_serialization() -> None:
    arrays = _load(MACHINE_CONTRACT)["canonicalization_semantics"]["semantic_arrays"]
    profiles = arrays["sort_tuple_profiles"]

    source_values = [
        {"aaa": "0", "source_id": "b", "source_version_or_digest": "1"},
        {"aaa": "9", "source_id": "a", "source_version_or_digest": "1"},
    ]
    assert [item["source_id"] for item in sorted(source_values, key=canonicalize_jcs_profile)] == ["b", "a"]
    assert [item["source_id"] for item in normalize_semantic_array(
        source_values,
        semantics="set",
        sort_tuple=profiles["source_reference_sort"],
        identity_key="source_id",
    )] == ["a", "b"]

    constraint_values = [
        {"constraint_id_or_digest": "z", "reference_id": "constraint-z"},
        {"constraint_id_or_digest": "a", "reference_id": "constraint-a"},
    ]
    assert [item["constraint_id_or_digest"] for item in normalize_semantic_array(
        constraint_values,
        semantics="set",
        sort_tuple=profiles["constraint_reference_sort"],
        identity_key="reference_id",
    )] == ["a", "z"]

    chronology_values = [
        {"reference_type": "review", "reference_id": "z"},
        {"reference_type": "memory", "reference_id": "a"},
    ]
    assert [item["reference_type"] for item in normalize_semantic_array(
        chronology_values,
        semantics="set",
        sort_tuple=profiles["chronology_reference_sort"],
        identity_key="reference_id",
    )] == ["memory", "review"]

    tied_vector = _load(REPO_ROOT / "fixtures/target-v2/gate3/design_cases.json")["reference_vectors"]["constraint_reference_primary_tie"]
    tied_constraints = tied_vector["input"]
    tied_normalized = normalize_semantic_array(
        tied_constraints,
        semantics="set",
        sort_tuple=profiles["constraint_reference_sort"],
        identity_key="reference_id",
    )
    assert tied_normalized == tied_vector["expected"]
    assert tied_normalized == normalize_semantic_array(
        list(reversed(tied_constraints)),
        semantics="set",
        sort_tuple=profiles["constraint_reference_sort"],
        identity_key="reference_id",
    )

    digest_values = [
        {"algorithm": "fixture-z", "parameter_set": "1", "output_encoding": "hex", "digest": "00"},
        {"algorithm": "fixture-a", "parameter_set": "1", "output_encoding": "hex", "digest": "ff"},
    ]
    assert [item["algorithm"] for item in normalize_semantic_array(
        digest_values,
        semantics="set",
        sort_tuple=profiles["digest_record_sort"],
    )] == ["fixture-a", "fixture-z"]

    with pytest.raises(ReferenceSemanticsError, match="conflicting duplicate declared sort tuple"):
        normalize_semantic_array(
            [{"algorithm": "a", "extra": 1}, {"algorithm": "a", "extra": 2}],
            semantics="set",
            sort_tuple=profiles["digest_record_sort"],
        )


def test_r11_sort_profiles_exclude_fields_owned_by_unapproved_refinements() -> None:
    machine_profiles = _load(MACHINE_CONTRACT)["canonicalization_semantics"]["semantic_arrays"]["sort_tuple_profiles"]
    derivation_profiles = _load(DERIVATION_SPEC)["canonical_numeric_and_interoperability_profile"]["sort_tuple_profiles"]

    expected = {
        "source_reference_sort": {
            "primary": ["source_id", "source_version_or_digest", "observed_at", "received_at", "record_source_type"],
            "final_tie_breaker": "normalized_item_JCS_bytes",
        },
        "constraint_reference_sort": {
            "primary": ["constraint_id_or_digest", "source_id"],
            "final_tie_breaker": "normalized_item_JCS_bytes",
        },
        "chronology_reference_sort": {
            "primary": ["reference_type", "reference_id", "version_or_digest"],
            "final_tie_breaker": "normalized_item_JCS_bytes",
        },
    }
    for name, rule in expected.items():
        assert machine_profiles[name] == rule
        assert derivation_profiles[name] == rule

    for profiles in (machine_profiles, derivation_profiles):
        primary_fields = {
            field
            for profile in profiles.values()
            for field in (profile["primary"] if isinstance(profile, dict) else profile)
        }
        assert primary_fields.isdisjoint(UNAPPROVED_SORT_FIELD_DEPENDENCIES)


def test_r01_response_genesis_is_machine_visible_for_both_origins() -> None:
    identity = _load(MACHINE_CONTRACT)["response_model"]["prepared_action_reference"]["proposal_version_identity"]

    assert identity["required_fields"] == ["value", "source_type"]
    assert identity["source_type_permitted_values"] == [
        "external_institution_or_orchestrator",
        "Nova_derived_proposal_fingerprint",
    ]
    assert identity["conditional_fields"]["when_source_type_is_Nova_derived_proposal_fingerprint"] == {
        "algorithm_qualification": "required",
        "material_scope": "canonical_prepared_action_material_only",
    }
    assert identity["establishes_action_lineage"] is False


def test_persistent_artifacts_use_merge_stable_repository_canonicality() -> None:
    contract = _load(MACHINE_CONTRACT)
    assert contract["canonicality_source"] == "authoritative_repository_main"
    for relative in PERSISTENT_LIFECYCLE_ARTIFACTS:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        for marker in BRANCH_RELATIVE_LIFECYCLE_MARKERS:
            assert marker not in text


def test_r11_jcs_baseline_and_financial_float_boundary_are_canonical() -> None:
    contract = _load(MACHINE_CONTRACT)["canonicalization_semantics"]
    assert contract["structural_baseline"] == "RFC_8785_JCS"
    assert contract["JCS_deviation"] is False
    assert contract["production_hash_algorithm_selected"] is False
    with pytest.raises(ReferenceSemanticsError):
        canonicalize_jcs_profile({"financial_value": 1.23})


def test_q15_preserves_history_without_claiming_equal_digest_values() -> None:
    canonical_bytes = canonicalize_jcs_profile({"semantic": "context"})
    digesters = {
        "fixture-a": lambda value: f"length:{len(value)}",
        "fixture-b": lambda value: f"sum:{sum(value)}",
    }
    evidence = build_digest_evidence(canonical_bytes, digesters)
    continuity = verify_semantic_identity_continuity(
        [canonical_bytes, canonical_bytes], evidence, digesters
    )

    assert continuity["continuous"] is True
    assert continuity["historical_digest_evidence_preserved"] is True
    assert continuity["digest_values_are_semantic_identity"] is False
    assert len(set(continuity["digest_values"])) == 2
    assert verify_semantic_identity_continuity([], evidence, digesters) == {
        "continuous": False,
        "reason": "canonical_material_unavailable",
    }


def test_unapproved_transport_shapes_and_all_runtime_authorities_remain_absent() -> None:
    contract = _load(MACHINE_CONTRACT)
    response = contract["response_model"]
    gate = contract["implementation_gate"]

    assert not (set(response) & FORBIDDEN_RESPONSE_SHAPES)
    assert response["reproducibility"]["required_fields"].count("context_hash") == 1
    assert contract["endpoint_exists"] is False
    assert contract["private_adapter_started"] is False
    assert contract["Gate_4_authority"] is False
    assert contract["approved_for_runtime_implementation"] is False
    assert gate["Gate_4_private_synthetic_adapter"] == {
        "status": "not_authorized",
        "implementation_started": False,
    }
    assert gate["target_v2_runtime"] == {
        "status": "not_implemented",
        "implementation_authority": False,
    }


def test_recorded_contract_digest_matches_exact_design_v2_1_bytes() -> None:
    reference = _load(DERIVATION_SPEC)["approved_contract"]
    assert reference["version"] == "design-v2.1"
    assert reference["incorporation_status"] == "incorporated_in_design_v2.1_contract"
    assert reference["canonicality_source"] == "authoritative_repository_main"
    assert reference["sha256"] == hashlib.sha256(MACHINE_CONTRACT.read_bytes()).hexdigest()
