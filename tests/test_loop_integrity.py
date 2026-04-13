import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


LOOP_TEST_KEYS = {
    "loop-key": {
        "owner": "loop-user",
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
}


@pytest.fixture
def client():
    keys_json = json.dumps(LOOP_TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.loop-test.json"}):
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
            os.remove(".usage.loop-test.json")
        except FileNotFoundError:
            pass


def test_loop_minor_rewording_does_not_bypass_prior_denial(client):
    headers = {"Authorization": "Bearer loop-key"}

    denied = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": "small size"},
    )
    retry = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": "small size please"},
    )

    assert denied.status_code == 422
    assert retry.status_code == 429
    payload = retry.json()
    assert payload["decision_status"] == "RETRY_DELAYED"
    assert payload["loop_classification"] == "ambiguous"
    assert payload["retry_count_by_family"] == 1
    assert payload["semantic_similarity_to_prior_denial"] >= 0.4


def test_loop_retry_counts_accumulate_by_family(client):
    headers = {"Authorization": "Bearer loop-key"}

    denied = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 500000},
    )
    retry_one = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )
    retry_two = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 20000},
    )

    assert denied.status_code == 200
    assert denied.json()["decision_status"] == "VETO"
    assert retry_one.status_code == 200
    assert retry_one.json()["retry_count_by_family"] == 1
    assert retry_two.status_code == 200
    assert retry_two.json()["retry_count_by_family"] == 2


def test_loop_semantically_similar_denials_are_classified_correctly(client):
    headers = {"Authorization": "Bearer loop-key"}

    client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": "small size"},
    )
    retry = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": "small size now"},
    )

    assert retry.status_code == 429
    payload = retry.json()
    assert payload["loop_classification"] == "ambiguous"
    assert payload["loop_integrity_state"] == "retry_delayed"
    assert payload["pressure_score"] > 0.0


def test_loop_pressure_retries_escalate_correctly(client):
    headers = {"Authorization": "Bearer loop-key"}
    params = {"intent": "trade", "asset": "ETH", "size": 500000, "strategy": "repeat oversized request"}

    first = client.get("/v1/context", headers=headers, params=params)
    second = client.get("/v1/context", headers=headers, params=params)
    third = client.get("/v1/context", headers=headers, params=params)
    fourth = client.get("/v1/context", headers=headers, params=params)

    assert first.status_code == 200
    assert first.json()["decision_status"] == "VETO"
    assert second.status_code == 429
    assert second.json()["decision_status"] == "RETRY_DELAYED"
    assert second.json()["loop_classification"] == "pressure_retry"
    assert third.status_code == 409
    assert third.json()["decision_status"] == "RETRY_BLOCKED"
    assert fourth.status_code == 409
    assert fourth.json()["decision_status"] == "PRESSURE_ESCALATED"
    assert fourth.json()["halt_recommendation"] == "HALT_RECOMMENDED"


def test_loop_materially_different_retries_can_remain_admissible(client):
    headers = {"Authorization": "Bearer loop-key"}

    denied = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 500000},
    )
    admissible = client.get(
        "/v1/context",
        headers=headers,
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )

    assert denied.status_code == 200
    assert denied.json()["decision_status"] == "VETO"
    assert admissible.status_code == 200
    payload = admissible.json()
    assert payload["loop_classification"] == "learning_retry"
    assert payload["loop_integrity_state"] == "learning_retry"
    assert payload["semantic_similarity_to_prior_denial"] < 0.4
    assert payload["decision_status"] == "CONSTRAIN"
