import importlib
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure the repo root is on sys.path so we can import the app module
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _make_client(tmp_path, env: dict):
    # Ensure environment is clean & deterministic for each test
    # Remove any known vars that may have been set by previous tests
    for key in [
        "NOVA_API_KEY",
        "NOVA_KEYS_JSON",
        "NOVA_USAGE_FILE",
        "NOVA_REDIS_URL",
    ]:
        os.environ.pop(key, None)

    os.environ.update(env)

    # Reload app module after environment changes so config is applied
    import app
    importlib.reload(app)

    return TestClient(app.app)


def test_health_endpoint():
    client = _make_client(tmp_path=None, env={"NOVA_API_KEY": "mytestkey"})
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_protected_endpoints_require_bearer():
    client = _make_client(tmp_path=None, env={"NOVA_API_KEY": "mytestkey"})
    r = client.get("/v1/regime")
    assert r.status_code == 401


def test_invalid_key_is_rejected():
    client = _make_client(tmp_path=None, env={"NOVA_API_KEY": "mytestkey"})
    r = client.get("/v1/regime", headers={"Authorization": "Bearer bad"})
    assert r.status_code == 403


def test_billable_endpoints_increment_usage(tmp_path):
    key_data = {
        "billable_user": {
            "owner": "test",
            "tier": "standard",
            "status": "active",
            "monthly_quota": 1000,
            "allowed_endpoints": [
                "/v1/regime",
                "/v1/epoch",
                "/v1/context",
                "/v1/key-info",
                "/v1/usage",
            ],
        }
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_USAGE_FILE": str(tmp_path / "usage_billable.json"),
        },
    )

    # Initial usage baseline
    r0 = client.get("/v1/usage", headers={"Authorization": "Bearer billable_user"})
    assert r0.status_code == 200
    baseline = r0.json()["usage"]["total_calls"]

    # Call each billable endpoint once
    client.get("/v1/regime", headers={"Authorization": "Bearer billable_user"})
    client.get("/v1/epoch", headers={"Authorization": "Bearer billable_user"})
    client.get("/v1/context", headers={"Authorization": "Bearer billable_user"})

    # Usage should increase by 3 calls (non-billable endpoints should not count)
    r1 = client.get("/v1/usage", headers={"Authorization": "Bearer billable_user"})
    assert r1.status_code == 200
    assert r1.json()["usage"]["total_calls"] == baseline + 3


def test_non_billable_endpoints_do_not_increment_usage(tmp_path):
    key_data = {
        "introspect_user": {
            "owner": "test",
            "tier": "standard",
            "status": "active",
            "monthly_quota": 1000,
            "allowed_endpoints": [
                "/v1/regime",
                "/v1/key-info",
                "/v1/usage",
            ],
        }
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_USAGE_FILE": str(tmp_path / "usage_nonbillable.json"),
        },
    )

    # Baseline usage
    r0 = client.get("/v1/usage", headers={"Authorization": "Bearer introspect_user"})
    assert r0.status_code == 200
    baseline = r0.json()["usage"]["total_calls"]

    # Non-billable call should not increase usage
    client.get("/v1/key-info", headers={"Authorization": "Bearer introspect_user"})

    r1 = client.get("/v1/usage", headers={"Authorization": "Bearer introspect_user"})
    assert r1.status_code == 200
    assert r1.json()["usage"]["total_calls"] == baseline


def test_usage_reset_is_admin_only(tmp_path):
    key_data = {
        "free_user": {
            "owner": "test",
            "tier": "standard",
            "status": "active",
            "monthly_quota": 1000,
            "allowed_endpoints": [
                "/v1/regime",
                "/v1/key-info",
                "/v1/usage",
            ],
        },
        "admin_user": {
            "owner": "test",
            "tier": "admin",
            "status": "active",
            "monthly_quota": 1000,
            "allowed_endpoints": [
                "/v1/regime",
                "/v1/key-info",
                "/v1/usage",
                "/v1/usage/reset",
            ],
        },
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_USAGE_FILE": str(tmp_path / "usage_reset.json"),
        },
    )

    # Free tier cannot reset
    r_free = client.post("/v1/usage/reset", headers={"Authorization": "Bearer free_user"})
    assert r_free.status_code == 403

    # Admin can reset
    r_admin = client.post("/v1/usage/reset", headers={"Authorization": "Bearer admin_user"})
    assert r_admin.status_code == 200


def test_monthly_quota_enforced(tmp_path):
    # Create a key that only allows 1 billable call per month but can still query key-info
    key_data = {
        "quota_user": {
            "owner": "test",
            "tier": "standard",
            "status": "active",
            "monthly_quota": 1,
            "allowed_endpoints": ["/v1/regime", "/v1/key-info"],
        }
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_USAGE_FILE": str(tmp_path / "usage_quota.json"),
        },
    )

    # Non-billable endpoint should not count towards quota
    r0 = client.get("/v1/key-info", headers={"Authorization": "Bearer quota_user"})
    assert r0.status_code == 200

    r1 = client.get("/v1/regime", headers={"Authorization": "Bearer quota_user"})
    assert r1.status_code == 200

    # Second billable call should be rejected due to quota
    r2 = client.get("/v1/regime", headers={"Authorization": "Bearer quota_user"})
    assert r2.status_code == 429


def test_rate_limit_enforced(tmp_path):
    key_data = {
        "rate_user": {
            "owner": "test",
            "tier": "standard",
            "status": "active",
            "monthly_quota": 1000,
            "rate_limit": {"window_seconds": 60, "max_calls": 1},
            "allowed_endpoints": ["/v1/regime"],
        }
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_USAGE_FILE": str(tmp_path / "usage_rate.json"),
        },
    )

    r1 = client.get("/v1/regime", headers={"Authorization": "Bearer rate_user"})
    assert r1.status_code == 200

    r2 = client.get("/v1/regime", headers={"Authorization": "Bearer rate_user"})
    assert r2.status_code == 429


def test_redis_backend_usage_and_quota(tmp_path):
    key_data = {
        "redis_user": {
            "owner": "test",
            "tier": "admin",
            "status": "active",
            "monthly_quota": 2,
            "allowed_endpoints": ["/v1/usage", "/v1/context"],
        }
    }
    client = _make_client(
        tmp_path,
        env={
            "NOVA_KEYS_JSON": json.dumps(key_data),
            "NOVA_REDIS_URL": "fakeredis://",
        },
    )

    # Usage endpoint is non-billable and should not count against quota
    r1 = client.get("/v1/usage", headers={"Authorization": "Bearer redis_user"})
    assert r1.status_code == 200

    r2 = client.get("/v1/usage", headers={"Authorization": "Bearer redis_user"})
    assert r2.status_code == 200

    # Billable endpoint should respect quota (monthly_quota=2)
    r3 = client.get("/v1/context", headers={"Authorization": "Bearer redis_user"})
    assert r3.status_code == 200

    r4 = client.get("/v1/context", headers={"Authorization": "Bearer redis_user"})
    assert r4.status_code == 200

    r5 = client.get("/v1/context", headers={"Authorization": "Bearer redis_user"})
    assert r5.status_code == 429
