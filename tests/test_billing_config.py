from __future__ import annotations

from core.billing_config import load_payment_destination_from_env


def test_payment_destination_absent_by_default(monkeypatch):
    monkeypatch.delenv("NOVA_PAYMENT_DESTINATION", raising=False)

    assert load_payment_destination_from_env() is None


def test_payment_destination_uses_explicit_environment_value(monkeypatch):
    configured_wallet = "0x" + "1" * 40
    monkeypatch.setenv("NOVA_PAYMENT_DESTINATION", configured_wallet)

    assert load_payment_destination_from_env() == configured_wallet


def test_blank_payment_destination_is_inactive(monkeypatch):
    monkeypatch.setenv("NOVA_PAYMENT_DESTINATION", "   ")

    assert load_payment_destination_from_env() is None
