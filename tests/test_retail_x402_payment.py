from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema.exceptions import ValidationError
from x402.http.constants import PAYMENT_REQUIRED_HEADER, PAYMENT_SIGNATURE_HEADER
from x402.http.utils import decode_payment_required_header
from x402.schemas import PaymentPayload, PaymentRequired, PaymentRequirements, SettleResponse, VerifyResponse

from retail_context.boundaries import validate_retail_package_imports
from retail_context.x402_payment import (
    ACCESS_EFFECT,
    ASSET_DECIMALS,
    AUTHORITY_EFFECT,
    DISPLAY_ASSET,
    DISPLAY_NETWORK,
    PAYMENT_ASSET,
    PAYMENT_NETWORK,
    PAYMENT_SCHEME,
    PRICING_MODEL,
    RETAIL_PAYMENT_HEADER_NAMES,
    RETAIL_RESOURCE_PRICE_CATALOG,
    SETTLEMENT_WALLET_ENV,
    X402_VERSION,
    RetailX402PaymentError,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    payment_receipt_allows_resource_access,
    process_retail_x402_payment,
    validate_retail_payment_requirement,
    validate_retail_x402_payment_record,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SETTLEMENT_WALLET = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"


class FakeFacilitator:
    def __init__(
        self,
        *,
        verify_response: VerifyResponse | dict[str, Any] | None = None,
        settle_response: SettleResponse | dict[str, Any] | None = None,
        verify_error: Exception | None = None,
        settle_error: Exception | None = None,
    ) -> None:
        self.verify_response = verify_response or VerifyResponse(
            is_valid=True, payer=PAYER
        )
        self.settle_response = settle_response or SettleResponse(
            success=True,
            payer=PAYER,
            transaction="0xsettled",
            network=PAYMENT_NETWORK,
            amount="2000",
        )
        self.verify_error = verify_error
        self.settle_error = settle_error
        self.calls: list[str] = []
        self.payloads: list[PaymentPayload] = []
        self.requirements: list[PaymentRequirements] = []

    def verify(self, payload: PaymentPayload, requirements: PaymentRequirements):
        self.calls.append("verify")
        self.payloads.append(payload)
        self.requirements.append(requirements)
        if self.verify_error:
            raise self.verify_error
        return self.verify_response

    def settle(self, payload: PaymentPayload, requirements: PaymentRequirements):
        self.calls.append("settle")
        self.payloads.append(payload)
        self.requirements.append(requirements)
        if self.settle_error:
            raise self.settle_error
        return self.settle_response


def requirement(
    resource_type: str = "state_ping",
    resource_uri: str = "/retail/v1/context/state-ping",
    settlement_wallet: str = SETTLEMENT_WALLET,
) -> dict[str, Any]:
    return build_retail_payment_requirement(
        resource_type=resource_type,
        resource_uri=resource_uri,
        settlement_wallet=settlement_wallet,
    )


def payment_payload(payment_requirement: dict[str, Any] | None = None) -> PaymentPayload:
    challenge = build_retail_payment_challenge(payment_requirement or requirement())
    return PaymentPayload(
        x402_version=2,
        payload={"signature": "deterministic-fixture-signature"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )


def successful_receipt(
    *,
    payment_requirement: dict[str, Any] | None = None,
    transaction: str = "0xsettled",
    payer: str | None = PAYER,
) -> dict[str, Any]:
    required = payment_requirement or requirement()
    facilitator = FakeFacilitator(
        settle_response=SettleResponse(
            success=True,
            payer=payer,
            transaction=transaction,
            network=PAYMENT_NETWORK,
            amount=required["amount_atomic"],
        )
    )
    return process_retail_x402_payment(
        requirement=required,
        payment_payload=payment_payload(required),
        facilitator=facilitator,
    )


@pytest.mark.parametrize(
    ("resource_type", "display", "atomic"),
    [("state_ping", "0.002", "2000"), ("context_delta", "0.02", "20000")],
)
def test_closed_resource_prices_are_exact_strings(
    resource_type: str, display: str, atomic: str
) -> None:
    uri = f"/retail/v1/context/{resource_type.replace('_', '-')}"
    built = requirement(resource_type, uri)
    assert built["display_price_usdc"] == display
    assert built["amount_atomic"] == atomic
    assert isinstance(built["amount_atomic"], str)


def test_pricing_model_is_pay_per_context_resource() -> None:
    assert requirement()["pricing_model"] == PRICING_MODEL == "pay_per_context_resource"


def test_unknown_resource_type_fails_closed() -> None:
    with pytest.raises(RetailX402PaymentError, match="resource_not_payable"):
        requirement("full_context", "/retail/v1/context/full")


def test_caller_cannot_override_canonical_price() -> None:
    assert "amount_atomic" not in inspect.signature(build_retail_payment_requirement).parameters
    with pytest.raises(TypeError):
        build_retail_payment_requirement(
            resource_type="state_ping",
            resource_uri="/state",
            settlement_wallet=SETTLEMENT_WALLET,
            amount_atomic="1",  # type: ignore[call-arg]
        )


def test_protocol_constants_are_fixed_to_base_usdc_v2_exact() -> None:
    built = requirement()
    assert built["x402_version"] == X402_VERSION == 2
    assert built["scheme"] == PAYMENT_SCHEME == "exact"
    assert built["network"] == PAYMENT_NETWORK == "eip155:8453"
    assert built["display_network"] == DISPLAY_NETWORK == "base"
    assert built["asset"] == PAYMENT_ASSET == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    assert built["display_asset"] == DISPLAY_ASSET == "USDC"
    assert built["asset_decimals"] == ASSET_DECIMALS == 6


def test_settlement_wallet_missing_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(SETTLEMENT_WALLET_ENV, raising=False)
    with pytest.raises(RetailX402PaymentError, match="settlement_wallet_not_configured"):
        build_retail_payment_requirement(resource_type="state_ping", resource_uri="/state")


def test_only_retail_owned_settlement_env_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(SETTLEMENT_WALLET_ENV, raising=False)
    monkeypatch.setenv("X402_SETTLEMENT_WALLET", SETTLEMENT_WALLET)
    monkeypatch.setenv("NOVA_X402_SETTLEMENT_WALLET", SETTLEMENT_WALLET)
    monkeypatch.setenv("CDP_API_KEY_ID", "not-used")
    with pytest.raises(RetailX402PaymentError, match="settlement_wallet_not_configured"):
        build_retail_payment_requirement(resource_type="state_ping", resource_uri="/state")


def test_retail_owned_settlement_env_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(SETTLEMENT_WALLET_ENV, SETTLEMENT_WALLET)
    built = build_retail_payment_requirement(resource_type="state_ping", resource_uri="/state")
    assert built["settlement_wallet"] == SETTLEMENT_WALLET


def test_requirement_has_no_subscription_tier_or_cadence_fields() -> None:
    rendered = json.dumps(requirement(), sort_keys=True).lower()
    for forbidden in ("subscription", "tier", "cadence", "overage", "monthly"):
        assert forbidden not in rendered


def test_price_catalog_is_closed_and_immutable() -> None:
    assert set(RETAIL_RESOURCE_PRICE_CATALOG) == {"state_ping", "context_delta"}
    with pytest.raises(TypeError):
        RETAIL_RESOURCE_PRICE_CATALOG["state_ping"] = {}  # type: ignore[index]


def test_identical_requirements_have_identical_identity() -> None:
    assert requirement() == requirement()
    assert requirement()["payment_requirement_id"] == requirement()["payment_requirement_id"]


@pytest.mark.parametrize(
    "changed",
    [
        requirement("context_delta", "/retail/v1/context/state-ping"),
        requirement("state_ping", "/retail/v1/context/another-state-ping"),
        requirement("state_ping", "/retail/v1/context/state-ping", "0x3333333333333333333333333333333333333333"),
    ],
)
def test_relevant_requirement_changes_change_identity(changed: dict[str, Any]) -> None:
    assert changed["payment_requirement_id"] != requirement()["payment_requirement_id"]


def test_requirement_serialization_is_deterministic() -> None:
    first = json.dumps(requirement(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(requirement(), sort_keys=True, separators=(",", ":"))
    assert first == second


def test_requirement_schema_rejects_amount_resource_mismatch() -> None:
    invalid = requirement()
    invalid["amount_atomic"] = "20000"
    with pytest.raises(ValidationError):
        validate_retail_x402_payment_record(invalid, "payment_requirement")


@pytest.mark.parametrize("field", ["resource_uri", "settlement_wallet"])
def test_requirement_identity_tampering_fails_closed(field: str) -> None:
    invalid = requirement()
    invalid[field] = f"{invalid[field]}-tampered"
    with pytest.raises(RetailX402PaymentError, match="invalid_payment_requirement"):
        validate_retail_payment_requirement(invalid)


def test_challenge_uses_actual_upstream_v2_models() -> None:
    challenge = build_retail_payment_challenge(requirement())
    assert isinstance(challenge.payment_required, PaymentRequired)
    assert isinstance(challenge.payment_required.accepts[0], PaymentRequirements)
    assert challenge.payment_required.x402_version == 2


def test_challenge_exposes_decodable_payment_required_header() -> None:
    challenge = build_retail_payment_challenge(requirement())
    decoded = decode_payment_required_header(challenge.payment_required_header)
    assert decoded == challenge.payment_required
    assert challenge.to_dict()["header_name"] == PAYMENT_REQUIRED_HEADER


def test_challenge_metadata_is_bounded_and_authority_neutral() -> None:
    challenge = build_retail_payment_challenge(requirement())
    assert challenge.metadata["authority_effect"] == "none"
    assert challenge.metadata["access_effect"] == "context_resource_access_only"
    validate_retail_x402_payment_record(challenge.to_dict(), "payment_challenge")


def test_verification_failure_skips_settlement_and_denies_access() -> None:
    facilitator = FakeFacilitator(verify_response=VerifyResponse(is_valid=False, invalid_reason="fixture"))
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert facilitator.calls == ["verify"]
    assert receipt["payment_verification_status"] == "failed"
    assert receipt["settlement_status"] == "not_attempted"
    assert receipt["access_status"] == "denied"
    assert receipt["failure_reason"] == "payment_verification_failed"


def test_verification_exception_fails_closed_without_settlement() -> None:
    facilitator = FakeFacilitator(verify_error=RuntimeError("fixture secret"))
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert facilitator.calls == ["verify"]
    assert receipt["failure_reason"] == "payment_verification_failed"
    assert "fixture secret" not in json.dumps(receipt)


def test_verification_success_alone_does_not_permit_access() -> None:
    facilitator = FakeFacilitator(
        settle_response=SettleResponse(
            success=False,
            error_reason="fixture",
            transaction="",
            network=PAYMENT_NETWORK,
        )
    )
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert receipt["payment_verification_status"] == "verified"
    assert receipt["settlement_status"] == "failed"
    assert receipt["access_status"] == "denied"


def test_facilitator_call_order_is_verify_then_settle() -> None:
    facilitator = FakeFacilitator()
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert facilitator.calls == ["verify", "settle"]
    assert facilitator.payloads[0] is facilitator.payloads[1]
    assert facilitator.requirements[0] == facilitator.requirements[1]
    assert receipt["access_status"] == "permitted"


def test_settlement_exception_denies_access() -> None:
    facilitator = FakeFacilitator(settle_error=RuntimeError("offline"))
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert receipt["failure_reason"] == "payment_settlement_failed"
    assert receipt["settlement_status"] == "failed"
    assert not payment_receipt_allows_resource_access(receipt)


@pytest.mark.parametrize(
    ("settlement", "reason"),
    [
        ({"success": True, "network": PAYMENT_NETWORK, "amount": "2000"}, "settlement_reference_missing"),
        ({"success": True, "transaction": "0xtx", "network": "eip155:1", "amount": "2000"}, "settlement_network_mismatch"),
        ({"success": True, "transaction": "0xtx", "network": PAYMENT_NETWORK, "amount": "1"}, "settlement_amount_mismatch"),
        ({"success": True, "transaction": "0xtx", "network": PAYMENT_NETWORK}, "settlement_amount_mismatch"),
    ],
)
def test_unreconciled_settlement_denies_access(
    settlement: dict[str, Any], reason: str
) -> None:
    receipt = process_retail_x402_payment(
        requirement=requirement(),
        payment_payload=payment_payload(),
        facilitator=FakeFacilitator(settle_response=settlement),
    )
    assert receipt["failure_reason"] == reason
    assert receipt["settlement_status"] == "failed"
    assert receipt["access_status"] == "denied"
    assert not payment_receipt_allows_resource_access(receipt)


def test_fully_reconciled_settlement_permits_access() -> None:
    receipt = successful_receipt()
    assert receipt["payment_verification_status"] == "verified"
    assert receipt["settlement_status"] == "settled"
    assert receipt["access_status"] == "permitted"
    assert receipt["failure_reason"] is None
    assert payment_receipt_allows_resource_access(receipt)


def test_context_delta_uses_its_exact_settlement_amount() -> None:
    required = requirement("context_delta", "/retail/v1/context/context-delta")
    receipt = successful_receipt(payment_requirement=required)
    assert receipt["amount_atomic"] == "20000"
    assert payment_receipt_allows_resource_access(receipt)


def test_payer_is_preserved_when_facilitator_supplies_it() -> None:
    assert successful_receipt(payer=PAYER)["payer"] == PAYER


def test_verify_payer_is_preserved_when_settlement_payer_is_absent() -> None:
    facilitator = FakeFacilitator(
        verify_response=VerifyResponse(is_valid=True, payer=PAYER),
        settle_response={
            "success": True,
            "transaction": "0xtx",
            "network": PAYMENT_NETWORK,
            "amount": "2000",
        },
    )
    receipt = process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert receipt["payer"] == PAYER


def test_receipt_never_exposes_raw_payload_or_credentials() -> None:
    receipt = successful_receipt()
    rendered = json.dumps(receipt).lower()
    for forbidden in ("signature", "authorization", "credential", "api_key", "bearer"):
        assert forbidden not in rendered


def test_v1_payload_is_explicitly_rejected_before_facilitator() -> None:
    facilitator = FakeFacilitator()
    receipt = process_retail_x402_payment(
        requirement=requirement(),
        payment_payload={"x402Version": 1, "payload": {}},
        facilitator=facilitator,
    )
    assert facilitator.calls == []
    assert receipt["failure_reason"] == "unsupported_x402_version"


def test_malformed_v2_payload_is_explicitly_rejected() -> None:
    facilitator = FakeFacilitator()
    receipt = process_retail_x402_payment(
        requirement=requirement(),
        payment_payload={"x402Version": 2, "payload": {}},
        facilitator=facilitator,
    )
    assert facilitator.calls == []
    assert receipt["failure_reason"] == "invalid_payment_payload"


def test_v2_payload_is_accepted_at_contract_boundary() -> None:
    facilitator = FakeFacilitator()
    process_retail_x402_payment(
        requirement=requirement(), payment_payload=payment_payload(), facilitator=facilitator
    )
    assert facilitator.calls == ["verify", "settle"]


def test_payload_requirement_identity_mismatch_fails_before_verify() -> None:
    required = requirement()
    payload = payment_payload(required)
    extensions = copy.deepcopy(payload.extensions)
    extensions["nova"]["paymentRequirementId"] = "payment-requirement-000000000000000000000000"
    mismatched = payload.model_copy(update={"extensions": extensions})
    facilitator = FakeFacilitator()
    receipt = process_retail_x402_payment(
        requirement=required, payment_payload=mismatched, facilitator=facilitator
    )
    assert facilitator.calls == []
    assert receipt["failure_reason"] == "invalid_payment_payload"


@pytest.mark.parametrize("field", ["resourceType", "resourceUri"])
def test_payload_resource_binding_mismatch_fails_before_verify(field: str) -> None:
    required = requirement()
    payload = payment_payload(required)
    extensions = copy.deepcopy(payload.extensions)
    extensions["nova"][field] = "different"
    facilitator = FakeFacilitator()
    receipt = process_retail_x402_payment(
        requirement=required,
        payment_payload=payload.model_copy(update={"extensions": extensions}),
        facilitator=facilitator,
    )
    assert facilitator.calls == []
    assert receipt["failure_reason"] == "invalid_payment_payload"


def test_current_payment_signature_header_is_public_contract() -> None:
    assert RETAIL_PAYMENT_HEADER_NAMES["payment_signature"] == PAYMENT_SIGNATURE_HEADER == "PAYMENT-SIGNATURE"


def test_legacy_x_payment_header_is_not_public_contract() -> None:
    assert "X-PAYMENT" not in RETAIL_PAYMENT_HEADER_NAMES.values()
    assert "x_payment" not in RETAIL_PAYMENT_HEADER_NAMES


def _all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys


def test_receipt_is_authority_neutral_access_only() -> None:
    receipt = successful_receipt()
    assert receipt["authority_effect"] == AUTHORITY_EFFECT == "none"
    assert receipt["access_effect"] == ACCESS_EFFECT == "context_resource_access_only"


def test_payment_outputs_have_no_authorized_or_epistemic_action_fields() -> None:
    outputs = [requirement(), build_retail_payment_challenge(requirement()).to_dict(), successful_receipt()]
    forbidden = {
        "authorized",
        "approved",
        "recommendation",
        "evidence_verified",
        "context_resolved",
        "action_authorized",
        "execution_authorized",
        "transaction_authorized",
        "capital_authority",
    }
    for output in outputs:
        assert not (_all_keys(output) & forbidden)


@pytest.mark.parametrize(
    "resource",
    [
        {
            "resource_type": "state_ping",
            "context_status": "partially_resolved",
            "confidence": {"level": "bounded"},
            "evidence": [{"evidence_id": "evidence-1"}],
            "contradictions": [],
        },
        {
            "resource_type": "context_delta",
            "context_status": "changed",
            "confidence": {"direction": "decreased"},
            "evidence": [{"evidence_id": "evidence-2"}],
            "contradictions": [{"contradiction_id": "contradiction-1"}],
        },
    ],
)
def test_payment_success_does_not_inspect_or_mutate_context_resource(resource: dict[str, Any]) -> None:
    before = copy.deepcopy(resource)
    assert payment_receipt_allows_resource_access(successful_receipt())
    assert resource == before


def test_settled_receipt_identity_is_deterministic() -> None:
    assert successful_receipt()["payment_receipt_id"] == successful_receipt()["payment_receipt_id"]


def test_different_transaction_changes_receipt_identity() -> None:
    first = successful_receipt(transaction="0xone")
    second = successful_receipt(transaction="0xtwo")
    assert first["payment_receipt_id"] != second["payment_receipt_id"]


def test_different_payer_changes_receipt_identity() -> None:
    first = successful_receipt(payer="0xaaaa")
    second = successful_receipt(payer="0xbbbb")
    assert first["payment_receipt_id"] != second["payment_receipt_id"]


def test_failed_receipt_cannot_masquerade_as_settled() -> None:
    failed = process_retail_x402_payment(
        requirement=requirement(),
        payment_payload=payment_payload(),
        facilitator=FakeFacilitator(verify_response=VerifyResponse(is_valid=False)),
    )
    assert failed["payment_receipt_id"].startswith("payment-receipt-failed-")
    assert not payment_receipt_allows_resource_access(failed)


@pytest.mark.parametrize("field", ["payment_requirement_id", "payment_receipt_id"])
def test_access_evaluator_recomputes_bounded_identities(field: str) -> None:
    receipt = successful_receipt()
    prefix = "payment-requirement" if field == "payment_requirement_id" else "payment-receipt"
    receipt[field] = f"{prefix}-000000000000000000000000"
    assert not payment_receipt_allows_resource_access(receipt)


@pytest.mark.parametrize(
    "changes",
    [
        {"payment_verification_status": "not_attempted"},
        {"payment_verification_status": "failed", "settlement_status": "not_attempted", "access_status": "denied", "failure_reason": "payment_verification_failed"},
        {"settlement_status": "not_attempted", "access_status": "denied", "failure_reason": "payment_settlement_failed"},
        {"settlement_status": "failed", "access_status": "denied", "failure_reason": "payment_settlement_failed"},
        {"access_status": "denied", "failure_reason": "payment_settlement_failed"},
        {"authority_effect": "approval"},
        {"transaction_reference": None},
    ],
)
def test_access_evaluator_rejects_every_incomplete_or_invalid_state(changes: dict[str, Any]) -> None:
    receipt = successful_receipt()
    receipt.update(changes)
    assert not payment_receipt_allows_resource_access(receipt)


def test_receipt_schema_rejects_generic_authorized_field() -> None:
    receipt = successful_receipt()
    receipt["authorized"] = True
    with pytest.raises(ValidationError):
        validate_retail_x402_payment_record(receipt, "payment_receipt")


def test_retail_payment_schema_is_draft_2020_12_and_strict() -> None:
    schema = json.loads((REPO_ROOT / "specs" / "retail_x402_payment_v0_1.schema.json").read_text())
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$defs"]["payment_receipt"]["additionalProperties"] is False


def test_retail_isolation_validator_remains_clean() -> None:
    assert validate_retail_package_imports(REPO_ROOT / "retail_context") == []


def test_rp6_module_has_no_legacy_or_live_facilitator_imports() -> None:
    source = (REPO_ROOT / "retail_context" / "x402_payment.py").read_text()
    forbidden = (
        "core.x402_config",
        "core.x402_middleware",
        "core.feed_pricing",
        "core.feed_metering",
        "core.feed_identity",
        "core.billing_config",
        "core.billing_state",
        "core.bazaar_metadata",
        "core.cdp_auth",
        "HTTPFacilitatorClientSync",
    )
    for module_name in forbidden:
        assert module_name not in source


def test_no_fastapi_endpoint_or_network_client_is_added() -> None:
    source = (REPO_ROOT / "retail_context" / "x402_payment.py").read_text()
    assert "FastAPI" not in source
    assert "APIRouter" not in source
    assert "httpx" not in source
    assert "requests" not in source
