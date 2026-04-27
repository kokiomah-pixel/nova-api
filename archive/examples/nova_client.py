"""Minimal Nova client wrapper for pre-execution decision gating."""

from __future__ import annotations

import os
from typing import Any, Dict

import httpx


DEFAULT_API_URL = os.getenv("NOVA_API_URL", "https://nova-api-ipz6.onrender.com")
DEFAULT_API_KEY = os.getenv("NOVA_API_KEY", "")

RISK_INCREASING_INTENTS = {
    "trade",
    "deploy_liquidity",
    "open_position",
    "increase_position",
}


def get_nova_context(
    intent: str,
    asset: str,
    size: float,
    api_url: str | None = None,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Call /v1/context and return the admission fields needed by integrators."""
    resolved_url = (api_url or DEFAULT_API_URL).rstrip("/")
    resolved_key = api_key if api_key is not None else DEFAULT_API_KEY

    if not resolved_key:
        raise ValueError("Missing API key. Set NOVA_API_KEY or pass api_key.")

    endpoint = f"{resolved_url}/v1/context"
    headers = {"Authorization": f"Bearer {resolved_key}"}
    params = {"intent": intent, "asset": asset, "size": size}

    with httpx.Client(timeout=20.0) as client:
        response = client.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()

    regime = payload.get("regime", "Unknown")
    action_policy = payload.get("guardrail", {}).get("action_policy", {})
    return {
        "regime": regime,
        "action_policy": action_policy,
        "timestamp_utc": payload.get("timestamp_utc"),
        "decision_status": payload.get("decision_status"),
        "decision_id": payload.get("decision_id"),
        "system_state": payload.get("system_state"),
        "raw": payload,
    }


def get_nova_proof(
    decision_id: str,
    api_url: str | None = None,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Call /v1/proof/{decision_id} and return the authoritative proof surface."""
    resolved_url = (api_url or DEFAULT_API_URL).rstrip("/")
    resolved_key = api_key if api_key is not None else DEFAULT_API_KEY

    if not resolved_key:
        raise ValueError("Missing API key. Set NOVA_API_KEY or pass api_key.")

    endpoint = f"{resolved_url}/v1/proof/{decision_id}"
    headers = {"Authorization": f"Bearer {resolved_key}"}

    with httpx.Client(timeout=20.0) as client:
        response = client.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()


# External execution check — remains independent of strategy logic
def get_nova_decision(
    intent: str,
    asset: str,
    size: float,
    api_url: str | None = None,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Derive a top-level Nova decision and bind it to proof."""
    context = get_nova_context(
        intent=intent,
        asset=asset,
        size=size,
        api_url=api_url,
        api_key=api_key,
    )

    action_policy = context["action_policy"]
    decision = context.get("decision_status") or "ALLOW"
    if decision == "VETO":
        reason = "new risk not allowed"
    elif decision == "CONSTRAIN":
        reason = "decision conditioned before capital movement"
    else:
        reason = "execution validated"

    proof = get_nova_proof(
        decision_id=context["decision_id"],
        api_url=api_url,
        api_key=api_key,
    )

    return {
        "decision": decision,
        "regime": context["regime"],
        "action_policy": action_policy,
        "timestamp_utc": context.get("timestamp_utc"),
        "decision_id": context.get("decision_id"),
        "system_state": context.get("system_state"),
        "constraint_effect": proof.get("constraint_effect"),
        "intervention_type": proof.get("intervention_type"),
        "failure_class": proof.get("failure_class"),
        "reproducibility_hash": proof.get("reproducibility_hash"),
        "reason": reason,
    }


if __name__ == "__main__":  # Minimal pre-execution gate
    decision = get_nova_decision(intent="trade", asset="ETH", size=10000)
    print(f"timestamp: {decision['timestamp_utc']}")
    print(f"regime: {decision['regime']}")
    print(f"decision: {decision['decision']}")
    print(f"decision_id: {decision['decision_id']}")
    print(f"system_state: {decision['system_state']}")
    print(f"reason: {decision['reason']}")
    print(f"constraint_effect: {decision['constraint_effect']}")
    print(f"intervention_type: {decision['intervention_type']}")
