import json
from pathlib import Path

from jsonschema import validate

from core.architect_data_operations import (
    build_bounded_runtime_evidence,
    generate_canonical_snapshot,
    load_bounded_evidence,
    render_architect_brief,
)


FIXTURE_ROOT = Path("fixtures/operations/architect_data_operations")
SCHEMA_PATH = Path("specs/architect_data_operations_snapshot.schema.json")
GENERATED_AT = "2026-07-16T12:00:00Z"


def _load_fixture(name):
    return load_bounded_evidence(FIXTURE_ROOT / f"{name}.json")


def _snapshot(evidence, tmp_path):
    return generate_canonical_snapshot(
        evidence,
        generated_at=GENERATED_AT,
        repo_root=tmp_path,
    )


def _root(snapshot):
    return snapshot["architect_data_operations_snapshot"]


def _anomaly_types(snapshot):
    return {anomaly["anomaly_type"] for anomaly in _root(snapshot)["anomalies"]}


def _anomaly(snapshot, anomaly_type):
    return next(anomaly for anomaly in _root(snapshot)["anomalies"] if anomaly["anomaly_type"] == anomaly_type)


def test_snapshot_schema_accepts_generated_fixture_snapshot(tmp_path):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    snapshot = _snapshot(_load_fixture("healthy_offline_observation_window"), tmp_path)

    validate(instance=snapshot, schema=schema)


def test_deterministic_snapshot_for_equivalent_inputs(tmp_path):
    evidence = _load_fixture("healthy_offline_observation_window")
    first = _snapshot(evidence, tmp_path)
    second = _snapshot(dict(reversed(list(evidence.items()))), tmp_path)

    assert _root(first)["snapshot_identity"]["canonical_hash"] == _root(second)["snapshot_identity"]["canonical_hash"]


def test_unknown_used_when_evidence_missing(tmp_path):
    snapshot = _snapshot(_load_fixture("no_observations"), tmp_path)

    assert _root(snapshot)["service_health"]["status"]["value"] == "unknown"
    assert _root(snapshot)["service_health"]["status"]["evidence_state"] == "unknown"


def test_no_rate_when_denominator_zero(tmp_path):
    snapshot = _snapshot(_load_fixture("no_observations"), tmp_path)

    proof_rate = _root(snapshot)["proof_health"]["proof_verification_rate"]
    replay_rate = _root(snapshot)["proof_health"]["replay_rate"]
    assert proof_rate["value"] is None
    assert proof_rate["reason"] == "no_observations"
    assert replay_rate["value"] is None
    assert replay_rate["reason"] == "no_observations"


def test_live_source_requires_verified_provenance(tmp_path):
    evidence = {
        "data_mode": "live",
        "records": [
            {
                "record_id": "unverified-live",
                "source_class": "live",
                "data_mode": "live",
                "live_provenance_verified": False,
                "provenance_complete": True,
                "authority_effect": "none",
            }
        ],
    }

    snapshot = _snapshot(evidence, tmp_path)

    assert _root(snapshot)["intake_health"]["source_classes"]["live"]["value"] == 0
    assert _root(snapshot)["intake_health"]["source_classes"]["unknown"]["value"] == 1


def test_expected_classification_change_not_labeled_drift(tmp_path):
    snapshot = _snapshot(_load_fixture("expected_governance_epoch_change"), tmp_path)

    assert "unexplained_classification_drift" not in _anomaly_types(snapshot)
    assert _root(snapshot)["context_health"]["expected_classification_changes"]["value"] == 1


def test_unexplained_classification_change_labeled_drift(tmp_path):
    snapshot = _snapshot(_load_fixture("unexplained_classification_drift"), tmp_path)

    assert "unexplained_classification_drift" in _anomaly_types(snapshot)


def test_proof_failure_detected(tmp_path):
    snapshot = _snapshot(_load_fixture("proof_replay_failure"), tmp_path)

    assert "proof_verification_failure" in _anomaly_types(snapshot)
    assert _root(snapshot)["proof_health"]["proof_verification_failed"]["value"] == 1


def test_replay_failure_detected(tmp_path):
    snapshot = _snapshot(_load_fixture("proof_replay_failure"), tmp_path)

    assert "replay_failure" in _anomaly_types(snapshot)
    assert _root(snapshot)["proof_health"]["replay_failed"]["value"] == 1


def test_chronology_failure_detected(tmp_path):
    snapshot = _snapshot(_load_fixture("chronology_link_failure"), tmp_path)

    assert "chronology_link_failure" in _anomaly_types(snapshot)
    assert _root(snapshot)["chronology_health"]["chronology_link_failures"]["value"] == 1


def test_invalid_authority_effect_is_critical(tmp_path):
    snapshot = _snapshot(_load_fixture("invalid_authority_effect"), tmp_path)
    anomaly = _anomaly(snapshot, "authority_effect_invalid")

    assert anomaly["severity"] == "critical"
    assert anomaly["Architect_notification"] is True
    assert _root(snapshot)["Architect_action"]["required"] is True


def test_execution_attempt_is_critical(tmp_path):
    evidence = _load_fixture("healthy_offline_observation_window")
    evidence["records"][0]["nova_execution_attempted"] = True

    snapshot = _snapshot(evidence, tmp_path)
    anomaly = _anomaly(snapshot, "execution_boundary_violation")

    assert anomaly["severity"] == "critical"
    assert anomaly["Architect_notification"] is True


def test_repeated_watch_anomaly_becomes_notification(tmp_path):
    evidence = {
        "data_mode": "offline_fixture",
        "records": [
            {
                "record_id": f"missing-{index}",
                "observed_at": f"2026-07-16T10:0{index}:00Z",
                "source_class": "synthetic",
                "data_mode": "offline_fixture",
                "live_provenance_verified": False,
                "provenance_missing": True,
                "authority_effect": "none",
            }
            for index in range(3)
        ],
    }

    snapshot = _snapshot(evidence, tmp_path)
    anomaly = _anomaly(snapshot, "source_provenance_missing")

    assert anomaly["severity"] == "watch"
    assert anomaly["Architect_notification"] is True
    assert _root(snapshot)["Architect_action"]["required"] is True


def test_isolated_noncritical_anomaly_remains_quiet(tmp_path):
    snapshot = _snapshot(_load_fixture("missing_provenance"), tmp_path)
    anomaly = _anomaly(snapshot, "source_provenance_missing")

    assert anomaly["Architect_notification"] is False
    assert _root(snapshot)["Architect_action"]["required"] is False
    assert _root(snapshot)["quiet_tracking"]


def test_sensitive_payload_not_emitted(tmp_path):
    evidence = {
        "data_mode": "offline_fixture",
        "records": [
            {
                "record_id": "sensitive-record",
                "source_class": "synthetic",
                "data_mode": "offline_fixture",
                "live_provenance_verified": False,
                "provenance_complete": True,
                "authority_effect": "none",
                "api_key": "secret-token-value-that-should-not-appear",
                "raw_payload": {
                    "wallet_credentials": "private"
                },
            }
        ],
    }

    snapshot_text = json.dumps(_snapshot(evidence, tmp_path), sort_keys=True)

    assert "secret-token-value-that-should-not-appear" not in snapshot_text
    assert "wallet_credentials" not in snapshot_text


def test_markdown_brief_matches_snapshot_action_state(tmp_path):
    snapshot = _snapshot(_load_fixture("invalid_authority_effect"), tmp_path)
    brief = render_architect_brief(snapshot)

    assert "Architect action is required" in brief
    assert "required: true" in brief
    assert "authority_effect_invalid" in brief


def test_markdown_brief_avoids_all_systems_normal_language(tmp_path):
    snapshot = _snapshot(_load_fixture("healthy_offline_observation_window"), tmp_path)
    brief = render_architect_brief(snapshot)

    assert "all systems normal" not in brief.lower()
    assert "No decision-relevant anomaly was observed in the available evidence." in brief


def test_bounded_runtime_mode_does_not_simulate_live_records(tmp_path):
    snapshot = _snapshot(build_bounded_runtime_evidence(), tmp_path)

    assert _root(snapshot)["environment"] == "bounded_runtime"
    assert _root(snapshot)["data_mode"] == "unknown"
    assert _root(snapshot)["snapshot_identity"]["input_record_count"] == 0
    assert _root(snapshot)["service_health"]["requests_observed"]["value"] == 0
