from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from cdp.auth.utils.jwt import JwtOptions, generate_jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from x402.http import FacilitatorConfig, HTTPFacilitatorClientSync
from x402.http.constants import (
    PAYMENT_REQUIRED_HEADER,
    PAYMENT_RESPONSE_HEADER,
    PAYMENT_SIGNATURE_HEADER,
    X_PAYMENT_HEADER,
)
from x402.http.facilitator_client_base import AuthHeaders, AuthProvider
from x402.http.utils import (
    decode_payment_signature_header,
    encode_payment_required_header,
    encode_payment_response_header,
)
from x402.schemas import PaymentPayload, PaymentPayloadV1, PaymentRequired, PaymentRequirements, ResourceInfo

from core.feed_identity import build_feed_consumer_identity
from core.feed_pricing import normalize_feed_tier
from core.x402_config import (
    X402_ASSET_ADDRESS,
    X402_FACILITATOR_NAME,
    X402_FACILITATOR_URL,
    X402_LEGACY_PAYMENT_HEADER,
    X402_MAX_TIMEOUT_SECONDS,
    X402_PAYMENT_ASSET,
    X402_PAYMENT_HEADER,
    X402_PAYMENT_NETWORK,
    X402_PROTOCOL_NETWORK,
    X402_RESOURCE_DESCRIPTION,
    X402_SETTLEMENT_WALLET,
    X402_USDC_AMOUNT_ATOMIC,
    X402_VERSION,
    is_x402_protected_feed,
    x402_payment_requirement,
)


CDP_API_KEY_ID_ENV = "CDP_API_KEY_ID"
CDP_API_KEY_SECRET_ENV = "CDP_API_KEY_SECRET"


class CDPFacilitatorAuthProvider(AuthProvider):
    def __init__(self, *, api_key_id: str, api_key_secret: str, facilitator_url: str) -> None:
        parsed = urlparse(facilitator_url)
        self._api_key_id = api_key_id
        self._api_key_secret = api_key_secret
        self._request_host = parsed.netloc
        self._base_path = parsed.path.rstrip("/")

    def _headers_for(self, *, method: str, suffix: str) -> Dict[str, str]:
        request_path = f"{self._base_path}/{suffix.lstrip('/')}"
        token = generate_jwt(
            JwtOptions(
                api_key_id=self._api_key_id,
                api_key_secret=self._api_key_secret,
                request_method=method,
                request_host=self._request_host,
                request_path=request_path,
                expires_in=120,
            )
        )
        return {"Authorization": f"Bearer {token}"}

    def get_auth_headers(self) -> AuthHeaders:
        return AuthHeaders(
            verify=self._headers_for(method="POST", suffix="verify"),
            settle=self._headers_for(method="POST", suffix="settle"),
            supported=self._headers_for(method="GET", suffix="supported"),
        )


@dataclass(frozen=True)
class X402SettlementResult:
    authorized: bool
    reason: Optional[str]
    feed_tier: str
    payer: str
    payment: Dict[str, Any]
    response_headers: Dict[str, str]
    verification: Dict[str, Any]


class X402PaymentGateway:
    def __init__(
        self,
        *,
        facilitator_client: Optional[HTTPFacilitatorClientSync] = None,
        facilitator_url: str = X402_FACILITATOR_URL,
    ) -> None:
        self._facilitator_url = facilitator_url.rstrip("/")
        self._facilitator_client = facilitator_client

    def payment_requirements(self, *, endpoint: str) -> PaymentRequirements:
        return PaymentRequirements(
            scheme="exact",
            network=X402_PROTOCOL_NETWORK,
            asset=X402_ASSET_ADDRESS,
            amount=str(X402_USDC_AMOUNT_ATOMIC),
            payTo=X402_SETTLEMENT_WALLET,
            maxTimeoutSeconds=X402_MAX_TIMEOUT_SECONDS,
            extra={
                "name": "USD Coin" if X402_PAYMENT_ASSET == "USDC" else X402_PAYMENT_ASSET,
                "version": "2",
                "displayAsset": X402_PAYMENT_ASSET,
                "displayNetwork": X402_PAYMENT_NETWORK,
                "resource": endpoint,
            },
        )

    def payment_required(self, *, endpoint: str, detail: str) -> PaymentRequired:
        return PaymentRequired(
            x402Version=X402_VERSION,
            error=detail,
            resource=ResourceInfo(
                url=endpoint,
                description=X402_RESOURCE_DESCRIPTION,
                mimeType="application/json",
            ),
            accepts=[self.payment_requirements(endpoint=endpoint)],
            extensions={
                "nova": {
                    "authority_layer": "non_admission_telemetry",
                    "sovereign_admission_required": True,
                    "non_substitution_rule": "telemetry_informs_posture_only",
                }
            },
        )

    def _auth_provider(self) -> CDPFacilitatorAuthProvider:
        api_key_id = os.getenv(CDP_API_KEY_ID_ENV, "").strip()
        api_key_secret = os.getenv(CDP_API_KEY_SECRET_ENV, "").strip()
        if not api_key_id or not api_key_secret:
            raise RuntimeError("cdp_facilitator_credentials_missing")
        return CDPFacilitatorAuthProvider(
            api_key_id=api_key_id,
            api_key_secret=api_key_secret,
            facilitator_url=self._facilitator_url,
        )

    def _client(self) -> HTTPFacilitatorClientSync:
        if self._facilitator_client is not None:
            return self._facilitator_client
        self._facilitator_client = HTTPFacilitatorClientSync(
            FacilitatorConfig(
                url=self._facilitator_url,
                auth_provider=self._auth_provider(),
            )
        )
        return self._facilitator_client

    @staticmethod
    def _feed_tier_from_payload(payload: PaymentPayload | PaymentPayloadV1) -> str:
        extensions = getattr(payload, "extensions", None)
        if isinstance(extensions, dict):
            return normalize_feed_tier(extensions.get("cadence_tier") or extensions.get("feed_tier"))
        return normalize_feed_tier(None)

    def verify_and_settle(
        self,
        *,
        payload: PaymentPayload | PaymentPayloadV1,
        endpoint: str,
    ) -> X402SettlementResult:
        if not is_x402_protected_feed(endpoint):
            return X402SettlementResult(
                authorized=False,
                reason="endpoint_not_x402_protected",
                feed_tier="developer",
                payer="x402_payer",
                payment={},
                response_headers={},
                verification={},
            )

        requirements = self.payment_requirements(endpoint=endpoint)
        client = self._client()
        verify_response = client.verify(payload, requirements)
        if not verify_response.is_valid:
            reason = verify_response.invalid_reason or "payment_verification_failed"
            return X402SettlementResult(
                authorized=False,
                reason=reason,
                feed_tier=self._feed_tier_from_payload(payload),
                payer=verify_response.payer or "x402_payer",
                payment={},
                response_headers={},
                verification={
                    "facilitator_verify": verify_response.model_dump(by_alias=True, exclude_none=True),
                },
            )

        settle_response = client.settle(payload, requirements)
        if not settle_response.success:
            return X402SettlementResult(
                authorized=False,
                reason=settle_response.error_reason or "payment_settlement_failed",
                feed_tier=self._feed_tier_from_payload(payload),
                payer=verify_response.payer or settle_response.payer or "x402_payer",
                payment={},
                response_headers={
                    PAYMENT_RESPONSE_HEADER: encode_payment_response_header(settle_response),
                },
                verification={
                    "facilitator_verify": verify_response.model_dump(by_alias=True, exclude_none=True),
                    "facilitator_settle": settle_response.model_dump(by_alias=True, exclude_none=True),
                },
            )

        feed_tier = self._feed_tier_from_payload(payload)
        payer = settle_response.payer or verify_response.payer or "x402_payer"
        return X402SettlementResult(
            authorized=True,
            reason=None,
            feed_tier=feed_tier,
            payer=payer,
            payment={
                "x402_version": payload.x402_version,
                "payment_network": X402_PAYMENT_NETWORK,
                "protocol_network": requirements.network,
                "payment_asset": X402_PAYMENT_ASSET,
                "asset_address": requirements.asset,
                "settlement_wallet": requirements.pay_to,
                "facilitator": X402_FACILITATOR_NAME,
                "facilitator_status": "settled",
                "payment_reference": settle_response.transaction,
                "settlement_network": settle_response.network,
                "settlement_amount": settle_response.amount,
            },
            response_headers={
                PAYMENT_RESPONSE_HEADER: encode_payment_response_header(settle_response),
            },
            verification={
                "facilitator_verify": verify_response.model_dump(by_alias=True, exclude_none=True),
                "facilitator_settle": settle_response.model_dump(by_alias=True, exclude_none=True),
            },
        )


_GATEWAY: Optional[X402PaymentGateway] = None


def get_x402_gateway() -> X402PaymentGateway:
    global _GATEWAY
    if _GATEWAY is None:
        _GATEWAY = X402PaymentGateway()
    return _GATEWAY


def _payment_header_value(request: Request) -> Optional[str]:
    return (
        request.headers.get(PAYMENT_SIGNATURE_HEADER)
        or request.headers.get(PAYMENT_SIGNATURE_HEADER.lower())
        or request.headers.get(X_PAYMENT_HEADER)
        or request.headers.get(X402_PAYMENT_HEADER)
        or request.headers.get(X402_LEGACY_PAYMENT_HEADER)
    )


def _parse_payment_header(value: Optional[str]) -> Optional[PaymentPayload | PaymentPayloadV1]:
    if not value:
        return None
    try:
        return decode_payment_signature_header(value)
    except Exception:
        return None


def build_x402_payment_required_response(*, endpoint: str, detail: str = "x402 payment required") -> JSONResponse:
    gateway = get_x402_gateway()
    payment_required = gateway.payment_required(endpoint=endpoint, detail=detail)
    payload = {
        "payment_required": True,
        "detail": detail,
        "network": X402_PAYMENT_NETWORK,
        "asset": X402_PAYMENT_ASSET,
        "settlement_wallet": X402_SETTLEMENT_WALLET,
        "authority_layer": "non_admission_telemetry",
        "sovereign_admission_required": True,
        "non_substitution_rule": "telemetry_informs_posture_only",
        "x402": x402_payment_requirement(endpoint=endpoint),
    }
    return JSONResponse(
        payload,
        status_code=402,
        headers={
            PAYMENT_REQUIRED_HEADER: encode_payment_required_header(payment_required),
            "x-accept-payment": PAYMENT_SIGNATURE_HEADER,
        },
    )


def verify_x402_payment_payload(
    *,
    payload: PaymentPayload | PaymentPayloadV1,
    endpoint: str,
) -> Dict[str, Any]:
    try:
        result = get_x402_gateway().verify_and_settle(payload=payload, endpoint=endpoint)
    except Exception as exc:
        return {
            "authorized": False,
            "reason": str(exc) or "payment_verification_failed",
            "feed_tier": "developer",
            "payer": "x402_payer",
            "payment": {},
            "response_headers": {},
            "verification": {},
        }

    return {
        "authorized": result.authorized,
        "reason": result.reason,
        "feed_tier": result.feed_tier,
        "payer": result.payer,
        "payment": result.payment,
        "response_headers": result.response_headers,
        "verification": result.verification,
    }


def authorize_x402_request(request: Request, endpoint: str) -> Dict[str, Any]:
    payment_payload = _parse_payment_header(_payment_header_value(request))
    if payment_payload is None:
        return {
            "authorized": False,
            "response": build_x402_payment_required_response(endpoint=endpoint),
        }

    verification = verify_x402_payment_payload(payload=payment_payload, endpoint=endpoint)
    if not verification["authorized"]:
        response = build_x402_payment_required_response(
            endpoint=endpoint,
            detail=verification["reason"] or "x402 payment verification failed",
        )
        for name, value in verification.get("response_headers", {}).items():
            response.headers[name] = value
        return {
            "authorized": False,
            "response": response,
            "verification": verification,
        }

    identity = build_feed_consumer_identity(
        f"x402:{verification['payer']}",
        {
            "feed_tier": verification["feed_tier"],
        },
    )
    return {
        "authorized": True,
        "feed_identity": identity,
        "x402_payment": verification["payment"],
        "response_headers": verification.get("response_headers", {}),
        "verification": verification,
    }
