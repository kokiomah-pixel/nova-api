from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse

from .production_config import RetailProductionControlConfig


PROOF_ACCESS_TOKEN_ENV = "NOVA_RETAIL_CONTROLLED_PROOF_ACCESS_TOKEN"
FACILITATOR_URL_ENV = "NOVA_RETAIL_X402_FACILITATOR_URL"
FACILITATOR_TIMEOUT_ENV = "NOVA_RETAIL_X402_FACILITATOR_TIMEOUT_SECONDS"
SETTLEMENT_WALLET_ENV = "NOVA_RETAIL_X402_SETTLEMENT_WALLET"
SOURCE_REGISTRY_PATH_ENV = "NOVA_RETAIL_SOURCE_REGISTRY_PATH"
MAX_REQUEST_BYTES_ENV = "NOVA_RETAIL_MAX_REQUEST_BYTES"
MAX_RESPONSE_BYTES_ENV = "NOVA_RETAIL_MAX_RESPONSE_BYTES"
PROOF_ACCESS_HEADER = "X-Nova-Retail-Controlled-Proof"
DEFAULT_FACILITATOR_TIMEOUT_SECONDS = 10.0
MAX_FACILITATOR_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_REQUEST_BYTES = 1_000_000
DEFAULT_MAX_RESPONSE_BYTES = 2_000_000


class RetailRuntimeConfigError(ValueError):
    def __init__(self, reason: str = "invalid_retail_runtime_config") -> None:
        self.reason = reason
        super().__init__(reason)


def _positive_int(value: object, *, maximum: int) -> int:
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise RetailRuntimeConfigError() from exc
    if isinstance(value, bool) or parsed <= 0 or parsed > maximum:
        raise RetailRuntimeConfigError()
    return parsed


def _bounded_timeout(value: object) -> float:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise RetailRuntimeConfigError() from exc
    if (
        not math.isfinite(parsed)
        or parsed <= 0
        or parsed > MAX_FACILITATOR_TIMEOUT_SECONDS
    ):
        raise RetailRuntimeConfigError()
    return parsed


@dataclass(frozen=True)
class RetailRuntimeConfig:
    controlled_proof_access_token: str = field(repr=False)
    facilitator_url: str
    facilitator_timeout_seconds: float
    settlement_wallet: str
    source_registry_path: Path
    max_request_bytes: int
    max_response_bytes: int
    production_controls: RetailProductionControlConfig

    def __post_init__(self) -> None:
        if not isinstance(self.production_controls, RetailProductionControlConfig):
            raise RetailRuntimeConfigError()
        if (
            not isinstance(self.controlled_proof_access_token, str)
            or len(self.controlled_proof_access_token) < 16
        ):
            raise RetailRuntimeConfigError()
        parsed_url = urlparse(self.facilitator_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise RetailRuntimeConfigError()
        object.__setattr__(
            self,
            "facilitator_timeout_seconds",
            _bounded_timeout(self.facilitator_timeout_seconds),
        )
        if not isinstance(self.settlement_wallet, str) or not self.settlement_wallet.strip():
            raise RetailRuntimeConfigError()
        object.__setattr__(self, "settlement_wallet", self.settlement_wallet.strip())
        object.__setattr__(
            self, "source_registry_path", Path(self.source_registry_path).expanduser()
        )
        object.__setattr__(
            self,
            "max_request_bytes",
            _positive_int(self.max_request_bytes, maximum=5_000_000),
        )
        object.__setattr__(
            self,
            "max_response_bytes",
            _positive_int(self.max_response_bytes, maximum=10_000_000),
        )

    @classmethod
    def from_env(
        cls, environ: Mapping[str, str] | None = None
    ) -> "RetailRuntimeConfig":
        source = os.environ if environ is None else environ
        required = {
            PROOF_ACCESS_TOKEN_ENV: source.get(PROOF_ACCESS_TOKEN_ENV),
            FACILITATOR_URL_ENV: source.get(FACILITATOR_URL_ENV),
            SETTLEMENT_WALLET_ENV: source.get(SETTLEMENT_WALLET_ENV),
            SOURCE_REGISTRY_PATH_ENV: source.get(SOURCE_REGISTRY_PATH_ENV),
        }
        if any(not value for value in required.values()):
            raise RetailRuntimeConfigError()
        return cls(
            controlled_proof_access_token=required[PROOF_ACCESS_TOKEN_ENV],  # type: ignore[arg-type]
            facilitator_url=required[FACILITATOR_URL_ENV],  # type: ignore[arg-type]
            facilitator_timeout_seconds=_bounded_timeout(
                source.get(
                    FACILITATOR_TIMEOUT_ENV,
                    DEFAULT_FACILITATOR_TIMEOUT_SECONDS,
                )
            ),
            settlement_wallet=required[SETTLEMENT_WALLET_ENV],  # type: ignore[arg-type]
            source_registry_path=Path(required[SOURCE_REGISTRY_PATH_ENV]),  # type: ignore[arg-type]
            max_request_bytes=_positive_int(
                source.get(MAX_REQUEST_BYTES_ENV, DEFAULT_MAX_REQUEST_BYTES),
                maximum=5_000_000,
            ),
            max_response_bytes=_positive_int(
                source.get(MAX_RESPONSE_BYTES_ENV, DEFAULT_MAX_RESPONSE_BYTES),
                maximum=10_000_000,
            ),
            production_controls=RetailProductionControlConfig.from_env(source),
        )
