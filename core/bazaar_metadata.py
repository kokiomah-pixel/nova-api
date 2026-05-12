from __future__ import annotations

from typing import Any, Dict, Optional

from core.feed_pricing import pricing_for_tier
from core.x402_config import x402_payment_requirement, x402_settlement_metadata


CONSTRAINT_PRESSURE_ENDPOINT = "/v1/feeds/constraint_pressure"
SERVICE_DESCRIPTION = "Machine-readable environmental conditioning telemetry for autonomous execution systems."
ENVIRONMENTAL_LABELS = [
    "ELEVATED",
    "FRAGMENTED",
    "DEFENSIVE",
    "RISING",
    "COMPRESSED",
    "UNSTABLE",
    "RECOVERING",
    "QUIET",
    "ESCALATING",
    "CONSTRAINED",
]


def constraint_pressure_service_metadata(*, base_url: Optional[str] = None) -> Dict[str, Any]:
    pricing = pricing_for_tier("developer")
    settlement = x402_settlement_metadata()
    endpoint = CONSTRAINT_PRESSURE_ENDPOINT
    url = f"{base_url.rstrip('/')}{endpoint}" if base_url else endpoint
    return {
        "service_name": "Nova Constraint Pressure",
        "name": "Nova Constraint Pressure",
        "endpoint": endpoint,
        "url": url,
        "service_type": "environmental_conditioning",
        "description": SERVICE_DESCRIPTION,
        "category": "Infrastructure",
        "runtime_role": "execution_posture_conditioning",
        "authority_layer": "non_admission_telemetry",
        "feed_authority": "non_admission_telemetry",
        "pricing_model": pricing["pricing_model"],
        "payment_asset": settlement["payment_asset"],
        "network": settlement["payment_network"],
        "supported_networks": [settlement["payment_network"]],
        "settlement_wallet": settlement["settlement_wallet"],
        "machine_consumable": True,
        "mcp_compatible": True,
        "x402_ready": True,
        "agentic_market_ready": True,
        "semantic_version": "v1",
        "semantic_stability": "versioned",
        "environmental_labels": ENVIRONMENTAL_LABELS,
        "orchestration_compatible": True,
        "runtime_consumable": True,
        "non_substitution_rule": "telemetry_informs_posture_only",
        "public_discovery_scope": "constraint_pressure_only",
        "x402": x402_payment_requirement(endpoint=endpoint),
    }


def build_services_manifest(*, base_url: Optional[str] = None) -> Dict[str, Any]:
    service = constraint_pressure_service_metadata(base_url=base_url)
    manifest_service = {
        "name": service["name"],
        "endpoint": service["endpoint"],
        "service_type": service["service_type"],
        "description": service["description"],
        "category": service["category"],
        "pricing_model": service["pricing_model"],
        "payment_asset": service["payment_asset"],
        "network": service["network"],
        "machine_consumable": service["machine_consumable"],
        "mcp_compatible": service["mcp_compatible"],
        "x402_ready": service["x402_ready"],
        "agentic_market_ready": service["agentic_market_ready"],
        "semantic_version": service["semantic_version"],
        "runtime_role": service["runtime_role"],
        "authority_layer": service["authority_layer"],
        "supported_networks": service["supported_networks"],
        "settlement_wallet": service["settlement_wallet"],
    }
    if base_url:
        manifest_service["url"] = service["url"]

    return {
        "manifest_version": "v1",
        "discovery_role": "agentic_market_runtime_service_discovery",
        "services": [manifest_service],
    }
