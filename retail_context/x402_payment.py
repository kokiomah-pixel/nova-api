from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from jsonschema import Draft202012Validator
from pydantic import ValidationError as PydanticValidationError
from x402.http.constants import (
    PAYMENT_REQUIRED_HEADER,
    PAYMENT_RESPONSE_HEADER,
    PAYMENT_SIGNATURE_HEADER,
)
from x402.http.utils import encode_payment_required_header
from x402.schemas import (
    PaymentPayload,
    PaymentRequired,
    PaymentRequirements,
    ResourceInfo,
    SettleResponse,
    VerifyResponse,
)


X402_VERSION = 2
PAYMENT_SCHEME = "exact"
PAYMENT_NETWORK = "eip155:8453"
DISPLAY_NETWORK = "base"
PAYMENT_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DISPLAY_ASSET = "USDC"
ASSET_DECIMALS = 6
MAX_TIMEOUT_SECONDS = 60
PRICING_MODEL = "pay_per_context_resource"
AUTHORITY_EFFECT = "none"
ACCESS_EFFECT = "context_resource_access_only"
SETTLEMENT_WALLET_ENV = "NOVA_RETAIL_X402_SETTLEMENT_WALLET"
SCHEMA_VERSION = "0.1.0"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "retail_x402_payment_v0_1.schema.json"
)

RETAIL_RESOURCE_PRICE_CATALOG = MappingProxyType(
    {
        "state_ping": MappingProxyType(
            {"display_price_usdc": "0.002", "amount_atomic": "2000"}
        ),
        "context_delta": MappingProxyType(
            {"display_price_usdc": "0.02", "amount_atomic": "20000"}
        ),
    }
)


class RetailX402PaymentError(ValueError):
    """A bounded, fail-closed retail payment contract error."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class RetailX402Facilitator(Protocol):
    """Injected verification/settlement boundary; RP6 supplies no live client."""

    def verify(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> VerifyResponse | Mapping[str, Any]: ...

    def settle(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> SettleResponse | Mapping[str, Any]: ...


@dataclass(frozen=True)
class RetailPaymentChallenge:
    """Pure in-process challenge representation, not an HTTP response."""

    payment_required: PaymentRequired
    payment_required_header: str
    metadata: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "record_type": "payment_challenge",
            "header_name": PAYMENT_REQUIRED_HEADER,
            "payment_required_header": self.payment_required_header,
            "payment_required": self.payment_required.model_dump(
                by_alias=True, exclude_none=True
            ),
            "metadata": dict(self.metadata),
        }


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _stable_id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256(_canonical_json(parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def load_retail_x402_payment_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def retail_x402_payment_validator(record_type: str) -> Draft202012Validator:
    schema = load_retail_x402_payment_schema()
    try:
        definition = schema["$defs"][record_type]
    except KeyError as exc:
        raise ValueError(f"unknown retail x402 record type: {record_type}") from exc
    return Draft202012Validator({"$ref": f"#/$defs/{record_type}", "$defs": schema["$defs"]})


def validate_retail_x402_payment_record(
    record: Mapping[str, Any], record_type: str
) -> None:
    retail_x402_payment_validator(record_type).validate(record)


def _requirement_identity_fields(requirement: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "x402_version": requirement["x402_version"],
        "scheme": requirement["scheme"],
        "network": requirement["network"],
        "asset": requirement["asset"],
        "amount_atomic": requirement["amount_atomic"],
        "settlement_wallet": requirement["settlement_wallet"],
        "max_timeout_seconds": requirement["max_timeout_seconds"],
        "resource_type": requirement["resource_type"],
        "resource_uri": requirement["resource_uri"],
        "pricing_model": requirement["pricing_model"],
        "authority_effect": requirement["authority_effect"],
        "access_effect": requirement["access_effect"],
    }


def validate_retail_payment_requirement(requirement: Mapping[str, Any]) -> None:
    """Validate both the schema and deterministic identity of a requirement."""

    validate_retail_x402_payment_record(requirement, "payment_requirement")
    expected = _stable_id(
        "payment-requirement", _requirement_identity_fields(requirement)
    )
    if requirement["payment_requirement_id"] != expected:
        raise RetailX402PaymentError("invalid_payment_requirement")


def _settlement_wallet(
    settlement_wallet: str | None,
    environ: Mapping[str, str] | None,
) -> str:
    if settlement_wallet is None:
        source = os.environ if environ is None else environ
        settlement_wallet = source.get(SETTLEMENT_WALLET_ENV)
    if not isinstance(settlement_wallet, str) or not settlement_wallet.strip():
        raise RetailX402PaymentError("settlement_wallet_not_configured")
    return settlement_wallet.strip()


def build_retail_payment_requirement(
    *,
    resource_type: str,
    resource_uri: str,
    settlement_wallet: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build one price-closed, deterministic retail resource requirement."""

    price = RETAIL_RESOURCE_PRICE_CATALOG.get(resource_type)
    if price is None:
        raise RetailX402PaymentError("resource_not_payable")
    if not isinstance(resource_uri, str) or not resource_uri.strip():
        raise RetailX402PaymentError("resource_not_payable")
    pay_to = _settlement_wallet(settlement_wallet, environ)
    resource_uri = resource_uri.strip()

    identity_fields = {
        "x402_version": X402_VERSION,
        "scheme": PAYMENT_SCHEME,
        "network": PAYMENT_NETWORK,
        "asset": PAYMENT_ASSET,
        "amount_atomic": price["amount_atomic"],
        "settlement_wallet": pay_to,
        "max_timeout_seconds": MAX_TIMEOUT_SECONDS,
        "resource_type": resource_type,
        "resource_uri": resource_uri,
        "pricing_model": PRICING_MODEL,
        "authority_effect": AUTHORITY_EFFECT,
        "access_effect": ACCESS_EFFECT,
    }
    requirement_id = _stable_id("payment-requirement", identity_fields)
    requirement = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "payment_requirement",
        "payment_requirement_id": requirement_id,
        **identity_fields,
        "display_network": DISPLAY_NETWORK,
        "display_asset": DISPLAY_ASSET,
        "asset_decimals": ASSET_DECIMALS,
        "display_price_usdc": price["display_price_usdc"],
    }
    validate_retail_payment_requirement(requirement)
    return requirement


def _upstream_requirements(requirement: Mapping[str, Any]) -> PaymentRequirements:
    validate_retail_payment_requirement(requirement)
    return PaymentRequirements(
        scheme=requirement["scheme"],
        network=requirement["network"],
        asset=requirement["asset"],
        amount=requirement["amount_atomic"],
        pay_to=requirement["settlement_wallet"],
        max_timeout_seconds=requirement["max_timeout_seconds"],
        extra={
            "nova": {
                "paymentRequirementId": requirement["payment_requirement_id"],
                "resourceType": requirement["resource_type"],
                "resourceUri": requirement["resource_uri"],
                "pricingModel": PRICING_MODEL,
                "authorityEffect": AUTHORITY_EFFECT,
                "accessEffect": ACCESS_EFFECT,
            }
        },
    )


def build_retail_payment_challenge(
    requirement: Mapping[str, Any],
) -> RetailPaymentChallenge:
    """Construct an upstream x402 v2 challenge without creating an endpoint."""

    requirements = _upstream_requirements(requirement)
    nova_metadata = {
        "payment_requirement_id": requirement["payment_requirement_id"],
        "resource_type": requirement["resource_type"],
        "resource_uri": requirement["resource_uri"],
        "pricing_model": PRICING_MODEL,
        "authority_effect": AUTHORITY_EFFECT,
        "access_effect": ACCESS_EFFECT,
    }
    payment_required = PaymentRequired(
        x402_version=X402_VERSION,
        resource=ResourceInfo(
            url=requirement["resource_uri"],
            description=f"Nova retail {requirement['resource_type']} context resource",
            mime_type="application/json",
        ),
        accepts=[requirements],
        extensions={"nova": requirements.extra["nova"]},
    )
    challenge = RetailPaymentChallenge(
        payment_required=payment_required,
        payment_required_header=encode_payment_required_header(payment_required),
        metadata=MappingProxyType(nova_metadata),
    )
    validate_retail_x402_payment_record(challenge.to_dict(), "payment_challenge")
    return challenge


def _failure_receipt(
    requirement: Mapping[str, Any],
    reason: str,
    *,
    verification_status: str = "not_attempted",
    settlement_status: str = "not_attempted",
    payer: str | None = None,
    transaction_reference: str | None = None,
) -> dict[str, Any]:
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "payment_receipt",
        "payment_receipt_id": _stable_id(
            "payment-receipt-failed",
            requirement["payment_requirement_id"],
            verification_status,
            settlement_status,
            reason,
            transaction_reference,
        ),
        "payment_requirement_id": requirement["payment_requirement_id"],
        "resource_type": requirement["resource_type"],
        "resource_uri": requirement["resource_uri"],
        "pricing_model": PRICING_MODEL,
        "payment_verification_status": verification_status,
        "settlement_status": settlement_status,
        "access_status": "denied",
        "payer": payer,
        "network": requirement["network"],
        "asset": requirement["asset"],
        "amount_atomic": requirement["amount_atomic"],
        "settlement_wallet": requirement["settlement_wallet"],
        "transaction_reference": transaction_reference,
        "failure_reason": reason,
        "authority_effect": AUTHORITY_EFFECT,
        "access_effect": ACCESS_EFFECT,
    }
    validate_retail_x402_payment_record(receipt, "payment_receipt")
    return receipt


def _parse_payload(payload: PaymentPayload | Mapping[str, Any]) -> PaymentPayload:
    if isinstance(payload, Mapping):
        version = payload.get("x402Version", payload.get("x402_version", X402_VERSION))
        if version != X402_VERSION:
            raise RetailX402PaymentError("unsupported_x402_version")
    elif payload.x402_version != X402_VERSION:
        raise RetailX402PaymentError("unsupported_x402_version")
    try:
        return (
            payload
            if isinstance(payload, PaymentPayload)
            else PaymentPayload.model_validate(payload)
        )
    except (PydanticValidationError, TypeError, ValueError) as exc:
        raise RetailX402PaymentError("invalid_payment_payload") from exc


def _payload_matches_requirement(
    payload: PaymentPayload,
    requirement: Mapping[str, Any],
    requirements: PaymentRequirements,
) -> bool:
    if payload.x402_version != X402_VERSION or payload.accepted != requirements:
        return False
    if payload.resource is None or payload.resource.url != requirement["resource_uri"]:
        return False
    nova = (payload.extensions or {}).get("nova")
    return isinstance(nova, Mapping) and nova == requirements.extra["nova"]


def _mapping(response: object) -> Mapping[str, Any]:
    if isinstance(response, Mapping):
        return response
    if isinstance(response, (VerifyResponse, SettleResponse)):
        return response.model_dump()
    return {}


def process_retail_x402_payment(
    *,
    requirement: Mapping[str, Any],
    payment_payload: PaymentPayload | Mapping[str, Any],
    facilitator: RetailX402Facilitator,
) -> dict[str, Any]:
    """Verify, then settle, then reconcile before permitting resource access."""

    validate_retail_payment_requirement(requirement)
    requirements = _upstream_requirements(requirement)
    try:
        payload = _parse_payload(payment_payload)
    except RetailX402PaymentError as exc:
        return _failure_receipt(requirement, exc.reason)
    if not _payload_matches_requirement(payload, requirement, requirements):
        return _failure_receipt(requirement, "invalid_payment_payload")

    try:
        verify_response = VerifyResponse.model_validate(
            _mapping(facilitator.verify(payload, requirements))
        )
    except Exception:
        return _failure_receipt(
            requirement,
            "payment_verification_failed",
            verification_status="failed",
        )
    if not verify_response.is_valid:
        return _failure_receipt(
            requirement,
            "payment_verification_failed",
            verification_status="failed",
            payer=verify_response.payer,
        )

    try:
        raw_settlement = _mapping(facilitator.settle(payload, requirements))
    except Exception:
        return _failure_receipt(
            requirement,
            "payment_settlement_failed",
            verification_status="verified",
            settlement_status="failed",
            payer=verify_response.payer,
        )

    if raw_settlement.get("success") is not True:
        return _failure_receipt(
            requirement,
            "payment_settlement_failed",
            verification_status="verified",
            settlement_status="failed",
            payer=raw_settlement.get("payer") or verify_response.payer,
            transaction_reference=raw_settlement.get("transaction"),
        )

    payer = raw_settlement.get("payer") or verify_response.payer
    transaction_reference = raw_settlement.get("transaction")
    if not isinstance(transaction_reference, str) or not transaction_reference.strip():
        return _failure_receipt(
            requirement,
            "settlement_reference_missing",
            verification_status="verified",
            settlement_status="failed",
            payer=payer,
        )
    transaction_reference = transaction_reference.strip()
    if raw_settlement.get("network") != requirement["network"]:
        return _failure_receipt(
            requirement,
            "settlement_network_mismatch",
            verification_status="verified",
            settlement_status="failed",
            payer=payer,
            transaction_reference=transaction_reference,
        )
    if raw_settlement.get("amount") != requirement["amount_atomic"]:
        return _failure_receipt(
            requirement,
            "settlement_amount_mismatch",
            verification_status="verified",
            settlement_status="failed",
            payer=payer,
            transaction_reference=transaction_reference,
        )

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "payment_receipt",
        "payment_receipt_id": _stable_id(
            "payment-receipt",
            requirement["payment_requirement_id"],
            transaction_reference,
            payer,
            requirement["network"],
            requirement["amount_atomic"],
        ),
        "payment_requirement_id": requirement["payment_requirement_id"],
        "resource_type": requirement["resource_type"],
        "resource_uri": requirement["resource_uri"],
        "pricing_model": PRICING_MODEL,
        "payment_verification_status": "verified",
        "settlement_status": "settled",
        "access_status": "permitted",
        "payer": payer,
        "network": requirement["network"],
        "asset": requirement["asset"],
        "amount_atomic": requirement["amount_atomic"],
        "settlement_wallet": requirement["settlement_wallet"],
        "transaction_reference": transaction_reference,
        "failure_reason": None,
        "authority_effect": AUTHORITY_EFFECT,
        "access_effect": ACCESS_EFFECT,
    }
    validate_retail_x402_payment_record(receipt, "payment_receipt")
    return receipt


run_retail_x402_payment_loop = process_retail_x402_payment


def payment_receipt_allows_resource_access(receipt: Mapping[str, Any]) -> bool:
    """Evaluate payment state only; never inspect or mutate resource content."""

    try:
        validate_retail_x402_payment_record(receipt, "payment_receipt")
    except Exception:
        return False
    if not (
        receipt["payment_verification_status"] == "verified"
        and receipt["settlement_status"] == "settled"
        and receipt["access_status"] == "permitted"
        and receipt["authority_effect"] == AUTHORITY_EFFECT
        and receipt["access_effect"] == ACCESS_EFFECT
        and receipt["failure_reason"] is None
        and bool(receipt["transaction_reference"])
    ):
        return False

    price = RETAIL_RESOURCE_PRICE_CATALOG.get(receipt["resource_type"])
    if price is None or price["amount_atomic"] != receipt["amount_atomic"]:
        return False
    requirement_fields = {
        "x402_version": X402_VERSION,
        "scheme": PAYMENT_SCHEME,
        "network": receipt["network"],
        "asset": receipt["asset"],
        "amount_atomic": receipt["amount_atomic"],
        "settlement_wallet": receipt["settlement_wallet"],
        "max_timeout_seconds": MAX_TIMEOUT_SECONDS,
        "resource_type": receipt["resource_type"],
        "resource_uri": receipt["resource_uri"],
        "pricing_model": receipt["pricing_model"],
        "authority_effect": receipt["authority_effect"],
        "access_effect": receipt["access_effect"],
    }
    expected_requirement_id = _stable_id(
        "payment-requirement", requirement_fields
    )
    if receipt["payment_requirement_id"] != expected_requirement_id:
        return False
    expected_receipt_id = _stable_id(
        "payment-receipt",
        expected_requirement_id,
        receipt["transaction_reference"],
        receipt["payer"],
        receipt["network"],
        receipt["amount_atomic"],
    )
    return receipt["payment_receipt_id"] == expected_receipt_id


RETAIL_PAYMENT_HEADER_NAMES = MappingProxyType(
    {
        "payment_signature": PAYMENT_SIGNATURE_HEADER,
        "payment_required": PAYMENT_REQUIRED_HEADER,
        "payment_response": PAYMENT_RESPONSE_HEADER,
    }
)
