from __future__ import annotations

import copy
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from x402.http.constants import (
    PAYMENT_REQUIRED_HEADER,
    PAYMENT_RESPONSE_HEADER,
    PAYMENT_SIGNATURE_HEADER,
)
from x402.http.utils import (
    decode_payment_required_header,
    decode_payment_response_header,
    encode_payment_signature_header,
)
from x402.schemas import PaymentPayload, SettleResponse, VerifyResponse
from x402.schemas.v1 import PaymentPayloadV1

from retail_context.context_delta import validate_context_delta
from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.facilitator import RetailHTTPFacilitatorAdapter
from retail_context.production_config import RetailProductionControlConfig
from retail_context.production_controls import set_retail_service_mode
from retail_context.request_binding import (
    prepare_context_delta_request,
    prepare_state_ping_request,
    retail_request_digest,
)
from retail_context.runtime_config import RetailRuntimeConfig, RetailRuntimeConfigError
from retail_context.runtime_delivery import (
    RetailDeliveryRecoveryError,
    RetailRuntimeDeliveryCapability,
    claim_or_resume_retail_delivery,
    deliver_or_redeliver_retail_resource,
)
from retail_context.schema import validate_retail_context_object
from retail_context.service import create_retail_app
from retail_context.x402_payment import (
    PAYMENT_NETWORK,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    process_retail_x402_payment,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OBSERVED_AT = "2026-08-27T16:00:00Z"
PROOF_TOKEN = "rp8-controlled-proof-token"
PROOF_HEADER = "X-Nova-Retail-Controlled-Proof"
SETTLEMENT_WALLET = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"


class FakeFacilitator:
    def __init__(
        self,
        *,
        transaction: str = "0xrp8-settled",
        network: str = PAYMENT_NETWORK,
        amount: str | None = None,
        verify_valid: bool = True,
        settle_success: bool = True,
    ) -> None:
        self.transaction = transaction
        self.network = network
        self.amount = amount
        self.verify_valid = verify_valid
        self.settle_success = settle_success
        self.calls: list[str] = []

    def verify(self, payload, requirements):
        self.calls.append("verify")
        return VerifyResponse(is_valid=self.verify_valid, payer=PAYER)

    def settle(self, payload, requirements):
        self.calls.append("settle")
        return SettleResponse(
            success=self.settle_success,
            payer=PAYER,
            transaction=self.transaction,
            network=self.network,
            amount=self.amount if self.amount is not None else requirements.amount,
        )


def positive_observation() -> dict[str, Any]:
    return json.loads(
        (
            REPO_ROOT
            / "fixtures"
            / "retail_context"
            / "sources"
            / "positive_observation.json"
        ).read_text()
    )


def source_entry(*, fixture_namespace: bool = False) -> dict[str, Any]:
    return {
        "source_id": "fixture-public-network",
        "source_type": "public_network_status",
        "display_name": "Server-owned bounded network source",
        "source_namespace": (
            "retail_fixture_sources" if fixture_namespace else "retail_public_sources"
        ),
        "access_class": "public",
        "authorization_state": "authorized",
        "licensing_state": "public",
        "configuration_state": "configured",
        "credential_requirement": "none",
        "credential_namespace": "none",
        "freshness_policy_reference": "server-policy:controlled-proof",
        "provenance_requirement": "required",
        "enabled": True,
        "authority_effect": "none",
    }


def source_registry(*, fixture_namespace: bool = False) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "registry_id": "server-owned-controlled-proof-registry",
        "registry_status": "active",
        "sources": [source_entry(fixture_namespace=fixture_namespace)],
        "authority_effect": "none",
    }


def state_ping_envelope(*, generated_at: str = "2026-08-27T16:00:00Z") -> dict[str, Any]:
    observation = positive_observation()
    return {
        "subject": observation["subject"],
        "observations": [observation],
        "generated_at": generated_at,
    }


def context_delta_envelope() -> dict[str, Any]:
    first = prepare_state_ping_request(
        state_ping_envelope(generated_at="2026-08-27T16:00:00Z"),
        source_registry=source_registry(),
    ).build_resource()
    second_envelope = state_ping_envelope(generated_at="2026-08-27T16:01:00Z")
    second_envelope["observations"][0]["source_status"] = "stale"
    second = prepare_state_ping_request(
        second_envelope,
        source_registry=source_registry(),
    ).build_resource()
    return {
        "previous_context": first,
        "current_context": second,
        "generated_at": "2026-08-27T16:02:00Z",
    }


def runtime_config(
    db_path: Path,
    *,
    state_ping_limit: int = 20,
    context_delta_limit: int = 20,
) -> RetailRuntimeConfig:
    return RetailRuntimeConfig(
        controlled_proof_access_token=PROOF_TOKEN,
        facilitator_url="https://facilitator.example.test",
        facilitator_timeout_seconds=4,
        settlement_wallet=SETTLEMENT_WALLET,
        source_registry_path=db_path.parent / "server-source-registry.json",
        max_request_bytes=1_000_000,
        max_response_bytes=2_000_000,
        production_controls=RetailProductionControlConfig(
            control_db_path=db_path,
            rate_limit_window_seconds=60,
            state_ping_max_requests=state_ping_limit,
            context_delta_max_requests=context_delta_limit,
        ),
    )


def build_client(
    tmp_path: Path,
    *,
    facilitator: FakeFacilitator | None = None,
    enabled: bool = True,
    registry: dict[str, Any] | None = None,
    state_ping_limit: int = 20,
) -> tuple[TestClient, SQLiteRetailProductionControlStore, FakeFacilitator, RetailRuntimeConfig]:
    db_path = tmp_path / "production_controls.sqlite3"
    store = SQLiteRetailProductionControlStore(db_path)
    store.initialize()
    if enabled:
        set_retail_service_mode(
            store=store, mode="controlled_proof", changed_at=OBSERVED_AT
        )
    fake = facilitator or FakeFacilitator()
    config = runtime_config(db_path, state_ping_limit=state_ping_limit)
    app = create_retail_app(
        config=config,
        store=store,
        facilitator=fake,
        source_registry=registry or source_registry(),
        clock=lambda: OBSERVED_AT,
    )
    return TestClient(app), store, fake, config


def prepared_for(resource_type: str, envelope: dict[str, Any]):
    if resource_type == "state_ping":
        return prepare_state_ping_request(envelope, source_registry=source_registry())
    return prepare_context_delta_request(envelope)


def payment_header_for(
    resource_type: str,
    envelope: dict[str, Any],
) -> str:
    prepared = prepared_for(resource_type, envelope)
    requirement = build_retail_payment_requirement(
        resource_type=resource_type,
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "rp8-raw-payment-fixture"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    return encode_payment_signature_header(payload)


def post(
    client: TestClient,
    resource_type: str,
    envelope: dict[str, Any],
    *,
    digest: str | None = None,
    proof_token: str | None = PROOF_TOKEN,
    payment_header: str | None = None,
    extra_headers: dict[str, str] | None = None,
):
    prepared = prepared_for(resource_type, envelope)
    slug = "state-ping" if resource_type == "state_ping" else "context-delta"
    headers = dict(extra_headers or {})
    if proof_token is not None:
        headers[PROOF_HEADER] = proof_token
    if payment_header is not None:
        headers[PAYMENT_SIGNATURE_HEADER] = payment_header
    return client.post(
        f"/retail/v1/context/{slug}/{digest or prepared.request_digest}",
        json=envelope,
        headers=headers,
    )


@pytest.mark.parametrize("path", ["/openapi.json", "/docs", "/redoc"])
def test_openapi_swagger_and_redoc_are_unavailable(tmp_path: Path, path: str) -> None:
    client, _, _, _ = build_client(tmp_path)
    assert client.get(path).status_code == 404


def test_health_route_is_minimal_and_non_sensitive(tmp_path: Path) -> None:
    client, _, _, _ = build_client(tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("token", [None, "wrong-proof-token"])
def test_controlled_proof_credential_is_required_before_payment(
    tmp_path: Path, token: str | None
) -> None:
    client, store, facilitator, _ = build_client(tmp_path)
    response = post(client, "state_ping", state_ping_envelope(), proof_token=token)
    assert response.status_code == 403
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert facilitator.calls == []
    assert store.get_runtime_request(
        prepared_for("state_ping", state_ping_envelope()).request_id
    ) is None


def test_legacy_and_institutional_credentials_do_not_grant_access(tmp_path: Path) -> None:
    client, _, facilitator, _ = build_client(tmp_path)
    response = post(
        client,
        "state_ping",
        state_ping_envelope(),
        proof_token=None,
        extra_headers={
            "Authorization": "Bearer legacy-key",
            "X-Nova-API-Key": "institutional-key",
        },
    )
    assert response.status_code == 403
    assert facilitator.calls == []


def test_invalid_json_is_rejected_after_proof_but_before_payment(tmp_path: Path) -> None:
    client, _, facilitator, _ = build_client(tmp_path)
    response = client.post(
        "/retail/v1/context/state-ping/" + "0" * 64,
        content=b"not-json",
        headers={PROOF_HEADER: PROOF_TOKEN},
    )
    assert response.status_code == 400
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert facilitator.calls == []


def test_request_digest_mismatch_is_rejected_before_payment(tmp_path: Path) -> None:
    client, _, facilitator, _ = build_client(tmp_path)
    response = post(
        client,
        "state_ping",
        state_ping_envelope(),
        digest="0" * 64,
    )
    assert response.status_code == 400
    assert response.json()["error"] == "request_digest_mismatch"
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert facilitator.calls == []


def test_disabled_service_blocks_before_payment(tmp_path: Path) -> None:
    client, _, facilitator, _ = build_client(tmp_path, enabled=False)
    response = post(client, "state_ping", state_ping_envelope())
    assert response.status_code == 503
    assert response.json()["error"] == "service_disabled"
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert facilitator.calls == []


def test_rate_limit_executes_pre_payment_and_paid_retry_is_same_logical_request(
    tmp_path: Path,
) -> None:
    client, _, facilitator, _ = build_client(tmp_path, state_ping_limit=1)
    first_body = state_ping_envelope(generated_at="2026-08-27T16:00:00Z")
    first = post(client, "state_ping", first_body)
    assert first.status_code == 402
    paid = post(
        client,
        "state_ping",
        first_body,
        payment_header=payment_header_for("state_ping", first_body),
    )
    assert paid.status_code == 200
    second_body = state_ping_envelope(generated_at="2026-08-27T16:00:01Z")
    second = post(client, "state_ping", second_body)
    assert second.status_code == 429
    assert second.json()["error"] == "rate_limit_exceeded"
    assert facilitator.calls == ["verify", "settle"]


def test_same_body_has_same_digest_and_changed_observation_changes_it() -> None:
    first = state_ping_envelope()
    assert retail_request_digest(first) == retail_request_digest(copy.deepcopy(first))
    changed = copy.deepcopy(first)
    changed["observations"][0]["source_status"] = "stale"
    assert retail_request_digest(first) != retail_request_digest(changed)


def test_changed_context_changes_context_delta_digest() -> None:
    first = context_delta_envelope()
    changed = copy.deepcopy(first)
    changed["generated_at"] = "2026-08-27T16:03:00Z"
    assert retail_request_digest(first) != retail_request_digest(changed)


@pytest.mark.parametrize("resource_type", ["state_ping", "context_delta"])
def test_payment_requirement_uri_contains_exact_request_digest(resource_type: str) -> None:
    envelope = state_ping_envelope() if resource_type == "state_ping" else context_delta_envelope()
    prepared = prepared_for(resource_type, envelope)
    requirement = build_retail_payment_requirement(
        resource_type=resource_type,
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    assert prepared.request_digest in requirement["resource_uri"]
    assert requirement["resource_uri"] == prepared.resource_uri


def test_state_ping_uses_server_owned_source_registry() -> None:
    prepared = prepare_state_ping_request(
        state_ping_envelope(), source_registry=source_registry()
    )
    resource = prepared.build_resource()
    validate_retail_context_object(resource)
    assert resource["evidence"]
    assert resource["authority_effect"] == "none"


@pytest.mark.parametrize(
    "caller_field", ["enabled", "authorized", "configured", "licensed", "source_entries"]
)
def test_caller_cannot_self_authorize_source_eligibility(caller_field: str) -> None:
    envelope = state_ping_envelope()
    envelope[caller_field] = True
    with pytest.raises(ValueError, match="invalid_state_ping_request"):
        prepare_state_ping_request(envelope, source_registry=source_registry())


def test_fixture_source_remains_ineligible() -> None:
    prepared = prepare_state_ping_request(
        state_ping_envelope(),
        source_registry=source_registry(fixture_namespace=True),
    )
    resource = prepared.build_resource()
    assert resource["context_status"] == "insufficient_evidence"
    assert resource["evidence"] == []


def test_context_delta_validation_and_directionality_are_preserved() -> None:
    envelope = context_delta_envelope()
    forward = prepare_context_delta_request(envelope).build_resource()
    reverse_envelope = {
        "previous_context": envelope["current_context"],
        "current_context": envelope["previous_context"],
        "generated_at": envelope["generated_at"],
    }
    reverse = prepare_context_delta_request(reverse_envelope).build_resource()
    validate_context_delta(forward)
    validate_context_delta(reverse)
    assert forward["resource_id"] != reverse["resource_id"]
    assert forward["authority_effect"] == reverse["authority_effect"] == "none"


@pytest.mark.parametrize("resource_type", ["state_ping", "context_delta"])
def test_missing_payment_returns_canonical_402(resource_type: str, tmp_path: Path) -> None:
    client, _, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope() if resource_type == "state_ping" else context_delta_envelope()
    response = post(client, resource_type, envelope)
    assert response.status_code == 402
    decoded = decode_payment_required_header(response.headers[PAYMENT_REQUIRED_HEADER])
    assert decoded.x402_version == 2
    assert decoded.accepts[0].network == PAYMENT_NETWORK
    assert decoded.accepts[0].amount == ("2000" if resource_type == "state_ping" else "20000")


def test_x402_v1_is_rejected_without_facilitator_call(tmp_path: Path) -> None:
    client, _, facilitator, _ = build_client(tmp_path)
    v1 = PaymentPayloadV1(
        x402_version=1,
        scheme="exact",
        network="base",
        payload={"signature": "legacy"},
    )
    response = post(
        client,
        "state_ping",
        state_ping_envelope(),
        payment_header=encode_payment_signature_header(v1),
    )
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_x402_version"
    assert facilitator.calls == []


@pytest.mark.parametrize(
    ("facilitator", "reason"),
    [
        (FakeFacilitator(network="eip155:1"), "settlement_network_mismatch"),
        (FakeFacilitator(amount="1"), "settlement_amount_mismatch"),
        (FakeFacilitator(transaction=""), "settlement_reference_missing"),
    ],
)
def test_settlement_reconciliation_failures_are_bounded(
    tmp_path: Path, facilitator: FakeFacilitator, reason: str
) -> None:
    client, store, _, _ = build_client(tmp_path, facilitator=facilitator)
    envelope = state_ping_envelope()
    response = post(
        client,
        "state_ping",
        envelope,
        payment_header=payment_header_for("state_ping", envelope),
    )
    assert response.status_code == 402
    assert response.json()["error"] == reason
    assert store.count_payment_claims() == 0


@pytest.mark.parametrize("resource_type", ["state_ping", "context_delta"])
def test_paid_resource_delivery_is_valid_and_has_payment_response(
    tmp_path: Path, resource_type: str
) -> None:
    client, store, facilitator, _ = build_client(tmp_path)
    envelope = state_ping_envelope() if resource_type == "state_ping" else context_delta_envelope()
    response = post(
        client,
        resource_type,
        envelope,
        payment_header=payment_header_for(resource_type, envelope),
    )
    assert response.status_code == 200
    if resource_type == "state_ping":
        validate_retail_context_object(response.json())
    else:
        validate_context_delta(response.json())
    payment_response = decode_payment_response_header(
        response.headers[PAYMENT_RESPONSE_HEADER]
    )
    assert payment_response.success
    assert payment_response.transaction == facilitator.transaction
    assert store.count_payment_claims() == 1
    assert response.json()["authority_effect"] == "none"


def test_payment_for_digest_a_cannot_serve_digest_b(tmp_path: Path) -> None:
    client, store, _, _ = build_client(tmp_path)
    body_a = state_ping_envelope(generated_at="2026-08-27T16:00:00Z")
    body_b = state_ping_envelope(generated_at="2026-08-27T16:00:01Z")
    response = post(
        client,
        "state_ping",
        body_b,
        payment_header=payment_header_for("state_ping", body_a),
    )
    assert response.status_code == 402
    assert response.json()["error"] == "invalid_payment_payload"
    assert store.count_payment_claims() == 0


def test_duplicate_settlement_returns_identical_resource_without_second_claim(tmp_path: Path) -> None:
    client, store, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    header = payment_header_for("state_ping", envelope)
    first = post(client, "state_ping", envelope, payment_header=header)
    second = post(client, "state_ping", envelope, payment_header=header)
    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert first.headers["X-Nova-Retail-Response-Digest"] == second.headers["X-Nova-Retail-Response-Digest"]
    assert first.headers["X-Nova-Retail-Delivery-Mode"] == "initial_delivery"
    assert second.headers["X-Nova-Retail-Delivery-Mode"] == "idempotent_redelivery"
    assert store.count_payment_claims() == 1


def test_pending_claim_resumes_only_with_fresh_same_payment_outcome(tmp_path: Path) -> None:
    client, store, facilitator, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    prepared = prepared_for("state_ping", envelope)
    challenge_response = post(client, "state_ping", envelope)
    assert challenge_response.status_code == 402
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "fresh-pending-proof"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    outcome = process_retail_x402_payment(
        requirement=requirement, payment_payload=payload, facilitator=facilitator
    )
    capability = claim_or_resume_retail_delivery(
        payment_outcome=outcome,
        prepared=prepared,
        store=store,
        observed_at=OBSERVED_AT,
    )
    assert capability.delivery_status == "pending"
    response = post(
        client,
        "state_ping",
        envelope,
        payment_header=encode_payment_signature_header(payload),
    )
    assert response.status_code == 200
    assert response.headers["X-Nova-Retail-Delivery-Mode"] == "initial_delivery"
    assert store.count_payment_claims() == 1


def test_serialized_rp6_receipt_cannot_claim_delivery(tmp_path: Path) -> None:
    _, store, facilitator, _ = build_client(tmp_path)
    prepared = prepared_for("state_ping", state_ping_envelope())
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "serialized-receipt-is-audit-only"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    outcome = process_retail_x402_payment(
        requirement=requirement, payment_payload=payload, facilitator=facilitator
    )
    serialized = json.loads(json.dumps(outcome.to_receipt()))
    with pytest.raises(RetailDeliveryRecoveryError, match="invalid_payment_outcome"):
        claim_or_resume_retail_delivery(
            payment_outcome=serialized,
            prepared=prepared,
            store=store,
            observed_at=OBSERVED_AT,
        )
    assert store.count_payment_claims() == 0


def test_fabricated_delivery_capability_cannot_deliver(tmp_path: Path) -> None:
    _, store, _, _ = build_client(tmp_path)
    prepared = prepared_for("state_ping", state_ping_envelope())
    fabricated = RetailRuntimeDeliveryCapability(
        claim_id="payment-claim-fabricated",
        delivery_status="pending",
        payment_receipt_id="payment-receipt-fabricated",
        request_id=prepared.request_id,
        resource_uri=prepared.resource_uri,
    )
    with pytest.raises(RetailDeliveryRecoveryError, match="invalid_delivery_capability"):
        deliver_or_redeliver_retail_resource(
            capability=fabricated,
            prepared=prepared,
            store=store,
            observed_at=OBSERVED_AT,
            max_response_bytes=2_000_000,
        )


def test_delivered_response_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    client, store, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    header = payment_header_for("state_ping", envelope)
    assert post(client, "state_ping", envelope, payment_header=header).status_code == 200
    with sqlite3.connect(store.db_path) as connection:
        connection.execute(
            "UPDATE retail_payment_consumption SET response_digest = ?",
            ("0" * 64,),
        )
    retry = post(client, "state_ping", envelope, payment_header=header)
    assert retry.status_code == 409
    assert retry.json()["error"] == "response_digest_mismatch"


def test_cross_request_replay_is_denied(tmp_path: Path) -> None:
    facilitator = FakeFacilitator(transaction="0xsame-transaction")
    client, store, _, _ = build_client(tmp_path, facilitator=facilitator)
    first_body = state_ping_envelope(generated_at="2026-08-27T16:00:00Z")
    second_body = state_ping_envelope(generated_at="2026-08-27T16:00:01Z")
    first = post(
        client,
        "state_ping",
        first_body,
        payment_header=payment_header_for("state_ping", first_body),
    )
    second = post(
        client,
        "state_ping",
        second_body,
        payment_header=payment_header_for("state_ping", second_body),
    )
    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["error"] == "payment_replay_conflict"
    assert store.count_payment_claims() == 1


def test_restart_preserves_replay_state_and_idempotent_redelivery(tmp_path: Path) -> None:
    client, store, facilitator, config = build_client(tmp_path)
    envelope = state_ping_envelope()
    header = payment_header_for("state_ping", envelope)
    first = post(client, "state_ping", envelope, payment_header=header)
    assert first.status_code == 200
    reopened = SQLiteRetailProductionControlStore(store.db_path)
    restarted = TestClient(
        create_retail_app(
            config=config,
            store=reopened,
            facilitator=facilitator,
            source_registry=source_registry(),
            clock=lambda: OBSERVED_AT,
        )
    )
    second = post(restarted, "state_ping", envelope, payment_header=header)
    assert second.status_code == 200
    assert second.content == first.content
    assert second.headers["X-Nova-Retail-Delivery-Mode"] == "idempotent_redelivery"
    assert reopened.count_payment_claims() == 1


def test_failed_delivery_does_not_grant_automatic_retry(tmp_path: Path) -> None:
    client, store, facilitator, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    prepared = prepared_for("state_ping", envelope)
    assert post(client, "state_ping", envelope).status_code == 402
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "failed-delivery-proof"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    outcome = process_retail_x402_payment(
        requirement=requirement, payment_payload=payload, facilitator=facilitator
    )
    capability = claim_or_resume_retail_delivery(
        payment_outcome=outcome,
        prepared=prepared,
        store=store,
        observed_at=OBSERVED_AT,
    )
    store.mark_delivery(
        claim_id=capability.claim_id,
        status="failed",
        occurred_at=OBSERVED_AT,
        processing_duration_ms=1,
        failure_reason="resource_render_failed",
    )
    retry = post(
        client,
        "state_ping",
        envelope,
        payment_header=encode_payment_signature_header(payload),
    )
    assert retry.status_code == 409
    assert retry.json()["error"] == "delivery_reconciliation_required"
    assert store.count_payment_claims() == 1


def test_kill_switch_disable_and_restore_affects_service_only(tmp_path: Path) -> None:
    client, store, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    before = copy.deepcopy(envelope)
    assert post(client, "state_ping", envelope).status_code == 402
    set_retail_service_mode(store=store, mode="disabled", changed_at=OBSERVED_AT)
    assert post(client, "state_ping", envelope).status_code == 503
    reopened = SQLiteRetailProductionControlStore(store.db_path)
    assert reopened.get_service_mode() == "disabled"
    set_retail_service_mode(
        store=reopened, mode="controlled_proof", changed_at=OBSERVED_AT
    )
    assert post(client, "state_ping", envelope).status_code == 402
    assert envelope == before


def test_no_raw_payment_material_is_logged_or_persisted(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    client, store, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    header = payment_header_for("state_ping", envelope)
    with caplog.at_level(logging.DEBUG):
        response = post(client, "state_ping", envelope, payment_header=header)
    assert response.status_code == 200
    rendered_logs = caplog.text
    database = store.db_path.read_bytes()
    assert header not in rendered_logs
    assert "rp8-raw-payment-fixture" not in rendered_logs
    assert header.encode() not in database
    assert b"rp8-raw-payment-fixture" not in database


def test_request_subject_context_body_and_provider_claim_are_not_persisted(
    tmp_path: Path,
) -> None:
    client, store, _, _ = build_client(tmp_path)
    envelope = state_ping_envelope()
    response = post(
        client,
        "state_ping",
        envelope,
        payment_header=payment_header_for("state_ping", envelope),
    )
    assert response.status_code == 200
    database = store.db_path.read_bytes()
    assert b"ethereum-mainnet" not in database
    assert b"The fixture reports nominal network operation." not in database
    assert b"fixture:network:001" not in database
    runtime_request = store.get_runtime_request(
        prepared_for("state_ping", envelope).request_id
    )
    assert runtime_request is not None
    assert len(runtime_request["subject_hash"]) == 64
    assert "ethereum-mainnet" not in json.dumps(store.list_telemetry())


def test_live_facilitator_adapter_uses_official_client_with_bounded_timeout() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"isValid": True, "payer": PAYER})

    http_client = httpx.Client(
        transport=httpx.MockTransport(handler), timeout=4
    )
    adapter = RetailHTTPFacilitatorAdapter(
        url="https://facilitator.example.test",
        timeout_seconds=4,
        http_client=http_client,
    )
    envelope = state_ping_envelope()
    prepared = prepared_for("state_ping", envelope)
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "adapter-fixture"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    response = adapter.verify(payload, challenge.payment_required.accepts[0])
    assert response.is_valid
    assert adapter.timeout_seconds == 4
    assert captured[0].url.path == "/verify"
    adapter.close()


def test_runtime_config_rejects_unbounded_facilitator_timeout(tmp_path: Path) -> None:
    with pytest.raises(RetailRuntimeConfigError):
        RetailRuntimeConfig(
            controlled_proof_access_token=PROOF_TOKEN,
            facilitator_url="https://facilitator.example.test",
            facilitator_timeout_seconds=31,
            settlement_wallet=SETTLEMENT_WALLET,
            source_registry_path=tmp_path / "registry.json",
            max_request_bytes=1000,
            max_response_bytes=1000,
            production_controls=RetailProductionControlConfig(
                tmp_path / "controls.sqlite3", 60, 2, 2
            ),
        )


def test_facilitator_adapter_itself_rejects_unbounded_timeout() -> None:
    with pytest.raises(ValueError, match="invalid_retail_facilitator_timeout"):
        RetailHTTPFacilitatorAdapter(
            url="https://facilitator.example.test",
            timeout_seconds=31,
        )


def test_runtime_config_does_not_fall_back_to_legacy_or_cdp_variables() -> None:
    with pytest.raises(RetailRuntimeConfigError):
        RetailRuntimeConfig.from_env(
            {
                "NOVA_API_KEY": PROOF_TOKEN,
                "X402_FACILITATOR_URL": "https://facilitator.example.test",
                "CDP_API_KEY_ID": "must-not-be-read",
                "CDP_WALLET_SECRET": "must-not-be-read",
                "NOVA_RETAIL_RATE_LIMIT_WINDOW_SECONDS": "60",
                "NOVA_RETAIL_STATE_PING_MAX_REQUESTS": "1",
                "NOVA_RETAIL_CONTEXT_DELTA_MAX_REQUESTS": "1",
            }
        )
