import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from x402.http.constants import PAYMENT_REQUIRED_HEADER, PAYMENT_RESPONSE_HEADER, PAYMENT_SIGNATURE_HEADER
from x402.http.utils import encode_payment_signature_header
from x402.schemas import PaymentPayload, ResourceInfo, SettleResponse, VerifyResponse

from core.x402_config import X402_SETTLEMENT_WALLET


X402_TEST_KEY = "x402-private-key"
X402_TEST_KEYS = {
    X402_TEST_KEY: {
        "owner": "x402-private-user",
        "tier": "pro",
        "feed_tier": "growth",
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
    },
}


class FakeFacilitatorClient:
    def __init__(
        self,
        *,
        verify_response: VerifyResponse | None = None,
        settle_response: SettleResponse | None = None,
    ) -> None:
        self.verify_calls = []
        self.settle_calls = []
        self.verify_response = verify_response or VerifyResponse(
            isValid=True,
            payer="0x1111111111111111111111111111111111111111",
        )
        self.settle_response = settle_response or SettleResponse(
            success=True,
            payer="0x1111111111111111111111111111111111111111",
            transaction="0xsettled",
            network="eip155:8453",
            amount="10000",
        )

    def verify(self, payload, requirements):
        self.verify_calls.append((payload, requirements))
        return self.verify_response

    def settle(self, payload, requirements):
        self.settle_calls.append((payload, requirements))
        return self.settle_response


@pytest.fixture
def x402_client():
    keys_json = json.dumps(X402_TEST_KEYS)
    test_files = [
        ".usage.x402-test.json",
        ".usage_state.x402-test.json",
        ".billing_state.x402-test.json",
        ".feed_usage.x402-test.json",
        ".proof.x402-test.json",
        "proof_retrieval_audit.x402-test.jsonl",
        ".reflex_governance_records.x402-test.jsonl",
        ".reflex_governance_signals.x402-test.json",
        ".reflex_governance_escalations.x402-test.json",
    ]
    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": keys_json,
            "NOVA_USAGE_FILE": test_files[0],
            "NOVA_USAGE_STATE_FILE": test_files[1],
            "NOVA_BILLING_STATE_FILE": test_files[2],
            "NOVA_FEED_USAGE_FILE": test_files[3],
            "NOVA_PROOF_FILE": test_files[4],
            "NOVA_PROOF_RETRIEVAL_AUDIT_FILE": test_files[5],
            "NOVA_REFLEX_GOVERNANCE_RECORDS_FILE": test_files[6],
            "NOVA_REFLEX_GOVERNANCE_SIGNALS_FILE": test_files[7],
            "NOVA_REFLEX_GOVERNANCE_ESCALATIONS_FILE": test_files[8],
            "NOVA_PUBLIC_SERVICE_DISCOVERY_ENABLED": "true",
            "NOVA_PUBLIC_X402_ENABLED": "true",
            "NOVA_X402_SETTLEMENT_ENABLED": "true",
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
        x402_middleware = importlib.import_module("core.x402_middleware")
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        feed_metering.reset_feed_usage_state_for_tests()
        yield TestClient(app_module.app), app_module, x402_middleware, feed_metering
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


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {X402_TEST_KEY}"}


def _payment_header(x402_middleware, cadence_tier: str = "developer") -> str:
    requirements = x402_middleware.X402PaymentGateway(
        facilitator_client=FakeFacilitatorClient()
    ).payment_requirements(endpoint="/v1/feeds/constraint_pressure")
    payment = PaymentPayload(
        payload={
            "signature": "0x" + ("11" * 65),
            "authorization": {
                "from": "0x1111111111111111111111111111111111111111",
                "to": "0x1111111111111111111111111111111111111111",
                "value": "10000",
                "validAfter": "0",
                "validBefore": "9999999999",
                "nonce": "0x" + ("22" * 32),
            },
        },
        accepted=requirements,
        resource=ResourceInfo(
            url="/v1/feeds/constraint_pressure",
            description="Nova Constraint Pressure",
            mimeType="application/json",
        ),
        extensions={"cadence_tier": cadence_tier},
    )
    return encode_payment_signature_header(payment)


def _patched_gateway(x402_middleware, facilitator):
    gateway = x402_middleware.X402PaymentGateway(facilitator_client=facilitator)
    return patch.object(x402_middleware, "get_x402_gateway", return_value=gateway)


def test_x402_generates_402_for_unpaid_constraint_pressure_request(x402_client):
    client, _, _, _ = x402_client

    response = client.get("/v1/feeds/constraint_pressure")

    assert response.status_code == 402
    payload = response.json()
    assert payload["payment_required"] is True
    assert payload["network"] == "base"
    assert payload["asset"] == "USDC"
    assert payload["settlement_wallet"] == X402_SETTLEMENT_WALLET
    assert payload["authority_layer"] == "non_admission_telemetry"
    assert payload["sovereign_admission_required"] is True
    assert payload["x402"]["payment_network"] == "base"
    assert payload["x402"]["payment_asset"] == "USDC"
    assert payload["x402"]["settlement_wallet"] == X402_SETTLEMENT_WALLET
    assert payload["x402"]["resource"] == "/v1/feeds/constraint_pressure"
    assert PAYMENT_REQUIRED_HEADER in response.headers
    assert response.headers["x-accept-payment"] == PAYMENT_SIGNATURE_HEADER


def test_x402_verifies_settles_and_grants_feed_access(x402_client):
    client, _, x402_middleware, _ = x402_client
    facilitator = FakeFacilitatorClient()

    with _patched_gateway(x402_middleware, facilitator):
        response = client.get(
            "/v1/feeds/constraint_pressure",
            headers={PAYMENT_SIGNATURE_HEADER: _payment_header(x402_middleware, "growth")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert len(facilitator.verify_calls) == 1
    assert len(facilitator.settle_calls) == 1
    assert response.headers[PAYMENT_RESPONSE_HEADER]
    assert payload["feed_name"] == "Nova Constraint Pressure"
    assert payload["feed_type"] == "environmental_conditioning"
    assert payload["authority_layer"] == "non_admission_telemetry"
    assert payload["x402_payment"]["payment_verified"] is True
    assert payload["x402_payment"]["payment_network"] == "base"
    assert payload["x402_payment"]["protocol_network"] == "eip155:8453"
    assert payload["x402_payment"]["payment_asset"] == "USDC"
    assert payload["x402_payment"]["payment_reference"] == "0xsettled"
    assert payload["feed_identity"]["identity_layer"] == "feed_consumer"
    assert payload["feed_identity"]["feed_tier"] == "growth"
    assert payload["feed_metering"]["monthly_feed_usage"] == 1
    assert "decision_status" not in payload
    assert "reflex_memory" not in payload


def test_x402_rejects_failed_facilitator_verification(x402_client):
    client, _, x402_middleware, _ = x402_client
    facilitator = FakeFacilitatorClient(
        verify_response=VerifyResponse(
            isValid=False,
            invalidReason="invalid_exact_evm_payload_signature",
            invalidMessage="Invalid signature",
        )
    )

    with _patched_gateway(x402_middleware, facilitator):
        response = client.get(
            "/v1/feeds/constraint_pressure",
            headers={PAYMENT_SIGNATURE_HEADER: _payment_header(x402_middleware)},
        )

    assert response.status_code == 402
    assert response.json()["detail"] == "invalid_exact_evm_payload_signature"
    assert len(facilitator.verify_calls) == 1
    assert facilitator.settle_calls == []


def test_x402_rejects_synthetic_local_payment_payload(x402_client):
    client, _, x402_middleware, _ = x402_client
    facilitator = FakeFacilitatorClient()

    with _patched_gateway(x402_middleware, facilitator):
        response = client.get(
            "/v1/feeds/constraint_pressure",
            headers={
                "x-payment": json.dumps(
                    {
                        "endpoint": "/v1/feeds/constraint_pressure",
                        "payment_network": "base",
                        "payment_asset": "USDC",
                        "settlement_wallet": X402_SETTLEMENT_WALLET,
                        "facilitator_status": "settled",
                        "signature": "nova-x402-valid-test-payment",
                    }
                )
            },
        )

    assert response.status_code == 402
    assert response.json()["detail"] == "x402 payment required"
    assert facilitator.verify_calls == []
    assert facilitator.settle_calls == []


def test_x402_does_not_govern_context_or_proof(x402_client):
    client, _, x402_middleware, _ = x402_client
    payment_header = _payment_header(x402_middleware)

    context_response = client.get(
        "/v1/context",
        headers={PAYMENT_SIGNATURE_HEADER: payment_header},
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )
    proof_response = client.get("/v1/proof/some-decision", headers={PAYMENT_SIGNATURE_HEADER: payment_header})

    assert context_response.status_code == 401
    assert proof_response.status_code == 401
    assert PAYMENT_REQUIRED_HEADER not in context_response.headers
    assert PAYMENT_REQUIRED_HEADER not in proof_response.headers
    assert context_response.json()["detail"] == "Missing API key"
    assert proof_response.json()["detail"] == "Missing API key"


def test_x402_paid_feed_does_not_alter_sovereign_authority_or_billing(x402_client):
    client, _, x402_middleware, _ = x402_client
    facilitator = FakeFacilitatorClient()
    context = client.get(
        "/v1/context",
        headers=_auth_headers(),
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    ).json()
    proof_before = client.get(f"/v1/proof/{context['decision_id']}", headers=_auth_headers()).json()
    billing_before = client.get("/v1/billing/summary", headers=_auth_headers()).json()

    with _patched_gateway(x402_middleware, facilitator):
        paid_feed = client.get(
            "/v1/feeds/constraint_pressure",
            headers={PAYMENT_SIGNATURE_HEADER: _payment_header(x402_middleware, "developer")},
        )

    feed_usage = client.get("/v1/feeds/usage", headers=_auth_headers()).json()
    billing_after = client.get("/v1/billing/summary", headers=_auth_headers()).json()
    proof_after = client.get(f"/v1/proof/{context['decision_id']}", headers=_auth_headers()).json()

    assert paid_feed.status_code == 200
    assert feed_usage["aggregate_feed_usage"]["constraint_pressure_calls"] == 1
    assert feed_usage["constraint_pressure_calls"] == 1
    assert feed_usage["feed_usage"]["constraint_pressure_calls"] == 0
    assert context["decision_status"] == "CONSTRAIN"
    assert proof_after["decision_status"] == proof_before["decision_status"]
    assert proof_after["decision_id"] == proof_before["decision_id"]
    assert billing_after["context_calls"] == billing_before["context_calls"]
    assert billing_after["proof_calls"] == billing_before["proof_calls"]
    assert billing_after["billable_context_calls"] == billing_before["billable_context_calls"]
    assert billing_after["amount_due_usd"] == billing_before["amount_due_usd"]
