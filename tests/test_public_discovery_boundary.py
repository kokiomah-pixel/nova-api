import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from x402.http.constants import PAYMENT_REQUIRED_HEADER


DISCOVERY_TEST_KEY = "discovery-boundary-key"
TELEMETRY_ADMIN_TEST_KEY = "telemetry-admin-key"
DISCOVERY_TEST_KEYS = {
    DISCOVERY_TEST_KEY: {
        "owner": "discovery-boundary-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 1000,
        "allowed_endpoints": [
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/billing/summary",
            "/v1/internal/runtime_config_status",
            "/v1/feeds/constraint_pressure",
            "/v1/feeds/usage",
            "/v1/usage",
        ],
    },
    TELEMETRY_ADMIN_TEST_KEY: {
        "owner": "misconfigured-telemetry-admin",
        "tier": "admin",
        "status": "active",
        "monthly_quota": 1000,
        "allowed_endpoints": [
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/internal/runtime_config_status",
            "/v1/feeds/usage",
        ],
    },
}


@pytest.fixture
def discovery_client():
    test_files = [
        ".usage.discovery-boundary-test.json",
        ".usage_state.discovery-boundary-test.json",
        ".billing_state.discovery-boundary-test.json",
        ".feed_usage.discovery-boundary-test.json",
        ".proof.discovery-boundary-test.json",
        "proof_retrieval_audit.discovery-boundary-test.jsonl",
        ".reflex_governance_records.discovery-boundary-test.jsonl",
        ".reflex_governance_signals.discovery-boundary-test.json",
        ".reflex_governance_escalations.discovery-boundary-test.json",
    ]
    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": json.dumps(DISCOVERY_TEST_KEYS),
            "NOVA_USAGE_FILE": test_files[0],
            "NOVA_USAGE_STATE_FILE": test_files[1],
            "NOVA_BILLING_STATE_FILE": test_files[2],
            "NOVA_FEED_USAGE_FILE": test_files[3],
            "NOVA_PROOF_FILE": test_files[4],
            "NOVA_PROOF_RETRIEVAL_AUDIT_FILE": test_files[5],
            "NOVA_REFLEX_GOVERNANCE_RECORDS_FILE": test_files[6],
            "NOVA_REFLEX_GOVERNANCE_SIGNALS_FILE": test_files[7],
            "NOVA_REFLEX_GOVERNANCE_ESCALATIONS_FILE": test_files[8],
            "NOVA_API_URL": "https://nova-api-ipz6.onrender.com",
            "CDP_API_KEY_ID": "server-secret-key-abcdef",
            "CDP_API_KEY_SECRET": "server-secret-value",
            "NOVA_TELEMETRY_ADMIN_KEY": TELEMETRY_ADMIN_TEST_KEY,
        },
    ):
        for module_name in [
            "app",
            "core.usage_meter",
            "core.billing_state",
            "core.feed_metering",
            "core.x402_middleware",
        ]:
            sys.modules.pop(module_name, None)
        app_module = importlib.import_module("app")
        feed_metering = importlib.import_module("core.feed_metering")
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        feed_metering.reset_feed_usage_state_for_tests()
        yield TestClient(app_module.app), app_module, feed_metering
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        feed_metering.reset_feed_usage_state_for_tests()
        for path in test_files:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def test_services_json_is_contained_by_default(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/services.json")

    assert response.status_code == 404
    rendered = json.dumps(response.json(), sort_keys=True)
    assert "Nova Constraint Pressure" not in rendered
    assert "/v1/feeds/constraint_pressure" not in rendered


def test_constraint_pressure_public_surface_is_contained_without_x402(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/v1/feeds/constraint_pressure")

    assert response.status_code == 404
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert "x-accept-payment" not in response.headers
    rendered = json.dumps(response.json(), sort_keys=True).lower()
    assert "settlement_wallet" not in rendered
    assert "facilitator" not in rendered


def test_context_is_not_public_x402_discoverable(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/v1/context?intent=allocate&asset=ETH&size=10000")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"
    assert PAYMENT_REQUIRED_HEADER not in response.headers


def test_proof_is_not_public_x402_discoverable(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/v1/proof/test")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"
    assert PAYMENT_REQUIRED_HEADER not in response.headers


def test_runtime_config_status_requires_api_key(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/v1/internal/runtime_config_status")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


def test_runtime_config_status_returns_only_non_secret_fingerprints(discovery_client):
    client, _, _ = discovery_client

    response = client.get(
        "/v1/internal/runtime_config_status",
        headers={"Authorization": f"Bearer {DISCOVERY_TEST_KEY}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cdp_key_id_present"] is True
    assert payload["cdp_secret_present"] is True
    assert payload["x402_settlement_wallet"] == "0xb29b02130138a6fF8e0f6D7812bDa8D436001BE4"
    assert payload["nova_api_url"] == "https://nova-api-ipz6.onrender.com"
    assert payload["cdp_key_id_suffix"] == "abcdef"
    rendered = json.dumps(payload, sort_keys=True)
    assert "server-secret-key-" not in rendered
    assert "server-secret-value" not in rendered


def test_telemetry_admin_key_can_read_feed_usage_and_billing(discovery_client):
    client, _, _ = discovery_client
    headers = {"Authorization": f"Bearer {TELEMETRY_ADMIN_TEST_KEY}"}

    usage_response = client.get("/v1/feeds/usage", headers=headers)
    billing_response = client.get("/v1/billing/summary", headers=headers)

    assert usage_response.status_code == 200
    assert billing_response.status_code == 200


def test_telemetry_admin_key_is_limited_to_inspection_routes(discovery_client):
    client, _, _ = discovery_client
    headers = {"Authorization": f"Bearer {TELEMETRY_ADMIN_TEST_KEY}"}

    context_response = client.get(
        "/v1/context?intent=allocate&asset=ETH&size=10000",
        headers=headers,
    )
    proof_response = client.get("/v1/proof/test", headers=headers)
    runtime_status_response = client.get("/v1/internal/runtime_config_status", headers=headers)

    assert context_response.status_code == 403
    assert context_response.json()["detail"] == "API key not allowed for this endpoint"
    assert proof_response.status_code == 403
    assert proof_response.json()["detail"] == "API key not allowed for this endpoint"
    assert runtime_status_response.status_code == 403
    assert runtime_status_response.json()["detail"] == "API key not allowed for this endpoint"
