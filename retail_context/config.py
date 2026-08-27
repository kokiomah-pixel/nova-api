from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


RETAIL_ENV_PREFIX = "NOVA_RETAIL_"
DEFAULT_RETAIL_STATE_DIR = ".nova_retail"
DEFAULT_RETAIL_ENDPOINT_PREFIX = "/retail/v1/context"


@dataclass(frozen=True)
class RetailContextConfig:
    """Configuration owned only by the retail-agent context plane."""

    endpoint_prefix: str
    state_dir: Path
    telemetry_namespace: str
    source_namespace: str
    credential_namespace: str

    @classmethod
    def from_env(cls) -> "RetailContextConfig":
        return cls(
            endpoint_prefix=os.getenv(
                f"{RETAIL_ENV_PREFIX}ENDPOINT_PREFIX",
                DEFAULT_RETAIL_ENDPOINT_PREFIX,
            ).strip(),
            state_dir=Path(
                os.getenv(
                    f"{RETAIL_ENV_PREFIX}STATE_DIR",
                    DEFAULT_RETAIL_STATE_DIR,
                )
            ).expanduser(),
            telemetry_namespace=os.getenv(
                f"{RETAIL_ENV_PREFIX}TELEMETRY_NAMESPACE",
                "retail_context",
            ).strip(),
            source_namespace=os.getenv(
                f"{RETAIL_ENV_PREFIX}SOURCE_NAMESPACE",
                "retail_public_sources",
            ).strip(),
            credential_namespace=os.getenv(
                f"{RETAIL_ENV_PREFIX}CREDENTIAL_NAMESPACE",
                "retail_context",
            ).strip(),
        )
