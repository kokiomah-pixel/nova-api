import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from x402.http.constants import PAYMENT_REQUIRED_HEADER, PAYMENT_SIGNATURE_HEADER


DISCOVERY_TEST_KEY = "discovery-boundary-key"
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
            "/v1/feeds/constraint_pressure",
            "/v1/feeds/usage",
            "/v1/usage",
        ],
    }
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


def test_services_json_publicly_exposes_only_constraint_pressure(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/services.json")

    assert response.status_code == 200
    rendered = json.dumps(response.json(), sort_keys=True)
    assert "Nova Constraint Pressure" in rendered
    assert "/v1/feeds/constraint_pressure" in rendered
    assert "/v1/context" not in rendered
    assert "/v1/proof" not in rendered
    assert "Reflex" not in rendered


def test_constraint_pressure_public_surface_returns_x402_402(discovery_client):
    client, _, _ = discovery_client

    response = client.get("/v1/feeds/constraint_pressure")

    assert response.status_code == 402
    payload = response.json()
    assert payload["payment_required"] is True
    assert payload["network"] == "base"
    assert payload["asset"] == "USDC"
    assert payload["settlement_wallet"] == "0xb29b02130138a6fF8e0f6D7812bDa8D436001BE4"
    assert payload["authority_layer"] == "non_admission_telemetry"
    assert PAYMENT_REQUIRED_HEADER in response.headers
    assert response.headers["x-accept-payment"] == PAYMENT_SIGNATURE_HEADER


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
