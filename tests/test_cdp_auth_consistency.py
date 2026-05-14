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
    assert live_x402_payment.build_cdp_auth_provider_from_env is build_cdp_auth_provider_from_env
    assert live_x402_payment.load_cdp_credentials_from_env is load_cdp_credentials_from_env


def test_live_payment_uses_official_http_helper_for_payment_headers():
    assert live_x402_payment.x402HTTPClientSync.__name__ == "x402HTTPClientSync"
    assert "encode_payment_signature_header" not in live_x402_payment.__dict__
    assert "decode_payment_required_header" not in live_x402_payment.__dict__


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


def test_live_auth_only_uses_verify_auth_without_signing_or_settling(monkeypatch, capsys):
    monkeypatch.setenv("CDP_API_KEY_ID", "server-key-id")
    monkeypatch.setenv("CDP_API_KEY_SECRET", "server-key-secret")
    calls = []

    class FakeHeaders:
        verify = {"Authorization": "Bearer fake-verify-token"}

    class FakeAuthProvider:
        def get_auth_headers(self):
            return FakeHeaders()

    class FakeResponse:
        status_code = 422
        text = '{"error":"invalid payment payload"}'

        def json(self):
            return {"error": "invalid payment payload"}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, *, headers, json):
            calls.append((url, headers, json))
            return FakeResponse()

        def get(self, *args, **kwargs):
            raise AssertionError("auth-only must not perform feed discovery")

    monkeypatch.setattr(
        live_x402_payment,
        "build_cdp_auth_provider_from_env",
        lambda *, facilitator_url: FakeAuthProvider(),
    )
    monkeypatch.setattr(live_x402_payment.httpx, "Client", FakeClient)

    assert live_x402_payment.main(["--auth-only"]) == 0

    output = capsys.readouterr().out
    assert "live_auth_only_attempted: yes" in output
    assert "live_auth_path_accepted: yes" in output
    assert "auth_failure_still_401: no" in output
    assert calls == [
        (
            f"{FACILITATOR_URL}/verify",
            {"Authorization": "Bearer fake-verify-token"},
            {"paymentPayload": {}, "paymentRequirements": {}},
        )
    ]


def test_live_auth_only_reports_401_as_rejected(monkeypatch, capsys):
    class FakeHeaders:
        verify = {"Authorization": "Bearer fake-verify-token"}

    class FakeAuthProvider:
        def get_auth_headers(self):
            return FakeHeaders()

    class FakeResponse:
        status_code = 401
        text = '{"error":"Unauthorized"}'

        def json(self):
            return {"error": "Unauthorized"}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        live_x402_payment,
        "build_cdp_auth_provider_from_env",
        lambda *, facilitator_url: FakeAuthProvider(),
    )
    monkeypatch.setattr(live_x402_payment.httpx, "Client", FakeClient)

    assert live_x402_payment.main(["--auth-only"]) == 1

    output = capsys.readouterr().out
    assert "live_auth_path_accepted: no" in output
    assert "auth_failure_still_401: yes" in output
