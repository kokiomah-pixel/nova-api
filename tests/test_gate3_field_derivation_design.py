from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.gate3_reference_semantics import (
    ReferenceSemanticsError,
    build_digest_evidence,
    canonical_semantic_bytes,
    canonicalize_jcs_profile,
    evaluate_proof_verification,
    normalize_exact_decimal,
    normalize_exact_integer,
    normalize_monetary_amount,
    normalize_reference_array,
    normalize_timestamp,
    parse_json_no_duplicates,
    project_semantic_material,
    verify_semantic_identity_continuity,
)
from scripts.validate_gate3_field_derivation import (
    APPROVED_AUTHORITY_HASHES,
    EXPECTED_GAPS,
    EXPECTED_FIXTURES,
    EXPECTED_SEMANTIC_COMPLETION_BLOCKERS,
    _required_response_leaf_paths,
    validate_repository,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "specs/review_context_field_derivation_v0_1.json"
GAPS_PATH = REPO_ROOT / "specs/review_context_contract_gaps_v0_1.json"
CONTRACT_PATH = REPO_ROOT / "specs/review_context_contract_v2.json"
FIXTURE_PATH = REPO_ROOT / "fixtures/target-v2/gate3/design_cases.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return canonicalize_jcs_profile(value)


def _set_path(value: dict[str, Any], path: str, replacement: Any) -> None:
    target = value
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = replacement


def _fixture_case(case_id: str) -> dict[str, Any]:
    fixtures = _load(FIXTURE_PATH)
    return next(case for case in fixtures["cases"] if case["id"] == case_id)


def _source_state(inputs: dict[str, Any]) -> str:
    if inputs["unavailable"]:
        return "unavailable"
    if inputs["conflicts"]:
        return "conflicted"
    if not set(inputs["required"]) <= set(inputs["observed"]):
        return "partial"
    return "complete"


def test_gate3_design_validator_passes() -> None:
    assert validate_repository() == []


def test_every_required_contract_leaf_has_exactly_one_rule() -> None:
    contract = _load(CONTRACT_PATH)
    rules = _load(SPEC_PATH)["field_rules"]
    required = _required_response_leaf_paths(contract)

    assert len(required) == 54
    assert set(rules) == required
    assert all(rule["rule_version"] == "0.1.0" for rule in rules.values())


def test_approved_contract_authorities_are_unchanged() -> None:
    for relative, expected in APPROVED_AUTHORITY_HASHES.items():
        assert hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest() == expected


def test_all_refinements_are_review_gated_and_noncanonical() -> None:
    register = _load(GAPS_PATH)
    records = register["contract_refinements"]

    assert {record["id"] for record in records} == EXPECTED_GAPS
    assert all(record["requires_CCO_review"] is True for record in records)
    assert all(record["requires_Architect_review"] is True for record in records)
    assert all(record["silently_canonical"] is False for record in records)
    assert all(record["authority_effect"] == "none" for record in records)
    assert all(record["execution_effect"] == "none" for record in records)
    assert set(register["semantic_completion_blockers"]) == EXPECTED_SEMANTIC_COMPLETION_BLOCKERS
    blocker_records = {record["id"] for record in records if record.get("semantic_completion_blocker") is True}
    assert blocker_records == EXPECTED_SEMANTIC_COMPLETION_BLOCKERS
    assert set(register["additional_gaps_discovered"]) == {"G3-R11", "G3-Q15"}
    by_id = {record["id"]: record for record in records}
    assert by_id["G3-R11"]["name"] == "canonical_numeric_and_interoperability_profile"
    assert by_id["G3-Q15"]["name"] == "semantic_identity_continuity_across_digest_migration"


def test_jcs_key_order_is_invariant_and_unicode_is_preserved_as_is() -> None:
    left = {"z": "same", "a": {"two": 2, "one": 1}}
    right = {"a": {"one": 1, "two": 2}, "z": "same"}

    assert _canonical_bytes(left) == _canonical_bytes(right)
    vectors = _load(FIXTURE_PATH)["reference_vectors"]["unicode"]
    assert _canonical_bytes(vectors["composed"]) != _canonical_bytes(vectors["decomposed"])
    assert vectors["expected_equal"] is False


def test_generated_record_metadata_changes_envelope_not_semantic_identity() -> None:
    fixtures = _load(FIXTURE_PATH)
    spec = _load(SPEC_PATH)
    response_a = fixtures["reference_response"]
    response_b = copy.deepcopy(response_a)
    response_b["context_id"] = "generated-context-b"
    response_b["request_id"] = "generated-request-b"
    response_b["created_at"] = "2027-08-24T12:00:00Z"
    response_b["temporal_context"]["review_context_created_at"] = "2027-08-24T12:00:00Z"
    response_b["reproducibility"]["signature"] = "fixture-signature-b"

    assert canonical_semantic_bytes(response_a, spec) == canonical_semantic_bytes(response_b, spec)
    assert _canonical_bytes(response_a) != _canonical_bytes(response_b)
    exclusions = set(_load(SPEC_PATH)["semantic_context_integrity_proposal"]["semantic_hash_exclusions"])
    assert {"review_context_response.context_id", "review_context_response.request_id", "review_context_response.created_at"} <= exclusions


def test_proposal_revision_changes_version_and_semantic_identity_only() -> None:
    fixtures = _load(FIXTURE_PATH)
    left = fixtures["base_semantic_context"]
    right = copy.deepcopy(left)
    _set_path(right, "prepared_action_identity.proposal_version_id", "synthetic-proposal-001-v2")

    assert left["prepared_action_identity"]["action_id"] == right["prepared_action_identity"]["action_id"]
    assert left["prepared_action_identity"]["proposal_version_id"] != right["prepared_action_identity"]["proposal_version_id"]
    assert _canonical_bytes(left) != _canonical_bytes(right)


def test_profile_version_change_is_visible_and_explainable() -> None:
    fixtures = _load(FIXTURE_PATH)
    left = fixtures["base_semantic_context"]
    right = copy.deepcopy(left)
    _set_path(right, "review_profile_reference.profile_version", "2")
    _set_path(right, "review_profile_reference.profile_hash.digest", "profile-v2")

    assert _canonical_bytes(left) != _canonical_bytes(right)
    case = _fixture_case("profile_version_change")
    assert case["expected"]["completeness_change_explained_by"] == "profile_version"


def test_source_state_precedence_is_deterministic_and_conflicts_have_no_winner() -> None:
    expected = {
        "complete_source_coverage": "complete",
        "partial_source_coverage": "partial",
        "required_source_unavailable": "unavailable",
        "unresolved_conflicting_sources": "conflicted",
    }
    for case_id, state in expected.items():
        case = _fixture_case(case_id)
        assert _source_state(case["inputs"]) == state
        assert case["expected"]["source_state"] == state
    assert _fixture_case("unresolved_conflicting_sources")["expected"]["Nova_selects_winner"] is False


def test_missing_timestamp_is_never_current_and_profile_threshold_is_deterministic() -> None:
    missing = _fixture_case("missing_timestamps")
    stale = _fixture_case("stale_under_profile_threshold")

    assert missing["inputs"]["observed_at"] is None
    assert missing["expected"] == {"context_state": "uncertain", "current": False}
    assert stale["inputs"]["age_seconds"] > stale["inputs"]["profile_max_age_seconds"]
    assert stale["expected"]["context_state"] == "stale"
    assert stale["expected"]["threshold_authority"] == "review_profile"


def test_mixed_source_packets_preserve_segments_without_live_promotion() -> None:
    synthetic_mix = _fixture_case("mixed_synthetic_production_like")
    live_mix = _fixture_case("mixed_production_like_live")

    assert synthetic_mix["expected"]["segmentation_preserved"] is True
    assert synthetic_mix["expected"]["promoted_to_live"] is False
    assert live_mix["expected"]["segmentation_preserved"] is True
    assert live_mix["expected"]["production_like_promoted"] is False


def test_legacy_outcome_change_cannot_change_target_semantic_context() -> None:
    fixtures = _load(FIXTURE_PATH)
    semantic = fixtures["base_semantic_context"]
    allow_input = {"semantic": semantic, "legacy": {"decision_status": "ALLOW"}}
    halt_input = {"semantic": semantic, "legacy": {"decision_status": "HALT"}}

    assert _canonical_bytes(allow_input["semantic"]) == _canonical_bytes(halt_input["semantic"])
    assert _fixture_case("legacy_outcome_changes_only")["expected"]["target_field_change"] is False
    prohibited = set(_load(SPEC_PATH)["prohibited_dependencies"])
    assert {"Legacy_v1_outcome", "decision_status", "ALLOW", "HALT"} <= prohibited


def test_chronology_and_model_claims_preserve_nonauthority_boundaries() -> None:
    chronology = _fixture_case("chronology_unknown_applicability")
    claim = _fixture_case("model_claim_provenance_no_authority")

    assert chronology["expected"]["chronology_write"] is False
    assert chronology["expected"]["applicability_inferred"] is False
    assert claim["expected"]["genesis_visible"] is True
    assert claim["expected"]["authority_effect"] == "none"


def test_key_suite_and_renewal_changes_preserve_semantic_identity() -> None:
    fixtures = _load(FIXTURE_PATH)
    spec = _load(SPEC_PATH)
    response = fixtures["reference_response"]
    semantic_bytes = canonical_semantic_bytes(response, spec)
    envelope = fixtures["base_proof_envelope"]
    variants = []
    for path, replacement in (
        ("attestation.key_reference", "fixture-key-b"),
        ("attestation.signature_algorithm", "fixture-suite-b"),
        ("created_at", "2027-08-24T12:00:00Z"),
    ):
        variant = copy.deepcopy(envelope)
        _set_path(variant, path, replacement)
        variants.append(variant)

    assert all(semantic_bytes == canonical_semantic_bytes(copy.deepcopy(response), spec) for _ in variants)
    assert all(_canonical_bytes(envelope) != _canonical_bytes(variant) for variant in variants)
    assert _load(SPEC_PATH)["proof_renewal_proposal"]["semantic_context_mutated"] is False


def test_crypto_failures_change_proof_state_without_collapsing_context_dimensions() -> None:
    dimensions = {"context_state": "current", "source_state": "complete", "review_completeness": "partial"}
    deprecated = evaluate_proof_verification(suite_status="deprecated", signature_valid=True, presented_profile_version=2, required_profile_version=2, **dimensions)
    unknown = evaluate_proof_verification(suite_status="unknown", signature_valid=None, presented_profile_version=2, required_profile_version=2, **dimensions)
    invalid = evaluate_proof_verification(suite_status="permitted", signature_valid=False, presented_profile_version=2, required_profile_version=2, **dimensions)
    downgrade = evaluate_proof_verification(suite_status="permitted", signature_valid=True, presented_profile_version=1, required_profile_version=2, **dimensions)

    assert deprecated["proof_verification_state"] == "verified_with_deprecated_suite"
    assert unknown["proof_verification_state"] == "unverifiable"
    assert invalid["proof_verification_state"] == "invalid"
    assert downgrade["proof_verification_state"] == "unverifiable"
    assert downgrade["downgrade_detected"] is True
    assert downgrade["downgrade_behavior"] == "fail_closed"
    for result in (deprecated, unknown, invalid, downgrade):
        assert {key: result[key] for key in dimensions} == dimensions


def test_parallel_attestations_and_digests_bind_one_semantic_context() -> None:
    attestations = _fixture_case("parallel_classical_pqc_attestations")["expected"]
    fixtures = _load(FIXTURE_PATH)
    semantic_bytes = canonical_semantic_bytes(fixtures["reference_response"], _load(SPEC_PATH))
    digesters = {
        "fixture-digest-a": lambda value: f"a:{sum(value) % 1_000_003}",
        "fixture-digest-b": lambda value: f"b:{len(value)}:{sum(reversed(value)) % 1_000_033}",
    }
    evidence = build_digest_evidence(semantic_bytes, digesters)
    continuity = verify_semantic_identity_continuity([semantic_bytes, semantic_bytes], evidence, digesters)

    assert attestations["semantic_identity_count"] == 1
    assert attestations["production_suite_selected"] is False
    assert continuity["continuous"] is True
    assert continuity["canonical_semantic_bytes_identical"] is True
    assert continuity["historical_digest_evidence_preserved"] is True
    assert continuity["digest_values_are_semantic_identity"] is False
    assert len(set(continuity["digest_values"])) == 2
    changed = semantic_bytes + b"changed"
    assert verify_semantic_identity_continuity([semantic_bytes, changed], evidence, digesters) == {"continuous": False, "reason": "canonical_semantic_bytes_changed"}


def test_numeric_decimal_and_monetary_reference_semantics_are_exact() -> None:
    vectors = _load(FIXTURE_PATH)["reference_vectors"]

    assert normalize_exact_integer(vectors["integer"]["negative_zero_input"], max_digits=10) == vectors["integer"]["negative_zero_expected"]
    with pytest.raises(ReferenceSemanticsError, match="without exponent or leading zeros"):
        normalize_exact_integer(vectors["integer"]["input"], max_digits=10)
    assert normalize_exact_decimal(vectors["decimal"]["input"], max_precision=vectors["decimal"]["max_precision"]) == vectors["decimal"]["expected"]
    assert normalize_exact_decimal(vectors["decimal_exponent"]["input"], max_precision=vectors["decimal_exponent"]["max_precision"]) == vectors["decimal_exponent"]["expected"]
    money = vectors["monetary_amount"]
    assert normalize_monetary_amount(money["input"], asset_id=money["asset_id"], scale=money["scale"], max_precision=money["max_precision"]) == money["expected"]
    with pytest.raises(ReferenceSemanticsError, match="rounding is prohibited"):
        normalize_monetary_amount("1.001", asset_id="SYNTH-USD", scale=2, max_precision=10)
    with pytest.raises(ReferenceSemanticsError, match="binary/implicit decimal"):
        canonicalize_jcs_profile({"amount": 1.25})
    assert canonicalize_jcs_profile(normalize_exact_decimal("1.2300", max_precision=10)) == canonicalize_jcs_profile(normalize_exact_decimal("1.23", max_precision=10))


def test_null_and_absent_are_distinct_and_required_absence_fails_projection() -> None:
    case = _fixture_case("null_absent_projection")

    assert canonicalize_jcs_profile(case["inputs"]["null_object"]) != canonicalize_jcs_profile(case["inputs"]["absent_object"])
    fixtures = _load(FIXTURE_PATH)
    response = copy.deepcopy(fixtures["reference_response"])
    del response["source_state"]["value"]
    with pytest.raises(ReferenceSemanticsError, match="required semantic field absent"):
        project_semantic_material(response, _load(SPEC_PATH))
    null_response = copy.deepcopy(fixtures["reference_response"])
    null_response["source_state"]["value"] = None
    with pytest.raises(ReferenceSemanticsError, match="null is not declared"):
        project_semantic_material(null_response, _load(SPEC_PATH))


def test_timestamp_normalization_is_utc_fixed_precision_and_never_rounds() -> None:
    vector = _load(FIXTURE_PATH)["reference_vectors"]["timestamp"]

    assert normalize_timestamp(vector["input"]) == vector["expected"]
    assert normalize_timestamp("2026-08-24T12:00:00.1Z") == "2026-08-24T12:00:00.100000Z"
    with pytest.raises(ReferenceSemanticsError, match="rounding is prohibited"):
        normalize_timestamp("2026-08-24T12:00:00.1234567Z")
    with pytest.raises(ReferenceSemanticsError, match="explicit offset"):
        normalize_timestamp("2026-08-24T12:00:00")


def test_reference_ordering_exact_deduplication_and_identity_collision() -> None:
    vector = _load(FIXTURE_PATH)["reference_vectors"]["references"]

    assert normalize_reference_array(vector["input"], identity_key="source_id") == vector["expected"]
    conflict = [{"source_id": "a", "value": 1}, {"source_id": "a", "value": 2}]
    with pytest.raises(ReferenceSemanticsError, match="conflicting duplicate reference identity"):
        normalize_reference_array(conflict, identity_key="source_id")
    with pytest.raises(ReferenceSemanticsError, match="duplicate object member"):
        parse_json_no_duplicates('{"a":1,"a":1}')


def test_projection_applies_declared_timestamp_and_reference_array_rules() -> None:
    fixtures = _load(FIXTURE_PATH)
    spec = _load(SPEC_PATH)
    projected = project_semantic_material(fixtures["reference_response"], spec)["review_context_response"]

    assert projected["temporal_context"]["source_observed_at"] == "2026-08-24T12:00:00.000000Z"
    assert [item["source_id"] for item in projected["source_state"]["sources"]] == ["source-a", "source-b"]
    assert projected["reproducibility"]["source_versions"] == ["source-a:v1", "source-b:v1"]
    assert "context_id" not in projected
    assert "request_id" not in projected
    assert "created_at" not in projected
    assert "signature" not in projected["reproducibility"]
    assert "context_hash" not in projected["reproducibility"]


def test_time_reconstruction_and_redaction_fail_closed() -> None:
    time_case = _fixture_case("missing_trusted_time_evidence")["expected"]
    reconstruction = _fixture_case("reconstruction_material_unavailable")["expected"]
    salt = _fixture_case("missing_external_identifier_salt")["expected"]

    assert time_case == {"trusted_time_claim": False, "verification_status": "unresolved"}
    assert reconstruction == {"reconstruction_scope": "reconstruction_unavailable", "full_reconstruction_claim": False}
    assert salt == {"output": "redacted", "raw_value_substituted": False}


def test_fixture_inventory_is_complete_and_synthetic() -> None:
    fixtures = _load(FIXTURE_PATH)

    assert fixtures["synthetic_only"] is True
    assert fixtures["production_connections"] is False
    assert {case["id"] for case in fixtures["cases"]} == EXPECTED_FIXTURES
