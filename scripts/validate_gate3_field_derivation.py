#!/usr/bin/env python3
"""Validate Gate 3 design artifacts without invoking target-v2 runtime behavior."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.gate3_reference_semantics import reference_self_check
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from gate3_reference_semantics import reference_self_check


REPO_ROOT = Path(__file__).resolve().parents[1]
DERIVATION_SPEC = REPO_ROOT / "specs/review_context_field_derivation_v0_1.json"
GAP_REGISTER = REPO_ROOT / "specs/review_context_contract_gaps_v0_1.json"
CONTRACT = REPO_ROOT / "specs/review_context_contract_v2.json"
FIXTURES = REPO_ROOT / "fixtures/target-v2/gate3/design_cases.json"

REQUIRED_DOCS = {
    "docs/target-v2/gate-3-field-derivation-ledger-v0.1.md": (
        "Every required field",
        "action_id != proposal_version_id",
        "proof_verification_state",
        "complete_for_design_v2.1_contract",
    ),
    "docs/target-v2/gate-3-contract-gap-report-v0.1.md": (
        "G3-R01",
        "G3-R10",
        "G3-R11",
        "G3-Q01",
        "G3-Q14",
        "G3-Q15",
        "design_review_complete_contract_revision_incorporated",
    ),
    "docs/target-v2/context-proof-canonicalization-v0.1.md": (
        "semantic_context_material",
        "proof_record_envelope",
        "null",
        "Unicode",
        "reconstruction_unavailable",
        "RFC 8785",
        "G3-R11",
        "G3-Q15",
    ),
}

REQUIRED_RULE_KEYS = {
    "derivation_class",
    "source_authority_scope",
    "derivation_rule",
    "rule_version",
    "required_inputs",
    "missing_input_behavior",
    "unavailable_input_behavior",
    "conflict_behavior",
    "temporal_behavior",
    "record_source_segmentation",
    "sensitivity_class",
    "semantic_hash_inclusion",
    "proof_envelope_inclusion",
    "proof_disclosure",
    "cryptographic_profile_dependency",
    "reconstruction_requirement",
    "contract_gap_references",
}

EXPECTED_GAPS = {
    *(f"G3-R{index:02d}" for index in range(1, 12)),
    *(f"G3-Q{index:02d}" for index in range(1, 16)),
}

EXPECTED_APPROVED_FOR_INCORPORATION = {
    "G3-R01",
    "G3-R03",
    "G3-R08",
    "G3-R11",
    "G3-Q15",
}

UNAPPROVED_SORT_FIELD_DEPENDENCIES = {
    "authority_scope": "G3-R04",
    "treatment_status": "G3-R10",
    "applicability_status": "G3-R10",
    "applicability_scope": "not_independently_defined_in_canonical_target_v2",
}

EXPECTED_FIXTURES = {
    "complete_source_coverage",
    "partial_source_coverage",
    "required_source_unavailable",
    "unresolved_conflicting_sources",
    "missing_timestamps",
    "stale_under_profile_threshold",
    "profile_version_change",
    "proposal_revision",
    "mixed_synthetic_production_like",
    "mixed_production_like_live",
    "chronology_unknown_applicability",
    "model_claim_provenance_no_authority",
    "legacy_outcome_changes_only",
    "same_context_different_signing_key",
    "same_context_different_signature_suite",
    "later_proof_renewal",
    "algorithm_deprecation",
    "unknown_signature_algorithm",
    "cryptographic_profile_downgrade",
    "parallel_classical_pqc_attestations",
    "parallel_digest_migration",
    "missing_trusted_time_evidence",
    "invalid_proof_signature",
    "reconstruction_material_unavailable",
    "missing_external_identifier_salt",
    "canonical_numeric_normalization",
    "unicode_codepoint_preservation",
    "null_absent_projection",
    "timestamp_precision_and_timezone",
    "reference_order_and_duplicates",
    "semantic_identity_digest_continuity",
    "request_response_identity_lineage",
    "review_completeness_contract_precedence",
    "all_semantic_array_rules",
    "timestamp_unknown_offset_rejection",
    "decimal_scale_exponent_bounds",
}


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _load_json(path: Path, errors: list[ValidationError]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(ValidationError(str(path.relative_to(REPO_ROOT)), str(exc)))
        return {}
    if not isinstance(value, dict):
        errors.append(ValidationError(str(path.relative_to(REPO_ROOT)), "root must be an object"))
        return {}
    return value


def _required_response_leaf_paths(contract: dict[str, Any]) -> set[str]:
    response = contract.get("response_model", {})
    paths: set[str] = set()
    for field in response.get("required_fields", []):
        definition = response.get(field)
        nested: list[str] = []
        if isinstance(definition, dict):
            if isinstance(definition.get("required_fields"), list):
                nested = definition["required_fields"]
            elif field in {"authority_handoff", "boundary"}:
                nested = list(definition)
        if nested:
            paths.update(f"review_context_response.{field}.{child}" for child in nested)
        else:
            paths.add(f"review_context_response.{field}")
    return paths


def _resolved_rule(spec: dict[str, Any], path: str) -> dict[str, Any]:
    rule = spec.get("field_rules", {}).get(path, {})
    template = spec.get("rule_templates", {}).get(rule.get("template"), {})
    return {**template, **rule}


def _validate_contract_revision_digest(spec: dict[str, Any], errors: list[ValidationError]) -> None:
    contract_reference = spec.get("approved_contract", {})
    relative = contract_reference.get("path")
    if relative != "specs/review_context_contract_v2.json":
        errors.append(ValidationError("spec.approved_contract.path", "must identify the target-v2 machine contract"))
        return
    try:
        actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(ValidationError(f"contract_revision.{relative}", str(exc)))
        return
    if contract_reference.get("sha256") != actual:
        errors.append(ValidationError("spec.approved_contract.sha256", "must match the design-v2.1 contract"))
    if contract_reference.get("version") != "design-v2.1":
        errors.append(ValidationError("spec.approved_contract.version", "must be design-v2.1"))
    if contract_reference.get("incorporation_status") != "incorporated_in_design_v2.1_contract":
        errors.append(ValidationError("spec.approved_contract.incorporation_status", "must record design-v2.1 incorporation"))
    if contract_reference.get("canonicality_source") != "authoritative_repository_main":
        errors.append(ValidationError("spec.approved_contract.canonicality_source", "must be authoritative_repository_main"))


def _validate_docs(errors: list[ValidationError]) -> None:
    for relative, markers in REQUIRED_DOCS.items():
        path = REPO_ROOT / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(ValidationError(f"documents.{relative}", str(exc)))
            continue
        for marker in markers:
            if marker not in text:
                errors.append(ValidationError(f"documents.{relative}", f"missing marker: {marker}"))


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    """Return deterministic design-coherence errors for the repository at *root*."""

    global REPO_ROOT, DERIVATION_SPEC, GAP_REGISTER, CONTRACT, FIXTURES
    original_root = REPO_ROOT
    if root.resolve() != REPO_ROOT.resolve():
        REPO_ROOT = root.resolve()
        DERIVATION_SPEC = REPO_ROOT / "specs/review_context_field_derivation_v0_1.json"
        GAP_REGISTER = REPO_ROOT / "specs/review_context_contract_gaps_v0_1.json"
        CONTRACT = REPO_ROOT / "specs/review_context_contract_v2.json"
        FIXTURES = REPO_ROOT / "fixtures/target-v2/gate3/design_cases.json"

    errors: list[ValidationError] = []
    try:
        contract = _load_json(CONTRACT, errors)
        spec = _load_json(DERIVATION_SPEC, errors)
        gaps = _load_json(GAP_REGISTER, errors)
        fixtures = _load_json(FIXTURES, errors)

        _validate_contract_revision_digest(spec, errors)
        _validate_docs(errors)

        if spec.get("design_only") is not True:
            errors.append(ValidationError("spec.design_only", "must be true"))
        if spec.get("status") != "design_review_complete_contract_revision_incorporated":
            errors.append(ValidationError("spec.status", "must record merge-stable design-v2.1 incorporation"))
        for key in ("runtime_implementation_authority", "authority_effect", "execution_effect"):
            expected: Any = False if key == "runtime_implementation_authority" else "none"
            if spec.get(key) != expected:
                errors.append(ValidationError(f"spec.{key}", f"must be {expected!r}"))

        required_paths = _required_response_leaf_paths(contract)
        field_rules = spec.get("field_rules", {})
        present_paths = set(field_rules) if isinstance(field_rules, dict) else set()
        for path in sorted(required_paths - present_paths):
            errors.append(ValidationError(f"field_rules.{path}", "missing derivation rule"))
        for path in sorted(present_paths - required_paths):
            errors.append(ValidationError(f"field_rules.{path}", "not a required approved-contract field"))

        gap_ids = {item.get("id") for item in gaps.get("contract_refinements", []) if isinstance(item, dict)}
        prohibited = set(spec.get("prohibited_dependencies", []))
        for path in sorted(required_paths & present_paths):
            resolved = _resolved_rule(spec, path)
            missing_keys = REQUIRED_RULE_KEYS - set(resolved)
            if missing_keys:
                errors.append(ValidationError(f"field_rules.{path}", f"missing metadata: {sorted(missing_keys)}"))
            if not resolved.get("rule_version"):
                errors.append(ValidationError(f"field_rules.{path}.rule_version", "must be non-empty"))
            dependencies = set(resolved.get("dependencies", [])) | set(resolved.get("required_inputs", []))
            bad_dependencies = dependencies & prohibited
            if bad_dependencies:
                errors.append(ValidationError(f"field_rules.{path}.dependencies", f"prohibited: {sorted(bad_dependencies)}"))
            unknown_gaps = set(resolved.get("contract_gap_references", [])) - gap_ids
            if unknown_gaps:
                errors.append(ValidationError(f"field_rules.{path}.contract_gap_references", f"unknown: {sorted(unknown_gaps)}"))
            if resolved.get("sensitivity_class", "").startswith("sensitive") and resolved.get("proof_disclosure") in {"public", "raw"}:
                errors.append(ValidationError(f"field_rules.{path}.proof_disclosure", "sensitive material cannot be raw-public"))

        if gap_ids != EXPECTED_GAPS:
            errors.append(ValidationError("contract_gaps.ids", f"expected {sorted(EXPECTED_GAPS)}, got {sorted(gap_ids)}"))
        if gaps.get("status") != "design_review_complete_contract_revision_incorporated":
            errors.append(ValidationError("contract_gaps.status", "must record merge-stable design-v2.1 incorporation"))
        if gaps.get("design_review_status") != "complete":
            errors.append(ValidationError("contract_gaps.design_review_status", "must record completed design review"))
        if set(gaps.get("active_semantic_completion_blockers", [])):
            errors.append(ValidationError("contract_gaps.active_semantic_completion_blockers", "must be empty after completed design review"))
        if set(gaps.get("historical_semantic_completion_blockers", [])) != EXPECTED_APPROVED_FOR_INCORPORATION:
            errors.append(ValidationError("contract_gaps.historical_semantic_completion_blockers", "must preserve the five historical blockers"))
        if set(gaps.get("approved_for_incorporation", [])) != EXPECTED_APPROVED_FOR_INCORPORATION:
            errors.append(ValidationError("contract_gaps.approved_for_incorporation", "must contain the five reviewed refinements"))
        expected_revision = {"status": "incorporated", "target": "design-v2.1", "canonicality_source": "authoritative_repository_main"}
        if gaps.get("canonical_contract_revision") != expected_revision:
            errors.append(ValidationError("contract_gaps.canonical_contract_revision", f"must be {expected_revision!r}"))
        if gaps.get("implementation_authority") is not False:
            errors.append(ValidationError("contract_gaps.implementation_authority", "must remain false"))

        semantic_completion = spec.get("semantic_completion", {})
        if semantic_completion.get("status") != "complete_for_design_v2.1_contract":
            errors.append(ValidationError("spec.semantic_completion.status", "must record completed design-v2.1 incorporation"))
        if set(semantic_completion.get("active_review_blockers", [])):
            errors.append(ValidationError("spec.semantic_completion.active_review_blockers", "must be empty"))
        if set(semantic_completion.get("historical_review_blockers", [])) != EXPECTED_APPROVED_FOR_INCORPORATION:
            errors.append(ValidationError("spec.semantic_completion.historical_review_blockers", "must preserve the five historical blockers"))
        if set(semantic_completion.get("approved_for_incorporation", [])) != EXPECTED_APPROVED_FOR_INCORPORATION:
            errors.append(ValidationError("spec.semantic_completion.approved_for_incorporation", "must contain the five reviewed refinements"))
        for gap in gaps.get("contract_refinements", []):
            if not isinstance(gap, dict):
                errors.append(ValidationError("contract_gaps.record", "must be an object"))
                continue
            for key, expected in (("authority_effect", "none"), ("execution_effect", "none"), ("silently_canonical", False)):
                if gap.get(key) != expected:
                    errors.append(ValidationError(f"contract_gaps.{gap.get('id')}.{key}", f"must be {expected!r}"))
            if gap.get("id") in EXPECTED_APPROVED_FOR_INCORPORATION:
                approved_expectations = {
                    "semantic_completion_blocker": False,
                    "historical_semantic_completion_blocker": True,
                    "CCO_review": "approved",
                    "Architect_review": "approved",
                    "design_disposition": "approved_for_incorporation",
                    "contract_revision_target": "design-v2.1",
                    "canonical_contract_status": "incorporated_in_design_v2.1_contract",
                    "canonicality_source": "authoritative_repository_main",
                    "implementation_authority": False,
                    "requires_CCO_review": False,
                    "requires_Architect_review": False,
                }
                for key, expected in approved_expectations.items():
                    if gap.get(key) != expected:
                        errors.append(ValidationError(f"contract_gaps.{gap.get('id')}.{key}", f"must be {expected!r}"))
            else:
                for key in ("requires_CCO_review", "requires_Architect_review"):
                    if gap.get(key) is not True:
                        errors.append(ValidationError(f"contract_gaps.{gap.get('id')}.{key}", "existing lifecycle must remain review-required"))

        design_review = spec.get("design_review", {})
        expected_design_review = {
            "status": "complete",
            "CCO": "complete",
            "Architect": "complete",
            "merge_authority": False,
            "deployment_authority": False,
            "implementation_authority": False,
        }
        for key, expected in expected_design_review.items():
            if design_review.get(key) != expected:
                errors.append(ValidationError(f"spec.design_review.{key}", f"must be {expected!r}"))
        if set(design_review.get("approved_for_incorporation", [])) != EXPECTED_APPROVED_FOR_INCORPORATION:
            errors.append(ValidationError("spec.design_review.approved_for_incorporation", "must contain the five reviewed refinements"))
        if design_review.get("canonical_contract_revision") != expected_revision:
            errors.append(ValidationError("spec.design_review.canonical_contract_revision", f"must be {expected_revision!r}"))
        reviewed_spec_sections = {
            "G3-R01": spec.get("identity_model", {}),
            "G3-R03": spec.get("record_source_type_proposal", {}),
            "G3-R08": spec.get("review_completeness_proposal", {}),
            "G3-R11": spec.get("canonical_numeric_and_interoperability_profile", {}),
            "G3-Q15": spec.get("semantic_identity_continuity_proposal", {}),
        }
        for gap_id, section in reviewed_spec_sections.items():
            if section.get("status") != "incorporated_in_design_v2.1_contract":
                errors.append(ValidationError(f"spec.{gap_id}.status", "must identify incorporation in design-v2.1"))

        if set(gaps.get("additional_gaps_discovered", [])) != {"G3-R11", "G3-Q15"}:
            errors.append(ValidationError("contract_gaps.additional_gaps_discovered", "must identify G3-R11 and G3-Q15"))
        gap_by_id = {item.get("id"): item for item in gaps.get("contract_refinements", []) if isinstance(item, dict)}
        expected_new_names = {
            "G3-R11": "canonical_numeric_and_interoperability_profile",
            "G3-Q15": "semantic_identity_continuity_across_digest_migration",
        }
        for gap_id, expected_name in expected_new_names.items():
            if gap_by_id.get(gap_id, {}).get("name") != expected_name:
                errors.append(ValidationError(f"contract_gaps.{gap_id}.name", f"must be {expected_name}"))

        crypto = spec.get("cryptographic_profile_proposal", {})
        attestation = crypto.get("attestation_policy", {})
        if attestation.get("unknown_suite_behavior") != "unverifiable":
            errors.append(ValidationError("crypto.unknown_suite_behavior", "must be unverifiable"))
        if attestation.get("downgrade_behavior") != "fail_closed":
            errors.append(ValidationError("crypto.downgrade_behavior", "must fail closed"))
        if crypto.get("production_algorithm_selected") is not False:
            errors.append(ValidationError("crypto.production_algorithm_selected", "must remain false"))
        if spec.get("proof_verification_state_proposal", {}).get("separate_from") != ["context_state", "source_state", "review_completeness"]:
            errors.append(ValidationError("proof_verification_state.separate_from", "state dimensions must remain separate"))

        numeric_profile = spec.get("canonical_numeric_and_interoperability_profile", {})
        if numeric_profile.get("base_standard") != "RFC_8785_JCS":
            errors.append(ValidationError("canonical_profile.base_standard", "must evaluate and adopt RFC 8785/JCS baseline"))
        if numeric_profile.get("JCS_deviation") is not False:
            errors.append(ValidationError("canonical_profile.JCS_deviation", "exact numeric handling must be an explicit application profile, not an unqualified JCS claim"))
        if numeric_profile.get("json_numbers", {}).get("binary_float_permitted_in_semantic_material") is not False:
            errors.append(ValidationError("canonical_profile.binary_float", "must be prohibited"))
        if numeric_profile.get("monetary_amount", {}).get("rounding") != "prohibited":
            errors.append(ValidationError("canonical_profile.monetary_rounding", "must be prohibited"))
        exact_decimal = numeric_profile.get("exact_decimal", {})
        if set(exact_decimal.get("required_limits", [])) != {"max_precision", "max_scale", "max_abs_exponent", "max_input_characters"}:
            errors.append(ValidationError("canonical_profile.decimal_limits", "must require max_precision, max_scale, max_abs_exponent, and max_input_characters"))
        if exact_decimal.get("max_scale") != "field_profile_required_nonnegative_bound_applied_to_generic_canonical_scale_after_insignificant_trailing_zero_trim_or_to_fixed_declared_scale":
            errors.append(ValidationError("canonical_profile.max_scale", "generic max_scale must apply after insignificant trailing-zero trimming"))
        if exact_decimal.get("excessive_scale_or_exponent") != "reject_before_coefficient_expansion":
            errors.append(ValidationError("canonical_profile.decimal_bounds", "must reject excessive scale/exponent before expansion"))
        if exact_decimal.get("excessive_input_size") != "reject_before_numeric_parsing":
            errors.append(ValidationError("canonical_profile.decimal_input_size", "must reject excessive input size before numeric parsing"))
        if numeric_profile.get("timestamp", {}).get("unknown_offset_minus_00_00") != "reject_not_UTC_equivalent":
            errors.append(ValidationError("canonical_profile.timestamp_unknown_offset", "RFC3339 -00:00 must not normalize to UTC"))
        intended_window_path = "review_context_response.temporal_context.intended_action_window"
        intended_window_rule = numeric_profile.get("timestamp_object_rules", {}).get(intended_window_path, {})
        if intended_window_rule.get("boundary_fields") != ["start", "end"]:
            errors.append(ValidationError("canonical_profile.intended_action_window.boundaries", "must explicitly normalize start and end"))
        if intended_window_rule.get("malformed_unknown_offset_or_over_precision") != "projection_failure_never_silent_normalization":
            errors.append(ValidationError("canonical_profile.intended_action_window.failures", "invalid boundaries must fail without silent normalization"))
        intended_field_rule = field_rules.get(intended_window_path, {})
        if intended_field_rule.get("unavailable_input_behavior") != "explicit_unresolved_boundary_state_required":
            errors.append(ValidationError("field_rules.intended_action_window.unavailable", "must require explicit unresolved boundary state"))

        array_rules = numeric_profile.get("array_rules", {})
        expected_sort_tuples = {
            "source_reference_sort": ["source_id", "source_version_or_digest", "observed_at", "received_at", "record_source_type"],
            "constraint_reference_sort": ["constraint_id_or_digest", "source_id"],
            "chronology_reference_sort": ["reference_type", "reference_id", "version_or_digest"],
            "digest_record_sort": ["algorithm", "parameter_set", "output_encoding", "digest"],
        }
        sort_tuple_profiles = numeric_profile.get("sort_tuple_profiles", {})
        for profile_name, expected_tuple in expected_sort_tuples.items():
            if sort_tuple_profiles.get(profile_name) != expected_tuple:
                errors.append(ValidationError(f"canonical_profile.sort_tuple_profiles.{profile_name}", f"must be {expected_tuple!r}"))
        primary_sort_fields = {
            field
            for profile in sort_tuple_profiles.values()
            for field in (profile.get("primary", []) if isinstance(profile, dict) else profile)
        }
        for field, defining_gap in UNAPPROVED_SORT_FIELD_DEPENDENCIES.items():
            if field in primary_sort_fields:
                errors.append(ValidationError(f"canonical_profile.unapproved_sort_field.{field}", f"must exclude field owned by {defining_gap}"))
        if "normalized_item_JCS_bytes" in json.dumps(sort_tuple_profiles, sort_keys=True):
            errors.append(ValidationError("canonical_profile.whole_item_JCS_sort", "whole-item JCS bytes require a future separately approved complete canonical item schema"))
        expected_collision = {
            "identical_normalized_item": {"behavior": "collapse_when_field_is_declared_set"},
            "different_normalized_item": {"behavior": "reject_as_conflict_until_explicitly_represented"},
        }
        if numeric_profile.get("primary_tuple_collision") != expected_collision:
            errors.append(ValidationError("canonical_profile.primary_tuple_collision", "must collapse identical set items and reject distinct collisions"))
        if numeric_profile.get("whole_item_JCS_tie_breaker") != "prohibited_without_future_separately_approved_complete_canonical_item_schema":
            errors.append(ValidationError("canonical_profile.whole_item_JCS_tie_breaker", "must prohibit whole-item JCS tie-breaking"))
        semantic_array_paths = set(numeric_profile.get("semantic_array_paths", []))
        if set(array_rules) != semantic_array_paths:
            errors.append(ValidationError("canonical_profile.array_rules", "every semantic array path must have exactly one explicit rule"))
        deterministic_paths = {
            path for path, rule in field_rules.items()
            if isinstance(rule, dict) and rule.get("template") == "deterministic_collection"
        }
        if not deterministic_paths <= set(array_rules):
            errors.append(ValidationError("canonical_profile.array_rules", f"deterministic collections missing rules: {sorted(deterministic_paths - set(array_rules))}"))
        for path, rule in array_rules.items():
            if rule.get("semantics") not in {"ordered_sequence", "set", "multiset"}:
                errors.append(ValidationError(f"canonical_profile.array_rules.{path}", "semantics must be ordered_sequence, set, or multiset"))
            if rule.get("semantics") == "set" and rule.get("exact_duplicate") != "collapse":
                errors.append(ValidationError(f"canonical_profile.array_rules.{path}", "set exact duplicates must collapse"))
            sort_profile = rule.get("sort_tuple_profile")
            if sort_profile not in sort_tuple_profiles:
                errors.append(ValidationError(f"canonical_profile.array_rules.{path}.sort_tuple_profile", "must name a declared field/type-specific tuple"))

        identity = spec.get("identity_model", {})
        action_identity = identity.get("action_id", {})
        proposal_identity = identity.get("proposal_version_id", {})
        if set(identity.get("scope", [])) != {"review_context_request", "review_context_response.prepared_action_reference"}:
            errors.append(ValidationError("identity.scope", "G3-R01 must cover request and response semantics"))
        if action_identity.get("authority") != "external_institution_or_orchestrator_only" or action_identity.get("Nova_content_derivation_permitted") is not False:
            errors.append(ValidationError("identity.action_id", "action lineage must be external and never content-derived"))
        if action_identity.get("missing_behavior") != ["preserve_lineage_as_unavailable", "do_not_infer_same_action_across_revisions"]:
            errors.append(ValidationError("identity.action_id.missing_behavior", "must preserve unavailable lineage without inference"))
        fallback = proposal_identity.get("fallback", {})
        if fallback.get("material_scope") != "canonical_prepared_action_material_only" or fallback.get("algorithm_qualified") is not True or fallback.get("explicit_label_required") is not True:
            errors.append(ValidationError("identity.proposal_version_id.fallback", "Nova fallback must be labeled, algorithm-qualified, and prepared-action-only"))

        source_type = spec.get("record_source_type_proposal", {})
        if source_type.get("permitted_values") != ["synthetic", "production_like", "live", "mixed"]:
            errors.append(ValidationError("record_source_type.permitted_values", "must add mixed without changing existing values"))
        if source_type.get("source_segmentation_authoritative_for_component_provenance") is not True or source_type.get("mixed_reduction_to_strongest_or_weakest") is not False:
            errors.append(ValidationError("record_source_type.mixed", "segmentation must remain authoritative without environment ranking"))

        completeness = spec.get("review_completeness_proposal", {})
        if completeness.get("precedence") != ["unavailable", "conflicted", "partial", "complete"]:
            errors.append(ValidationError("review_completeness.precedence", "must be target-v2 contract-level unavailable, conflicted, partial, complete"))
        if completeness.get("profile_may_redefine_enum_meaning_or_precedence") is not False:
            errors.append(ValidationError("review_completeness.profile_authority", "profiles must not redefine enum meaning or precedence"))
        if set(completeness.get("complete_does_not_mean", [])) != {"policy_satisfied", "safe", "permitted", "approved", "executable"}:
            errors.append(ValidationError("review_completeness.boundary", "complete must preserve all non-authorization meanings"))
        continuity = spec.get("semantic_identity_continuity_proposal", {})
        if continuity.get("individual_algorithm_qualified_digest_is_semantic_identity") is not False:
            errors.append(ValidationError("semantic_identity_continuity.digest_is_identity", "must be false"))
        if continuity.get("historical_digest_evidence_preserved") is not True or continuity.get("same_hash_value_claim_permitted") is not False:
            errors.append(ValidationError("semantic_identity_continuity.evidence", "must preserve history and prohibit same-hash-value claims"))

        exclusions = set(spec.get("semantic_context_integrity_proposal", {}).get("semantic_hash_exclusions", []))
        required_exclusions = {"review_context_response.context_id", "review_context_response.request_id", "review_context_response.created_at", "signature_bytes", "signature_algorithm", "key_reference", "key_epoch", "proof_renewal_time"}
        if not required_exclusions <= exclusions:
            errors.append(ValidationError("semantic_hash.exclusions", f"missing: {sorted(required_exclusions - exclusions)}"))
        for path in ("review_context_response.context_id", "review_context_response.request_id", "review_context_response.created_at", "review_context_response.reproducibility.signature"):
            if _resolved_rule(spec, path).get("semantic_hash_inclusion") is not False:
                errors.append(ValidationError(f"field_rules.{path}.semantic_hash_inclusion", "generated/attestation metadata must be excluded"))

        fixture_ids = {case.get("id") for case in fixtures.get("cases", []) if isinstance(case, dict)}
        if fixtures.get("synthetic_only") is not True or fixtures.get("production_connections") is not False:
            errors.append(ValidationError("fixtures.scope", "fixtures must be synthetic and disconnected from production"))
        if fixture_ids != EXPECTED_FIXTURES:
            errors.append(ValidationError("fixtures.ids", f"missing={sorted(EXPECTED_FIXTURES - fixture_ids)} extra={sorted(fixture_ids - EXPECTED_FIXTURES)}"))
        for message in reference_self_check(spec, fixtures):
            errors.append(ValidationError("reference_semantics", message))
    finally:
        if REPO_ROOT != original_root:
            REPO_ROOT = original_root
            DERIVATION_SPEC = REPO_ROOT / "specs/review_context_field_derivation_v0_1.json"
            GAP_REGISTER = REPO_ROOT / "specs/review_context_contract_gaps_v0_1.json"
            CONTRACT = REPO_ROOT / "specs/review_context_contract_v2.json"
            FIXTURES = REPO_ROOT / "fixtures/target-v2/gate3/design_cases.json"
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("gate3_field_derivation_design: invalid", file=sys.stderr)
        for error in errors:
            print(f"- {error.format()}", file=sys.stderr)
        return 1
    spec = json.loads(DERIVATION_SPEC.read_text(encoding="utf-8"))
    gaps = json.loads(GAP_REGISTER.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    print("gate3_field_derivation_design:")
    print("  status: coherent")
    print(f"  required_response_fields_with_rules: {len(spec['field_rules'])}")
    print(f"  contract_gaps_recorded: {len(gaps['contract_refinements'])}")
    print(f"  synthetic_fixture_cases: {len(fixtures['cases'])}")
    print("  executable_reference_semantics: passed")
    print("  semantic_completion: complete_for_design_v2.1_contract")
    print("  canonical_contract_revision: incorporated_canonicality_from_authoritative_main")
    print("  runtime_implementation_authority: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
