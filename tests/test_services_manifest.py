import importlib
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from core.bazaar_metadata import build_services_manifest


def _load_services_json() -> dict:
    return json.loads(Path("services.json").read_text(encoding="utf-8"))


def test_services_json_is_valid_crawler_manifest():
    manifest = _load_services_json()

    assert manifest["manifest_version"] == "v1"
    assert manifest["discovery_role"] == "agentic_market_runtime_service_discovery"
    assert isinstance(manifest["services"], list)
    assert len(manifest["services"]) == 1

    service = manifest["services"][0]
    assert service["name"] == "Nova Constraint Pressure"
    assert service["endpoint"] == "/v1/feeds/constraint_pressure"
    assert service["service_type"] == "environmental_conditioning"
    assert service["description"] == (
        "Machine-readable environmental conditioning telemetry for autonomous execution systems."
    )
    assert service["category"] == "Infrastructure"
    assert service["pricing_model"] == "subscription_plus_volume"
    assert service["payment_asset"] == "USDC"
    assert service["network"] == "base"
    assert service["machine_consumable"] is True
    assert service["mcp_compatible"] is True
    assert service["x402_ready"] is True
    assert service["agentic_market_ready"] is True
    assert service["semantic_version"] == "v1"


def test_services_json_only_exposes_public_constraint_pressure_feed():
    manifest = _load_services_json()
    rendered = json.dumps(manifest, sort_keys=True).lower()

    assert "/v1/feeds/constraint_pressure" in rendered
    assert "/v1/context" not in rendered
    assert "/v1/proof" not in rendered
    assert "reflex" not in rendered
    assert "drift" not in rendered
    assert "stability" not in rendered


def test_services_json_matches_generated_manifest():
    assert _load_services_json() == build_services_manifest()


def test_services_manifest_endpoint_is_public_and_machine_readable():
    os.environ.setdefault("NOVA_KEYS_JSON", "{}")
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    client = TestClient(app_module.app)

    response = client.get("/services.json")

    assert response.status_code == 200
    assert response.json() == build_services_manifest()
