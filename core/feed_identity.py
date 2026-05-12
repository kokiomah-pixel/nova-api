from __future__ import annotations

import hashlib
from typing import Any, Dict

from core.feed_pricing import normalize_feed_tier


FEED_IDENTITY_NAMESPACE = "nova-feed-consumer"


def feed_consumer_id_from_api_key(api_key: Any) -> str:
    raw = f"{FEED_IDENTITY_NAMESPACE}:{api_key or 'anonymous'}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:24]
    return f"feed_{digest}"


def feed_tier_from_record(record: Dict[str, Any]) -> str:
    feed_tier = record.get("feed_tier") or record.get("telemetry_tier")
    if feed_tier:
        return normalize_feed_tier(feed_tier)
    return "developer"


def build_feed_consumer_identity(api_key: Any, record: Dict[str, Any]) -> Dict[str, Any]:
    feed_tier = feed_tier_from_record(record)
    return {
        "feed_consumer_id": feed_consumer_id_from_api_key(api_key),
        "feed_tier": feed_tier,
        "identity_layer": "feed_consumer",
        "authority_separation": "conditioning_not_decision_authority",
        "machine_consumable": True,
        "orchestration_client": True,
        "agentic_market_enabled": True,
        "x402_ready": True,
    }
