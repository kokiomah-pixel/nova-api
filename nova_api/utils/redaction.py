from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


REDACTED = "[REDACTED]"
SENSITIVE_KEY_PARTS = (
    "authorization",
    "bearer",
    "token",
    "secret",
    "private",
    "signature",
    "credential",
    "api_key",
    "apikey",
    "auth",
)
BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
HEX_SIGNATURE_PATTERN = re.compile(r"0x[a-fA-F0-9]{96,}")


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def redact_text(value: str) -> str:
    value = BEARER_PATTERN.sub("Bearer [REDACTED]", value)
    value = HEX_SIGNATURE_PATTERN.sub("0x[REDACTED]", value)
    return value


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: REDACTED if is_sensitive_key(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value

