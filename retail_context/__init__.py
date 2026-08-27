"""Isolated retail-agent context plane for Nova Context Network.

This package is intentionally separate from institutional target-v2 review
context, accepted chronology, accepted-state synchronization, institutional
constraints, and institutional Reflex Memory.
"""

from .boundaries import assert_retail_module_allowed, validate_retail_package_imports
from .config import RetailContextConfig
from .context_delta import (
    build_context_delta,
    load_context_delta_schema,
    validate_context_delta,
)
from .schema import (
    SCHEMA_VERSION,
    load_retail_context_schema,
    retail_context_validator,
    validate_retail_context_object,
)
from .sources import (
    FixtureRetailSourceAdapter,
    RetailSourceAdapter,
    is_source_usable,
    load_source_observation_schema,
    load_source_registry_schema,
    validate_source_observation,
    validate_source_registry,
)
from .state_ping import build_state_ping
from .x402_payment import (
    ACCESS_EFFECT,
    AUTHORITY_EFFECT,
    PAYMENT_ASSET,
    PAYMENT_NETWORK,
    PAYMENT_SCHEME,
    PRICING_MODEL,
    RETAIL_PAYMENT_HEADER_NAMES,
    RETAIL_RESOURCE_PRICE_CATALOG,
    X402_VERSION,
    RetailPaymentChallenge,
    RetailX402Facilitator,
    RetailX402PaymentError,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    load_retail_x402_payment_schema,
    payment_receipt_allows_resource_access,
    process_retail_x402_payment,
    run_retail_x402_payment_loop,
    validate_retail_payment_requirement,
    validate_retail_x402_payment_record,
)

__all__ = [
    "RetailContextConfig",
    "FixtureRetailSourceAdapter",
    "RetailSourceAdapter",
    "RetailPaymentChallenge",
    "RetailX402Facilitator",
    "RetailX402PaymentError",
    "SCHEMA_VERSION",
    "ACCESS_EFFECT",
    "AUTHORITY_EFFECT",
    "PAYMENT_ASSET",
    "PAYMENT_NETWORK",
    "PAYMENT_SCHEME",
    "PRICING_MODEL",
    "RETAIL_PAYMENT_HEADER_NAMES",
    "RETAIL_RESOURCE_PRICE_CATALOG",
    "X402_VERSION",
    "assert_retail_module_allowed",
    "build_context_delta",
    "build_state_ping",
    "build_retail_payment_challenge",
    "build_retail_payment_requirement",
    "is_source_usable",
    "load_retail_context_schema",
    "load_context_delta_schema",
    "load_source_observation_schema",
    "load_source_registry_schema",
    "load_retail_x402_payment_schema",
    "payment_receipt_allows_resource_access",
    "process_retail_x402_payment",
    "retail_context_validator",
    "validate_retail_context_object",
    "validate_context_delta",
    "validate_retail_package_imports",
    "validate_retail_payment_requirement",
    "validate_retail_x402_payment_record",
    "validate_source_observation",
    "validate_source_registry",
    "run_retail_x402_payment_loop",
]
