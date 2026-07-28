import base64
import json

import scripts.live_x402_constraint_pressure_payment as live_x402_payment
from nova_api.telemetry.x402_observability import (
    X402FailureCategory,
    X402_EVENT_NAMES,
    challenge_metadata,
    classify_facilitator_failure,
    facilitator_response_metadata,
    helper_metadata,
    structured_event,
    wallet_environment_metadata,
)
from nova_api.utils.redaction import REDACTED, redact


TEST_SETTLEMENT_WALLET = "0x" + ("3" * 40)


def _payment_required_header() -> str:
    payload = {
        "x402Version": 2,
        "resource": {"url": "/v1/feeds/constraint_pressure"},
        "accepts": [
            {
                "scheme": "exact",
                "network": "eip155:8453",
                "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "amount": "10000",
                "payTo": TEST_SETTLEMENT_WALLET,
                "maxTimeoutSeconds": 60,
            }
        ],
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


class FakeAccepted:
    scheme = "exact"
    network = "eip155:8453"
    asset = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    amount = "10000"
    pay_to = TEST_SETTLEMENT_WALLET


class FakeResource:
    url = "/v1/feeds/constraint_pressure"


class FakePaymentPayload:
    accepted = FakeAccepted()
    resource = FakeResource()

    def model_dump(self, **kwargs):
        return {
            "x402Version": 2,
            "accepted": {"network": "eip155:8453"},
            "payload": {"signature": "0x" + ("11" * 65)},
            "resource": {"url": "/v1/feeds/constraint_pressure"},
        }


def test_redaction_removes_sensitive_material_from_nested_values():
    payload = redact(
        {
            "Authorization": "Bearer secret-token-value",
            "payload": {
                "signature": "0x" + ("11" * 65),
                "network": "eip155:8453",
            },
            "api_key_secret": "server-secret",
        }
    )

    assert payload["Authorization"] == REDACTED
    assert payload["payload"]["signature"] == REDACTED
    assert payload["payload"]["network"] == "eip155:8453"
    assert payload["api_key_secret"] == REDACTED


def test_challenge_metadata_extracts_live_402_shape_without_secret_fields():
    metadata = challenge_metadata(
        status_code=402,
        headers={
            "PAYMENT-REQUIRED": _payment_required_header(),
            "x-accept-payment": "PAYMENT-SIGNATURE",
        },
        facilitator_endpoint="https://api.cdp.coinbase.com/platform/v2/x402",
    )

    assert metadata["http_status"] == 402
    assert metadata["challenge_headers_present"] is True
    assert metadata["x402_version"] == 2
    assert metadata["network"] == "eip155:8453"
    assert metadata["chain_id"] == 8453
    assert metadata["amount"] == "10000"
    assert metadata["resource"] == "/v1/feeds/constraint_pressure"
    assert metadata["challenge_expiration_metadata"]["max_timeout_seconds"] == 60


def test_helper_metadata_serializes_helper_generated_payload_shape():
    metadata = helper_metadata(payment_payload=FakePaymentPayload())

    assert metadata["helper_path_invoked"] is True
    assert metadata["helper_name"] == "x402HTTPClientSync"
    assert "payload" in metadata["payment_payload_keys"]
    assert metadata["network"] == "eip155:8453"
    assert metadata["chain_id"] == 8453
    assert metadata["amount"] == "10000"
    assert metadata["resource"] == "/v1/feeds/constraint_pressure"


def test_facilitator_failure_classification_covers_interoperability_categories():
    assert (
        classify_facilitator_failure(
            status_code=400,
            body={"invalidReason": "invalid_payload"},
        )
        == X402FailureCategory.INVALID_CHALLENGE
    )
    assert (
        classify_facilitator_failure(
            status_code=400,
            body={"error": "unsupported network"},
        )
        == X402FailureCategory.UNSUPPORTED_NETWORK
    )
    assert (
        classify_facilitator_failure(
            status_code=400,
            body={"error": "signature rejected"},
        )
        == X402FailureCategory.SIGNATURE_REJECTION
    )


def test_facilitator_response_metadata_redacts_and_names_failure_fields():
    metadata = facilitator_response_metadata(
        status_code=400,
        body={
            "invalidReason": "invalid_payload",
            "signature": "0x" + ("11" * 65),
        },
        headers={"retry-after": "10"},
    )

    assert metadata["facilitator_response_code"] == 400
    assert metadata["retry_after"] == "10"
    assert metadata["settlement_failure_reason"] == "INVALID_CHALLENGE"
    assert metadata["facilitator_rejection_body"]["signature"] == REDACTED
    assert "payload" in metadata["malformed_field_identifiers"]


def test_structured_event_emits_redacted_serializable_payload():
    event = structured_event(
        "x402.facilitator.rejected",
        Authorization="Bearer secret-token-value",
        network="eip155:8453",
    )
    payload = event.to_dict()

    assert payload["event"] == "x402.facilitator.rejected"
    assert payload["fields"]["Authorization"] == REDACTED
    assert json.loads(event.to_json())["fields"]["network"] == "eip155:8453"


def test_observability_event_surface_names_required_chronology():
    assert "x402.challenge.received" in X402_EVENT_NAMES
    assert "x402.challenge.parsed" in X402_EVENT_NAMES
    assert "x402.helper.invoked" in X402_EVENT_NAMES
    assert "x402.payload.generated" in X402_EVENT_NAMES
    assert "x402.facilitator.rejected" in X402_EVENT_NAMES
    assert "x402.settlement.retry" in X402_EVENT_NAMES
    assert "x402.interoperability.failure" in X402_EVENT_NAMES


def test_live_script_uses_observability_without_replacing_helper_path():
    assert live_x402_payment.x402HTTPClientSync.__name__ == "x402HTTPClientSync"
    assert live_x402_payment.emit_event.__name__ == "emit_event"
    assert live_x402_payment.helper_metadata.__name__ == "helper_metadata"
    assert "encode_payment_signature_header" not in live_x402_payment.__dict__


def test_wallet_environment_metadata_is_public_only():
    metadata = wallet_environment_metadata(
        wallet_address="0x93607a2b9E60eE550977e2793c114A13cE1E2846",
        network="eip155:8453",
    )

    assert metadata["wallet_address"].startswith("0x9360")
    assert metadata["chain_id"] == 8453
    assert metadata["payer_key_environment"] == "loaded"
    assert "private" not in metadata
