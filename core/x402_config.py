from __future__ import annotations

import os
from typing import Any, Dict

from core.billing_config import USDC_PAYMENT_WALLET
from core.feed_pricing import pricing_for_tier


X402_VERSION = 2
X402_PAYMENT_HEADER = "PAYMENT-SIGNATURE"
X402_LEGACY_PAYMENT_HEADER = "x-payment"
X402_PROTECTED_FEED_ENDPOINTS = {"/v1/feeds/constraint_pressure"}
X402_DISCOVERABLE_ENDPOINTS = {"/v1/feeds/constraint_pressure"}
X402_PAYMENT_NETWORK = os.getenv("X402_NETWORK") or os.getenv("NOVA_X402_PAYMENT_NETWORK", "base")
X402_PROTOCOL_NETWORK = os.getenv("X402_PROTOCOL_NETWORK") or os.getenv(
    "NOVA_X402_PROTOCOL_NETWORK",
    "eip155:8453" if X402_PAYMENT_NETWORK == "base" else X402_PAYMENT_NETWORK,
)
X402_PAYMENT_ASSET = os.getenv("X402_ASSET") or os.getenv("NOVA_X402_PAYMENT_ASSET", "USDC")
X402_ASSET_ADDRESS = os.getenv("X402_ASSET_ADDRESS") or os.getenv(
    "NOVA_X402_ASSET_ADDRESS",
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
)
X402_USDC_AMOUNT_ATOMIC = os.getenv("X402_USDC_AMOUNT_ATOMIC") or os.getenv(
    "NOVA_X402_USDC_AMOUNT_ATOMIC",
    "10000",
)
X402_MAX_TIMEOUT_SECONDS = int(
    os.getenv("X402_MAX_TIMEOUT_SECONDS") or os.getenv("NOVA_X402_MAX_TIMEOUT_SECONDS", "60")
)
X402_SETTLEMENT_WALLET = (
    os.getenv("X402_SETTLEMENT_WALLET")
    or os.getenv("NOVA_X402_SETTLEMENT_WALLET")
    or USDC_PAYMENT_WALLET
)
X402_FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL") or os.getenv(
    "NOVA_X402_FACILITATOR_URL",
    "https://api.cdp.coinbase.com/platform/v2/x402",
)
X402_FACILITATOR_NAME = os.getenv("X402_FACILITATOR_NAME") or os.getenv(
    "NOVA_X402_FACILITATOR_NAME",
    "coinbase-cdp-x402-facilitator",
)
X402_RESOURCE_DESCRIPTION = "Nova Constraint Pressure environmental conditioning telemetry"


def is_x402_protected_feed(path: str) -> bool:
    return path in X402_PROTECTED_FEED_ENDPOINTS


def is_x402_discoverable_endpoint(path: str) -> bool:
    return path in X402_DISCOVERABLE_ENDPOINTS


def x402_payment_requirement(*, endpoint: str, feed_tier: Any = "developer") -> Dict[str, Any]:
    pricing = pricing_for_tier(feed_tier)
    return {
        "x402_version": X402_VERSION,
        "payment_required": True,
        "payment_network": X402_PAYMENT_NETWORK,
        "protocol_network": X402_PROTOCOL_NETWORK,
        "payment_asset": X402_PAYMENT_ASSET,
        "asset_address": X402_ASSET_ADDRESS,
        "amount_atomic": X402_USDC_AMOUNT_ATOMIC,
        "settlement_wallet": X402_SETTLEMENT_WALLET,
        "pricing_model": pricing["pricing_model"],
        "base_subscription_usd": pricing["base_subscription_usd"],
        "included_requests": pricing["included_requests"],
        "overage_per_1000": pricing["overage_per_1000"],
        "cadence_tier": pricing["cadence_tier"],
        "cadence_seconds": pricing["cadence_seconds"],
        "facilitator": {
            "name": X402_FACILITATOR_NAME,
            "url": X402_FACILITATOR_URL,
            "verification_mode": "facilitator_settlement",
        },
        "resource": endpoint,
        "accepted_payment_header": X402_PAYMENT_HEADER,
        "legacy_payment_header": X402_LEGACY_PAYMENT_HEADER,
    }


def x402_settlement_metadata() -> Dict[str, Any]:
    return {
        "payment_network": X402_PAYMENT_NETWORK,
        "payment_asset": X402_PAYMENT_ASSET,
        "settlement_wallet": X402_SETTLEMENT_WALLET,
        "facilitator": {
            "name": X402_FACILITATOR_NAME,
            "url": X402_FACILITATOR_URL,
        },
    }
