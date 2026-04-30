import json
import os
import re
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from core.billing_config import (
    DEFAULT_PRICE_PER_DECISION_USD,
    FREE_CONTEXT_CALL_LIMIT,
    USDC_PAYMENT_WALLET,
)
from core.identity import ANONYMOUS_ACTOR_ID


BILLING_STATE_FILE_ENV = "NOVA_BILLING_STATE_FILE"
DEFAULT_BILLING_STATE_FILE = ".billing_state.json"
BILLING_MODES = {"evaluation", "pilot", "active"}

_ETH_WALLET_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
_BILLING_STATE: Dict[str, Dict[str, Any]] = {}
_BILLING_STATE_FILE: Optional[Path] = None
_BILLING_STATE_LOCK = Lock()


def _state_file() -> Path:
    return Path(os.getenv(BILLING_STATE_FILE_ENV, DEFAULT_BILLING_STATE_FILE)).expanduser()


def _load_state(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return {str(key): value for key, value in raw.items() if isinstance(value, dict)}
    except Exception:
        return {}
    return {}


def _write_state(path: Path, state: Dict[str, Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _ensure_loaded_unlocked() -> Path:
    global _BILLING_STATE, _BILLING_STATE_FILE

    path = _state_file()
    if _BILLING_STATE_FILE != path:
        _BILLING_STATE = _load_state(path)
        _BILLING_STATE_FILE = path
    return path


def _round_usd(amount: float) -> float:
    return round(float(amount), 2)


def _empty_billing_record(actor_id: str) -> Dict[str, Any]:
    normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
    return {
        "actor_id": normalized_actor,
        "billing_mode": "evaluation",
        "usdc_wallet": None,
        "payment_destination": USDC_PAYMENT_WALLET,
        "decisions_billed": 0,
        "amount_due_usd": 0.0,
    }


def _ensure_record_unlocked(actor_id: str) -> Dict[str, Any]:
    normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
    record = _BILLING_STATE.setdefault(normalized_actor, _empty_billing_record(normalized_actor))
    record["actor_id"] = normalized_actor
    record["billing_mode"] = (
        record.get("billing_mode") if record.get("billing_mode") in BILLING_MODES else "evaluation"
    )
    record.setdefault("usdc_wallet", None)
    record["payment_destination"] = USDC_PAYMENT_WALLET
    record["decisions_billed"] = int(record.get("decisions_billed", 0) or 0)
    record["amount_due_usd"] = _round_usd(record.get("amount_due_usd", 0.0) or 0.0)
    return record


def validate_wallet_format(wallet: str) -> bool:
    return bool(_ETH_WALLET_PATTERN.fullmatch((wallet or "").strip()))


def bind_wallet(actor_id: str, payer_wallet: str) -> Dict[str, Any]:
    wallet = (payer_wallet or "").strip()
    if not validate_wallet_format(wallet):
        raise ValueError("Invalid payer_wallet")

    with _BILLING_STATE_LOCK:
        path = _ensure_loaded_unlocked()
        record = _ensure_record_unlocked(actor_id)
        record["usdc_wallet"] = wallet
        record["billing_mode"] = "pilot"
        record["payment_destination"] = USDC_PAYMENT_WALLET
        _write_state(path, _BILLING_STATE)
        return dict(record)


def sync_context_usage(actor_id: str, context_calls: int) -> Optional[Dict[str, Any]]:
    try:
        with _BILLING_STATE_LOCK:
            path = _ensure_loaded_unlocked()
            record = _ensure_record_unlocked(actor_id)
            billable_decisions = max(int(context_calls or 0) - FREE_CONTEXT_CALL_LIMIT, 0)
            record["decisions_billed"] = billable_decisions
            record["amount_due_usd"] = _round_usd(
                billable_decisions * DEFAULT_PRICE_PER_DECISION_USD
            )
            record["payment_destination"] = USDC_PAYMENT_WALLET
            _write_state(path, _BILLING_STATE)
            return dict(record)
    except Exception:
        return None


def get_billing_record(actor_id: str) -> Dict[str, Any]:
    try:
        with _BILLING_STATE_LOCK:
            _ensure_loaded_unlocked()
            normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
            record = _BILLING_STATE.get(normalized_actor)
            if not isinstance(record, dict):
                return _empty_billing_record(normalized_actor)
            merged = _empty_billing_record(normalized_actor)
            merged.update(record)
            merged["payment_destination"] = USDC_PAYMENT_WALLET
            merged["decisions_billed"] = int(merged.get("decisions_billed", 0) or 0)
            merged["amount_due_usd"] = _round_usd(merged.get("amount_due_usd", 0.0) or 0.0)
            return merged
    except Exception:
        return _empty_billing_record(actor_id or ANONYMOUS_ACTOR_ID)


def reset_billing_state_for_tests() -> None:
    with _BILLING_STATE_LOCK:
        _BILLING_STATE.clear()
