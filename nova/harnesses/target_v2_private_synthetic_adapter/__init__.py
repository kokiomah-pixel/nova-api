"""Offline target-v2 synthetic reference adapter.

This package is a Gate 4 harness.  It is intentionally disconnected from the
application runtime and exposes no transport, service, or provider integration.
"""

from .adapter import AdapterResult, SyntheticAdapterError, TargetV2SyntheticAdapter
from .canonicalization import (
    CanonicalizationError,
    canonicalize_jcs,
    fixture_checksum_v0,
    normalize_declared_set,
    normalize_exact_decimal,
    normalize_monetary_amount,
    normalize_timestamp,
)

__all__ = [
    "AdapterResult",
    "CanonicalizationError",
    "SyntheticAdapterError",
    "TargetV2SyntheticAdapter",
    "canonicalize_jcs",
    "fixture_checksum_v0",
    "normalize_declared_set",
    "normalize_exact_decimal",
    "normalize_monetary_amount",
    "normalize_timestamp",
]
