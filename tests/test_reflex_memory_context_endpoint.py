import importlib
import json
import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


TEST_KEYS = {
    "reflex-context-key": {
        "owner": "reflex-context-user",
        "tier": "pro",
        "status": "active",
        "monthly_quota": 100,
        "allowed_endpoints": [
            "/v1/regime",
            "/v1/epoch",
            "/v1/context",
            "/v1/key-info",
            "/v1/usage",
        ],
    },
}


@pytest.fixture
def reflex_context_client():
    keys_json = json.dumps(TEST_KEYS)
    with patch.dict(os.environ, {"NOVA_KEYS_JSON": keys_json, "NOVA_USAGE_FILE": ".usage.reflex-context.test.json"}):
        sys.modules.pop("app", None)
        app_module = importlib.import_module("app")
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
        yield TestClient(app_module.app)
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
        try:
            os.remove(".usage.reflex-context.test.json")
        except FileNotFoundError:
            pass


def _headers() -> dict:
    return {"Authorization": "Bearer reflex-context-key"}


def test_context_endpoint_includes_reflex_memory_context(reflex_context_client) -> None:
    response = reflex_context_client.get(
        "/v1/context",
        headers=_headers(),
        params={"intent": "allocate", "asset": "ETH", "size": "10000"},
    )
    assert response.status_code == 200

    payload = response.json()
    reflex_context = payload["reflex_memory_context"]

    assert reflex_context["present"] is True
    assert reflex_context["version"] == "reflex_memory_v0_1"

    by_id = {entry["reflex_id"]: entry for entry in reflex_context["entries"]}
    assert by_id["RM-0001"]["review_posture_effect"] == "require_source_reconciliation_context"
    assert by_id["RM-0001"]["authority_effect"] == "none"


def test_context_endpoint_preserves_non_authority_boundary(reflex_context_client) -> None:
    response = reflex_context_client.get(
        "/v1/context",
        headers=_headers(),
        params={"intent": "allocate", "asset": "ETH", "size": "10000"},
    )
    assert response.status_code == 200

    payload = response.json()

    assert payload["local_authority"]["nova_authority"] == "none"
    assert payload["canonical_boundary"] == [
        "Agent prepares action.",
        "Nova structures review context.",
        "Local authority decides.",
        "Nova does not execute.",
    ]
