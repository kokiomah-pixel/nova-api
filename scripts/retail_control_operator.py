#!/usr/bin/env python3
"""Operator-only controls for the isolated retail controlled-proof service."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from retail_context.config import DEFAULT_RETAIL_STATE_DIR
from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.production_config import (
    CONTROL_DB_ENV,
    DEFAULT_CONTROL_DB_NAME,
    RetailProductionControlConfig,
    RetailProductionControlConfigError,
)
from retail_context.production_controls import (
    evaluate_retail_control_readiness,
    set_retail_service_mode,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _control_db_path(environ: Mapping[str, str]) -> Path:
    configured = environ.get(CONTROL_DB_ENV)
    if configured:
        return Path(configured).expanduser()
    state_dir = Path(
        environ.get("NOVA_RETAIL_STATE_DIR", DEFAULT_RETAIL_STATE_DIR)
    ).expanduser()
    return state_dir / DEFAULT_CONTROL_DB_NAME


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Operate the bounded Nova retail service mode without HTTP."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("show-mode")
    set_mode = subcommands.add_parser("set-mode")
    set_mode.add_argument("mode", choices=("disabled", "controlled_proof"))
    subcommands.add_parser("read-readiness")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> int:
    args = _parser().parse_args(argv)
    source = os.environ if environ is None else environ
    observed_at = _utc_now()
    store = SQLiteRetailProductionControlStore(_control_db_path(source))
    try:
        store.initialize()
        if args.command == "show-mode":
            result = {
                "operating_mode": store.get_service_mode(),
                "authority_effect": "none",
            }
        elif args.command == "set-mode":
            set_retail_service_mode(
                store=store,
                mode=args.mode,
                changed_at=observed_at,
            )
            result = {
                "operating_mode": store.get_service_mode(),
                "changed_at": observed_at,
                "authority_effect": "none",
            }
        else:
            try:
                config: object = RetailProductionControlConfig.from_env(source)
            except RetailProductionControlConfigError:
                config = object()
            result = evaluate_retail_control_readiness(
                store=store,
                config=config,
                observed_at=observed_at,
            )
    except Exception:
        result = {
            "status": "not_ready",
            "failure_reason": "control_store_unavailable",
            "authority_effect": "none",
        }
        print(json.dumps(result, separators=(",", ":"), sort_keys=True))
        return 1
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
