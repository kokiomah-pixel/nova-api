"""Controlled execution loop pilot for Sharpe Nova OS.

This pilot does not trade, route orders, or move capital. It proves that a
downstream execution surface can only simulate execution after Nova returns an
admitted decision state.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import httpx


NOVA_API_URL = os.getenv("NOVA_API_URL", "http://127.0.0.1:8000")
NOVA_API_KEY = os.getenv("NOVA_API_KEY", "mytestkey")
REQUEST_TIMEOUT_SECONDS = 20.0

ADMITTED_STATUSES = {"ALLOW", "CONSTRAIN"}
REFUSAL_STATUSES = {"DENY", "DELAY", "HALT", "VETO"}
REPORT_STATUSES = ("ALLOW", "CONSTRAIN", "DENY", "DELAY", "HALT", "VETO")

BASE_DECISIONS: List[Dict[str, Any]] = [
    {"intent": "allocate", "asset": "ETH", "size": 10000},
    {"intent": "trade", "asset": "BTC", "size": 75000, "strategy": "larger allocation"},
    {"intent": "trade", "asset": "ETH", "size": 15000, "strategy": "same-family allocation"},
    {"intent": "deploy_liquidity", "asset": "UNI", "size": 12000, "strategy": "protocol entry"},
    {
        "intent": "high_risk_allocation",
        "asset": "SOL",
        "size": 30000,
        "strategy": "high risk expansion under macro volatility",
    },
    {"intent": "increase_position", "asset": "ETH", "size": 25000, "strategy": "risk increase"},
    {"intent": "rebalance", "asset": "BTC", "size": 15000},
    {"intent": "reduce_position", "asset": "ETH", "size": 5000, "strategy": "exposure reduction"},
    {"intent": "governance_exposure", "asset": "LDO", "size": 8000, "strategy": "delegate concentration"},
    {
        "intent": "validator_staking",
        "asset": "stETH",
        "size": 18000,
        "strategy": "validator staking uptime review",
    },
]

DECISIONS: List[Dict[str, Any]] = (BASE_DECISIONS * 10)[:100]


def proposed_size(proposal: Dict[str, Any]) -> float:
    return float(proposal["size"])


def normalize_status(value: Any) -> str:
    return str(value or "UNAVAILABLE").strip().upper()


def fetch_context(
    client: httpx.Client,
    proposal: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    endpoint = f"{NOVA_API_URL.rstrip('/')}/v1/context"
    headers = {"Authorization": f"Bearer {NOVA_API_KEY}"}

    try:
        response = client.get(endpoint, headers=headers, params=proposal)
    except httpx.HTTPError as exc:
        return None, f"transport error: {exc}"

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict) and payload.get("decision_status"):
        return payload, None

    if response.is_error:
        detail = payload.get("detail") if isinstance(payload, dict) else response.text
        return None, f"HTTP {response.status_code}: {detail}"

    return None, "Nova response did not include decision_status"


def fetch_proof(
    client: httpx.Client,
    decision_id: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    endpoint = f"{NOVA_API_URL.rstrip('/')}/v1/proof/{decision_id}"
    headers = {"Authorization": f"Bearer {NOVA_API_KEY}"}

    try:
        response = client.get(endpoint, headers=headers)
    except httpx.HTTPError as exc:
        return None, f"transport error: {exc}"

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if response.is_error:
        detail = payload.get("detail") if isinstance(payload, dict) else response.text
        return None, f"HTTP {response.status_code}: {detail}"

    if not isinstance(payload, dict):
        return None, "proof response was not a JSON object"

    return payload, None


def proof_is_valid(
    proof: Dict[str, Any],
    *,
    decision_id: str,
    decision_status: str,
) -> Tuple[bool, Optional[str]]:
    required_fields = ("decision_id", "decision_status", "reproducibility_hash")
    missing = [field for field in required_fields if not proof.get(field)]
    if missing:
        return False, f"proof missing required fields: {', '.join(missing)}"

    if str(proof.get("decision_id")) != decision_id:
        return False, "proof decision_id did not match context decision_id"

    proof_status = normalize_status(proof.get("decision_status"))
    if proof_status != decision_status:
        return False, f"proof decision_status {proof_status} did not match context {decision_status}"

    return True, None


def adjusted_size_from_context(context: Dict[str, Any]) -> Optional[float]:
    impact = context.get("impact_on_outcomes")
    if not isinstance(impact, dict):
        return None

    adjusted_size = impact.get("adjusted_size")
    if adjusted_size is None:
        return None

    try:
        return float(adjusted_size)
    except (TypeError, ValueError):
        return None


def simulate_execution(
    *,
    proposal: Dict[str, Any],
    context: Dict[str, Any],
    decision_status: str,
) -> Tuple[float, Optional[str]]:
    size = proposed_size(proposal)

    if decision_status == "ALLOW":
        return size, None

    if decision_status == "CONSTRAIN":
        adjusted_size = adjusted_size_from_context(context)
        if adjusted_size is None or adjusted_size < 0:
            return 0.0, "CONSTRAIN response did not include a valid adjusted_size"
        return adjusted_size, None

    return 0.0, None


def format_amount(value: float) -> str:
    if value.is_integer():
        return f"{value:.0f}"
    return f"{value:.2f}"


def print_report(
    *,
    status_counts: Counter[str],
    total_decisions: int,
    total_proposed: float,
    total_admitted: float,
    proof_retrieved: int,
    proof_failures: int,
    bypass_count: int,
    failed_closed_count: int,
    reproducibility_hashes: List[str],
    final_pass: bool,
) -> None:
    prevented_exposure = total_proposed - total_admitted
    proof_eligible = total_decisions - failed_closed_count
    proof_coverage = 0.0 if proof_eligible <= 0 else (proof_retrieved / proof_eligible) * 100
    other_statuses = {
        status: count
        for status, count in sorted(status_counts.items())
        if status not in REPORT_STATUSES
    }

    print("CONTROLLED EXECUTION LOOP PILOT")
    print()
    print(f"Using Nova API: {NOVA_API_URL}")
    print()
    print(f"Total decisions: {total_decisions}")
    for status in REPORT_STATUSES:
        print(f"{status}: {status_counts.get(status, 0)}")
    if other_statuses:
        print(f"OTHER NON-ADMITTED: {sum(other_statuses.values())}")
        for status, count in other_statuses.items():
            print(f"{status}: {count}")
    print()
    print(f"Total proposed exposure: {format_amount(total_proposed)}")
    print(f"Total admitted exposure: {format_amount(total_admitted)}")
    print(f"Prevented exposure: {format_amount(prevented_exposure)}")
    print()
    print(f"Proof retrieved: {proof_retrieved}")
    print(f"Proof failures: {proof_failures}")
    print(f"Proof coverage: {proof_coverage:.2f}%")
    print(f"Reproducibility hashes collected: {len(reproducibility_hashes)}")
    print(f"Bypass count: {bypass_count}")
    print(f"Failed-closed count: {failed_closed_count}")
    print()
    print("FINAL DETERMINATION:")
    print("PASS" if final_pass else "FAIL")


def main() -> None:
    status_counts: Counter[str] = Counter()
    total_proposed = 0.0
    total_admitted = 0.0
    proof_retrieved = 0
    proof_failures = 0
    bypass_count = 0
    failed_closed_count = 0
    policy_violations: List[str] = []
    reproducibility_hashes: List[str] = []

    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        for index, proposal in enumerate(DECISIONS, start=1):
            total_proposed += proposed_size(proposal)
            context, context_error = fetch_context(client, proposal)

            if context is None:
                failed_closed_count += 1
                policy_violations.append(f"decision {index} failed closed: {context_error}")
                continue

            decision_status = normalize_status(context.get("decision_status"))
            status_counts[decision_status] += 1

            executed_size, execution_error = simulate_execution(
                proposal=proposal,
                context=context,
                decision_status=decision_status,
            )
            if execution_error:
                failed_closed_count += 1
                policy_violations.append(f"decision {index} failed closed: {execution_error}")
                executed_size = 0.0

            if executed_size > 0 and decision_status not in ADMITTED_STATUSES:
                bypass_count += 1
                policy_violations.append(
                    f"decision {index} executed {executed_size:g} without admission state {decision_status}"
                )

            if decision_status in REFUSAL_STATUSES and executed_size > 0:
                policy_violations.append(f"decision {index} executed during refusal state {decision_status}")

            total_admitted += executed_size

            decision_id = context.get("decision_id")
            if not decision_id:
                proof_failures += 1
                policy_violations.append(f"decision {index} missing decision_id for proof retrieval")
                continue

            proof, proof_error = fetch_proof(client, str(decision_id))
            if proof is None:
                proof_failures += 1
                policy_violations.append(f"decision {index} proof retrieval failed: {proof_error}")
                continue

            valid_proof, proof_validation_error = proof_is_valid(
                proof,
                decision_id=str(decision_id),
                decision_status=decision_status,
            )
            if not valid_proof:
                proof_failures += 1
                policy_violations.append(f"decision {index} proof validation failed: {proof_validation_error}")
                continue

            proof_retrieved += 1
            reproducibility_hashes.append(str(proof["reproducibility_hash"]))

    final_pass = (
        bypass_count == 0
        and failed_closed_count == 0
        and proof_failures == 0
        and not policy_violations
    )

    print_report(
        status_counts=status_counts,
        total_decisions=len(DECISIONS),
        total_proposed=total_proposed,
        total_admitted=total_admitted,
        proof_retrieved=proof_retrieved,
        proof_failures=proof_failures,
        bypass_count=bypass_count,
        failed_closed_count=failed_closed_count,
        reproducibility_hashes=reproducibility_hashes,
        final_pass=final_pass,
    )

    if bypass_count > 0:
        raise RuntimeError("Execution bypass detected: simulated execution occurred without Nova admission.")


if __name__ == "__main__":
    main()
