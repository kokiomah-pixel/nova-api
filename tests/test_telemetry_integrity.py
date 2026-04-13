import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


TELEMETRY_TEST_KEYS = {
    "telemetry-key": {
        "owner": "telemetry-user",
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
    keys_json = json.dumps(TELEMETRY_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.telemetry-test.json"}):
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
            os.remove(".usage.telemetry-test.json")
        except FileNotFoundError:
            pass


def test_stale_telemetry_triggers_delay(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer telemetry-key"},
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
    assert payload["decision_status"] == "DELAY"
    assert payload["telemetry_freshness_state"] == "stale"
    assert payload["telemetry_integrity_state"] == "stale_telemetry"
    assert payload["telemetry_admissible"] is False


def test_insufficient_reliability_blocks_admission(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.5,
        },
    )

    assert response.status_code == 429
    payload = response.json()
    assert payload["decision_status"] == "DENY"
    assert payload["telemetry_reliability_score"] == 0.5
    assert payload["minimum_required_reliability"] == 0.8
    assert payload["telemetry_integrity_state"] == "insufficient_reliability"
    assert payload["telemetry_admissible"] is False


def test_cross_source_disagreement_is_detected_and_surfaced(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_source_scores": "source_a:0.9,source_b:0.5",
        },
    )

    assert response.status_code == 429
    payload = response.json()
    assert payload["decision_status"] == "DENY"
    assert payload["cross_source_disagreement"] is True
    assert payload["telemetry_integrity_state"] == "cross_source_disagreement"
    assert payload["telemetry_admissible"] is False


def test_degraded_telemetry_can_escalate_to_halt(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_source_scores": "source_a:0.95,source_b:0.1",
        },
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["decision_status"] == "HALT"
    assert payload["cross_source_disagreement"] is True
    assert payload["telemetry_integrity_state"] == "telemetry_degraded"
    assert payload["halt_recommendation"] == "HALT due to telemetry degradation."


def test_telemetry_is_evaluated_before_normal_admission_logic(client, monkeypatch):
    app_module = importlib.import_module("app")

    def fail_guardrail(*args, **kwargs):
        raise AssertionError("build_guardrail should not run when telemetry integrity blocks first")

    monkeypatch.setattr(app_module, "build_guardrail", fail_guardrail)
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer telemetry-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 1200,
            "telemetry_reliability": 0.95,
        },
    )

    assert response.status_code == 429
    assert response.json()["decision_status"] == "DELAY"
