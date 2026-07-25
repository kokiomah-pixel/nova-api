from __future__ import annotations

import importlib
import os
import sys
from contextlib import contextmanager
from typing import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


PUBLIC_SURFACE_FLAGS = {
    "NOVA_PUBLIC_API_DOCUMENTATION_ENABLED": "false",
    "NOVA_PUBLIC_SERVICE_DISCOVERY_ENABLED": "false",
    "NOVA_PUBLIC_X402_ENABLED": "false",
    "NOVA_X402_SETTLEMENT_ENABLED": "false",
}

PROHIBITED_DOCUMENTATION_TERMS = (
    "decision_status",
    "decision_admission_record",
    "ALLOW",
    "CONSTRAIN",
    "DENY",
    "VETO",
    "HALT",
)


@contextmanager
def _isolated_client(*, documentation_enabled: bool) -> Iterator[TestClient]:
    environment = {
        **PUBLIC_SURFACE_FLAGS,
        "NOVA_PUBLIC_API_DOCUMENTATION_ENABLED": (
            "true" if documentation_enabled else "false"
        ),
    }
    previous_app_module = sys.modules.pop("app", None)
    try:
        with patch.dict(os.environ, environment):
            app_module = importlib.import_module("app")
            yield TestClient(app_module.app)
    finally:
        sys.modules.pop("app", None)
        if previous_app_module is not None:
            sys.modules["app"] = previous_app_module


@pytest.fixture(scope="module")
def contained_client() -> Iterator[TestClient]:
    with _isolated_client(documentation_enabled=False) as client:
        yield client


def _assert_no_legacy_contract_terms(response_text: str) -> None:
    normalized = response_text.casefold()
    for term in PROHIBITED_DOCUMENTATION_TERMS:
        assert term.casefold() not in normalized


def test_openapi_is_disabled_by_default(contained_client):
    response = contained_client.get("/openapi.json")

    assert response.status_code == 404
    _assert_no_legacy_contract_terms(response.text)


def test_swagger_is_disabled_by_default(contained_client):
    response = contained_client.get("/docs")

    assert response.status_code == 404
    _assert_no_legacy_contract_terms(response.text)


def test_redoc_is_disabled_by_default(contained_client):
    response = contained_client.get("/redoc")

    assert response.status_code == 404
    _assert_no_legacy_contract_terms(response.text)


def test_internal_openapi_generation_remains_available(contained_client):
    schema = contained_client.app.openapi()

    assert "/v1/context" in schema["paths"]
    assert contained_client.get("/openapi.json").status_code == 404


def test_health_remains_available(contained_client):
    response = contained_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_context_remains_authenticated(contained_client):
    response = contained_client.get(
        "/v1/context?intent=allocate&asset=ETH&size=10000"
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing API key"}


def test_proof_remains_authenticated(contained_client):
    response = contained_client.get("/v1/proof/test")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing API key"}


def test_services_manifest_remains_contained(contained_client):
    response = contained_client.get("/services.json")

    assert response.status_code == 404


def test_x402_feed_remains_contained(contained_client):
    response = contained_client.get("/v1/feeds/constraint_pressure")

    assert response.status_code == 404


def test_explicit_test_enablement_restores_only_documentation_routes():
    with _isolated_client(documentation_enabled=True) as client:
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/docs").status_code == 200
        assert client.get("/redoc").status_code == 200


def test_documentation_flag_does_not_enable_other_public_surfaces():
    with _isolated_client(documentation_enabled=True) as client:
        assert client.get("/services.json").status_code == 404
        assert client.get("/v1/feeds/constraint_pressure").status_code == 404
