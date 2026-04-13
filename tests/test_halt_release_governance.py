import importlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


HALT_RELEASE_TEST_KEYS = {
    "halt-release-key": {
        "owner": "halt-release-user",
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


def _normal_params() -> dict:
    return {
        "intent": "reduce_position",
        "asset": "ETH",
        "size": 1000,
        "telemetry_age_seconds": 10,
        "telemetry_reliability": 0.95,
    }


@pytest.fixture
def client():
    keys_json = json.dumps(HALT_RELEASE_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.halt-release-test.json"}):
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
            os.remove(".usage.halt-release-test.json")
        except FileNotFoundError:
            pass


def _trigger_halt(client):
    return client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params={
            "intent": "trade",
            "asset": "ETH",
            "size": 10000,
            "telemetry_age_seconds": 10,
            "telemetry_source_scores": "source_a:0.95,source_b:0.1",
        },
    )


def test_halt_related_states_surface_release_requirements_correctly(client):
    halted = _trigger_halt(client)
    assert halted.status_code == 409

    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["decision_status"] == "HALT"
    assert payload["halt_release_required"] is True
    assert payload["system_state"] == "HALT_ACTIVE"


def test_release_authority_and_evidence_fields_are_present_where_required(client):
    _trigger_halt(client)
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    )
    payload = response.json()

    assert payload["halt_release_authority"] == "risk_committee"
    assert payload["halt_release_evidence"] == [
        "control_integrity_review",
        "fresh_telemetry_confirmation",
    ]
    assert payload["post_release_cooldown"]["seconds_remaining"] == 120


def test_post_release_cooldown_is_enforced(client):
    _trigger_halt(client)
    release = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params={
            **_normal_params(),
            "halt_release_authority_input": "risk_committee",
            "halt_release_evidence_input": "control_integrity_review,fresh_telemetry_confirmation",
        },
    )

    assert release.status_code == 429
    release_payload = release.json()
    assert release_payload["decision_status"] == "DELAY"
    assert release_payload["halt_release_required"] is False
    assert release_payload["re_evaluation_required"] is True
    assert release_payload["post_release_cooldown"]["seconds_remaining"] == 120

    cooldown = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    )
    assert cooldown.status_code == 429
    assert cooldown.json()["decision_status"] == "DELAY"


def test_re_evaluation_requirements_are_surfaced_after_release(client, monkeypatch):
    app_module = importlib.import_module("app")
    base_time = datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(app_module, "get_current_datetime", lambda: base_time)
    _trigger_halt(client)

    client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params={
            **_normal_params(),
            "halt_release_authority_input": "risk_committee",
            "halt_release_evidence_input": "control_integrity_review,fresh_telemetry_confirmation",
        },
    )

    monkeypatch.setattr(app_module, "get_current_datetime", lambda: base_time + timedelta(seconds=121))
    reevaluated = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    )

    assert reevaluated.status_code == 200
    payload = reevaluated.json()
    assert payload["re_evaluation_required"] is True
    assert payload["system_state"] == "RECOVERY_REVIEW_REQUIRED"


def test_halt_exit_behavior_is_deterministic_and_auditable(client, monkeypatch):
    app_module = importlib.import_module("app")
    base_time = datetime(2026, 4, 13, 13, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(app_module, "get_current_datetime", lambda: base_time)
    _trigger_halt(client)

    blocked = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    ).json()

    client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params={
            **_normal_params(),
            "halt_release_authority_input": "risk_committee",
            "halt_release_evidence_input": "control_integrity_review,fresh_telemetry_confirmation",
        },
    )

    monkeypatch.setattr(app_module, "get_current_datetime", lambda: base_time + timedelta(seconds=121))
    first_clear = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    ).json()
    second_clear = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer halt-release-key"},
        params=_normal_params(),
    ).json()

    assert blocked["halt_release_required"] is True
    assert first_clear["re_evaluation_required"] is True
    assert first_clear["state_transition_reason"] == "re_evaluation_required_after_halt_release"
    assert second_clear["system_state"] == "NORMAL"
    assert second_clear["state_transition_reason"] == "recovery_review_cleared_to_normal"
