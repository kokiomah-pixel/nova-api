import copy
import hashlib
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from core.architect_data_operations import (
    apply_field_allowlist,
    apply_severity_policy,
    build_proof_registry_pilot_evidence,
    classify_live_provenance,
    generate_canonical_snapshot,
    hash_permitted_identifier,
    load_runtime_evidence_policy,
    validate_source_authorization,
)


POLICY_PATH = Path("config/architect_data_operations_policy.yaml")
POLICY_SCHEMA_PATH = Path("specs/architect_data_operations_policy.schema.json")
GENERATED_AT = "2026-07-17T12:00:00Z"


def _policy_copy(tmp_path, mutate=None):
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    if mutate:
        mutate(policy)
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
    return path


def _proof_registry(tmp_path, *, created_at="2026-07-17T11:30:00Z"):
    path = tmp_path / ".proof_registry.json"
    path.write_text(
        json.dumps(
            {
                "proof-raw-id-001": {
                    "decision_id": "decision-raw-id-001",
                    "created_at": created_at,
                    "reproducibility_hash": "repro-hash-001",
                    "proof": {
                        "validation": {
                            "reproducibility_hash": "repro-hash-001"
                        }
                    },
                    "normalized_request": {
                        "asset": "ETH",
                        "intent": "trade"
                    },
                    "raw_payload": {
                        "secret": "do-not-emit"
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def _eligible_proof_registry(tmp_path):
    path = tmp_path / ".proof_registry.json"
    path.write_text(
        json.dumps(
            {
                "proof-raw-id-eligible": {
                    "decision_id": "decision-raw-id-eligible",
                    "request_id": "request-raw-id-eligible",
                    "chronology_record_id": "chronology-raw-id-eligible",
                    "raw_external_identifier": "external-raw-id-eligible",
                    "created_at": "2026-07-17T11:30:00Z",
                    "data_mode": "offline_fixture",
                    "source_class": "synthetic",
                    "live_provenance_verified": False,
                    "authority_effect": "none",
                    "nova_execution_attempted": False,
                    "reproducibility_hash": "eligible-repro-hash",
                    "unexpected_runtime_note": "unknown-field-value-must-not-emit",
                    "proof": {
                        "decision_id": "decision-raw-id-eligible",
                        "validation": {
                            "reproducibility_hash": "eligible-repro-hash"
                        }
                    },
                    "normalized_request": {
                        "asset": "ETH",
                        "intent": "trade"
                    },
                },
                "proof-raw-id-old": {
                    "decision_id": "decision-raw-id-old",
                    "created_at": "2026-07-15T11:30:00Z",
                    "data_mode": "offline_fixture",
                    "source_class": "synthetic",
                    "authority_effect": "none",
                    "reproducibility_hash": "old-repro-hash",
                    "proof": {
                        "validation": {
                            "reproducibility_hash": "old-repro-hash"
                        }
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_policy_schema_accepts_machine_readable_policy():
    schema = json.loads(POLICY_SCHEMA_PATH.read_text(encoding="utf-8"))
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

    validate(instance=policy, schema=schema)


def test_policy_required_before_runtime_ingestion(tmp_path):
    with pytest.raises(ValueError, match="policy is required"):
        build_proof_registry_pilot_evidence(policy_path=tmp_path / "missing.yaml", repo_root=tmp_path)


def test_invalid_policy_fails_closed(tmp_path):
    policy_path = _policy_copy(
        tmp_path,
        lambda policy: policy["runtime_evidence_policy"]["activation"].__setitem__("runtime_mutation_allowed", True),
    )

    with pytest.raises((ValueError, ValidationError)):
        load_runtime_evidence_policy(policy_path)


def test_unapproved_source_rejected():
    policy = load_runtime_evidence_policy(POLICY_PATH)

    with pytest.raises(ValueError, match="not approved"):
        validate_source_authorization(policy, "wallet_surveillance")


def test_allowlist_drops_unknown_fields():
    clean, unexpected, rejected = apply_field_allowlist(
        {"proof_id": "p1", "surprise": "drop-me"},
        ["proof_id"],
        ["raw_payload"],
    )

    assert clean == {"proof_id": "p1"}
    assert unexpected == ["surprise"]
    assert rejected == []


def test_prohibited_field_not_emitted():
    clean, _unexpected, rejected = apply_field_allowlist(
        {"proof_id": "p1", "raw_payload": "secret"},
        ["proof_id"],
        ["raw_payload"],
    )

    assert clean == {"proof_id": "p1"}
    assert rejected == ["raw_payload"]


def test_raw_identifier_not_emitted_without_salt(tmp_path):
    registry = _proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    snapshot_text = json.dumps(generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path))

    assert "proof-raw-id-001" not in snapshot_text
    assert "decision-raw-id-001" not in snapshot_text
    assert "redacted" in snapshot_text


def test_identifier_hash_requires_external_salt():
    missing = hash_permitted_identifier("decision-1", None)
    hashed = hash_permitted_identifier("decision-1", "external-test-salt")

    assert missing["value"] == "redacted"
    assert missing["reason"] == "identifier_hash_policy_not_configured"
    assert hashed["value"].startswith("sha256:")


def test_unverified_live_record_downgraded_to_unknown():
    policy = load_runtime_evidence_policy(POLICY_PATH)

    assert classify_live_provenance({"source_class": "live"}, policy) == "unknown"


def test_fixture_record_never_classified_live():
    policy = load_runtime_evidence_policy(POLICY_PATH)

    assert classify_live_provenance({"source_class": "offline_fixture"}, policy) == "synthetic"


def test_observation_window_filters_records(tmp_path):
    registry = _proof_registry(tmp_path, created_at="2026-07-15T11:30:00Z")
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
        identifier_salt="external-test-salt",
    )

    assert evidence["records"] == []


def test_historical_linked_record_not_counted_as_current_volume(tmp_path):
    registry = _proof_registry(tmp_path, created_at="2026-07-15T11:30:00Z")
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
        identifier_salt="external-test-salt",
    )
    snapshot = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)
    root = snapshot["architect_data_operations_snapshot"]

    assert root["snapshot_identity"]["input_record_count"] == 0
    assert root["runtime_observation"]["records_ingested"] == 0


def test_repeated_anomaly_requires_independent_records():
    assert apply_severity_policy("proof_verification_failure", 3, 1) == "watch"
    assert apply_severity_policy("proof_verification_failure", 3, 2) == "material"


def test_authority_effect_other_than_none_is_critical(tmp_path):
    registry = tmp_path / ".proof_registry.json"
    registry.write_text(
        json.dumps(
            {
                "proof-001": {
                    "decision_id": "decision-001",
                    "created_at": "2026-07-17T11:30:00Z",
                    "authority_effect": "approval",
                    "reproducibility_hash": "hash",
                    "proof": {"validation": {"reproducibility_hash": "hash"}},
                }
            }
        ),
        encoding="utf-8",
    )
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
        identifier_salt="external-test-salt",
    )
    snapshot = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)
    anomalies = snapshot["architect_data_operations_snapshot"]["anomalies"]

    assert any(anomaly["anomaly_type"] == "authority_effect_invalid" and anomaly["severity"] == "critical" for anomaly in anomalies)


def test_source_file_not_modified(tmp_path):
    registry = _proof_registry(tmp_path)
    before = _sha256(registry)

    build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
        identifier_salt="external-test-salt",
    )

    assert _sha256(registry) == before


def test_generated_snapshot_contains_no_raw_payload(tmp_path):
    registry = _proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
        identifier_salt="external-test-salt",
    )
    snapshot_text = json.dumps(generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path))

    assert "normalized_request" not in snapshot_text
    assert "do-not-emit" not in snapshot_text


def test_no_external_alert_delivery():
    policy = load_runtime_evidence_policy(POLICY_PATH)

    assert policy["runtime_evidence_policy"]["notification_policy"]["automatic_delivery"] is False
    assert policy["runtime_evidence_policy"]["activation"]["external_alert_delivery_enabled"] is False


def test_no_records_ingested_means_health_unknown(tmp_path):
    registry = _proof_registry(tmp_path, created_at="2026-07-15T11:30:00Z")
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    root = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)["architect_data_operations_snapshot"]

    assert root["service_health"]["status"]["value"] == "unknown"
    assert root["proof_health"]["status"]["value"] == "unknown"


def test_valid_policy_clears_policy_dependency_list(tmp_path):
    registry = _proof_registry(tmp_path, created_at="2026-07-15T11:30:00Z")
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    root = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)["architect_data_operations_snapshot"]

    assert root["policy_status"] == "loaded_and_validated"
    assert root["policy_dependencies"]["unresolved"] == []


def test_eligible_proof_record_is_ingested(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    root = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)["architect_data_operations_snapshot"]

    assert len(evidence["records"]) == 1
    assert root["runtime_observation"]["records_ingested"] == 1
    assert root["runtime_observation"]["status"] == "partial_records_ingested"
    assert root["proof_health"]["records_ingested"]["value"] == 1


def test_out_of_window_proof_record_is_excluded_from_current_volume(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    snapshot_text = json.dumps(generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path))

    assert len(evidence["records"]) == 1
    assert "old-repro-hash" not in snapshot_text
    assert "proof-raw-id-old" not in snapshot_text


def test_missing_external_salt_redacts_identifier_for_eligible_record(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    record = evidence["records"][0]

    assert record["proof_id_hash"]["value"] == "redacted"
    assert record["proof_id_hash"]["evidence_state"] == "unavailable"
    assert record["proof_id_hash"]["reason"] == "identifier_hash_policy_not_configured"


def test_raw_identifier_never_reaches_eligible_snapshot(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    snapshot_text = json.dumps(generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path))

    assert "proof-raw-id-eligible" not in snapshot_text
    assert "decision-raw-id-eligible" not in snapshot_text
    assert "request-raw-id-eligible" not in snapshot_text
    assert "chronology-raw-id-eligible" not in snapshot_text
    assert "external-raw-id-eligible" not in snapshot_text
    assert "raw_external_identifier" not in snapshot_text


def test_real_shape_unknown_fields_are_dropped_with_field_name_only(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    snapshot = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)
    snapshot_text = json.dumps(snapshot)

    assert "unknown-field-value-must-not-emit" not in snapshot_text
    assert "unexpected_runtime_note" in snapshot_text
    assert any(
        anomaly["anomaly_type"] == "unexpected_source_field"
        for anomaly in snapshot["architect_data_operations_snapshot"]["anomalies"]
    )


def test_original_registry_hash_remains_unchanged_for_eligible_validation(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    before = _sha256(registry)

    build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )

    assert _sha256(registry) == before


def test_one_record_does_not_establish_full_service_health(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    root = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)["architect_data_operations_snapshot"]

    assert root["service_health"]["status"]["value"] == "unknown"
    assert root["chronology_health"]["status"]["value"] == "unknown"
    assert root["live_operating_health_established"] is False


def test_proof_health_scope_is_limited_to_observed_record(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    root = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)["architect_data_operations_snapshot"]

    assert root["proof_health"]["scope"]["value"] == "bounded_to_observed_record"
    assert root["proof_health"]["production_health_claim_supported"] is False


def test_eligible_fixture_record_is_not_classified_live(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    record = evidence["records"][0]

    assert record["source_class"] == "synthetic"
    assert record["live_provenance_verified"] is False


def test_eligible_record_preserves_non_authority_boundary(tmp_path):
    registry = _eligible_proof_registry(tmp_path)
    evidence = build_proof_registry_pilot_evidence(
        policy_path=POLICY_PATH,
        repo_root=tmp_path,
        generated_at=GENERATED_AT,
        proof_registry_path=registry,
    )
    snapshot = generate_canonical_snapshot(evidence, generated_at=GENERATED_AT, repo_root=tmp_path)
    record = evidence["records"][0]

    assert record["authority_effect"] == "none"
    assert record["nova_execution_attempted"] is False
    assert not any(
        anomaly["anomaly_type"] in {"execution_boundary_violation", "authority_effect_invalid"}
        for anomaly in snapshot["architect_data_operations_snapshot"]["anomalies"]
    )
