import importlib
import json
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


TEST_KEYS = {
    "queue-key": {
        "owner": "queue-user",
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
    "queue-expiry-key": {
        "owner": "queue-expiry-user",
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
        "decision_queue_governance": {
            "request_ttl_seconds": 90,
        },
    },
}


@pytest.fixture
def queue_client():
    keys_json = json.dumps(TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.queue.test.json"}, clear=False):
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
            os.remove(".usage.queue.test.json")
        except FileNotFoundError:
            pass


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def test_queue_metadata_is_present_and_deterministic(queue_client):
    client, app_module = queue_client
    params = {"intent": "trade", "asset": "ETH", "size": "10000"}

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        first = client.get("/v1/context", headers=_headers("queue-key"), params=params)
    app_module.DECISION_QUEUE_STATE.clear()
    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        second = client.get("/v1/context", headers=_headers("queue-key"), params=params)

    assert first.status_code == 200
    assert second.status_code == 200

    first_payload = first.json()
    second_payload = second.json()
    fields = (
        "queue_priority",
        "queue_position",
        "conflict_group_id",
        "batch_review_required",
        "request_expiry_at",
    )

    for field in fields:
        assert field in first_payload
        assert field in second_payload

    assert first_payload["queue_priority"] == "normal"
    assert first_payload["queue_position"] == 1
    assert first_payload["conflict_group_id"] is None
    assert first_payload["batch_review_required"] is False
    assert first_payload["request_expiry_at"] is None
    assert {field: first_payload[field] for field in fields} == {
        field: second_payload[field] for field in fields
    }


def test_conflicting_requests_receive_conflict_grouping_and_batch_review(queue_client):
    client, _ = queue_client

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        first = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "trade", "asset": "ETH", "size": "10000"},
        )
    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:05Z"}, clear=False):
        second = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "increase_position", "asset": "ETH", "size": "5000"},
        )
    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:10Z"}, clear=False):
        third = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "reduce_position", "asset": "ETH", "size": "5000"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 200

    first_payload = first.json()
    second_payload = second.json()
    third_payload = third.json()

    assert first_payload["conflict_group_id"] is None
    assert second_payload["conflict_group_id"] is not None
    assert second_payload["batch_review_required"] is True
    assert third_payload["conflict_group_id"] == second_payload["conflict_group_id"]
    assert third_payload["batch_review_required"] is True
    assert second_payload["queue_position"] == 2
    assert third_payload["queue_priority"] == "high"
    assert third_payload["queue_position"] == 1


def test_request_expiry_is_machine_readable_when_configured(queue_client):
    client, _ = queue_client

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        response = client.get(
            "/v1/context",
            headers=_headers("queue-expiry-key"),
            params={"intent": "trade", "asset": "BTC", "size": "2500"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request_expiry_at"] == "2026-04-13T12:01:30+00:00"
    assert payload["queue_position"] == 1


def test_regime_change_expires_stale_queue_candidates(queue_client, monkeypatch):
    client, app_module = queue_client

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        first = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "trade", "asset": "SOL", "size": "3000"},
        )

    monkeypatch.setattr(app_module, "DEFAULT_REGIME", "Stress")

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:10Z"}, clear=False):
        second = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "trade", "asset": "SOL", "size": "3000"},
        )

    assert first.status_code == 200
    assert second.status_code == 200

    payload = second.json()
    assert payload["queue_position"] == 1
    assert payload["conflict_group_id"] is None
    assert payload["batch_review_required"] is False


def test_queue_governance_does_not_bypass_denial_first_controls(queue_client):
    client, _ = queue_client

    with patch.dict(os.environ, {"NOVA_NOW_UTC": "2026-04-13T12:00:00Z"}, clear=False):
        response = client.get(
            "/v1/context",
            headers=_headers("queue-key"),
            params={"intent": "trade", "asset": "ETH", "size": "small size"},
        )

    assert response.status_code == 422
    payload = response.json()
    assert payload["decision_status"] == "VETO"
    assert payload["constraint_analysis"]["constraint_category"] == "ambiguous_constraint_language"
    assert payload["queue_priority"] == "normal"
    assert payload["queue_position"] == 1
    assert "batch_review_required" in payload
    assert "request_expiry_at" in payload
