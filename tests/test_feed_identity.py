from core.feed_identity import (
    build_feed_consumer_identity,
    feed_consumer_id_from_api_key,
    feed_tier_from_record,
)
from core.identity import actor_id_from_api_key


def test_feed_consumer_id_is_separate_from_sovereign_actor_id():
    api_key = "same-underlying-key"

    feed_consumer_id = feed_consumer_id_from_api_key(api_key)
    actor_id = actor_id_from_api_key(api_key)

    assert feed_consumer_id.startswith("feed_")
    assert actor_id.startswith("actor_")
    assert feed_consumer_id != actor_id


def test_feed_tier_does_not_reuse_sovereign_tier_by_default():
    record = {
        "tier": "enterprise",
        "owner": "sovereign-decision-actor",
    }

    assert feed_tier_from_record(record) == "developer"


def test_explicit_feed_tier_controls_conditioning_identity():
    identity = build_feed_consumer_identity(
        "telemetry-key",
        {
            "tier": "pro",
            "feed_tier": "growth",
            "owner": "decision-owner",
        },
    )

    assert identity["feed_tier"] == "growth"
    assert identity["identity_layer"] == "feed_consumer"
    assert identity["authority_separation"] == "conditioning_not_decision_authority"
    assert identity["machine_consumable"] is True
    assert identity["orchestration_client"] is True
    assert identity["agentic_market_enabled"] is True
    assert identity["x402_ready"] is True
    assert "actor_id" not in identity
    assert "api_key" not in identity
    assert "reflex" not in "".join(identity.keys()).lower()


def test_unknown_feed_tier_falls_back_to_developer():
    identity = build_feed_consumer_identity(
        "telemetry-key",
        {
            "feed_tier": "experimental-alpha",
        },
    )

    assert identity["feed_tier"] == "developer"
