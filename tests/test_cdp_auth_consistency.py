import pytest

import core.cdp_auth as cdp_auth
import scripts.check_cdp_x402_auth as check_cdp_x402_auth
import scripts.live_x402_constraint_pressure_payment as live_x402_payment
from core.cdp_auth import (
    CDPFacilitatorAuthProvider,
    build_cdp_auth_provider_from_env,
    load_cdp_credentials_from_env,
)
from core.x402_middleware import X402PaymentGateway


FACILITATOR_URL = "https://api.cdp.coinbase.com/platform/v2/x402"


def test_probe_live_script_and_middleware_share_cdp_auth_builder(monkeypatch):
    monkeypatch.setenv("CDP_API_KEY_ID", "server-key-id")
    monkeypatch.setenv("CDP_API_KEY_SECRET", "server-key-secret")

    gateway = X402PaymentGateway(facilitator_url=FACILITATOR_URL)

    assert isinstance(gateway._auth_provider(), CDPFacilitatorAuthProvider)
    assert check_cdp_x402_auth.build_cdp_auth_provider_from_env is build_cdp_auth_provider_from_env
    assert live_x402_payment.load_cdp_credentials_from_env is load_cdp_credentials_from_env


def test_cdp_auth_headers_use_expected_facilitator_paths(monkeypatch):
    monkeypatch.setenv("CDP_API_KEY_ID", "server-key-id")
    monkeypatch.setenv("CDP_API_KEY_SECRET", "server-key-secret")
    calls = []

    def fake_generate_jwt(options):
        calls.append(options)
        suffix = options.request_path.rsplit("/", 1)[-1]
        return f"token-{options.request_method}-{suffix}"

    monkeypatch.setattr(cdp_auth, "generate_jwt", fake_generate_jwt)

    provider = build_cdp_auth_provider_from_env(facilitator_url=FACILITATOR_URL)
    headers = provider.get_auth_headers()

    assert headers.verify["Authorization"] == "Bearer token-POST-verify"
    assert headers.settle["Authorization"] == "Bearer token-POST-settle"
    assert headers.supported["Authorization"] == "Bearer token-GET-supported"
    assert [call.request_path for call in calls] == [
        "/platform/v2/x402/verify",
        "/platform/v2/x402/settle",
        "/platform/v2/x402/supported",
    ]


def test_missing_cdp_env_fails_without_secret_leak(monkeypatch):
    monkeypatch.delenv("CDP_API_KEY_ID", raising=False)
    monkeypatch.setenv("CDP_API_KEY_SECRET", "secret-value-that-must-not-print")

    with pytest.raises(RuntimeError) as exc:
        load_cdp_credentials_from_env()

    message = str(exc.value)
    assert "CDP_API_KEY_ID" in message
    assert "secret-value-that-must-not-print" not in message


def test_placeholder_cdp_env_fails_without_secret_leak(monkeypatch):
    monkeypatch.setenv("CDP_API_KEY_ID", "server-key-id")
    monkeypatch.setenv("CDP_API_KEY_SECRET", "PASTE_SECRET_LOCALLY_ONLY")

    with pytest.raises(RuntimeError) as exc:
        load_cdp_credentials_from_env()

    message = str(exc.value)
    assert "CDP_API_KEY_SECRET" in message
    assert "PASTE_SECRET_LOCALLY_ONLY" not in message
