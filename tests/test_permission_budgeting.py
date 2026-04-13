import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


PERMISSION_BUDGET_TEST_KEYS = {
    "budget-key": {
        "owner": "budget-user",
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
        "permission_budgeting": {
            "default_daily_budget": 5000,
            "risk_increasing_daily_budget": 10000,
            "risk_reducing_daily_budget": 25000,
            "exception_budget": 3,
            "low_remaining_ratio": 0.2,
        },
    },
    "budget-delay-key": {
        "owner": "budget-delay-user",
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
        "permission_budgeting": {
            "default_daily_budget": 5000,
            "risk_increasing_daily_budget": 5000,
            "risk_reducing_daily_budget": 25000,
            "exception_budget": 1,
            "delay_on_exhaustion": True,
        },
    },
}


@pytest.fixture
def client():
    keys_json = json.dumps(PERMISSION_BUDGET_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.permission-budget-test.json"}):
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
            os.remove(".usage.permission-budget-test.json")
        except FileNotFoundError:
            pass


def test_admitted_exposure_consumes_permission_budget(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer budget-key"},
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["permission_budget_class"] == "risk_increasing"
    assert payload["budget_consumed_by_request"] == 4000.0
    assert payload["permission_budget_remaining"] == 6000.0
    assert payload["budget_exhausted"] is False
    assert payload["exception_budget_remaining"] == 3


def test_low_remaining_budget_can_trigger_reduced_admission(client):
    headers = {"Authorization": "Bearer budget-key"}
    client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )
    reduced = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 20000},
    )

    assert reduced.status_code == 200
    payload = reduced.json()
    assert payload["decision_status"] == "REDUCE"
    assert payload["impact_on_outcomes"]["adjusted_size"] == 6000.0
    assert payload["budget_consumed_by_request"] == 6000.0
    assert payload["permission_budget_remaining"] == 0.0
    assert payload["budget_exhausted"] is True


def test_exhausted_budget_blocks_or_delays_further_admission(client):
    headers = {"Authorization": "Bearer budget-delay-key"}
    client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 12500},
    )
    exhausted = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 1000},
    )

    assert exhausted.status_code == 429
    payload = exhausted.json()
    assert payload["decision_status"] == "DELAY"
    assert payload["permission_budget_remaining"] == 0.0
    assert payload["budget_consumed_by_request"] == 0.0
    assert payload["budget_exhausted"] is True


def test_budget_state_is_attached_to_relevant_responses(client):
    response = client.get(
        "/v1/context",
        headers={"Authorization": "Bearer budget-key"},
        params={"intent": "reduce_position", "asset": "ETH", "size": 1000},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "permission_budget_class" in payload
    assert "permission_budget_remaining" in payload
    assert "budget_consumed_by_request" in payload
    assert "budget_exhausted" in payload
    assert "exception_budget_remaining" in payload


def test_budget_behavior_is_deterministic_across_repeated_requests(client):
    headers = {"Authorization": "Bearer budget-key"}
    first = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    ).json()
    second = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 20000},
    ).json()
    third = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 1000},
    ).json()

    assert first["permission_budget_remaining"] == 6000.0
    assert second["decision_status"] == "REDUCE"
    assert second["permission_budget_remaining"] == 0.0
    assert third["decision_status"] == "DENY"
    assert third["permission_budget_remaining"] == 0.0
    assert third["budget_consumed_by_request"] == 0.0
