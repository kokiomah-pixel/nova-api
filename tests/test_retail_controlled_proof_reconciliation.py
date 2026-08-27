from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from x402.http.constants import PAYMENT_SIGNATURE_HEADER
from x402.http.utils import encode_payment_signature_header
from x402.schemas import PaymentPayload, SettleResponse, VerifyResponse

from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.production_config import RetailProductionControlConfig
from retail_context.production_controls import set_retail_service_mode
from retail_context.request_binding import prepare_state_ping_request
from retail_context.runtime_config import RetailRuntimeConfig
from retail_context.runtime_delivery import claim_or_resume_retail_delivery
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
    def __init__(self, *, transaction: str = "0xrp8-reconciliation") -> None:
        self.transaction = transaction
        self.calls: list[str] = []

    def verify(self, payload, requirements):
        self.calls.append("verify")
        return VerifyResponse(is_valid=True, payer=PAYER)

    def settle(self, payload, requirements):
        self.calls.append("settle")
        return SettleResponse(
            success=True,
            payer=PAYER,
            transaction=self.transaction,
            network=PAYMENT_NETWORK,
            amount=requirements.amount,
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


def source_registry(*, configured: bool = True) -> dict[str, Any]:
    entry = {
        "source_id": "fixture-public-network",
        "source_type": "public_network_status",
        "display_name": "Server-owned bounded network source",
        "source_namespace": "retail_public_sources",
        "access_class": "public",
        "authorization_state": "authorized",
        "licensing_state": "public",
        "configuration_state": "configured" if configured else "not_configured",
        "credential_requirement": "none",
        "credential_namespace": "none",
        "freshness_policy_reference": "server-policy:controlled-proof",
        "provenance_requirement": "required",
        "enabled": True,
        "authority_effect": "none",
    }
    return {
        "schema_version": "0.1.0",
        "registry_id": "server-owned-controlled-proof-registry",
        "registry_status": "active",
        "sources": [entry],
        "authority_effect": "none",
    }


def state_ping_envelope() -> dict[str, Any]:
    observation = positive_observation()
    return {
        "subject": observation["subject"],
        "observations": [observation],
        "generated_at": OBSERVED_AT,
    }


def runtime_config(db_path: Path, *, retry_limit: int = 3) -> RetailRuntimeConfig:
    return RetailRuntimeConfig(
        controlled_proof_access_token=PROOF_TOKEN,
        facilitator_url="https://facilitator.example.test",
        facilitator_timeout_seconds=4,
        settlement_wallet=SETTLEMENT_WALLET,
        source_registry_path=db_path.parent / "registry.json",
        max_request_bytes=1_000_000,
        max_response_bytes=2_000_000,
        production_controls=RetailProductionControlConfig(
            control_db_path=db_path,
            rate_limit_window_seconds=60,
            state_ping_max_requests=1,
            context_delta_max_requests=1,
        ),
        retry_max_requests=retry_limit,
    )


def build_client(
    db_path: Path,
    facilitator: FakeFacilitator,
    registry: dict[str, Any],
    *,
    retry_limit: int = 3,
) -> tuple[TestClient, SQLiteRetailProductionControlStore]:
    store = SQLiteRetailProductionControlStore(db_path)
    store.initialize()
    if store.get_service_mode() != "controlled_proof":
        set_retail_service_mode(
            store=store,
            mode="controlled_proof",
            changed_at=OBSERVED_AT,
        )
    app = create_retail_app(
        config=runtime_config(db_path, retry_limit=retry_limit),
        store=store,
        facilitator=facilitator,
        source_registry=registry,
        clock=lambda: OBSERVED_AT,
    )
    return TestClient(app), store


def payment_payload(prepared) -> PaymentPayload:
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    return PaymentPayload(
        x402_version=2,
        payload={"signature": "rp8-reconciliation-payment"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )


def post(client: TestClient, prepared, *, payload: PaymentPayload | None = None):
    headers = {PROOF_HEADER: PROOF_TOKEN}
    if payload is not None:
        headers[PAYMENT_SIGNATURE_HEADER] = encode_payment_signature_header(payload)
    return client.post(
        f"/retail/v1/context/state-ping/{prepared.request_digest}",
        json=prepared.request_envelope,
        headers=headers,
    )


def make_pending_claim(store, facilitator, prepared, payload):
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri=prepared.resource_uri,
        settlement_wallet=SETTLEMENT_WALLET,
    )
    outcome = process_retail_x402_payment(
        requirement=requirement,
        payment_payload=payload,
        facilitator=facilitator,
    )
    return claim_or_resume_retail_delivery(
        payment_outcome=outcome,
        prepared=prepared,
        store=store,
        observed_at=OBSERVED_AT,
    )


def test_source_binding_changes_paid_resource_identity() -> None:
    envelope = state_ping_envelope()
    first = prepare_state_ping_request(envelope, source_registry=source_registry())
    changed = prepare_state_ping_request(
        envelope, source_registry=source_registry(configured=False)
    )
    assert first.request_digest == changed.request_digest
    assert first.source_binding_digest != changed.source_binding_digest
    assert first.resource_uri != changed.resource_uri


def test_pending_claim_fails_closed_after_server_source_binding_drift(tmp_path: Path) -> None:
    db_path = tmp_path / "controls.sqlite3"
    facilitator = FakeFacilitator()
    first_registry = source_registry()
    client, store = build_client(db_path, facilitator, first_registry)
    first = prepare_state_ping_request(state_ping_envelope(), source_registry=first_registry)
    assert post(client, first).status_code == 402
    payload = payment_payload(first)
    capability = make_pending_claim(store, facilitator, first, payload)
    assert capability.delivery_status == "pending"

    changed_registry = source_registry(configured=False)
    restarted, reopened = build_client(db_path, facilitator, changed_registry)
    changed = prepare_state_ping_request(
        state_ping_envelope(), source_registry=changed_registry
    )
    response = post(restarted, changed, payload=payment_payload(changed))
    assert response.status_code == 400
    assert response.json()["error"] == "source_binding_reconciliation_failed"
    claim = reopened.get_payment_claim(capability.claim_id)
    assert claim is not None and claim["delivery_status"] == "pending"


def test_unchanged_source_binding_resumes_pending_claim_after_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "controls.sqlite3"
    facilitator = FakeFacilitator()
    registry = source_registry()
    client, store = build_client(db_path, facilitator, registry)
    prepared = prepare_state_ping_request(state_ping_envelope(), source_registry=registry)
    assert post(client, prepared).status_code == 402
    payload = payment_payload(prepared)
    capability = make_pending_claim(store, facilitator, prepared, payload)
    assert capability.delivery_status == "pending"

    restarted, reopened = build_client(db_path, facilitator, copy.deepcopy(registry))
    response = post(restarted, prepared, payload=payload)
    assert response.status_code == 200
    claim = reopened.get_payment_claim(capability.claim_id)
    assert claim is not None and claim["delivery_status"] == "delivered"


def test_retry_budget_survives_restart_and_denies_before_facilitator(tmp_path: Path) -> None:
    db_path = tmp_path / "controls.sqlite3"
    facilitator = FakeFacilitator()
    registry = source_registry()
    client, store = build_client(db_path, facilitator, registry, retry_limit=1)
    prepared = prepare_state_ping_request(state_ping_envelope(), source_registry=registry)
    payload = payment_payload(prepared)

    assert post(client, prepared).status_code == 402
    assert post(client, prepared, payload=payload).status_code == 200
    assert facilitator.calls == ["verify", "settle"]
    assert post(client, prepared, payload=payload).status_code == 200
    assert facilitator.calls == ["verify", "settle", "verify", "settle"]
    claim_count = store.count_payment_claims()

    restarted, reopened = build_client(
        db_path, facilitator, copy.deepcopy(registry), retry_limit=1
    )
    calls_before = list(facilitator.calls)
    claim_before = reopened.get_payment_claim_by_settlement(
        network=PAYMENT_NETWORK,
        transaction_reference=facilitator.transaction,
    )
    denied = post(restarted, prepared, payload=payload)
    assert denied.status_code == 429
    assert denied.json()["error"] == "rate_limit_exceeded"
    assert facilitator.calls == calls_before
    assert reopened.count_payment_claims() == claim_count
    assert reopened.get_payment_claim_by_settlement(
        network=PAYMENT_NETWORK,
        transaction_reference=facilitator.transaction,
    ) == claim_before
