from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx
from eth_account import Account
from x402 import prefer_network, prefer_scheme, x402ClientSync
from x402.http.constants import PAYMENT_REQUIRED_HEADER, PAYMENT_RESPONSE_HEADER, PAYMENT_SIGNATURE_HEADER
from x402.http.utils import (
    decode_payment_required_header,
    decode_payment_response_header,
    encode_payment_signature_header,
)
from x402.mechanisms.evm.exact import ExactEvmScheme


TARGET_PATH = "/v1/feeds/constraint_pressure"
EXPECTED_NETWORK = "eip155:8453"
EXPECTED_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
EXPECTED_SETTLEMENT_WALLET = "0xb29b02130138a6fF8e0f6D7812bDa8D436001BE4"
PLACEHOLDER_PREFIX = "PASTE_"


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith(PLACEHOLDER_PREFIX):
        raise RuntimeError(f"{name} missing")
    return value


def _bool_text(value: bool) -> str:
    return "yes" if value else "no"


def _get_header(headers: httpx.Headers, name: str) -> str | None:
    return headers.get(name) or headers.get(name.lower())


def _validate_requirements(payment_required: Any) -> None:
    if not payment_required.accepts:
        raise RuntimeError("payment requirements missing")

    requirement = payment_required.accepts[0]
    if requirement.network != EXPECTED_NETWORK:
        raise RuntimeError("unexpected payment network")
    if str(requirement.asset).lower() != EXPECTED_ASSET.lower():
        raise RuntimeError("unexpected payment asset")
    if str(requirement.pay_to).lower() != EXPECTED_SETTLEMENT_WALLET.lower():
        raise RuntimeError("unexpected settlement wallet")


def main() -> int:
    settlement_succeeded = False
    paid_access_succeeded = False
    http_status = 0

    try:
        base_url = _env("NOVA_API_URL").rstrip("/")
        private_key = _env("EVM_PRIVATE_KEY")
    except Exception:
        print("settlement succeeded: no")
        print("HTTP status: 0")
        print("paid access succeeded: no")
        return 2

    target_url = f"{base_url}{TARGET_PATH}"

    try:
        account = Account.from_key(private_key)
        x402_client = x402ClientSync()
        x402_client.register(EXPECTED_NETWORK, ExactEvmScheme(signer=account))
        x402_client.register_policy(prefer_network(EXPECTED_NETWORK))
        x402_client.register_policy(prefer_scheme("exact"))

        with httpx.Client(timeout=30, follow_redirects=True) as client:
            discovery_response = client.get(target_url)
            if discovery_response.status_code != 402:
                http_status = discovery_response.status_code
                raise RuntimeError("expected 402 discovery response")

            required_header = _get_header(discovery_response.headers, PAYMENT_REQUIRED_HEADER)
            if not required_header:
                http_status = discovery_response.status_code
                raise RuntimeError("payment required header missing")

            payment_required = decode_payment_required_header(required_header)
            _validate_requirements(payment_required)

            payment_payload = x402_client.create_payment_payload(payment_required)
            payment_header = encode_payment_signature_header(payment_payload)

            paid_response = client.get(
                target_url,
                headers={
                    PAYMENT_SIGNATURE_HEADER: payment_header,
                    "Access-Control-Expose-Headers": PAYMENT_RESPONSE_HEADER,
                },
            )
            http_status = paid_response.status_code
            paid_access_succeeded = paid_response.status_code == 200

            settlement_header = _get_header(paid_response.headers, PAYMENT_RESPONSE_HEADER)
            if settlement_header:
                settlement = decode_payment_response_header(settlement_header)
                settlement_succeeded = bool(settlement.success)

            if paid_access_succeeded:
                payload = paid_response.json()
                paid_access_succeeded = all(
                    [
                        payload.get("feed_name") == "Nova Constraint Pressure",
                        payload.get("feed_type") == "environmental_conditioning",
                        payload.get("authority_layer") == "non_admission_telemetry",
                        payload.get("sovereign_admission_required") is True,
                        payload.get("x402_ready") is True,
                        payload.get("agentic_market_ready") is True,
                    ]
                )

            if not settlement_succeeded and paid_response.text:
                try:
                    body = paid_response.json()
                    compact = {
                        "detail": body.get("detail"),
                        "error": body.get("error"),
                    }
                    print(f"settlement error: {json.dumps(compact, sort_keys=True)}")
                except Exception:
                    pass

    except Exception as exc:
        print(f"settlement error: {type(exc).__name__}")

    print(f"settlement succeeded: {_bool_text(settlement_succeeded)}")
    print(f"HTTP status: {http_status}")
    print(f"paid access succeeded: {_bool_text(paid_access_succeeded)}")

    return 0 if settlement_succeeded and paid_access_succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
