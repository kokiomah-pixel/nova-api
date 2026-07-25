from __future__ import annotations

import os


PUBLIC_SERVICE_DISCOVERY_ENV = "NOVA_PUBLIC_SERVICE_DISCOVERY_ENABLED"
PUBLIC_API_DOCUMENTATION_ENV = "NOVA_PUBLIC_API_DOCUMENTATION_ENABLED"
PUBLIC_X402_ENV = "NOVA_PUBLIC_X402_ENABLED"
X402_SETTLEMENT_ENV = "NOVA_X402_SETTLEMENT_ENABLED"

_TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def public_service_discovery_enabled() -> bool:
    return _enabled(PUBLIC_SERVICE_DISCOVERY_ENV)


def public_api_documentation_enabled() -> bool:
    return _enabled(PUBLIC_API_DOCUMENTATION_ENV)


def public_x402_enabled() -> bool:
    return _enabled(PUBLIC_X402_ENV)


def x402_settlement_enabled() -> bool:
    return _enabled(X402_SETTLEMENT_ENV)


def public_x402_operational() -> bool:
    return public_x402_enabled() and x402_settlement_enabled()
