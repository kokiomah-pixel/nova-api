import importlib
import json
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


TEST_KEYS = {
    "memory-key": {
        "owner": "memory-user",
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
    "memory-confidence-key": {
        "owner": "memory-confidence-user",
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
        "memory_governance": {
            "confidence_weights": {
                "validated": 0.25,
            },
        },
    },
    "memory-stale-key": {
        "owner": "memory-stale-user",
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
        "memory_governance": {
            "memory_age_seconds": 7200,
            "stale_after_seconds": 300,
        },
    },
    "memory-inadmissible-key": {
        "owner": "memory-inadmissible-user",
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
        "memory_governance": {
            "admissible_reflex_classes": [
                "baseline_monitoring",
            ],
        },
    },
}


@pytest.fixture
def memory_client():
    keys_json = json.dumps(TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.memory.test.json"}, clear=False):
        sys.modules.pop("app", None)
        app_module = importlib.import_module("app")
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
        app_module.DECISION_QUEUE_STATE.clear()
        yield TestClient(app_module.app), app_module
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
        app_module.DECISION_QUEUE_STATE.clear()
        try:
            os.remove(".usage.memory.test.json")
        except FileNotFoundError:
            pass


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def test_admissible_memory_class_and_invocation_are_surfaced(memory_client):
    client, _ = memory_client
    response = client.get(
        "/v1/context",
        headers=_headers("memory-key"),
        params={"intent": "trade", "asset": "ETH", "size": "10000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_influence_invoked"] is True
    assert payload["reflex_memory_class"] == "liquidity_deterioration"
    assert payload["memory_age_state"] == "fresh"
    assert payload["stale_memory_flag"] is False
    assert payload["reflex_memory"]["influence_applied"] is True


def test_memory_confidence_weight_is_machine_readable_and_discounted(memory_client):
    client, _ = memory_client
    response = client.get(
        "/v1/context",
        headers=_headers("memory-confidence-key"),
        params={"intent": "trade", "asset": "ETH", "size": "10000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_confidence_weight"] == 0.25
    assert payload["memory_influence_invoked"] is True
    assert payload["impact_on_outcomes"]["adjusted_size"] == 8500.0
    assert payload["decision_status"] == "CONSTRAIN"


def test_stale_memory_is_flagged_and_blocked_from_governing(memory_client):
    client, _ = memory_client
    response = client.get(
        "/v1/context",
        headers=_headers("memory-stale-key"),
        params={"intent": "trade", "asset": "ETH", "size": "10000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reflex_memory_class"] == "liquidity_deterioration"
    assert payload["memory_age_state"] == "stale"
    assert payload["stale_memory_flag"] is True
    assert payload["memory_influence_invoked"] is False
    assert payload["reflex_memory"]["influence_applied"] is False
    assert payload["reflex_memory"]["proof"] is None
    assert payload["impact_on_outcomes"]["adjusted_size"] == 5000.0


def test_inadmissible_memory_does_not_silently_govern_admission(memory_client):
    client, _ = memory_client
    response = client.get(
        "/v1/context",
        headers=_headers("memory-inadmissible-key"),
        params={"intent": "trade", "asset": "ETH", "size": "10000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reflex_memory_class"] == "liquidity_deterioration"
    assert payload["stale_memory_flag"] is False
    assert payload["memory_influence_invoked"] is False
    assert payload["reflex_memory"]["influence_applied"] is False
    assert payload["impact_on_outcomes"]["adjusted_size"] == 5000.0


def test_no_active_memory_entry_reports_not_applicable(memory_client, monkeypatch):
    client, app_module = memory_client
    monkeypatch.setattr(app_module, "DEFAULT_REGIME", "Stable")

    response = client.get(
        "/v1/context",
        headers=_headers("memory-key"),
        params={"intent": "trade", "asset": "ETH", "size": "10000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_influence_invoked"] is False
    assert payload["reflex_memory_class"] is None
    assert payload["memory_confidence_weight"] is None
    assert payload["memory_age_state"] == "not_applicable"
    assert payload["stale_memory_flag"] is False
