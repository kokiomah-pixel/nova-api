import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


SYSTEM_STATE_TEST_KEYS = {
    "state-loop-key": {
        "owner": "state-loop-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/key-info",
            "/v1/usage",
        ],
        "loop_integrity": {
            "pressure_similarity_threshold": 0.75,
            "ambiguous_similarity_threshold": 0.4,
            "retry_block_threshold": 2,
            "pressure_escalation_threshold": 3,
            "denial_history_limit": 10,
        },
    },
    "state-telemetry-key": {
        "owner": "state-telemetry-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/key-info",
            "/v1/usage",
        ],
        "telemetry_integrity": {
            "stale_after_seconds": 300,
            "default_min_reliability": 0.7,
            "risk_increasing_min_reliability": 0.8,
            "risk_reducing_min_reliability": 0.6,
            "disagreement_threshold": 0.35,
            "halt_disagreement_threshold": 0.7,
            "halt_on_degraded": True,
        },
    },
}


@pytest.fixture
def client():
    keys_json = json.dumps(SYSTEM_STATE_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.system-state-test.json"}):
        sys.modules.pop("app", None)
        app_module = importlib.import_module("app")
        app = app_module.app
        app_module.USAGE_TRACKING.clear()
        app_module.REJECTION_LEDGER.clear()
        app_module.EXCEPTION_REGISTER.clear()
        app_module.HALT_SIGNAL_STATE.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.TEMPORAL_GOVERNANCE_STATE.clear()
        app_module.LOOP_INTEGRITY_STATE.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.PERMISSION_BUDGET_STATE.clear()
        app_module.HALT_RELEASE_STATE.clear()
        yield TestClient(app)
        app_module.USAGE_TRACKING.clear()
        app_module.REJECTION_LEDGER.clear()
        app_module.EXCEPTION_REGISTER.clear()
        app_module.HALT_SIGNAL_STATE.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.TEMPORAL_GOVERNANCE_STATE.clear()
        app_module.LOOP_INTEGRITY_STATE.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.PERMISSION_BUDGET_STATE.clear()
        app_module.HALT_RELEASE_STATE.clear()
        try:
            os.remove(".usage.system-state-test.json")
        except FileNotFoundError:
            pass


def test_system_enters_pressure_elevated_under_retry_pressure(client):
    headers = {"Authorization": "Bearer state-loop-key"}
    params = {"intent": "trade", "asset": "ETH", "size": 500000, "strategy": "repeat oversized request"}

    client.get("/v1/context", headers=headers, params=params)
    pressured = client.get("/v1/context", headers=headers, params=params)

    assert pressured.status_code == 429
    payload = pressured.json()
    assert payload["decision_status"] == "RETRY_DELAYED"
    assert payload["system_state"] == "PRESSURE_ELEVATED"
    assert payload["state_transition_reason"] == "pressure_condition_detected"


def test_system_enters_telemetry_degraded_under_telemetry_failure(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer state-telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 1200,
            "telemetry_reliability": 0.95,
        },
    )

    assert response.status_code == 429
    payload = response.json()
    assert payload["system_state"] == "TELEMETRY_DEGRADED"
    assert payload["state_transition_reason"] == "telemetry_state_stale_telemetry"


def test_halt_related_conditions_produce_halt_oriented_system_state(client):
    telemetry_halt = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer state-telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_source_scores": "source_a:0.95,source_b:0.1",
        },
    )
    assert telemetry_halt.status_code == 409
    assert telemetry_halt.json()["system_state"] == "HALT_ACTIVE"

    headers = {"Authorization": "Bearer state-loop-key"}
    params = {"intent": "trade", "asset": "ETH", "size": 500000, "strategy": "repeat oversized request"}
    client.get("/v1/context", headers=headers, params=params)
    client.get("/v1/context", headers=headers, params=params)
    client.get("/v1/context", headers=headers, params=params)
    escalated = client.get("/v1/context", headers=headers, params=params)

    assert escalated.status_code == 409
    assert escalated.json()["system_state"] == "HALT_RECOMMENDED"
    assert escalated.json()["escalation_flag"] is True


def test_system_state_transitions_are_deterministic_and_machine_readable(client):
    headers = {"Authorization": "Bearer state-telemetry-key"}
    degraded = client.get(
        "/v1/context",
        headers=headers,
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 1200,
            "telemetry_reliability": 0.95,
        },
    ).json()
    recovery = client.get(
        "/v1/context",
        headers=headers,
        params={
            "intent": "reduce_position",
            "asset": "ETH",
            "size": 1000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.95,
        },
    ).json()
    cleared = client.get(
        "/v1/context",
        headers=headers,
        params={
            "intent": "reduce_position",
            "asset": "ETH",
            "size": 1000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.95,
        },
    ).json()

    assert degraded["system_state"] == "TELEMETRY_DEGRADED"
    assert recovery["system_state"] == "RECOVERY_REVIEW_REQUIRED"
    assert recovery["state_transition_reason"] == "recovery_review_required_after_telemetry_degraded"
    assert cleared["system_state"] == "NORMAL"
    assert cleared["state_transition_reason"] == "recovery_review_cleared_to_normal"


def test_system_state_metadata_is_attached_to_context_responses(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer state-telemetry-key"},
        params={
            "intent": "reduce_position",
            "asset": "ETH",
            "size": 1000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.95,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "system_state" in payload
    assert "state_transition_reason" in payload
    assert "state_entered_at" in payload
    assert "state_release_condition" in payload
    assert "escalation_flag" in payload
