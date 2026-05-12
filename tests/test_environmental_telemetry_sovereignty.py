import importlib
import json
import os
import sys
from typing import Any, Dict, Set

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from core.feed_metering import reset_feed_usage_state_for_tests
from examples.controlled_execution_loop import simulate_execution


SOVEREIGNTY_TEST_KEY = "environmental-sovereignty-key"
SOVEREIGNTY_TEST_KEYS = {
    SOVEREIGNTY_TEST_KEY: {
        "owner": "environmental-sovereignty-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 500,
        "allowed_endpoints": [
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/billing/summary",
            "/v1/feeds/constraint_pressure",
            "/v1/feeds/usage",
            "/v1/key-info",
            "/v1/usage",
        ],
    },
}

PROTECTED_PUBLIC_FEED_KEYS = {
    "decision_id",
    "request_id",
    "actor_id",
    "api_key",
    "owner",
    "decision_status",
    "decision_admission_record",
    "request_snapshot",
    "raw_decision_logs",
    "reflex_memory",
    "reflex_memory_class",
    "proof",
    "constraint_trace",
    "constraint_analysis",
    "impact_on_outcomes",
    "adjustment",
    "exception_register",
    "rejection_ledger",
    "reason",
    "why_this_happened",
    "deny_reason",
    "deny_probability",
    "recommended_action",
    "policy",
    "policy_weight",
    "policy_weights",
    "threshold",
    "thresholds",
    "constraint_weight",
    "admissibility_delta",
    "decision_divergence_score",
    "minimum_required_reliability",
    "telemetry_reliability_score",
    "causal_explanation",
    "admission_logic",
}
ADMISSION_STATUSES = {"ALLOW", "CONSTRAIN", "DENY", "DELAY", "HALT", "VETO", "REDUCE"}


@pytest.fixture
def sovereignty_client():
    keys_json = json.dumps(SOVEREIGNTY_TEST_KEYS)
    test_files = [
        ".usage.environmental-sovereignty-test.json",
        ".usage_state.environmental-sovereignty-test.json",
        ".billing_state.environmental-sovereignty-test.json",
        ".feed_usage.environmental-sovereignty-test.json",
        ".proof.environmental-sovereignty-test.json",
        "proof_retrieval_audit.environmental-sovereignty-test.jsonl",
        ".reflex_governance_records.environmental-sovereignty-test.jsonl",
        ".reflex_governance_signals.environmental-sovereignty-test.json",
        ".reflex_governance_escalations.environmental-sovereignty-test.json",
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
        for module_name in ["app", "core.usage_meter", "core.billing_state"]:
            sys.modules.pop(module_name, None)
        app_module = importlib.import_module("app")
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        reset_feed_usage_state_for_tests()
        yield TestClient(app_module.app), app_module
        app_module.USAGE_TRACKING.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.INTERNAL_TELEMETRY_ENGINE.clear()
        app_module.PROOF_REGISTRY.clear()
        app_module.REFLEX_GOVERNANCE_RECORDS.clear()
        app_module.decision_usage_meter.reset_usage_state_for_tests()
        app_module.usdc_billing_state.reset_billing_state_for_tests()
        reset_feed_usage_state_for_tests()
        for path in test_files:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def _headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {SOVEREIGNTY_TEST_KEY}"}


def _context(client: TestClient, **params: Any) -> Dict[str, Any]:
    response = client.get("/v1/context", headers=_headers(), params=params)
    assert response.status_code == 200
    return response.json()


def _feed(client: TestClient) -> Dict[str, Any]:
    response = client.get("/v1/feeds/constraint_pressure", headers=_headers())
    assert response.status_code == 200
    return response.json()


def _proof(client: TestClient, decision_id: str) -> Dict[str, Any]:
    response = client.get(f"/v1/proof/{decision_id}", headers=_headers())
    assert response.status_code == 200
    return response.json()


def _billing_summary(client: TestClient) -> Dict[str, Any]:
    response = client.get("/v1/billing/summary", headers=_headers())
    assert response.status_code == 200
    return response.json()


def _collect_keys(value: Any) -> Set[str]:
    if isinstance(value, dict):
        keys = set(value.keys())
        for nested in value.values():
            keys.update(_collect_keys(nested))
        return keys
    if isinstance(value, list):
        keys: Set[str] = set()
        for item in value:
            keys.update(_collect_keys(item))
        return keys
    return set()


def _collect_scalar_values(value: Any) -> Set[str]:
    if isinstance(value, dict):
        values: Set[str] = set()
        for nested in value.values():
            values.update(_collect_scalar_values(nested))
        return values
    if isinstance(value, list):
        values = set()
        for item in value:
            values.update(_collect_scalar_values(item))
        return values
    if value is None:
        return set()
    return {str(value)}


def _public_feed_without_signature(feed: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in feed.items() if key != "signature"}


def _sovereign_billing_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    fields = {
        "actor_id",
        "billing_mode",
        "context_calls",
        "proof_calls",
        "free_context_call_limit",
        "billable_context_calls",
        "price_per_decision_usd",
        "amount_due_usd",
        "payment_destination",
    }
    return {key: payload[key] for key in fields}


def test_constraint_pressure_feed_preserves_sovereignty_boundary(sovereignty_client):
    client, _ = sovereignty_client
    denied_context = _context(client, intent="trade", asset="ETH", size=300000)
    feed = _feed(client)

    public_keys = _collect_keys(feed)
    leaked_keys = PROTECTED_PUBLIC_FEED_KEYS.intersection(public_keys)
    assert leaked_keys == set()

    public_values = _collect_scalar_values(feed)
    decision_id = str(denied_context["decision_id"])
    request_id = str(denied_context["decision_admission_record"]["request_id"])
    assert decision_id not in public_values
    assert request_id not in public_values
    assert denied_context["adjustment"] not in public_values
    assert denied_context["constraint_analysis"]["why_this_happened"] not in public_values
    assert "guardrail_veto" not in public_values


def test_feed_schema_keeps_marketplace_semantics_stable(sovereignty_client):
    client, _ = sovereignty_client
    feed = _feed(client)

    assert feed["feed_name"] == "Nova Constraint Pressure"
    assert feed["feed_type"] == "environmental_conditioning"
    assert feed["authority_layer"] == "non_admission_telemetry"
    assert feed["runtime_role"] == "execution_posture_conditioning"
    assert feed["feed_authority"] == "non_admission_telemetry"
    assert feed["sovereign_admission_required"] is True
    assert feed["source_layer"] == "derived_environmental_state"
    assert feed["machine_consumable"] is True
    assert feed["mcp_compatible"] is True
    assert feed["x402_ready"] is True
    assert feed["agentic_market_ready"] is True
    assert feed["non_substitution_rule"] == "telemetry_informs_posture_only"
    assert feed["pricing_model"] == "subscription_plus_volume"
    assert feed["cadence_tier"] == "developer"
    assert isinstance(feed["allow_rate"], float)
    assert isinstance(feed["constrain_rate"], float)
    assert isinstance(feed["deny_rate"], float)
    assert isinstance(feed["pressure_score"], float)


def test_feed_cannot_substitute_for_context_admission(sovereignty_client):
    client, _ = sovereignty_client
    _context(client, intent="trade", asset="ETH", size=10000)
    feed = _feed(client)

    assert feed["constraint_pressure"] in {"QUIET", "RISING", "ELEVATED", "CONSTRAINED"}
    assert feed["constraint_pressure"] not in ADMISSION_STATUSES
    assert "decision_status" not in feed
    assert "admitted" not in feed
    assert "admissible" not in feed
    assert "permission" not in feed
    assert feed["sovereign_admission_required"] is True

    non_compliant_actor_would_execute = feed["constraint_pressure"] != "HIGH"
    assert non_compliant_actor_would_execute is True

    authoritative_context = _context(client, intent="trade", asset="ETH", size=300000)
    assert authoritative_context["decision_status"] == "VETO"


def test_feed_does_not_mutate_context_proof_billing_or_controlled_loop_contracts(sovereignty_client):
    client, _ = sovereignty_client
    constrained_context = _context(client, intent="trade", asset="ETH", size=10000)
    assert constrained_context["decision_status"] == "CONSTRAIN"

    decision_id = constrained_context["decision_id"]
    proof_before = _proof(client, decision_id)
    billing_before = _billing_summary(client)

    for _ in range(5):
        feed = _feed(client)
        assert feed["sovereign_admission_required"] is True

    billing_after = _billing_summary(client)
    proof_after = _proof(client, decision_id)
    repeated_context = _context(client, intent="trade", asset="ETH", size=10000)

    assert _sovereign_billing_fields(billing_after) == _sovereign_billing_fields(billing_before)
    assert billing_before["telemetry_usage"]["constraint_pressure_calls"] == 0
    assert billing_after["telemetry_usage"]["constraint_pressure_calls"] == 5
    assert _public_feed_without_signature(proof_after) == _public_feed_without_signature(proof_before)
    assert repeated_context["decision_status"] == constrained_context["decision_status"]
    assert repeated_context["impact_on_outcomes"]["adjusted_size"] == constrained_context["impact_on_outcomes"]["adjusted_size"]

    executed_size, execution_error = simulate_execution(
        proposal={"intent": "trade", "asset": "ETH", "size": 10000},
        context=constrained_context,
        decision_status=constrained_context["decision_status"],
    )
    assert execution_error is None
    assert executed_size == constrained_context["impact_on_outcomes"]["adjusted_size"]


def test_feed_moves_from_aggregate_state_not_single_decision_leakage(sovereignty_client):
    client, _ = sovereignty_client
    proposals = []
    for index in range(59):
        phase = index % 4
        if phase == 0:
            proposals.append({"intent": "allocate", "asset": "ETH", "size": 10000 + index})
        elif phase == 1:
            proposals.append({"intent": "trade", "asset": "ETH", "size": 10000 + index})
        elif phase == 2:
            proposals.append({"intent": "reduce_position", "asset": "ETH", "size": 5000 + index})
        else:
            proposals.append({"intent": "trade", "asset": "ETH", "size": 300000 + index})

    for proposal in proposals:
        _context(client, **proposal)

    feed_before = _feed(client)
    final_context = _context(client, intent="trade", asset="ETH", size=350000)
    feed_after = _feed(client)

    assert final_context["decision_status"] == "VETO"
    assert abs(feed_after["deny_rate"] - feed_before["deny_rate"]) <= 0.02
    assert abs(feed_after["allow_rate"] - feed_before["allow_rate"]) <= 0.02
    assert abs(feed_after["constrain_rate"] - feed_before["constrain_rate"]) <= 0.02
    assert abs(feed_after["pressure_score"] - feed_before["pressure_score"]) <= 0.08

    feed_values = _collect_scalar_values(feed_after)
    assert str(final_context["decision_id"]) not in feed_values
    assert str(final_context["decision_admission_record"]["request_id"]) not in feed_values
    assert final_context["constraint_analysis"]["why_this_happened"] not in feed_values
