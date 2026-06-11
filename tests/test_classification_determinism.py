import json

import app as app_module
from core.governance_identity import UNCLASSIFIED_GOVERNANCE_EVENT, compute_canonical_signature


def test_identical_normalized_inputs_produce_stable_signature_classification_and_domain_trace():
    first = {"requested_action": " Trade ", "asset": " eth ", "intent": " RISK_INCREASING "}
    second = {"intent": "risk_increasing", "requested_action": "trade", "asset": "ETH"}

    assert compute_canonical_signature(first) == compute_canonical_signature(second)

    payload = {
        "decision_status": "CONSTRAIN",
        "decision_context": {"intent": "trade", "asset": "ETH"},
        "constraint_analysis": {"constraint_category": "permission_budgeting"},
        "constraint_trace": {"telemetry_domain": "decision_telemetry"},
    }
    classifications = [app_module._classify_proof(dict(payload)) for _ in range(5)]
    assert classifications == [["market_system_risk"]] * 5

    traces = [
        app_module._infer_domain_trace(
            api_key="determinism-key",
            intent="trade",
            asset="USDC",
            venue="thin_order_book",
            strategy="validator uptime risk with stablecoin peg pressure and volatility",
            decision_status="CONSTRAIN",
            guardrail={"advisory": "liquidity fragility present"},
        )
        for _ in range(5)
    ]
    assert traces == [traces[0]] * 5
    assert traces[0]["constraint_category"] == "stablecoin"
    assert traces[0]["telemetry_domain"] == "stablecoin_telemetry"


def test_classification_fallback_is_explicit_for_ambiguous_allow_payload():
    payload = {
        "decision_status": "ALLOW",
        "decision_context": {"intent": "unknown_action", "asset": "UNKNOWN"},
        "constraint_analysis": {},
        "constraint_trace": {},
    }

    assert app_module._classify_proof(payload) == [UNCLASSIFIED_GOVERNANCE_EVENT]


def test_canonical_signature_uses_stable_json_serialization():
    signature = compute_canonical_signature(
        {"requested_action": "TRADE", "intent": "Risk Increasing", "asset": " eth "}
    )

    assert signature == '{"asset":"ETH","intent":"risk increasing","requested_action":"trade"}'
    assert json.loads(signature) == {
        "asset": "ETH",
        "intent": "risk increasing",
        "requested_action": "trade",
    }
