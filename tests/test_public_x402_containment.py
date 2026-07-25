from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from x402.http.constants import PAYMENT_REQUIRED_HEADER, PAYMENT_SIGNATURE_HEADER

import app as app_module
from core import x402_middleware


PUBLIC_SURFACE_FLAGS = (
    "NOVA_PUBLIC_SERVICE_DISCOVERY_ENABLED",
    "NOVA_PUBLIC_X402_ENABLED",
    "NOVA_X402_SETTLEMENT_ENABLED",
)


def _disable_public_surface(monkeypatch) -> None:
    for name in PUBLIC_SURFACE_FLAGS:
        monkeypatch.delenv(name, raising=False)


def test_public_discovery_is_disabled_by_default(monkeypatch):
    _disable_public_surface(monkeypatch)
    response = TestClient(app_module.app).get("/services.json")

    assert response.status_code == 404
    assert "services" not in response.json()


def test_public_x402_feed_is_disabled_without_a_payment_challenge(monkeypatch):
    _disable_public_surface(monkeypatch)
    response = TestClient(app_module.app).get("/v1/feeds/constraint_pressure")

    assert response.status_code == 404
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert "x-accept-payment" not in response.headers
    rendered = response.text.lower()
    assert "settlement_wallet" not in rendered
    assert "facilitator" not in rendered


def test_disabled_surface_never_calls_facilitator_verify_or_settle(monkeypatch):
    _disable_public_surface(monkeypatch)
    client = TestClient(app_module.app)

    with patch.object(
        x402_middleware,
        "get_x402_gateway",
        side_effect=AssertionError("facilitator gateway must remain unreachable"),
    ):
        response = client.get(
            "/v1/feeds/constraint_pressure",
            headers={PAYMENT_SIGNATURE_HEADER: "synthetic-disabled-payment"},
        )

    assert response.status_code == 404
    assert PAYMENT_REQUIRED_HEADER not in response.headers


def test_settlement_gate_short_circuits_facilitator_client(monkeypatch):
    monkeypatch.delenv("NOVA_X402_SETTLEMENT_ENABLED", raising=False)
    facilitator_client = MagicMock()
    gateway = x402_middleware.X402PaymentGateway(
        facilitator_client=facilitator_client,
    )

    result = gateway.verify_and_settle(
        payload=MagicMock(extensions={}),
        endpoint="/v1/feeds/constraint_pressure",
    )

    assert result.authorized is False
    assert result.reason == "x402_settlement_disabled"
    facilitator_client.verify.assert_not_called()
    facilitator_client.settle.assert_not_called()


def test_settlement_gate_blocks_challenge_even_if_public_route_flag_is_enabled(monkeypatch):
    monkeypatch.setenv("NOVA_PUBLIC_X402_ENABLED", "true")
    monkeypatch.delenv("NOVA_X402_SETTLEMENT_ENABLED", raising=False)
    response = TestClient(app_module.app).get("/v1/feeds/constraint_pressure")

    assert response.status_code == 503
    assert PAYMENT_REQUIRED_HEADER not in response.headers
    assert "settlement_wallet" not in response.text.lower()
    assert "facilitator" not in response.text.lower()


def test_health_remains_public_when_containment_is_active(monkeypatch):
    _disable_public_surface(monkeypatch)
    response = TestClient(app_module.app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_explicit_synthetic_test_mode_can_enable_surface(monkeypatch):
    for name in PUBLIC_SURFACE_FLAGS:
        monkeypatch.setenv(name, "true")
    client = TestClient(app_module.app)

    manifest = client.get("/services.json")
    challenge = client.get("/v1/feeds/constraint_pressure")

    assert manifest.status_code == 200
    assert manifest.json()["services"][0]["x402_ready"] is True
    assert manifest.json()["services"][0]["mcp_compatible"] is False
    assert manifest.json()["services"][0]["agentic_market_ready"] is False
    assert challenge.status_code == 402
    assert PAYMENT_REQUIRED_HEADER in challenge.headers
