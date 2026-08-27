from __future__ import annotations

import json

from x402.schemas import PaymentPayload, SettleResponse, VerifyResponse

from retail_context.x402_payment import (
    PAYMENT_NETWORK,
    RetailPaymentOutcome,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    payment_receipt_allows_resource_access,
    process_retail_x402_payment,
    validate_retail_x402_payment_record,
)


SETTLEMENT_WALLET = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"


class FakeFacilitator:
    def __init__(self, *, verify_valid: bool = True, settle_success: bool = True) -> None:
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
            transaction="0xsettled" if self.settle_success else "",
            network=PAYMENT_NETWORK,
            amount=requirements.amount,
        )


def _requirement() -> dict:
    return build_retail_payment_requirement(
        resource_type="state_ping",
        resource_uri="/retail/v1/context/state-ping",
        settlement_wallet=SETTLEMENT_WALLET,
    )


def _payload(requirement: dict) -> PaymentPayload:
    challenge = build_retail_payment_challenge(requirement)
    return PaymentPayload(
        x402_version=2,
        payload={"signature": "deterministic-fixture-signature"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )


def _successful_outcome() -> RetailPaymentOutcome:
    requirement = _requirement()
    return process_retail_x402_payment(
        requirement=requirement,
        payment_payload=_payload(requirement),
        facilitator=FakeFacilitator(),
    )


def test_direct_successful_outcome_permits_access() -> None:
    outcome = _successful_outcome()
    assert isinstance(outcome, RetailPaymentOutcome)
    assert payment_receipt_allows_resource_access(outcome)


def test_serialized_successful_receipt_does_not_independently_permit_access() -> None:
    outcome = _successful_outcome()
    serialized = json.dumps(outcome, sort_keys=True)
    deserialized = json.loads(serialized)
    validate_retail_x402_payment_record(deserialized, "payment_receipt")
    assert deserialized == outcome.to_receipt()
    assert not payment_receipt_allows_resource_access(deserialized)


def test_copied_successful_receipt_does_not_independently_permit_access() -> None:
    outcome = _successful_outcome()
    copied = dict(outcome)
    validate_retail_x402_payment_record(copied, "payment_receipt")
    assert copied == outcome.to_receipt()
    assert not payment_receipt_allows_resource_access(copied)


def test_fabricated_schema_valid_permitted_receipt_does_not_grant_access() -> None:
    outcome = _successful_outcome()
    fabricated = outcome.to_receipt()
    validate_retail_x402_payment_record(fabricated, "payment_receipt")
    assert fabricated["payment_verification_status"] == "verified"
    assert fabricated["settlement_status"] == "settled"
    assert fabricated["access_status"] == "permitted"
    assert not payment_receipt_allows_resource_access(fabricated)


def test_receipt_serialization_is_deterministic_and_capability_free() -> None:
    first = _successful_outcome()
    second = _successful_outcome()
    assert first.to_receipt() == second.to_receipt()
    assert json.dumps(first.to_receipt(), sort_keys=True) == json.dumps(
        second.to_receipt(), sort_keys=True
    )
    assert "_access_capability" not in first.to_receipt()


def test_failed_outcome_never_permits_access() -> None:
    requirement = _requirement()
    outcome = process_retail_x402_payment(
        requirement=requirement,
        payment_payload=_payload(requirement),
        facilitator=FakeFacilitator(verify_valid=False),
    )
    assert isinstance(outcome, RetailPaymentOutcome)
    assert not payment_receipt_allows_resource_access(outcome)
