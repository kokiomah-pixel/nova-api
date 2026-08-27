from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from x402.schemas import PaymentPayload, SettleResponse, VerifyResponse

from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.production_controls import (
    claim_settled_payment_for_delivery,
    delivery_outcome_allows_resource_delivery,
    mark_retail_delivery_complete,
    mark_retail_delivery_failed,
    set_retail_service_mode,
)
from retail_context.x402_payment import (
    PAYMENT_NETWORK,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    process_retail_x402_payment,
)


OBSERVED_AT = "2026-08-27T13:00:00Z"
SETTLEMENT_WALLET = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"


class FakeFacilitator:
    def __init__(self, transaction: str) -> None:
        self.transaction = transaction

    def verify(self, payload, requirements):
        return VerifyResponse(is_valid=True, payer=PAYER)

    def settle(self, payload, requirements):
        return SettleResponse(
            success=True,
            payer=PAYER,
            transaction=self.transaction,
            network=PAYMENT_NETWORK,
            amount=requirements.amount,
        )


class TelemetryFailingStore(SQLiteRetailProductionControlStore):
    @staticmethod
    def _insert_telemetry(connection, event):
        raise sqlite3.OperationalError("injected_telemetry_failure")


def payment_outcome(*, transaction: str):
    requirement = build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri="/retail/v1/context/state-ping",
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "atomicity-test-signature"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    return process_retail_x402_payment(
        requirement=requirement,
        payment_payload=payload,
        facilitator=FakeFacilitator(transaction),
    )


def controlled_store(path: Path) -> SQLiteRetailProductionControlStore:
    store = SQLiteRetailProductionControlStore(path)
    store.initialize()
    set_retail_service_mode(
        store=store,
        mode="controlled_proof",
        changed_at=OBSERVED_AT,
    )
    return store


def test_payment_claim_rolls_back_when_required_telemetry_cannot_commit(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    healthy = controlled_store(path)
    payment = payment_outcome(transaction="0xatomic-claim")
    failing = TelemetryFailingStore(path)

    denied = claim_settled_payment_for_delivery(
        payment_outcome=payment,
        request_id="request-atomic-claim",
        store=failing,
        observed_at=OBSERVED_AT,
    )

    assert denied["failure_reason"] == "control_store_unavailable"
    assert not delivery_outcome_allows_resource_delivery(denied)
    assert healthy.count_payment_claims() == 0

    recovered = claim_settled_payment_for_delivery(
        payment_outcome=payment,
        request_id="request-atomic-claim-retry",
        store=healthy,
        observed_at="2026-08-27T13:00:01Z",
    )
    assert delivery_outcome_allows_resource_delivery(recovered)
    assert healthy.count_payment_claims() == 1


def test_delivery_complete_rolls_back_when_required_telemetry_cannot_commit(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    healthy = controlled_store(path)
    payment = payment_outcome(transaction="0xatomic-delivery-complete")
    delivery = claim_settled_payment_for_delivery(
        payment_outcome=payment,
        request_id="request-delivery-complete",
        store=healthy,
        observed_at=OBSERVED_AT,
    )
    assert delivery_outcome_allows_resource_delivery(delivery)

    failing = TelemetryFailingStore(path)
    with pytest.raises(sqlite3.OperationalError, match="injected_telemetry_failure"):
        mark_retail_delivery_complete(
            delivery_outcome=delivery,
            store=failing,
            observed_at="2026-08-27T13:00:01Z",
            response_digest="a" * 64,
            response_bytes=128,
            processing_duration_ms=9,
        )

    assert healthy.get_payment_claim(delivery["claim_id"])["delivery_status"] == "pending"

    persisted = mark_retail_delivery_complete(
        delivery_outcome=delivery,
        store=healthy,
        observed_at="2026-08-27T13:00:02Z",
        response_digest="a" * 64,
        response_bytes=128,
        processing_duration_ms=9,
    )
    assert persisted["delivery_status"] == "delivered"


def test_delivery_failure_rolls_back_when_required_observability_cannot_commit(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    healthy = controlled_store(path)
    payment = payment_outcome(transaction="0xatomic-delivery-failed")
    delivery = claim_settled_payment_for_delivery(
        payment_outcome=payment,
        request_id="request-delivery-failed",
        store=healthy,
        observed_at=OBSERVED_AT,
    )
    assert delivery_outcome_allows_resource_delivery(delivery)

    failing = TelemetryFailingStore(path)
    with pytest.raises(sqlite3.OperationalError, match="injected_telemetry_failure"):
        mark_retail_delivery_failed(
            delivery_outcome=delivery,
            store=failing,
            observed_at="2026-08-27T13:00:01Z",
            failure_reason="resource_render_failed",
            processing_duration_ms=11,
        )

    assert healthy.get_payment_claim(delivery["claim_id"])["delivery_status"] == "pending"
    assert healthy.list_incidents() == []

    persisted = mark_retail_delivery_failed(
        delivery_outcome=delivery,
        store=healthy,
        observed_at="2026-08-27T13:00:02Z",
        failure_reason="resource_render_failed",
        processing_duration_ms=11,
    )
    assert persisted["delivery_status"] == "failed"
    assert any(
        item["incident_type"] == "delivery_failure"
        for item in healthy.list_incidents()
    )
