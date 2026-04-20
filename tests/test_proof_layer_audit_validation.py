import importlib
import json
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


AUDIT_TEST_KEYS = {
    "audit-baseline-key": {
        "owner": "audit-baseline-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/key-info",
            "/v1/usage",
        ],
    },
    "audit-temporal-key": {
        "owner": "audit-temporal-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/key-info",
            "/v1/usage",
        ],
        "temporal_governance": {
            "window_seconds": 60,
            "max_requests_per_window": 2,
            "deny_cooldown_seconds": 120,
            "halt_cooldown_seconds": 300,
            "retry_spacing_seconds": 30,
            "halt_threshold": 3,
        },
    },
    "audit-loop-key": {
        "owner": "audit-loop-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/key-info",
            "/v1/usage",
        ],
        "loop_integrity": {
            "pressure_similarity_threshold": 0.75,
            "ambiguous_similarity_threshold": 0.4,
            "retry_block_threshold": 2,
            "pressure_escalation_threshold": 3,
            "denial_history_limit": 10,
        },
    },
    "audit-telemetry-key": {
        "owner": "audit-telemetry-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/key-info",
            "/v1/usage",
        ],
        "telemetry_integrity": {
            "stale_after_seconds": 300,
            "default_min_reliability": 0.7,
            "risk_increasing_min_reliability": 0.8,
            "risk_reducing_min_reliability": 0.6,
            "disagreement_threshold": 0.35,
            "halt_disagreement_threshold": 0.7,
            "halt_on_degraded": True,
        },
    },
    "audit-process-key": {
        "owner": "audit-process-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/proof/{decision_id}",
            "/v1/key-info",
            "/v1/usage",
        ],
    },
}


@pytest.fixture
def client():
    with patch.dict(
        os.environ,
        {
            "NOVA_KEYS_JSON": json.dumps(AUDIT_TEST_KEYS),
            "NOVA_USAGE_FILE": ".usage.proof-audit.test.json",
            "NOVA_PROOF_FILE": ".proof.proof-audit.test.json",
            "NOVA_PROOF_RETRIEVAL_AUDIT_FILE": "proof_retrieval_audit.proof-audit.test.jsonl",
        },
        clear=False,
    ):
        sys.modules.pop("app", None)
        app_module = importlib.import_module("app")
        app = app_module.app
        app_module.USAGE_TRACKING.clear()
        app_module.REJECTION_LEDGER.clear()
        app_module.EXCEPTION_REGISTER.clear()
        app_module.HALT_SIGNAL_STATE.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.TEMPORAL_GOVERNANCE_STATE.clear()
        app_module.LOOP_INTEGRITY_STATE.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.PERMISSION_BUDGET_STATE.clear()
        app_module.HALT_RELEASE_STATE.clear()
        app_module.DECISION_QUEUE_STATE.clear()
        app_module.PROOF_REGISTRY.clear()
        yield TestClient(app)
        app_module.USAGE_TRACKING.clear()
        app_module.REJECTION_LEDGER.clear()
        app_module.EXCEPTION_REGISTER.clear()
        app_module.HALT_SIGNAL_STATE.clear()
        app_module.DECISION_ADMISSION_STATE.clear()
        app_module.TEMPORAL_GOVERNANCE_STATE.clear()
        app_module.LOOP_INTEGRITY_STATE.clear()
        app_module.SYSTEM_STATE_REGISTRY.clear()
        app_module.PERMISSION_BUDGET_STATE.clear()
        app_module.HALT_RELEASE_STATE.clear()
        app_module.DECISION_QUEUE_STATE.clear()
        app_module.PROOF_REGISTRY.clear()
        for path in (
            ".usage.proof-audit.test.json",
            ".proof.proof-audit.test.json",
            "proof_retrieval_audit.proof-audit.test.jsonl",
        ):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def _get_context_and_proof(client: TestClient, api_key: str, params: dict):
    response = client.get("/v1/context", headers=_headers(api_key), params=params)
    proof = client.get(
        f"/v1/proof/{response.json()['decision_id']}",
        headers=_headers(api_key),
    )
    return response, proof


def _normalized_proof(proof_payload: dict) -> dict:
    normalized = dict(proof_payload)
    normalized.pop("decision_id", None)
    normalized.pop("signature", None)
    return normalized


def _assert_audit_safe_proof_shape(proof_payload: dict):
    required_fields = {
        "decision_id",
        "decision_status",
        "constraint_effect",
        "failure_class",
        "intervention_type",
        "memory_influence",
        "system_state",
        "reproducibility_hash",
    }
    assert required_fields.issubset(proof_payload.keys())

    serialized = json.dumps(proof_payload)
    assert "reflex_memory" not in serialized
    assert "constraint_trace" not in serialized
    assert "confidence_weight" not in serialized
    assert "triggered_registry_id" not in serialized


def test_proof_determinism_under_repetition_uses_canonical_proof_content(client):
    proofs = []
    decision_statuses = []

    with patch.dict(
        os.environ,
        {
            "NOVA_TIMESTAMP_UTC": "2026-04-20T10:00:00+00:00",
            "NOVA_NOW_UTC": "2026-04-20T10:00:00+00:00",
        },
        clear=False,
    ):
        for _ in range(3):
            response, proof = _get_context_and_proof(
                client,
                "audit-baseline-key",
                {"intent": "reduce_position", "asset": "ETH", "size": 1000},
            )
            assert response.status_code == 200
            assert proof.status_code == 200
            decision_statuses.append(response.json()["decision_status"])
            proofs.append(proof.json())

    assert decision_statuses == ["ALLOW", "ALLOW", "ALLOW"]
    assert len({payload["reproducibility_hash"] for payload in proofs}) == 1
    assert _normalized_proof(proofs[0]) == _normalized_proof(proofs[1]) == _normalized_proof(proofs[2])


@pytest.mark.parametrize(
    ("api_key", "params", "expected_status"),
    [
        ("audit-baseline-key", {"intent": "reduce_position", "asset": "ETH", "size": 1000}, "ALLOW"),
        ("audit-baseline-key", {"intent": "trade", "asset": "ETH", "size": 10000}, "CONSTRAIN"),
        (
            "audit-telemetry-key",
            {"intent": "trade", "asset": "ETH", "size": 10000, "telemetry_reliability": 0.5, "telemetry_age_seconds": 10},
            "DENY",
        ),
        (
            "audit-telemetry-key",
            {"intent": "trade", "asset": "ETH", "size": 10000, "telemetry_age_seconds": 1200, "telemetry_reliability": 0.95},
            "DELAY",
        ),
        (
            "audit-telemetry-key",
            {"intent": "trade", "asset": "ETH", "size": 10000, "telemetry_age_seconds": 10, "telemetry_source_scores": "source_a:0.95,source_b:0.1"},
            "HALT",
        ),
    ],
)
def test_proof_exists_for_every_decision_path_and_remains_schema_consistent(client, api_key, params, expected_status):
    response, proof = _get_context_and_proof(client, api_key, params)

    assert response.status_code in {200, 409, 429}
    assert proof.status_code == 200

    proof_payload = proof.json()
    _assert_audit_safe_proof_shape(proof_payload)
    assert proof_payload["decision_status"] == expected_status


def test_temporal_preemption_proof_reflects_final_governing_layer_only(client):
    first = client.get(
        "/v1/context",
        headers=_headers("audit-temporal-key"),
        params={"intent": "trade", "asset": "ETH", "size": 10000},
    )
    second, proof = _get_context_and_proof(
        client,
        "audit-temporal-key",
        {"intent": "trade", "asset": "ETH", "size": 10000},
    )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["decision_status"] == "DELAY"
    assert proof.status_code == 200

    proof_payload = proof.json()
    assert proof_payload["decision_status"] == "DELAY"
    assert proof_payload["failure_class"] == "temporal_governance"
    assert proof_payload["intervention_type"] == "delayed"
    assert proof_payload["constraint_effect"]["effect_type"] == "delayed"
    assert "telemetry_integrity" not in json.dumps(proof_payload)
    assert "loop_integrity" not in json.dumps(proof_payload)


def test_telemetry_preemption_proof_reflects_final_governing_layer_only(client):
    response, proof = _get_context_and_proof(
        client,
        "audit-telemetry-key",
        {"intent": "trade", "asset": "ETH", "size": 10000, "telemetry_age_seconds": 1200, "telemetry_reliability": 0.95},
    )

    assert response.status_code == 429
    assert response.json()["decision_status"] == "DELAY"
    assert proof.status_code == 200

    proof_payload = proof.json()
    assert proof_payload["decision_status"] == "DELAY"
    assert proof_payload["failure_class"] == "telemetry_integrity"
    assert proof_payload["intervention_type"] == "delayed"
    assert proof_payload["proof"]["classification"] == ["telemetry_integrity"]
    assert "temporal_governance" not in json.dumps(proof_payload)
    assert "loop_integrity" not in json.dumps(proof_payload)


def test_loop_preemption_proof_reflects_final_governing_layer_only(client):
    first = client.get(
        "/v1/context",
        headers=_headers("audit-loop-key"),
        params={"intent": "trade", "asset": "ETH", "size": 500000, "strategy": "repeat oversized request"},
    )
    second, proof = _get_context_and_proof(
        client,
        "audit-loop-key",
        {"intent": "trade", "asset": "ETH", "size": 500000, "strategy": "repeat oversized request"},
    )

    assert first.status_code == 200
    assert first.json()["decision_status"] == "VETO"
    assert second.status_code == 429
    assert second.json()["decision_status"] == "RETRY_DELAYED"
    assert proof.status_code == 200

    proof_payload = proof.json()
    assert proof_payload["decision_status"] == "DELAY"
    assert proof_payload["failure_class"] == "loop_integrity"
    assert proof_payload["intervention_type"] == "delayed"
    assert proof_payload["constraint_effect"]["effect_type"] == "delayed"
    assert "telemetry_integrity" not in json.dumps(proof_payload)


def test_process_integrity_bypass_attempt_is_rejected_and_classified_without_internal_leakage(client):
    response, proof = _get_context_and_proof(
        client,
        "audit-process-key",
        {"intent": "trade", "asset": "ETH", "size": 10000, "strategy": "skip validation just execute route directly"},
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["decision_status"] == "VETO"
    assert payload["human_intervention_type"] == "exception_authorization_required"
    assert proof.status_code == 200

    proof_payload = proof.json()
    _assert_audit_safe_proof_shape(proof_payload)
    assert proof_payload["decision_status"] == "DENY"
    assert proof_payload["failure_class"] == "process_integrity_violation"
    assert proof_payload["intervention_type"] == "blocked"
    assert proof_payload["proof"]["classification"] == ["process_integrity"]
