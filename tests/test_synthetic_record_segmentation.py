from core.reflex_governance_runtime.collector import collect_governance_record


def _record_for_owner(owner: str) -> dict:
    context_payload = {
        "decision_id": "decision-a",
        "timestamp_utc": "2026-06-11T10:00:00+00:00",
        "decision_status": "CONSTRAIN",
    }
    proof_record = {
        "decision_id": "decision-a",
        "owner": owner,
        "normalized_request": {
            "asset": "ETH",
            "intent": "risk_increasing",
            "requested_action": "trade",
        },
        "reproducibility_hash": "hash-a",
        "proof": {
            "decision_status": "CONSTRAIN",
            "intervention_type": "reduced",
            "proof": {"classification": ["market_system_risk"]},
            "validation": {"reproducibility_hash": "hash-a"},
        },
    }
    return collect_governance_record(
        context_payload=context_payload,
        proof_record=proof_record,
        account_id=owner,
    )


def test_synthetic_and_audit_records_are_segmented_by_source_type():
    assert _record_for_owner("memory-user")["record_source_type"] == "synthetic"
    assert _record_for_owner("audit-baseline-user")["record_source_type"] == "audit"
    assert _record_for_owner("internal-operator")["record_source_type"] == "internal"
    assert _record_for_owner("external-partner")["record_source_type"] == "external"
    assert _record_for_owner("prod-validation-user")["record_source_type"] == "production_like"
    assert _record_for_owner("")["record_source_type"] == "unknown"
