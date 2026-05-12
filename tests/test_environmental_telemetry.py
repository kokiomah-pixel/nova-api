import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from core.environmental_state_engine import EnvironmentalStateEngine
from core.feed_metering import reset_feed_usage_state_for_tests
from core.telemetry_engine import InternalTelemetryEngine


ENVIRONMENTAL_TEST_KEYS = {
    "environmental-key": {
        "owner": "environmental-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/context",
            "/v1/feeds/constraint_pressure",
            "/v1/key-info",
            "/v1/usage",
        ],
    },
}


@pytest.fixture
def environmental_client():
    keys_json = json.dumps(ENVIRONMENTAL_TEST_KEYS)
    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": keys_json,
            "NOVA_USAGE_FILE": ".usage.environmental-test.json",
            "NOVA_FEED_USAGE_FILE": ".feed_usage.environmental-test.json",
            "NOVA_PROOF_FILE": ".proof.environmental-test.json",
            "NOVA_REFLEX_GOVERNANCE_RECORDS_FILE": ".reflex_governance_records.environmental-test.jsonl",
            "NOVA_REFLEX_GOVERNANCE_SIGNALS_FILE": ".reflex_governance_signals.environmental-test.json",
            "NOVA_REFLEX_GOVERNANCE_ESCALATIONS_FILE": ".reflex_governance_escalations.environmental-test.json",
        },
    ):
        sys.modules.pop("app", None)
        app_module = importlib.import_module("app")
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        reset_feed_usage_state_for_tests()
        yield TestClient(app_module.app), app_module
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        reset_feed_usage_state_for_tests()
        for path in [
            ".usage.environmental-test.json",
            ".feed_usage.environmental-test.json",
            ".proof.environmental-test.json",
            ".reflex_governance_records.environmental-test.jsonl",
            ".reflex_governance_signals.environmental-test.json",
            ".reflex_governance_escalations.environmental-test.json",
        ]:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def _auth_headers() -> dict:
    return {"Authorization": "Bearer environmental-key"}


def test_constraint_pressure_feed_is_non_admission_telemetry(environmental_client):
    client, _ = environmental_client

    response = client.get("/v1/feeds/constraint_pressure", headers=_auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["feed_name"] == "Nova Constraint Pressure"
    assert payload["feed_type"] == "environmental_conditioning"
    assert payload["authority_layer"] == "non_admission_telemetry"
    assert payload["feed_authority"] == "non_admission_telemetry"
    assert payload["runtime_role"] == "execution_posture_conditioning"
    assert payload["source_layer"] == "derived_environmental_state"
    assert payload["sovereign_admission_required"] is True
    assert payload["machine_consumable"] is True
    assert payload["mcp_compatible"] is True
    assert payload["x402_ready"] is True
    assert payload["constraint_pressure"] == "QUIET"
    assert payload["environment_posture"] == "QUIET"

    protected_fields = {
        "decision_status",
        "reflex_memory",
        "constraint_trace",
        "request_snapshot",
        "decision_id",
        "api_key",
        "actor_id",
        "deny_probability",
        "recommended_action",
        "reason",
        "admissibility_delta",
    }
    assert protected_fields.isdisjoint(payload)


def test_constraint_pressure_feed_derives_aggregate_rates(environmental_client):
    client, app_module = environmental_client

    allow = client.get(
        "/v1/context",
        headers=_auth_headers(),
        params={"intent": "allocate", "asset": "ETH", "size": 10000},
    )
    constrain = client.get(
        "/v1/context",
        headers=_auth_headers(),
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )
    deny = client.get(
        "/v1/context",
        headers=_auth_headers(),
        params={"intent": "trade", "asset": "ETH", "size": 300000},
    )

    assert allow.status_code == 200
    assert allow.json()["decision_status"] == "ALLOW"
    assert constrain.status_code == 200
    assert constrain.json()["decision_status"] == "CONSTRAIN"
    assert deny.status_code == 200
    assert deny.json()["decision_status"] == "VETO"
    assert len(app_module.INTERNAL_TELEMETRY_ENGINE.snapshot()) == 3

    response = client.get("/v1/feeds/constraint_pressure", headers=_auth_headers())

    assert response.status_code == 200
    payload = response.json()
    assert payload["allow_rate"] == 0.333
    assert payload["constrain_rate"] == 0.333
    assert payload["deny_rate"] == 0.333
    assert payload["pressure_score"] > 0.45
    assert payload["constraint_pressure"] in {"ELEVATED", "CONSTRAINED"}
    assert payload["environment_posture"] in {"CONSTRAINED", "DEFENSIVE"}
    assert "decision_status" not in payload
    assert payload["non_substitution_rule"] == "telemetry_informs_posture_only"


def test_internal_engine_strips_raw_decision_material():
    engine = InternalTelemetryEngine()
    record = engine.capture_decision(
        {
            "timestamp_utc": "2026-05-12T00:00:00+00:00",
            "epoch": 494000,
            "decision_status": "VETO",
            "system_state": "PRESSURE_ELEVATED",
            "pressure_score": 0.72,
            "constraint_trace": {
                "constraint_category": "guardrail_veto",
                "reflex_memory_class": "fragility_escalation",
            },
            "decision_admission_record": {
                "request_snapshot": {"intent": "trade", "asset": "ETH", "size": "300000"},
            },
            "reflex_memory": {"active_registry_id": "protected"},
            "api_key": "protected-key",
            "actor_id": "protected-actor",
        }
    )

    assert record["decision_status"] == "VETO"
    assert record["constraint_category"] == "guardrail_veto"
    assert record["environment_posture"] == "ESCALATING"
    assert "decision_admission_record" not in record
    assert "request_snapshot" not in record
    assert "reflex_memory" not in record
    assert "api_key" not in record
    assert "actor_id" not in record


def test_environmental_state_engine_derives_private_stability_and_drift():
    engine = EnvironmentalStateEngine()
    records = [
        {
            "decision_status": "ALLOW",
            "constraint_weight": 0.0,
            "decision_divergence_score": 0.0,
            "admissibility_delta": 0.0,
            "loop_pressure_score": 0.0,
            "temporal_constraint_triggered": False,
            "cross_source_disagreement": False,
            "environment_posture": "QUIET",
            "system_state": "NORMAL",
        },
        {
            "decision_status": "CONSTRAIN",
            "constraint_weight": 0.6,
            "decision_divergence_score": 0.5,
            "admissibility_delta": 0.55,
            "loop_pressure_score": 0.4,
            "temporal_constraint_triggered": False,
            "cross_source_disagreement": False,
            "environment_posture": "CONSTRAINED",
            "system_state": "CONSTRAINED_OPERATION",
        },
        {
            "decision_status": "DENY",
            "constraint_weight": 0.9,
            "decision_divergence_score": 0.88,
            "admissibility_delta": 0.88,
            "loop_pressure_score": 0.8,
            "temporal_constraint_triggered": True,
            "cross_source_disagreement": True,
            "environment_posture": "DEFENSIVE",
            "system_state": "PRESSURE_ELEVATED",
        },
    ]

    states = engine.derive_environmental_states(records)

    assert set(states) == {"constraint_pressure", "decision_stability", "agent_drift"}
    assert states["constraint_pressure"]["constraint_pressure"] in {"ELEVATED", "CONSTRAINED"}
    assert states["decision_stability"]["decision_stability"] in {"FRAGMENTED", "UNSTABLE", "RECOVERING"}
    assert states["agent_drift"]["agent_drift"] in {"RISING", "ESCALATING"}
