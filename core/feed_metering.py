from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from core.feed_pricing import calculate_feed_cost, pricing_for_tier


FEED_USAGE_FILE_ENV = "NOVA_FEED_USAGE_FILE"
DEFAULT_FEED_USAGE_FILE = ".feed_usage.json"
ROLLING_WINDOW_SECONDS = 60

_FEED_USAGE_STATE: Dict[str, Dict[str, Any]] = {}
_FEED_USAGE_FILE: Optional[Path] = None
_FEED_USAGE_LOCK = Lock()


def _state_file() -> Path:
    return Path(os.getenv(FEED_USAGE_FILE_ENV, DEFAULT_FEED_USAGE_FILE)).expanduser()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _month_key(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m")


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


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
    global _FEED_USAGE_FILE, _FEED_USAGE_STATE

    path = _state_file()
    if _FEED_USAGE_FILE != path:
        _FEED_USAGE_STATE = _load_state(path)
        _FEED_USAGE_FILE = path
    return path


def _empty_record(feed_consumer_id: str, feed_tier: str, now: datetime) -> Dict[str, Any]:
    return {
        "feed_consumer_id": feed_consumer_id,
        "cadence_tier": feed_tier,
        "feed_calls": 0,
        "constraint_pressure_calls": 0,
        "last_request_timestamp": None,
        "request_timestamps": [],
        "current_month": _month_key(now),
        "monthly_feed_usage": 0,
        "billable_feed_events": 0,
    }


def _ensure_record_unlocked(feed_consumer_id: str, feed_tier: str, now: datetime) -> Dict[str, Any]:
    record = _FEED_USAGE_STATE.setdefault(feed_consumer_id, _empty_record(feed_consumer_id, feed_tier, now))
    record["feed_consumer_id"] = feed_consumer_id
    record["cadence_tier"] = feed_tier
    if record.get("current_month") != _month_key(now):
        record["current_month"] = _month_key(now)
        record["monthly_feed_usage"] = 0
        record["billable_feed_events"] = 0
    record.setdefault("feed_calls", 0)
    record.setdefault("constraint_pressure_calls", 0)
    record.setdefault("last_request_timestamp", None)
    record.setdefault("request_timestamps", [])
    record.setdefault("monthly_feed_usage", 0)
    record.setdefault("billable_feed_events", 0)
    return record


def _prune_rolling_timestamps(timestamps: List[str], now: datetime) -> List[str]:
    retained = []
    for timestamp in timestamps:
        parsed = _parse_timestamp(timestamp)
        if parsed is None:
            continue
        if (now - parsed).total_seconds() <= ROLLING_WINDOW_SECONDS:
            retained.append(_isoformat(parsed))
    return retained


def record_feed_request(
    *,
    feed_consumer_id: str,
    feed_name: str,
    feed_tier: str,
    requested_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = requested_at or _now_utc()
    pricing = pricing_for_tier(feed_tier)

    with _FEED_USAGE_LOCK:
        path = _ensure_loaded_unlocked()
        record = _ensure_record_unlocked(feed_consumer_id, str(pricing["cadence_tier"]), now)
        previous_request = _parse_timestamp(record.get("last_request_timestamp"))
        elapsed_seconds = None
        if previous_request is not None:
            elapsed_seconds = max((now - previous_request).total_seconds(), 0.0)

        cadence_seconds = int(pricing["cadence_seconds"])
        cadence_limited = elapsed_seconds is not None and elapsed_seconds < cadence_seconds

        record["feed_calls"] = int(record.get("feed_calls", 0) or 0) + 1
        if feed_name == "constraint_pressure":
            record["constraint_pressure_calls"] = int(record.get("constraint_pressure_calls", 0) or 0) + 1
        record["monthly_feed_usage"] = int(record.get("monthly_feed_usage", 0) or 0) + 1
        record["last_request_timestamp"] = _isoformat(now)
        timestamps = _prune_rolling_timestamps(list(record.get("request_timestamps", [])), now)
        timestamps.append(_isoformat(now))
        record["request_timestamps"] = timestamps[-500:]

        cost = calculate_feed_cost(
            monthly_feed_usage=int(record["monthly_feed_usage"]),
            feed_tier=pricing["cadence_tier"],
        )
        record["billable_feed_events"] = int(cost["billable_requests"])
        _write_state(path, _FEED_USAGE_STATE)

        return {
            "feed_consumer_id": feed_consumer_id,
            "feed_name": feed_name,
            "cadence_tier": pricing["cadence_tier"],
            "cadence_seconds": cadence_seconds,
            "cadence_limited": cadence_limited,
            "cadence_state": "within_cadence_window" if cadence_limited else "cadence_available",
            "rolling_window_requests": len(record["request_timestamps"]),
            "monthly_feed_usage": int(record["monthly_feed_usage"]),
            "billable_feed_events": int(record["billable_feed_events"]),
            "last_request_timestamp": record["last_request_timestamp"],
        }


def get_feed_usage_record(*, feed_consumer_id: str, feed_tier: str) -> Dict[str, Any]:
    now = _now_utc()
    pricing = pricing_for_tier(feed_tier)
    with _FEED_USAGE_LOCK:
        _ensure_loaded_unlocked()
        record = _ensure_record_unlocked(feed_consumer_id, str(pricing["cadence_tier"]), now)
        record["request_timestamps"] = _prune_rolling_timestamps(list(record.get("request_timestamps", [])), now)
        cost = calculate_feed_cost(
            monthly_feed_usage=int(record.get("monthly_feed_usage", 0) or 0),
            feed_tier=pricing["cadence_tier"],
        )
        record["billable_feed_events"] = int(cost["billable_requests"])
        return dict(record)


def build_feed_usage_summary(*, feed_consumer_id: str, feed_tier: str) -> Dict[str, Any]:
    record = get_feed_usage_record(feed_consumer_id=feed_consumer_id, feed_tier=feed_tier)
    cost = calculate_feed_cost(
        monthly_feed_usage=int(record.get("monthly_feed_usage", 0) or 0),
        feed_tier=record.get("cadence_tier") or feed_tier,
    )
    return {
        "constraint_pressure_calls": int(record.get("constraint_pressure_calls", 0) or 0),
        "cadence_tier": cost["cadence_tier"],
        "cadence_seconds": cost["cadence_seconds"],
        "included_requests": int(cost["included_requests"]),
        "rolling_window_requests": len(record.get("request_timestamps", []) or []),
        "monthly_feed_usage": int(record.get("monthly_feed_usage", 0) or 0),
        "billable_requests": int(cost["billable_requests"]),
        "billable_feed_events": int(record.get("billable_feed_events", 0) or 0),
        "estimated_monthly_cost_usd": cost["estimated_monthly_cost_usd"],
        "last_request_timestamp": record.get("last_request_timestamp"),
        "pricing_model": cost["pricing_model"],
        "base_subscription_usd": cost["base_subscription_usd"],
        "overage_per_1000": cost["overage_per_1000"],
    }


def reset_feed_usage_state_for_tests() -> None:
    with _FEED_USAGE_LOCK:
        _FEED_USAGE_STATE.clear()
