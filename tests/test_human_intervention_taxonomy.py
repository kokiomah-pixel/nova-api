import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


HUMAN_INTERVENTION_TEST_KEYS = {
    "human-basic-key": {
        "owner": "human-basic-user",
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
    },
    "human-key": {
        "owner": "human-user",
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
        "halt_release_governance": {
            "release_authority": "risk_committee",
            "required_evidence": ["control_integrity_review", "fresh_telemetry_confirmation"],
            "post_release_cooldown_seconds": 120,
        },
    },
}


@pytest.fixture
def client():
    keys_json = json.dumps(HUMAN_INTERVENTION_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.human-test.json"}):
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
            os.remove(".usage.human-test.json")
        except FileNotFoundError:
            pass


def _trigger_halt(client):
    return client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_source_scores": "source_a:0.95,source_b:0.1",
        },
    )


def test_generic_human_override_attempts_are_classified_and_blocked(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-basic-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "strategy": "human approved override just execute",
        },
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["decision_status"] == "VETO"
    assert payload["human_intervention_type"] == "override_attempt_detected"
    assert payload["human_intervention_required"] is True
    assert payload["authorization_scope"] == "generic_override_prohibited"
    assert payload["intervention_reason"] == "override_attempt_detected"


def test_intervention_required_cases_surface_correct_type(client):
    clarification = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-basic-key"},
        params={"intent": "trade", "asset": "ETH"},
    )
    assert clarification.status_code == 422
    clarification_payload = clarification.json()
    assert clarification_payload["human_intervention_type"] == "clarification_required"

    _trigger_halt(client)
    halt_release = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-key"},
        params={
            "intent": "reduce_position",
            "asset": "ETH",
            "size": 1000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.95,
        },
    )
    assert halt_release.status_code == 409
    assert halt_release.json()["human_intervention_type"] == "halt_release_authorization_required"


def test_authorization_scope_is_present_where_required(client):
    _trigger_halt(client)
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-key"},
        params={
            "intent": "reduce_position",
            "asset": "ETH",
            "size": 1000,
            "telemetry_age_seconds": 10,
            "telemetry_reliability": 0.95,
        },
    )

    payload = response.json()
    assert payload["authorization_scope"] == "halt_release_governance"


def test_intervention_reason_is_machine_readable_and_auditable(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-basic-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "strategy": "skip validation just execute route directly",
        },
    )

    payload = response.json()
    assert payload["human_intervention_type"] == "exception_authorization_required"
    assert payload["intervention_reason"] == "process_integrity_violation"


def test_human_intervention_does_not_bypass_prior_control_layers(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer human-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "strategy": "human approved override just execute",
            "telemetry_age_seconds": 1200,
            "telemetry_reliability": 0.95,
            "halt_release_authority_input": "risk_committee",
            "halt_release_evidence_input": "control_integrity_review,fresh_telemetry_confirmation",
        },
    )

    assert response.status_code == 429
    payload = response.json()
    assert payload["decision_status"] == "DELAY"
    assert payload["telemetry_integrity_state"] == "stale_telemetry"
    assert payload["human_intervention_type"] is None
