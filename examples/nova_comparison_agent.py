"""Minimal side-by-side demo: agent without Nova vs with Nova guardrails."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

import httpx


NOVA_API_URL = os.getenv("NOVA_API_URL", "https://nova-api-ipz6.onrender.com")
NOVA_API_KEY = os.getenv("NOVA_API_KEY", "nova_live_key_001")


@dataclass(frozen=True)
class Scenario:
    intent: str
    asset: str
    size: float


def run_without_nova(scenario: Scenario) -> Dict[str, str]:
    return {
        "decision": "EXECUTE",
        "result": f"{scenario.intent} executes at full size ({scenario.size:g})",
    }


def fetch_nova_context(scenario: Scenario) -> Dict[str, Any]:
    endpoint = f"{NOVA_API_URL.rstrip('/')}/v1/context"
    params = {
        "intent": scenario.intent,
        "asset": scenario.asset,
        "size": scenario.size,
    }
    headers = {"Authorization": f"Bearer {NOVA_API_KEY}"}

    with httpx.Client(timeout=20.0) as client:
        response = client.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


def is_risk_increasing_intent(intent: str) -> bool:
    return intent in {"trade", "deploy_liquidity", "open_position", "increase_position"}


def run_with_nova(scenario: Scenario) -> Dict[str, str]:
    context = fetch_nova_context(scenario)

    regime = context.get("regime", "Unknown")
    action_policy = context.get("guardrail", {}).get("action_policy", {})

    allow_new_risk = bool(action_policy.get("allow_new_risk", False))
    allow_position_increase = bool(action_policy.get("allow_position_increase", False))

    if not allow_new_risk and is_risk_increasing_intent(scenario.intent):
        decision = "VETO"
        result = "Action blocked by Nova guardrail"
    elif not allow_position_increase and is_risk_increasing_intent(scenario.intent):
        reduced_size = max(scenario.size * 0.25, 1)
        decision = "CONSTRAIN"
        result = f"{scenario.intent} executes at reduced size ({reduced_size:g} vs {scenario.size:g})"
    else:
        decision = "ALLOW"
        result = f"{scenario.intent} executes at full size ({scenario.size:g})"

    return {
        "regime": regime,
        "action_policy": json.dumps(action_policy, sort_keys=True),
        "decision": decision,
        "result": result,
    }


def print_scenario_comparison(scenario: Scenario) -> None:
    print("=" * 50)
    print(f"Scenario: {scenario.intent} | {scenario.asset} | {scenario.size:g}")
    print()

    without_nova = run_without_nova(scenario)
    print("WITHOUT NOVA")
    print(f"Decision: {without_nova['decision']}")
    print(f"Result: {without_nova['result']}")
    print()

    print("WITH NOVA")
    try:
        with_nova = run_with_nova(scenario)
        print(f"Regime: {with_nova['regime']}")
        print(f"Action Policy: {with_nova['action_policy']}")
        print(f"Decision: {with_nova['decision']}")
        print(f"Result: {with_nova['result']}")
    except Exception as exc:
        # Fail-safe behavior is explicit so demo output stays understandable.
        print("Regime: Unknown")
        print("Action Policy: unavailable")
        print("Decision: VETO")
        print(f"Result: Failed to fetch Nova context ({exc})")

    print("=" * 50)


def main() -> None:
    scenarios: List[Scenario] = [
        Scenario("trade", "ETH", 10000),
        Scenario("trade", "BTC", 50000),
        Scenario("deploy_liquidity", "ETH", 20000),
        Scenario("trade", "ETH", 500),
    ]

    for scenario in scenarios:
        print_scenario_comparison(scenario)
        print()


if __name__ == "__main__":
    main()
