import app as app_module


def _proof_input(**overrides):
    payload = {
        "timestamp_utc": "2026-06-11T10:00:00+00:00",
        "decision_id": "runtime-id-a",
        "decision_status": "CONSTRAIN",
        "system_state": "PRESSURE_ELEVATED",
        "decision_context": {
            "asset": " ETH ",
            "intent": "trade",
        },
        "constraint_analysis": {
            "constraint_category": "permission_budgeting",
        },
        "constraint_trace": {
            "telemetry_domain": "decision_telemetry",
        },
        "impact_on_outcomes": {
            "adjusted_size": 4000,
        },
    }
    payload.update(overrides)
    return payload


def test_identical_proof_inputs_with_reordered_runtime_metadata_produce_identical_hashes():
    first = app_module._build_proof_payload(_proof_input())
    second = app_module._build_proof_payload(
        _proof_input(
            timestamp_utc="2026-06-11T11:15:00+00:00",
            decision_id="runtime-id-b",
        )
    )

    assert first["validation"]["reproducibility_hash"] == second["validation"]["reproducibility_hash"]
    assert first["reproducibility_hash"] == second["reproducibility_hash"]
    assert first["proof"]["classification"] == second["proof"]["classification"]
    assert first["decision_context"] == second["decision_context"]


def test_reordered_proof_input_dicts_keep_same_reproducibility_hash():
    first_payload = _proof_input()
    second_payload = {
        "impact_on_outcomes": {"adjusted_size": 4000},
        "constraint_trace": {"telemetry_domain": "decision_telemetry"},
        "constraint_analysis": {"constraint_category": "permission_budgeting"},
        "decision_context": {"intent": "trade", "asset": "ETH"},
        "system_state": "PRESSURE_ELEVATED",
        "decision_status": "CONSTRAIN",
        "decision_id": "runtime-id-c",
        "timestamp_utc": "2026-06-12T00:00:00+00:00",
    }

    first = app_module._build_proof_payload(first_payload)
    second = app_module._build_proof_payload(second_payload)

    assert first["validation"]["reproducibility_hash"] == second["validation"]["reproducibility_hash"]
