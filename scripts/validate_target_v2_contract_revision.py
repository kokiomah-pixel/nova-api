#!/usr/bin/env python3
"""Validate the design-v2.1 target-v2 contract revision.

This validator is design-only. It does not import runtime code, select
production cryptography, or authorize an endpoint, adapter, Gate 4, or merge.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HUMAN_CONTRACT = Path("docs/architecture/external-review-context-contract-v2.md")
MACHINE_CONTRACT = Path("specs/review_context_contract_v2.json")
DERIVATION_SPEC = Path("specs/review_context_field_derivation_v0_1.json")
GAP_REGISTER = Path("specs/review_context_contract_gaps_v0_1.json")
TARGET_README = Path("docs/target-v2/README.md")
PERSISTENT_LIFECYCLE_ARTIFACTS = (
    HUMAN_CONTRACT,
    TARGET_README,
    Path("docs/target-v2/context-proof-canonicalization-v0.1.md"),
    Path("docs/target-v2/gate-3-contract-gap-report-v0.1.md"),
    Path("docs/target-v2/gate-3-field-derivation-ledger-v0.1.md"),
    MACHINE_CONTRACT,
    DERIVATION_SPEC,
    GAP_REGISTER,
)
BRANCH_RELATIVE_LIFECYCLE_MARKERS = {
    "contract_revision_status",
    "contract_revision_candidate",
    "candidate_present",
    "canonical_on_main",
    "false_until_merge",
    "approved_contract_modified",
}

INCORPORATED_REFINEMENTS = {"G3-R01", "G3-R03", "G3-R08", "G3-R11", "G3-Q15"}
ALL_GAPS = {
    *(f"G3-R{index:02d}" for index in range(1, 12)),
    *(f"G3-Q{index:02d}" for index in range(1, 16)),
}
UNAPPROVED_REFINEMENTS = ALL_GAPS - INCORPORATED_REFINEMENTS
UNAPPROVED_SORT_FIELD_DEPENDENCIES = {
    "authority_scope": "G3-R04",
    "treatment_status": "G3-R10",
    "applicability_status": "G3-R10",
    "applicability_scope": "not_independently_defined_in_canonical_target_v2",
}
EXPECTED_ARRAY_PATHS = {
    "review_context_response.record_source_type.source_segmentation",
    "review_context_response.context_state.reasons",
    "review_context_response.source_state.sources",
    "review_context_response.source_state.unresolved_source_conflicts",
    "review_context_response.constraint_context.observed_constraints",
    "review_context_response.constraint_context.constraint_sources",
    "review_context_response.constraint_context.unresolved_constraint_questions",
    "review_context_response.temporal_context.temporal_conflicts",
    "review_context_response.temporal_context.pending_state",
    "review_context_response.contradiction_context.source_conflicts",
    "review_context_response.contradiction_context.constraint_conflicts",
    "review_context_response.contradiction_context.temporal_conflicts",
    "review_context_response.contradiction_context.chronology_conflicts",
    "review_context_response.contradiction_context.unresolved_questions",
    "review_context_response.review_completeness.missing_context",
    "review_context_response.review_completeness.unresolved_conditions",
    "review_context_response.chronology_context.prior_review_references",
    "review_context_response.chronology_context.accepted_memory_references",
    "review_context_response.chronology_context.relevant_changes_since_prior_review",
    "review_context_response.reproducibility.source_versions",
    "review_context_response.reproducibility.source_segmentation",
}
FORBIDDEN_RESPONSE_SHAPES = {
    "cryptographic_profile_reference",
    "proof_attestations",
    "proof_verification_state",
    "reconstruction_scope",
    "time_evidence",
    "semantic_digests",
    "context_hashes",
}


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _load_json(root: Path, relative: Path, errors: list[ValidationError]) -> dict[str, Any]:
    try:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(ValidationError(str(relative), str(exc)))
        return {}
    if not isinstance(value, dict):
        errors.append(ValidationError(str(relative), "root must be an object"))
        return {}
    return value


def _expect(
    errors: list[ValidationError],
    condition: bool,
    field: str,
    message: str,
) -> None:
    if not condition:
        errors.append(ValidationError(field, message))


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    """Return deterministic contract-revision coherence errors."""

    root = root.resolve()
    errors: list[ValidationError] = []
    contract = _load_json(root, MACHINE_CONTRACT, errors)
    derivation = _load_json(root, DERIVATION_SPEC, errors)
    gaps = _load_json(root, GAP_REGISTER, errors)
    try:
        human = (root / HUMAN_CONTRACT).read_text(encoding="utf-8")
        readme = (root / TARGET_README).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(ValidationError("human_artifacts", str(exc)))
        return errors

    _expect(errors, contract.get("version") == "design-v2.1", "contract.version", "must be design-v2.1")
    _expect(errors, contract.get("canonicality_source") == "authoritative_repository_main", "contract.canonicality_source", "must be authoritative_repository_main")
    human_versions = set(re.findall(r"version:\s*(design-v[^\s]+)", human))
    _expect(errors, human_versions == {"design-v2.1"}, "human_contract.version", "must match design-v2.1 exactly")
    _expect(
        errors,
        set(contract.get("incorporated_Gate_3_refinements", [])) == INCORPORATED_REFINEMENTS,
        "contract.incorporated_Gate_3_refinements",
        "must contain exactly G3-R01, G3-R03, G3-R08, G3-R11, and G3-Q15",
    )

    for field, expected in {
        "implementation_status": "not_implemented",
        "authority_model": "non_authority",
        "authority_effect": "none",
        "execution_effect": "none",
        "runtime_implemented": False,
        "approved_for_runtime_implementation": False,
        "endpoint_exists": False,
        "private_adapter_started": False,
        "Gate_4_authority": False,
    }.items():
        _expect(errors, contract.get(field) == expected, f"contract.{field}", f"must be {expected!r}")
    _expect(
        errors,
        contract.get("canonical_boundary") == [
            "Agent prepares action.",
            "Nova structures review context.",
            "Local authority decides.",
            "External systems execute.",
            "Nova does not execute.",
        ],
        "contract.canonical_boundary",
        "must preserve the non-authority boundary",
    )

    request_identity = contract.get("request_model", {}).get("prepared_action_identity_semantics", {})
    action_id = request_identity.get("action_id", {})
    proposal_id = request_identity.get("proposal_version_id", {})
    fallback = proposal_id.get("fallback", {})
    _expect(errors, request_identity.get("identities_distinct") is True, "G3-R01.identities_distinct", "must be true")
    _expect(errors, action_id.get("authority") == "external_institution_or_orchestrator_only", "G3-R01.action_id.authority", "must be external only")
    _expect(errors, action_id.get("Nova_content_derivation_permitted") is False, "G3-R01.action_id.Nova_content_derivation_permitted", "must be false")
    _expect(errors, action_id.get("missing_behavior") == "lineage_unavailable_and_no_same_action_inference", "G3-R01.action_id.missing_behavior", "must preserve unavailable lineage")
    _expect(errors, fallback.get("source") == "Nova_derived_proposal_fingerprint", "G3-R01.fallback.source", "must be explicitly Nova-derived")
    _expect(errors, fallback.get("explicit_label_required") is True, "G3-R01.fallback.label", "must be explicit")
    _expect(errors, fallback.get("material_scope") == "canonical_prepared_action_material_only", "G3-R01.fallback.scope", "must be prepared-action-only")
    _expect(errors, fallback.get("algorithm_qualified") is True, "G3-R01.fallback.algorithm", "must be qualified")
    _expect(errors, fallback.get("establishes_action_lineage") is False, "G3-R01.fallback.lineage", "must not establish lineage")
    response_identity = contract.get("response_model", {}).get("prepared_action_reference", {})
    _expect(errors, "proposal_version_identity" in response_identity.get("required_fields", []), "G3-R01.response.proposal_version_identity", "must bind structured exact proposal identity")
    _expect(errors, "action_id" in response_identity.get("optional_fields", []), "G3-R01.response.action_id", "must bind external lineage when available")
    response_proposal = response_identity.get("proposal_version_identity", {})
    _expect(errors, response_proposal.get("required_fields") == ["value", "source_type"], "G3-R01.response.genesis", "value and source_type must be machine-visible")
    _expect(errors, response_proposal.get("source_type_permitted_values") == ["external_institution_or_orchestrator", "Nova_derived_proposal_fingerprint"], "G3-R01.response.source_type", "must distinguish external from Nova-derived genesis")
    nova_condition = response_proposal.get("conditional_fields", {}).get("when_source_type_is_Nova_derived_proposal_fingerprint", {})
    _expect(errors, nova_condition == {"algorithm_qualification": "required", "material_scope": "canonical_prepared_action_material_only"}, "G3-R01.response.Nova_derived", "must expose algorithm qualification and prepared-action-only scope")
    _expect(errors, response_proposal.get("establishes_action_lineage") is False, "G3-R01.response.lineage", "proposal identity must not establish action lineage")

    source_type = contract.get("response_model", {}).get("record_source_type", {})
    _expect(errors, source_type.get("permitted_values") == ["synthetic", "production_like", "live", "mixed"], "G3-R03.permitted_values", "must add only mixed")
    _expect(errors, source_type.get("semantics", {}).get("mixed") == "more_than_one_evidence_environment_class_is_represented", "G3-R03.mixed", "must have deterministic meaning")
    _expect(errors, source_type.get("source_segmentation_authoritative_for_component_provenance") is True, "G3-R03.segmentation", "must remain authoritative")
    _expect(errors, source_type.get("aggregate_environment_ranking") == "prohibited", "G3-R03.ranking", "must be prohibited")
    _expect(errors, source_type.get("production_like_may_be_represented_as_live") is False, "G3-R03.promotion", "must be false")
    _expect(errors, source_type.get("mixed_reduction_to_strongest_or_weakest") is False, "G3-R03.reduction", "must be false")

    completeness = contract.get("response_model", {}).get("review_completeness", {})
    precedence = ["unavailable", "conflicted", "partial", "complete"]
    _expect(errors, completeness.get("precedence") == precedence, "G3-R08.precedence", "must be unavailable, conflicted, partial, complete")
    _expect(errors, completeness.get("permitted_values") == precedence, "G3-R08.permitted_values", "must match canonical precedence")
    _expect(errors, set(completeness.get("meanings", {})) == set(precedence), "G3-R08.meanings", "must define every state")
    _expect(errors, completeness.get("profile_may_redefine_enum_meaning_or_precedence") is False, "G3-R08.profile_authority", "must be false")
    _expect(errors, set(completeness.get("complete_does_not_mean", [])) == {"policy_satisfied", "safe", "permitted", "approved", "executable"}, "G3-R08.complete_non_authority", "must preserve all five non-authority meanings")
    complete_non_authority = set(completeness.get("does_not_mean", []))
    _expect(errors, {"institutional_policy_satisfied", "transaction_permitted", "action_executable"} <= complete_non_authority, "G3-R08.complete_boundary", "must retain non-authority meaning")

    canonical = contract.get("canonicalization_semantics", {})
    numeric = canonical.get("numeric", {})
    decimal = numeric.get("exact_decimal", {})
    money = numeric.get("monetary_amount", {})
    timestamp = canonical.get("timestamp", {})
    semantic_arrays = canonical.get("semantic_arrays", {})
    array_rules = semantic_arrays.get("array_rules", {})
    _expect(errors, canonical.get("structural_baseline") == "RFC_8785_JCS", "G3-R11.structural_baseline", "must be RFC 8785/JCS")
    _expect(errors, canonical.get("JCS_deviation") is False, "G3-R11.JCS_deviation", "must be false")
    _expect(errors, canonical.get("production_hash_algorithm_selected") is False, "G3-R11.production_hash", "must be false")
    _expect(errors, numeric.get("binary_floating_point_financial_values") == "prohibited", "G3-R11.binary_float", "must be prohibited")
    _expect(errors, set(decimal.get("required_limits", [])) == {"max_precision", "max_scale", "max_abs_exponent", "max_input_characters"}, "G3-R11.decimal_limits", "must declare all four bounds")
    _expect(errors, decimal.get("negative_zero") == "coefficient_zero_without_sign", "G3-R11.negative_zero", "must be deterministic")
    _expect(errors, decimal.get("generic_trailing_zeros") == "trim_before_canonical_resulting_scale_validation", "G3-R11.trailing_zero", "must trim before max_scale")
    _expect(errors, money.get("asset_or_unit_inference") == "prohibited" and money.get("scale_inference") == "prohibited", "G3-R11.money", "asset and scale must be explicit")
    _expect(errors, set(money.get("required_limits", [])) == {"max_precision", "max_scale", "max_abs_exponent", "max_input_characters"}, "G3-R11.money_limits", "must declare all four bounds")
    _expect(errors, money.get("rounding") == "prohibited", "G3-R11.money_rounding", "must be prohibited")
    _expect(errors, timestamp.get("fractional_second_digits") == 6, "G3-R11.timestamp_precision", "must be six")
    _expect(errors, timestamp.get("unknown_offset_minus_00_00") == "reject_not_UTC_equivalent", "G3-R11.unknown_offset", "must reject -00:00")
    _expect(errors, set(array_rules) == EXPECTED_ARRAY_PATHS, "G3-R11.array_rules", "must classify every semantic response array")
    _expect(errors, all(rule.get("classification") == "set" for rule in array_rules.values()), "G3-R11.array_classification", "declared response arrays must have explicit set semantics")
    expected_sort_tuples = {
        "source_reference_sort": ["source_id", "source_version_or_digest", "observed_at", "received_at", "record_source_type"],
        "constraint_reference_sort": ["constraint_id_or_digest", "source_id"],
        "chronology_reference_sort": ["reference_type", "reference_id", "version_or_digest"],
        "digest_record_sort": ["algorithm", "parameter_set", "output_encoding", "digest"],
    }
    sort_tuple_profiles = semantic_arrays.get("sort_tuple_profiles", {})
    for profile_name, expected_tuple in expected_sort_tuples.items():
        _expect(errors, sort_tuple_profiles.get(profile_name) == expected_tuple, f"G3-R11.sort_tuple_profiles.{profile_name}", f"must be {expected_tuple!r}")
    primary_sort_fields = {
        field
        for profile in sort_tuple_profiles.values()
        for field in (profile.get("primary", []) if isinstance(profile, dict) else profile)
    }
    for field, defining_gap in UNAPPROVED_SORT_FIELD_DEPENDENCIES.items():
        _expect(errors, field not in primary_sort_fields, f"G3-R11.unapproved_sort_field.{field}", f"must exclude field owned by {defining_gap}")
    _expect(errors, "normalized_item_JCS_bytes" not in json.dumps(sort_tuple_profiles, sort_keys=True), "G3-R11.whole_item_JCS_sort", "whole-item JCS bytes require a future separately approved complete canonical item schema")
    set_semantics = semantic_arrays.get("set_semantics", {})
    expected_collision = {
        "identical_normalized_item": {"behavior": "collapse_when_field_is_declared_set"},
        "different_normalized_item": {"behavior": "reject_as_conflict_until_explicitly_represented"},
    }
    _expect(errors, set_semantics.get("deterministic_sort_key") == "declared_field_or_type_specific_primary_tuple", "G3-R11.set_sort_key", "must use only declared primary tuples")
    _expect(errors, set_semantics.get("JCS_role") == "serialize_normalized_result_after_declared_type_specific_ordering_not_a_semantic_tie_breaker", "G3-R11.JCS_role", "JCS must be serialization-only")
    _expect(errors, set_semantics.get("primary_tuple_collision") == expected_collision, "G3-R11.primary_tuple_collision", "must collapse identical set items and reject distinct collisions")
    _expect(errors, set_semantics.get("whole_item_JCS_tie_breaker") == "prohibited_without_future_separately_approved_complete_canonical_item_schema", "G3-R11.whole_item_JCS_tie_breaker", "must prohibit whole-item tie-breaking")
    _expect(errors, all(rule.get("sort_tuple_profile") in sort_tuple_profiles for rule in array_rules.values()), "G3-R11.array_sort_profiles", "every set must name a declared tuple profile")

    continuity = contract.get("semantic_identity_continuity", {})
    _expect(errors, continuity.get("semantic_identity_is_individual_digest") is False, "G3-Q15.digest_identity", "must be false")
    _expect(errors, continuity.get("historical_digest_evidence_preserved") is True, "G3-Q15.history", "must preserve history")
    _expect(errors, continuity.get("successor_or_parallel_digest_overwrites_history") is False, "G3-Q15.overwrite", "must be false")
    _expect(errors, continuity.get("same_hash_value_claim_across_algorithms") == "prohibited", "G3-Q15.same_hash", "must be prohibited")
    _expect(errors, continuity.get("unverifiable_semantic_bytes_behavior") == "continuity_unresolved", "G3-Q15.unresolved", "must remain unresolved")
    _expect(errors, continuity.get("transport_shape", {}).get("plural_digest_response_shape_incorporated") is False, "G3-Q15.Q13_boundary", "must not incorporate G3-Q13")

    response_model = contract.get("response_model", {})
    _expect(errors, not (set(response_model) & FORBIDDEN_RESPONSE_SHAPES), "unapproved_gap_incorporation.response_shapes", "forbidden unapproved response shape present")
    reproducibility_fields = response_model.get("reproducibility", {}).get("required_fields", [])
    _expect(errors, reproducibility_fields.count("context_hash") == 1, "unapproved_gap_incorporation.digest_shape", "compatibility context_hash must remain singular")

    records = gaps.get("contract_refinements", [])
    by_id = {record.get("id"): record for record in records if isinstance(record, dict)}
    _expect(errors, set(by_id) == ALL_GAPS and len(records) == 26, "gap_register.inventory", "must preserve all 26 historical records")
    for gap_id in INCORPORATED_REFINEMENTS:
        record = by_id.get(gap_id, {})
        for field, expected in {
            "design_disposition": "approved_for_incorporation",
            "contract_revision_target": "design-v2.1",
            "canonical_contract_status": "incorporated_in_design_v2.1_contract",
            "canonicality_source": "authoritative_repository_main",
            "implementation_authority": False,
            "silently_canonical": False,
        }.items():
            _expect(errors, record.get(field) == expected, f"gap_register.{gap_id}.{field}", f"must be {expected!r}")
    for gap_id in UNAPPROVED_REFINEMENTS:
        record = by_id.get(gap_id, {})
        _expect(errors, record.get("requires_CCO_review") is True, f"gap_register.{gap_id}.requires_CCO_review", "must remain true")
        _expect(errors, record.get("requires_Architect_review") is True, f"gap_register.{gap_id}.requires_Architect_review", "must remain true")
        _expect(errors, "contract_revision_target" not in record, f"gap_register.{gap_id}.contract_revision_target", "must not be incorporated")

    contract_reference = derivation.get("approved_contract", {})
    actual_digest = hashlib.sha256((root / MACHINE_CONTRACT).read_bytes()).hexdigest()
    _expect(errors, contract_reference.get("sha256") == actual_digest, "derivation.approved_contract.sha256", "must match machine contract bytes")
    _expect(errors, contract_reference.get("version") == "design-v2.1", "derivation.approved_contract.version", "must be design-v2.1")
    _expect(errors, contract_reference.get("incorporation_status") == "incorporated_in_design_v2.1_contract", "derivation.approved_contract.incorporation_status", "must record incorporation")
    _expect(errors, contract_reference.get("canonicality_source") == "authoritative_repository_main", "derivation.approved_contract.canonicality_source", "must be merge-stable")
    _expect(errors, derivation.get("design_only") is True, "derivation.design_only", "must remain true")
    _expect(errors, derivation.get("runtime_implementation_authority") is False, "derivation.runtime_implementation_authority", "must remain false")

    gate = contract.get("implementation_gate", {})
    gate4 = gate.get("Gate_4_private_synthetic_adapter", {})
    runtime = gate.get("target_v2_runtime", {})
    _expect(errors, gate.get("endpoint_exists") is False, "implementation_gate.endpoint_exists", "must remain false")
    _expect(errors, gate.get("approved_for_runtime_implementation") is False, "implementation_gate.runtime_authority", "must remain false")
    _expect(errors, gate4 == {"status": "not_authorized", "implementation_started": False}, "implementation_gate.Gate_4", "must remain stopped")
    _expect(errors, runtime == {"status": "not_implemented", "implementation_authority": False}, "implementation_gate.target_v2_runtime", "must remain stopped")
    for marker in (
        "field_derivation_complete: true",
        "runtime_implemented: false",
        "private_adapter_implemented: false",
        "Gate_4_status: authorized_for_bounded_branch_implementation",
        "Gate 3 design completion does not activate Gate 4.",
    ):
        _expect(errors, marker in readme, "target_v2.README", f"missing marker: {marker}")
    for relative in PERSISTENT_LIFECYCLE_ARTIFACTS:
        text = (root / relative).read_text(encoding="utf-8")
        for marker in BRANCH_RELATIVE_LIFECYCLE_MARKERS:
            _expect(errors, marker not in text, f"merge_stable_lifecycle.{relative}", f"must not contain branch-relative marker: {marker}")
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("target_v2_contract_revision: invalid", file=sys.stderr)
        for error in errors:
            print(f"- {error.format()}", file=sys.stderr)
        return 1
    print("target_v2_contract_revision:")
    print("  status: coherent_design_v2.1_contract")
    print("  contract_version: design-v2.1")
    print("  incorporated_refinements: [G3-R01, G3-R03, G3-R08, G3-R11, G3-Q15]")
    print("  historical_gap_count: 26")
    print("  unapproved_refinements_incorporated: 0")
    print("  runtime_implementation_authority: false")
    print("  Gate_4_authority: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
