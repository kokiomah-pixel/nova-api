import importlib
import json
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from core.billing_config import (
    DEFAULT_PRICE_PER_DECISION_USD,
    FREE_CONTEXT_CALL_LIMIT,
    USDC_PAYMENT_WALLET,
)
from core.identity import actor_id_from_api_key, actor_id_from_authorization


PAYER_WALLET = "0x1111111111111111111111111111111111111111"

ALLOWED_ENDPOINTS = [
    "/v1/context",
    "/v1/proof/{decision_id}",
    "/v1/billing/bind_wallet",
    "/v1/billing/summary",
    "/v1/usage",
]


def _key(owner: str) -> dict:
    return {
        "owner": owner,
        "tier": "pro",
        "status": "active",
        "monthly_quota": 1000,
        "allowed_endpoints": list(ALLOWED_ENDPOINTS),
    }


TEST_KEYS = {
    "billing-key": _key("billing-user"),
    "failure-key": _key("failure-user"),
    "decision-control-key": _key("decision-control-user"),
    "decision-metered-key": _key("decision-metered-user"),
}


@pytest.fixture
def billing_client(tmp_path):
    usage_state_file = tmp_path / ".usage_state.json"
    billing_state_file = tmp_path / ".billing_state.json"
    proof_file = tmp_path / ".proof.billing-bridge.json"
    proof_audit_file = tmp_path / "proof_retrieval.billing-bridge.jsonl"
    legacy_usage_file = tmp_path / ".usage.billing-bridge.json"
    legacy_billing_file = tmp_path / ".billing.prepaid-bridge.json"

    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": json.dumps(TEST_KEYS),
            "NOVA_USAGE_FILE": str(legacy_usage_file),
            "NOVA_BILLING_FILE": str(legacy_billing_file),
            "NOVA_USAGE_STATE_FILE": str(usage_state_file),
            "NOVA_BILLING_STATE_FILE": str(billing_state_file),
            "NOVA_PROOF_FILE": str(proof_file),
            "NOVA_PROOF_RETRIEVAL_AUDIT_FILE": str(proof_audit_file),
            "NOVA_RUNTIME_MODE": "test",
            "NOVA_ENABLE_BILLING_ENFORCEMENT": "0",
        },
        clear=False,
    ):
        for module_name in ["app", "core.usage_meter", "core.billing_state"]:
            sys.modules.pop(module_name, None)

        app_module = importlib.import_module("app")
        app_module.USAGE_TRACKING.clear()
        app_module.BILLING_LEDGER.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REJECTION_LEDGER.clear()
        app_module.EXCEPTION_REGISTER.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()

        yield TestClient(app_module.app), app_module, usage_state_file, billing_state_file

        sys.modules.pop("app", None)


def _headers(api_key: str = "billing-key") -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def _context(client: TestClient, api_key: str = "billing-key"):
    return client.get(
        "/v1/context",
        headers=_headers(api_key),
        params={"intent": "reduce_position", "asset": "ETH", "size": 1000},
    )


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_api_key_maps_to_stable_actor_id():
    first = actor_id_from_api_key("billing-key")
    second = actor_id_from_api_key("billing-key")

    assert first == second
    assert first != "billing-key"
    assert actor_id_from_authorization("Bearer billing-key") == first
    assert actor_id_from_authorization(None) == "anonymous"


def test_raw_api_key_is_never_stored_in_bridge_state(billing_client):
    client, _, usage_state_file, billing_state_file = billing_client

    response = _context(client)
    assert response.status_code == 200

    bind = client.post(
        "/v1/billing/bind_wallet",
        headers=_headers(),
        json={"payer_wallet": PAYER_WALLET},
    )
    assert bind.status_code == 200

    persisted = json.dumps({
        "usage": _read_json(usage_state_file),
        "billing": _read_json(billing_state_file),
    })
    assert "billing-key" not in persisted
    assert actor_id_from_api_key("billing-key") in persisted


def test_context_increments_identity_bound_usage(billing_client):
    client, _, usage_state_file, _ = billing_client

    response = _context(client)
    assert response.status_code == 200

    actor_id = actor_id_from_api_key("billing-key")
    usage_record = _read_json(usage_state_file)[actor_id]
    assert usage_record["actor_id"] == actor_id
    assert usage_record["context_calls"] == 1
    assert usage_record["proof_calls"] == 0


def test_proof_retrieval_increments_proof_count(billing_client):
    client, _, usage_state_file, _ = billing_client

    response = _context(client)
    assert response.status_code == 200
    proof = client.get(
        f"/v1/proof/{response.json()['decision_id']}",
        headers=_headers(),
    )
    assert proof.status_code == 200

    usage_record = _read_json(usage_state_file)[actor_id_from_api_key("billing-key")]
    assert usage_record["context_calls"] == 1
    assert usage_record["proof_calls"] == 1


def test_first_fifty_context_calls_remain_evaluation(billing_client):
    client, _, usage_state_file, _ = billing_client

    for _ in range(FREE_CONTEXT_CALL_LIMIT):
        response = _context(client)
        assert response.status_code == 200

    usage_record = _read_json(usage_state_file)[actor_id_from_api_key("billing-key")]
    assert usage_record["context_calls"] == FREE_CONTEXT_CALL_LIMIT
    assert usage_record["usage_state"] == "evaluation"


def test_fifty_first_context_call_sets_evaluation_limit_reached(billing_client):
    client, _, usage_state_file, _ = billing_client

    latest = None
    for _ in range(FREE_CONTEXT_CALL_LIMIT + 1):
        latest = _context(client)
        assert latest.status_code == 200

    usage_record = _read_json(usage_state_file)[actor_id_from_api_key("billing-key")]
    assert usage_record["context_calls"] == FREE_CONTEXT_CALL_LIMIT + 1
    assert usage_record["usage_state"] == "evaluation_limit_reached"
    assert latest.json()["decision_status"] == "ALLOW"


def test_wallet_binding_stores_payer_wallet(billing_client):
    client, _, _, billing_state_file = billing_client

    response = client.post(
        "/v1/billing/bind_wallet",
        headers=_headers(),
        json={"payer_wallet": PAYER_WALLET},
    )

    assert response.status_code == 200
    assert response.json() == {
        "billing_mode": "pilot",
        "payer_wallet": PAYER_WALLET,
        "payment_destination": USDC_PAYMENT_WALLET,
    }

    billing_record = _read_json(billing_state_file)[actor_id_from_api_key("billing-key")]
    assert billing_record["billing_mode"] == "pilot"
    assert billing_record["usdc_wallet"] == PAYER_WALLET
    assert billing_record["payment_destination"] == USDC_PAYMENT_WALLET


def test_billing_summary_returns_canonical_payment_destination(billing_client):
    client, _, _, _ = billing_client

    bind = client.post(
        "/v1/billing/bind_wallet",
        headers=_headers(),
        json={"payer_wallet": PAYER_WALLET},
    )
    assert bind.status_code == 200

    for _ in range(FREE_CONTEXT_CALL_LIMIT + 2):
        response = _context(client)
        assert response.status_code == 200

    summary = client.get("/v1/billing/summary", headers=_headers())
    assert summary.status_code == 200

    payload = summary.json()
    assert payload["actor_id"] == actor_id_from_api_key("billing-key")
    assert payload["billing_mode"] == "pilot"
    assert payload["context_calls"] == FREE_CONTEXT_CALL_LIMIT + 2
    assert payload["free_context_call_limit"] == FREE_CONTEXT_CALL_LIMIT
    assert payload["billable_context_calls"] == 2
    assert payload["price_per_decision_usd"] == DEFAULT_PRICE_PER_DECISION_USD
    assert payload["amount_due_usd"] == 0.04
    assert payload["payment_destination"] == USDC_PAYMENT_WALLET


def test_metering_failure_does_not_break_context(billing_client):
    client, app_module, _, _ = billing_client

    with patch.object(
        app_module.decision_usage_meter,
        "increment_context_call",
        side_effect=RuntimeError("meter unavailable"),
    ):
        response = _context(client, api_key="failure-key")

    assert response.status_code == 200
    assert response.json()["decision_status"] == "ALLOW"


def test_decision_status_is_unchanged_by_billing_logic(billing_client):
    client, app_module, _, _ = billing_client
    params = {"intent": "trade", "asset": "ETH", "size": 10000}

    with patch.object(
        app_module.decision_usage_meter,
        "increment_context_call",
        return_value={"context_calls": 1},
    ), patch.object(app_module.usdc_billing_state, "sync_context_usage", return_value=None):
        control = client.get(
            "/v1/context",
            headers=_headers("decision-control-key"),
            params=params,
        )

    metered = client.get(
        "/v1/context",
        headers=_headers("decision-metered-key"),
        params=params,
    )

    assert control.status_code == 200
    assert metered.status_code == 200
    assert control.json()["decision_status"] == metered.json()["decision_status"]
    assert metered.json()["decision_status"] == "CONSTRAIN"
