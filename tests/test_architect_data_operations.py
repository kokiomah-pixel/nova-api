import json
from pathlib import Path

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from core.architect_data_operations import (
    build_bounded_runtime_evidence,
    discover_runtime_evidence_sources,
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


def _runtime_surface_repo(tmp_path):
    (tmp_path / ".proof_registry.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".reflex_governance_records.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "app.py").write_text("# contract surface\n", encoding="utf-8")
    (tmp_path / "core").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "fixtures").mkdir()
    return tmp_path


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
    assert _root(snapshot)["service_health"]["status"]["reason"] == "no_runtime_records_ingested"


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


def test_runtime_source_existence_does_not_imply_operating_health(tmp_path):
    repo_root = _runtime_surface_repo(tmp_path)
    snapshot = _snapshot(build_bounded_runtime_evidence(), repo_root)
    root = _root(snapshot)

    assert root["runtime_observation"]["status"] == "sources_discovered_no_records_ingested"
    assert root["runtime_observation"]["records_ingested"] == 0
    assert root["runtime_evidence"]["live_operating_health_established"] is False
    for layer in (
        "service_health",
        "intake_health",
        "context_health",
        "proof_health",
        "chronology_health",
        "boundary_health",
    ):
        assert root[layer]["status"]["value"] == "unknown"
        assert root[layer]["status"]["reason"] == "no_runtime_records_ingested"


def test_repository_contract_not_counted_as_runtime_record(tmp_path):
    repo_root = _runtime_surface_repo(tmp_path)
    sources, _missing = discover_runtime_evidence_sources(repo_root, verified_at=GENERATED_AT)
    application_contract = next(source for source in sources if source["name"] == "application_code_contract")

    assert application_contract["source_kind"] == "repository_contract"
    assert application_contract["availability"]["basis"] == "repository_contract"
    assert application_contract["availability"]["records_ingested"] is False
    assert application_contract["availability"]["record_count"] == 0


def test_source_and_policy_dependencies_are_separated(tmp_path):
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    source_dependencies = set(_root(snapshot)["source_dependencies"]["missing_or_unconnected"])
    policy_dependencies = set(_root(snapshot)["policy_dependencies"]["unresolved"])

    assert source_dependencies
    assert policy_dependencies
    assert source_dependencies.isdisjoint(policy_dependencies)


def test_empty_runtime_evidence_produces_unknown_health(tmp_path):
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    root = _root(snapshot)
    layers = [
        root["service_health"],
        root["intake_health"],
        root["context_health"],
        root["proof_health"],
        root["chronology_health"],
        root["boundary_health"],
    ]

    assert all(layer["status"]["value"] == "unknown" for layer in layers)
    assert sum(1 for layer in layers if layer["status"]["value"] == "healthy") == 0


def test_no_record_brief_states_live_health_not_established(tmp_path):
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    brief = render_architect_brief(snapshot)

    assert "no bounded operating records were ingested" in brief
    assert "health therefore remain unknown" in brief
    assert "does not establish that the operating environment is healthy" in brief


def test_missing_runtime_observation_does_not_create_false_critical_alert(tmp_path):
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    root = _root(snapshot)

    assert root["Architect_action"]["required"] is False
    assert root["runtime_observation"]["limitations"]
    assert not any(anomaly["severity"] == "critical" for anomaly in root["anomalies"])


def test_schema_rejects_unsupported_availability_basis(tmp_path):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    _root(snapshot)["evidence_sources"][0]["availability"]["basis"] = "filesystem_vibes"

    try:
        validate(instance=snapshot, schema=schema)
    except ValidationError:
        pass
    else:
        raise AssertionError("schema accepted unsupported availability basis")


def test_schema_rejects_negative_record_count(tmp_path):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    snapshot = _snapshot(build_bounded_runtime_evidence(), _runtime_surface_repo(tmp_path))
    _root(snapshot)["evidence_sources"][0]["availability"]["record_count"] = -1

    try:
        validate(instance=snapshot, schema=schema)
    except ValidationError:
        pass
    else:
        raise AssertionError("schema accepted negative record count")
