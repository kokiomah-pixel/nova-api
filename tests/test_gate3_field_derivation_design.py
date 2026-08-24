from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

from scripts.validate_gate3_field_derivation import (
    APPROVED_AUTHORITY_HASHES,
    EXPECTED_GAPS,
    EXPECTED_FIXTURES,
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


def _normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", str(key)): _normalized(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalized(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


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


def test_canonical_key_order_and_unicode_normalization_are_stable() -> None:
    left = {"z": "e\u0301", "a": {"two": 2, "one": 1}}
    right = {"a": {"one": 1, "two": 2}, "z": "é"}

    assert _canonical_bytes(left) == _canonical_bytes(right)


def test_generated_record_metadata_changes_envelope_not_semantic_identity() -> None:
    fixtures = _load(FIXTURE_PATH)
    semantic = fixtures["base_semantic_context"]
    envelope_a = fixtures["base_proof_envelope"]
    envelope_b = copy.deepcopy(envelope_a)
    envelope_b["context_id"] = "generated-context-b"
    envelope_b["request_id"] = "generated-request-b"
    envelope_b["created_at"] = "2027-08-24T12:00:00Z"

    assert _canonical_bytes(semantic) == _canonical_bytes(copy.deepcopy(semantic))
    assert _canonical_bytes(envelope_a) != _canonical_bytes(envelope_b)
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
    semantic = fixtures["base_semantic_context"]
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

    assert all(_canonical_bytes(semantic) == _canonical_bytes(copy.deepcopy(semantic)) for _ in variants)
    assert all(_canonical_bytes(envelope) != _canonical_bytes(variant) for variant in variants)
    assert _load(SPEC_PATH)["proof_renewal_proposal"]["semantic_context_mutated"] is False


def test_crypto_failures_change_proof_state_without_collapsing_context_dimensions() -> None:
    deprecated = _fixture_case("algorithm_deprecation")["expected"]
    unknown = _fixture_case("unknown_signature_algorithm")["expected"]
    invalid = _fixture_case("invalid_proof_signature")["expected"]
    downgrade = _fixture_case("cryptographic_profile_downgrade")["expected"]

    assert deprecated["historical_attestation_preserved"] is True
    assert deprecated["context_state_automatic_change"] is False
    assert unknown == {"proof_verification_state": "unverifiable", "silent_success": False}
    assert invalid["proof_verification_state"] == "invalid"
    assert invalid["context_state_automatic_change"] is False
    assert invalid["source_state_automatic_change"] is False
    assert invalid["review_completeness_automatic_change"] is False
    assert downgrade == {"downgrade_detected": True, "fallback": "fail_closed"}


def test_parallel_attestations_and_digests_bind_one_semantic_context() -> None:
    attestations = _fixture_case("parallel_classical_pqc_attestations")["expected"]
    digests = _fixture_case("parallel_digest_migration")["expected"]

    assert attestations["semantic_identity_count"] == 1
    assert attestations["production_suite_selected"] is False
    assert digests["canonical_semantic_bytes_identical"] is True
    assert digests["semantic_material_count"] == 1


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
