from __future__ import annotations

from typing import Any, Dict


PRICING_MODEL = "subscription_plus_volume"

FEED_TIER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "developer": {
        "cadence_tier": "developer",
        "cadence_seconds": 300,
        "cadence_description": "5_minute_delayed_cadence",
        "base_subscription_usd": 299,
        "included_requests": 100000,
        "overage_per_1000": 0.50,
        "marketplace_package": "developer_environmental_conditioning",
    },
    "growth": {
        "cadence_tier": "growth",
        "cadence_seconds": 30,
        "cadence_description": "30_second_cadence",
        "base_subscription_usd": 2500,
        "included_requests": 100000,
        "overage_per_1000": 0.50,
        "marketplace_package": "growth_orchestration_conditioning",
    },
    "enterprise": {
        "cadence_tier": "enterprise",
        "cadence_seconds": 5,
        "cadence_description": "near_realtime_cadence",
        "base_subscription_usd": 10000,
        "included_requests": 1000000,
        "overage_per_1000": 0.25,
        "marketplace_package": "enterprise_embedded_conditioning",
    },
}


def normalize_feed_tier(value: Any) -> str:
    normalized = str(value or "developer").strip().lower()
    if normalized in FEED_TIER_DEFINITIONS:
        return normalized
    return "developer"


def pricing_for_tier(feed_tier: Any) -> Dict[str, Any]:
    normalized_tier = normalize_feed_tier(feed_tier)
    tier_config = dict(FEED_TIER_DEFINITIONS[normalized_tier])
    return {
        "pricing_model": PRICING_MODEL,
        **tier_config,
    }


def calculate_feed_cost(*, monthly_feed_usage: int, feed_tier: Any) -> Dict[str, Any]:
    pricing = pricing_for_tier(feed_tier)
    included_requests = int(pricing["included_requests"])
    billable_requests = max(int(monthly_feed_usage or 0) - included_requests, 0)
    overage_per_1000 = float(pricing["overage_per_1000"])
    overage_cost = (billable_requests / 1000) * overage_per_1000
    estimated_monthly_cost = round(float(pricing["base_subscription_usd"]) + overage_cost, 2)
    return {
        **pricing,
        "monthly_feed_usage": int(monthly_feed_usage or 0),
        "billable_requests": billable_requests,
        "estimated_monthly_cost_usd": estimated_monthly_cost,
    }
