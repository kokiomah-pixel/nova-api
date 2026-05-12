import importlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from core.feed_metering import (
    build_feed_usage_summary,
    record_feed_request,
    reset_feed_usage_state_for_tests,
)
from core.feed_pricing import calculate_feed_cost, pricing_for_tier


FEED_METERING_KEY = "feed-metering-key"
FEED_METERING_KEYS = {
    FEED_METERING_KEY: {
        "owner": "feed-metering-user",
        "tier": "pro",
        "feed_tier": "growth",
        "status": "active",
        "monthly_quota": 1000,
        "allowed_endpoints": [
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/billing/summary",
            "/v1/feeds/constraint_pressure",
            "/v1/feeds/usage",
            "/v1/usage",
        ],
    },
}


@pytest.fixture
def feed_metering_client():
    keys_json = json.dumps(FEED_METERING_KEYS)
    test_files = [
        ".usage.feed-metering-test.json",
        ".usage_state.feed-metering-test.json",
        ".billing_state.feed-metering-test.json",
        ".feed_usage.feed-metering-test.json",
        ".proof.feed-metering-test.json",
        "proof_retrieval_audit.feed-metering-test.jsonl",
        ".reflex_governance_records.feed-metering-test.jsonl",
        ".reflex_governance_signals.feed-metering-test.json",
        ".reflex_governance_escalations.feed-metering-test.json",
    ]
    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": keys_json,
            "NOVA_USAGE_FILE": test_files[0],
            "NOVA_USAGE_STATE_FILE": test_files[1],
            "NOVA_BILLING_STATE_FILE": test_files[2],
            "NOVA_FEED_USAGE_FILE": test_files[3],
            "NOVA_PROOF_FILE": test_files[4],
            "NOVA_PROOF_RETRIEVAL_AUDIT_FILE": test_files[5],
            "NOVA_REFLEX_GOVERNANCE_RECORDS_FILE": test_files[6],
            "NOVA_REFLEX_GOVERNANCE_SIGNALS_FILE": test_files[7],
            "NOVA_REFLEX_GOVERNANCE_ESCALATIONS_FILE": test_files[8],
        },
    ):
        for module_name in ["app", "core.usage_meter", "core.billing_state", "core.feed_metering"]:
            sys.modules.pop(module_name, None)
        app_module = importlib.import_module("app")
        feed_metering = importlib.import_module("core.feed_metering")
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        feed_metering.reset_feed_usage_state_for_tests()
        yield TestClient(app_module.app), app_module
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        feed_metering.reset_feed_usage_state_for_tests()
        for path in test_files:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def _headers() -> dict:
    return {"Authorization": f"Bearer {FEED_METERING_KEY}"}


def _without_signature(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key != "signature"}


def test_feed_pricing_metadata_defines_required_cadence_tiers():
    developer = pricing_for_tier("developer")
    growth = pricing_for_tier("growth")
    enterprise = pricing_for_tier("enterprise")

    assert developer["pricing_model"] == "subscription_plus_volume"
    assert developer["cadence_seconds"] == 300
    assert developer["base_subscription_usd"] == 299
    assert growth["cadence_seconds"] == 30
    assert growth["base_subscription_usd"] == 2500
    assert enterprise["cadence_seconds"] == 5
    assert enterprise["base_subscription_usd"] == 10000


def test_feed_metering_tracks_requests_cadence_and_pricing(tmp_path):
    usage_file = tmp_path / "feed_usage.json"
    started_at = datetime(2026, 5, 12, 12, 0, tzinfo=timezone.utc)

    with patch.dict(os.environ, {"NOVA_FEED_USAGE_FILE": str(usage_file)}):
        reset_feed_usage_state_for_tests()
        first = record_feed_request(
            feed_consumer_id="feed_test_consumer",
            feed_name="constraint_pressure",
            feed_tier="developer",
            requested_at=started_at,
        )
        second = record_feed_request(
            feed_consumer_id="feed_test_consumer",
            feed_name="constraint_pressure",
            feed_tier="developer",
            requested_at=started_at + timedelta(seconds=10),
        )
        summary = build_feed_usage_summary(
            feed_consumer_id="feed_test_consumer",
            feed_tier="developer",
        )

    assert first["cadence_limited"] is False
    assert second["cadence_limited"] is True
    assert second["cadence_state"] == "within_cadence_window"
    assert summary["constraint_pressure_calls"] == 2
    assert summary["cadence_tier"] == "developer"
    assert summary["included_requests"] == 100000
    assert summary["monthly_feed_usage"] == 2
    assert summary["billable_requests"] == 0
    assert summary["estimated_monthly_cost_usd"] == 299


def test_feed_pricing_calculates_volume_overage():
    cost = calculate_feed_cost(monthly_feed_usage=102000, feed_tier="developer")

    assert cost["billable_requests"] == 2000
    assert cost["estimated_monthly_cost_usd"] == 300.0


def test_feed_usage_endpoint_accounts_for_telemetry_without_sovereign_usage(feed_metering_client):
    client, _ = feed_metering_client

    initial_usage = client.get("/v1/feeds/usage", headers=_headers()).json()
    assert initial_usage["feed_usage"]["constraint_pressure_calls"] == 0

    first_feed = client.get("/v1/feeds/constraint_pressure", headers=_headers()).json()
    second_feed = client.get("/v1/feeds/constraint_pressure", headers=_headers()).json()
    feed_usage = client.get("/v1/feeds/usage", headers=_headers()).json()
    billing_summary = client.get("/v1/billing/summary", headers=_headers()).json()

    assert first_feed["agentic_market_ready"] is True
    assert first_feed["pricing_model"] == "subscription_plus_volume"
    assert first_feed["cadence_tier"] == "growth"
    assert first_feed["feed_identity"]["feed_tier"] == "growth"
    assert second_feed["feed_metering"]["cadence_limited"] is True
    assert feed_usage["feed_authority"] == "non_admission_telemetry"
    assert feed_usage["feed_usage"]["constraint_pressure_calls"] == 2
    assert feed_usage["feed_usage"]["cadence_tier"] == "growth"
    assert feed_usage["feed_usage"]["estimated_monthly_cost_usd"] == 2500
    assert feed_usage["telemetry_billing"]["telemetry_amount_due_usd"] == 2500

    assert billing_summary["context_calls"] == 0
    assert billing_summary["proof_calls"] == 0
    assert billing_summary["billable_context_calls"] == 0
    assert billing_summary["amount_due_usd"] == 0.0
    assert billing_summary["telemetry_usage"]["constraint_pressure_calls"] == 2
    assert billing_summary["telemetry_authority"] == "non_admission_telemetry"


def test_feed_commercialization_does_not_alter_context_proof_or_reflex_memory(feed_metering_client):
    client, app_module = feed_metering_client
    context = client.get(
        "/v1/context",
        headers=_headers(),
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    ).json()
    proof_before = client.get(f"/v1/proof/{context['decision_id']}", headers=_headers()).json()
    billing_before = client.get("/v1/billing/summary", headers=_headers()).json()
    internal_telemetry_count = len(app_module.INTERNAL_TELEMETRY_ENGINE.snapshot())

    client.get("/v1/feeds/constraint_pressure", headers=_headers())
    client.get("/v1/feeds/constraint_pressure", headers=_headers())
    client.get("/v1/feeds/usage", headers=_headers())

    billing_after = client.get("/v1/billing/summary", headers=_headers()).json()
    proof_after = client.get(f"/v1/proof/{context['decision_id']}", headers=_headers()).json()

    assert context["decision_status"] == "CONSTRAIN"
    assert len(app_module.INTERNAL_TELEMETRY_ENGINE.snapshot()) == internal_telemetry_count
    assert billing_after["context_calls"] == billing_before["context_calls"]
    assert billing_after["proof_calls"] == billing_before["proof_calls"]
    assert billing_after["amount_due_usd"] == billing_before["amount_due_usd"]
    assert billing_after["telemetry_usage"]["constraint_pressure_calls"] == 2
    assert _without_signature(proof_after) == _without_signature(proof_before)
    assert "decision_status" not in client.get("/v1/feeds/usage", headers=_headers()).json()["feed_usage"]
