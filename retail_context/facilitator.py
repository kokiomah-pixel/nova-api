from __future__ import annotations

import math
from typing import Any
from urllib.parse import urlparse

from x402.http.facilitator_client import (
    FacilitatorConfig,
    HTTPFacilitatorClientSync,
)
from x402.schemas import (
    PaymentPayload,
    PaymentRequirements,
    SettleResponse,
    VerifyResponse,
)

from .runtime_config import MAX_FACILITATOR_TIMEOUT_SECONDS, RetailRuntimeConfig


class RetailHTTPFacilitatorAdapter:
    """Retail-only wrapper over the official x402 synchronous HTTP client."""

    def __init__(
        self,
        *,
        url: str,
        timeout_seconds: float,
        http_client: Any = None,
    ) -> None:
        parsed_url = urlparse(url)
        if (
            parsed_url.scheme != "https"
            or not parsed_url.netloc
            or parsed_url.username is not None
            or parsed_url.password is not None
        ):
            raise ValueError("invalid_retail_facilitator_url")
        if (
            isinstance(timeout_seconds, bool)
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
            or timeout_seconds > MAX_FACILITATOR_TIMEOUT_SECONDS
        ):
            raise ValueError("invalid_retail_facilitator_timeout")
        self.url = url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._client = HTTPFacilitatorClientSync(
            FacilitatorConfig(
                url=self.url,
                timeout=timeout_seconds,
                http_client=http_client,
                identifier="nova-retail-controlled-proof",
            )
        )

    @classmethod
    def from_runtime_config(
        cls, config: RetailRuntimeConfig
    ) -> "RetailHTTPFacilitatorAdapter":
        return cls(
            url=config.facilitator_url,
            timeout_seconds=config.facilitator_timeout_seconds,
        )

    def verify(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> VerifyResponse:
        return self._client.verify(payload, requirements)

    def settle(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> SettleResponse:
        return self._client.settle(payload, requirements)

    def close(self) -> None:
        self._client.close()
