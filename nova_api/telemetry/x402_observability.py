from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from importlib import metadata
from typing import Any, Mapping

from nova_api.utils.redaction import redact


PAYMENT_REQUIRED_HEADER_NAME = "payment-required"
X402_EVENT_NAMES = (
    "x402.challenge.received",
    "x402.challenge.parsed",
    "x402.helper.invoked",
    "x402.payload.generated",
    "x402.facilitator.rejected",
    "x402.settlement.retry",
    "x402.interoperability.failure",
    "x402.wallet.environment.visible",
)


class X402FailureCategory(str, Enum):
    INVALID_CHALLENGE = "INVALID_CHALLENGE"
    STALE_CHALLENGE = "STALE_CHALLENGE"
    UNSUPPORTED_NETWORK = "UNSUPPORTED_NETWORK"
    UNSUPPORTED_ASSET = "UNSUPPORTED_ASSET"
    ROUTE_REJECTION = "ROUTE_REJECTION"
    SIGNATURE_REJECTION = "SIGNATURE_REJECTION"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    UNKNOWN_INTEROPERABILITY_FAILURE = "UNKNOWN_INTEROPERABILITY_FAILURE"


@dataclass(frozen=True)
class X402DiagnosticEvent:
    event: str
    fields: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return redact(
            {
                "event": self.event,
                "timestamp": self.timestamp,
                "fields": dict(self.fields),
            }
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


def structured_event(event: str, **fields: Any) -> X402DiagnosticEvent:
    return X402DiagnosticEvent(event=event, fields=fields)


def emit_event(event: str, **fields: Any) -> None:
    print(structured_event(event, **fields).to_json())


def safe_headers(headers: Mapping[str, Any]) -> dict[str, Any]:
    return redact(dict(headers))


def x402_helper_version() -> str:
    try:
        return metadata.version("x402")
    except metadata.PackageNotFoundError:
        return "unknown"


def _header_lookup(headers: Mapping[str, Any], name: str) -> Any:
    lower = name.lower()
    for key, value in headers.items():
        if str(key).lower() == lower:
            return value
    return None


def _decode_payment_required(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        padding = "=" * (-len(value) % 4)
        decoded = base64.b64decode(f"{value}{padding}").decode()
        payload = json.loads(decoded)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {"decode_error": "invalid_payment_required_header"}


def _first_accept(challenge: Mapping[str, Any]) -> Mapping[str, Any]:
    accepts = challenge.get("accepts")
    if isinstance(accepts, list) and accepts and isinstance(accepts[0], Mapping):
        return accepts[0]
    return {}


def _chain_id(network: Any) -> int | None:
    text = str(network or "")
    if text.startswith("eip155:"):
        try:
            return int(text.split(":", 1)[1])
        except ValueError:
            return None
    return None


def challenge_metadata(
    *,
    status_code: int,
    headers: Mapping[str, Any],
    facilitator_endpoint: str,
) -> dict[str, Any]:
    required = _header_lookup(headers, PAYMENT_REQUIRED_HEADER_NAME)
    challenge = _decode_payment_required(str(required) if required else None)
    accepted = _first_accept(challenge)
    network = accepted.get("network") or challenge.get("network")
    return redact(
        {
            "http_status": status_code,
            "challenge_headers_present": bool(required),
            "challenge_timestamp": datetime.now(timezone.utc).isoformat(),
            "facilitator_endpoint": facilitator_endpoint,
            "x_accept_payment": _header_lookup(headers, "x-accept-payment"),
            "retry_after": _header_lookup(headers, "retry-after"),
            "x402_version": challenge.get("x402Version")
            or challenge.get("x402_version"),
            "scheme": accepted.get("scheme"),
            "network": network,
            "chain_id": _chain_id(network),
            "asset": accepted.get("asset"),
            "amount": accepted.get("amount"),
            "settlement_wallet": accepted.get("payTo") or accepted.get("pay_to"),
            "resource": (
                challenge.get("resource", {}).get("url")
                if isinstance(challenge.get("resource"), Mapping)
                else challenge.get("resource")
            ),
            "max_timeout_seconds": accepted.get("maxTimeoutSeconds"),
            "challenge_expiration_metadata": {
                "max_timeout_seconds": accepted.get("maxTimeoutSeconds"),
            },
        }
    )


def helper_metadata(*, payment_payload: Any, helper_name: str = "x402HTTPClientSync") -> dict[str, Any]:
    payload_data = payment_payload.model_dump(by_alias=True, exclude_none=True)
    accepted = payment_payload.accepted
    resource = getattr(payment_payload, "resource", None)
    return redact(
        {
            "helper_path_invoked": True,
            "helper_name": helper_name,
            "helper_version": x402_helper_version(),
            "payment_payload_keys": sorted(payload_data.keys()),
            "network": getattr(accepted, "network", None),
            "chain_id": _chain_id(getattr(accepted, "network", None)),
            "asset": getattr(accepted, "asset", None),
            "amount": str(getattr(accepted, "amount", "")),
            "settlement_wallet": getattr(accepted, "pay_to", None),
            "resource": str(getattr(resource, "url", resource or "")),
            "settlement_route": {
                "scheme": getattr(accepted, "scheme", None),
                "network": getattr(accepted, "network", None),
            },
            "chain_network_normalization": {
                "canonical_network": getattr(accepted, "network", None),
                "chain_id": _chain_id(getattr(accepted, "network", None)),
            },
        }
    )


def wallet_environment_metadata(
    *,
    wallet_address: str,
    network: str,
    funding_state_visibility: str = "not_checked",
) -> dict[str, Any]:
    return {
        "wallet_address": wallet_address,
        "network_connected": network,
        "chain_id": _chain_id(network),
        "funding_state_visibility": funding_state_visibility,
        "payer_key_environment": "loaded",
    }


def classify_facilitator_failure(
    *,
    status_code: int | None = None,
    body: Any = None,
    headers: Mapping[str, Any] | None = None,
) -> X402FailureCategory:
    text = json.dumps(body, sort_keys=True, default=str).lower()
    if "stale" in text or "expired" in text or "timeout" in text:
        return X402FailureCategory.STALE_CHALLENGE
    if "network" in text and ("unsupported" in text or "invalid" in text):
        return X402FailureCategory.UNSUPPORTED_NETWORK
    if "asset" in text and ("unsupported" in text or "invalid" in text):
        return X402FailureCategory.UNSUPPORTED_ASSET
    if "version" in text or "x402version" in text:
        return X402FailureCategory.VERSION_MISMATCH
    if "invalid_payload" in text or "invalid payload" in text or "malformed" in text:
        return X402FailureCategory.INVALID_CHALLENGE
    if "signature" in text or "invalid signer" in text or "invalidmessage" in text:
        return X402FailureCategory.SIGNATURE_REJECTION
    if status_code in {404, 405}:
        return X402FailureCategory.ROUTE_REJECTION
    retry_after = _header_lookup(headers or {}, "retry-after")
    if retry_after:
        return X402FailureCategory.ROUTE_REJECTION
    return X402FailureCategory.UNKNOWN_INTEROPERABILITY_FAILURE


def facilitator_response_metadata(
    *,
    status_code: int,
    body: Any,
    headers: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    category = classify_facilitator_failure(
        status_code=status_code,
        body=body,
        headers=headers or {},
    )
    safe_body = redact(body)
    return {
        "facilitator_response_code": status_code,
        "facilitator_rejection_body": safe_body,
        "retry_after": _header_lookup(headers or {}, "retry-after"),
        "settlement_failure_reason": category.value,
        "malformed_field_identifiers": _malformed_field_identifiers(safe_body),
        "unsupported_route_indicators": _unsupported_route_indicators(safe_body),
    }


def _malformed_field_identifiers(body: Any) -> list[str]:
    text = json.dumps(body, sort_keys=True, default=str).lower()
    candidates = ("payload", "signature", "network", "asset", "amount", "resource")
    return [candidate for candidate in candidates if candidate in text]


def _unsupported_route_indicators(body: Any) -> list[str]:
    text = json.dumps(body, sort_keys=True, default=str).lower()
    indicators = []
    if "unsupported" in text:
        indicators.append("unsupported")
    if "route" in text:
        indicators.append("route")
    if "not found" in text:
        indicators.append("not_found")
    return indicators
