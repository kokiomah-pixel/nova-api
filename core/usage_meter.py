import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from core.billing_config import FREE_CONTEXT_CALL_LIMIT
from core.identity import ANONYMOUS_ACTOR_ID


USAGE_STATE_FILE_ENV = "NOVA_USAGE_STATE_FILE"
DEFAULT_USAGE_STATE_FILE = ".usage_state.json"

_USAGE_STATE: Dict[str, Dict[str, Any]] = {}
_USAGE_STATE_FILE: Optional[Path] = None
_USAGE_STATE_LOCK = Lock()


def _current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_file() -> Path:
    return Path(os.getenv(USAGE_STATE_FILE_ENV, DEFAULT_USAGE_STATE_FILE)).expanduser()


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
    global _USAGE_STATE, _USAGE_STATE_FILE

    path = _state_file()
    if _USAGE_STATE_FILE != path:
        _USAGE_STATE = _load_state(path)
        _USAGE_STATE_FILE = path
    return path


def _empty_usage_record(actor_id: str) -> Dict[str, Any]:
    normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
    return {
        "actor_id": normalized_actor,
        "context_calls": 0,
        "proof_calls": 0,
        "first_seen": None,
        "last_seen": None,
        "usage_state": "evaluation",
    }


def _ensure_record_unlocked(actor_id: str) -> Dict[str, Any]:
    normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
    now = _current_timestamp()
    record = _USAGE_STATE.setdefault(normalized_actor, _empty_usage_record(normalized_actor))
    record["actor_id"] = normalized_actor
    record["context_calls"] = int(record.get("context_calls", 0) or 0)
    record["proof_calls"] = int(record.get("proof_calls", 0) or 0)
    record.setdefault("first_seen", now)
    if record["first_seen"] is None:
        record["first_seen"] = now
    record.setdefault("last_seen", now)
    record.setdefault("usage_state", "evaluation")
    return record


def increment_context_call(actor_id: str) -> Optional[Dict[str, Any]]:
    try:
        with _USAGE_STATE_LOCK:
            path = _ensure_loaded_unlocked()
            record = _ensure_record_unlocked(actor_id)
            record["context_calls"] += 1
            record["last_seen"] = _current_timestamp()
            if record["context_calls"] > FREE_CONTEXT_CALL_LIMIT:
                record["usage_state"] = "evaluation_limit_reached"
            else:
                record.setdefault("usage_state", "evaluation")
            _write_state(path, _USAGE_STATE)
            return dict(record)
    except Exception:
        return None


def increment_proof_call(actor_id: str) -> Optional[Dict[str, Any]]:
    try:
        with _USAGE_STATE_LOCK:
            path = _ensure_loaded_unlocked()
            record = _ensure_record_unlocked(actor_id)
            record["proof_calls"] += 1
            record["last_seen"] = _current_timestamp()
            _write_state(path, _USAGE_STATE)
            return dict(record)
    except Exception:
        return None


def get_usage_record(actor_id: str) -> Dict[str, Any]:
    try:
        with _USAGE_STATE_LOCK:
            _ensure_loaded_unlocked()
            normalized_actor = actor_id or ANONYMOUS_ACTOR_ID
            record = _USAGE_STATE.get(normalized_actor)
            if not isinstance(record, dict):
                return _empty_usage_record(normalized_actor)
            merged = _empty_usage_record(normalized_actor)
            merged.update(record)
            merged["context_calls"] = int(merged.get("context_calls", 0) or 0)
            merged["proof_calls"] = int(merged.get("proof_calls", 0) or 0)
            return merged
    except Exception:
        return _empty_usage_record(actor_id or ANONYMOUS_ACTOR_ID)


def reset_usage_state_for_tests() -> None:
    with _USAGE_STATE_LOCK:
        _USAGE_STATE.clear()
