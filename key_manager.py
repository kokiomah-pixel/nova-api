import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

KEY_STORE = Path("keys.json")
_KEY_LOCK = Lock()


def get_quota(tier: str) -> Optional[int]:
    return {
        "emerging": 50000,
        "core": 200000,
        "enterprise": None,
        "free": 1000,
        "pro": 100000,
        "admin": 1000000,
    }.get((tier or "").lower(), 1000)


def generate_api_key() -> str:
    return f"nova_{uuid.uuid4().hex[:24]}"


def load_keys() -> Dict[str, Dict[str, Any]]:
    if not KEY_STORE.exists():
        return {}
    try:
        return json.loads(KEY_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_keys(data: Dict[str, Dict[str, Any]]) -> None:
    KEY_STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = KEY_STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(KEY_STORE)


def store_key(api_key: str, tier: str, owner: str = "stripe") -> Dict[str, Any]:
    normalized_tier = (tier or "free").lower()
    quota = get_quota(normalized_tier)
    record = {
        "owner": owner,
        "tier": normalized_tier,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "quota": quota,
        "monthly_quota": quota,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/key-info",
            "/v1/usage",
            "/health",
        ],
    }

    with _KEY_LOCK:
        data = load_keys()
        data[api_key] = record
        _write_keys(data)

    return record


def manual_create_key(email: str, tier: str) -> str:
    api_key = generate_api_key()
    store_key(api_key, tier=tier, owner=email)
    print(f"[MANUAL] {email} -> {api_key}")
    return api_key
