from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .config import DEFAULT_RETAIL_STATE_DIR


CONTROL_DB_ENV = "NOVA_RETAIL_CONTROL_DB_PATH"
RATE_LIMIT_WINDOW_ENV = "NOVA_RETAIL_RATE_LIMIT_WINDOW_SECONDS"
STATE_PING_MAX_REQUESTS_ENV = "NOVA_RETAIL_STATE_PING_MAX_REQUESTS"
CONTEXT_DELTA_MAX_REQUESTS_ENV = "NOVA_RETAIL_CONTEXT_DELTA_MAX_REQUESTS"
DEFAULT_CONTROL_DB_NAME = "production_controls.sqlite3"


class RetailProductionControlConfigError(ValueError):
    def __init__(self, reason: str = "invalid_control_config") -> None:
        self.reason = reason
        super().__init__(reason)


def _positive_integer(value: object) -> int:
    if isinstance(value, bool):
        raise RetailProductionControlConfigError()
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise RetailProductionControlConfigError() from exc
    if parsed <= 0 or str(parsed) != str(value).strip():
        raise RetailProductionControlConfigError()
    return parsed


@dataclass(frozen=True)
class RetailProductionControlConfig:
    """Retail-owned operational settings with no permissive production defaults."""

    control_db_path: Path
    rate_limit_window_seconds: int
    state_ping_max_requests: int
    context_delta_max_requests: int

    def __post_init__(self) -> None:
        path = Path(self.control_db_path).expanduser()
        if not str(path).strip() or str(path) == ":memory:":
            raise RetailProductionControlConfigError()
        object.__setattr__(self, "control_db_path", path)
        for field_name in (
            "rate_limit_window_seconds",
            "state_ping_max_requests",
            "context_delta_max_requests",
        ):
            object.__setattr__(
                self,
                field_name,
                _positive_integer(getattr(self, field_name)),
            )

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> "RetailProductionControlConfig":
        source = os.environ if environ is None else environ
        state_dir = Path(source.get("NOVA_RETAIL_STATE_DIR", DEFAULT_RETAIL_STATE_DIR))
        configured_path = source.get(CONTROL_DB_ENV)
        control_db_path = (
            Path(configured_path) if configured_path else state_dir / DEFAULT_CONTROL_DB_NAME
        )
        required = (
            source.get(RATE_LIMIT_WINDOW_ENV),
            source.get(STATE_PING_MAX_REQUESTS_ENV),
            source.get(CONTEXT_DELTA_MAX_REQUESTS_ENV),
        )
        if any(value is None for value in required):
            raise RetailProductionControlConfigError()
        return cls(
            control_db_path=control_db_path,
            rate_limit_window_seconds=_positive_integer(required[0]),
            state_ping_max_requests=_positive_integer(required[1]),
            context_delta_max_requests=_positive_integer(required[2]),
        )

    def max_requests_for(self, resource_type: str) -> int | None:
        if resource_type == "state_ping":
            return self.state_ping_max_requests
        if resource_type == "context_delta":
            return self.context_delta_max_requests
        return None
