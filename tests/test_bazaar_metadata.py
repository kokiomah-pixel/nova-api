from core.bazaar_metadata import (
    CONSTRAINT_PRESSURE_ENDPOINT,
    ENVIRONMENTAL_LABELS,
    build_services_manifest,
    constraint_pressure_service_metadata,
)


BANNED_POSITIONING_TERMS = {
    "ai analytics",
    "alpha signals",
    "execution intelligence",
    "market prediction",
    "risk dashboards",
}


def test_constraint_pressure_metadata_is_contained_by_default():
    metadata = constraint_pressure_service_metadata()

    assert metadata["service_name"] == "Nova Constraint Pressure"
    assert metadata["endpoint"] == CONSTRAINT_PRESSURE_ENDPOINT
    assert metadata["service_type"] == "environmental_conditioning"
    assert metadata["description"] == (
        "Machine-readable environmental conditioning telemetry for autonomous execution systems."
    )
    assert metadata["category"] == "Infrastructure"
    assert metadata["runtime_role"] == "non_authority_environmental_conditioning"
    assert metadata["authority_layer"] == "non_admission_telemetry"
    assert metadata["machine_consumable"] is True
    assert metadata["mcp_compatible"] is False
    assert metadata["x402_ready"] is False
    assert metadata["agentic_market_ready"] is False
    assert "supported_networks" not in metadata
    assert "payment_asset" not in metadata
    assert "settlement_wallet" not in metadata
    assert metadata["semantic_stability"] == "versioned"


def test_metadata_keeps_environmental_semantics_stable():
    metadata = constraint_pressure_service_metadata()

    assert metadata["environmental_labels"] == ENVIRONMENTAL_LABELS
    assert "ELEVATED" in metadata["environmental_labels"]
    assert "DEFENSIVE" in metadata["environmental_labels"]
    assert "CONSTRAINED" in metadata["environmental_labels"]
    assert metadata["non_substitution_rule"] == "telemetry_informs_posture_only"
    assert metadata["public_discovery_scope"] == "constraint_pressure_only"


def test_metadata_positioning_avoids_analytics_and_prediction_language():
    metadata = constraint_pressure_service_metadata()
    rendered = str(metadata).lower()

    for banned in BANNED_POSITIONING_TERMS:
        assert banned not in rendered


def test_services_manifest_generation_only_declares_constraint_pressure():
    manifest = build_services_manifest()

    assert manifest["manifest_version"] == "v1"
    assert manifest["discovery_role"] == "agentic_market_runtime_service_discovery"
    assert len(manifest["services"]) == 1
    service = manifest["services"][0]
    assert service["endpoint"] == "/v1/feeds/constraint_pressure"
    assert service["service_type"] == "environmental_conditioning"
    assert service["x402_ready"] is False
    assert service["agentic_market_ready"] is False
    assert "/v1/context" not in str(manifest)
    assert "/v1/proof" not in str(manifest)
    assert "reflex_memory" not in str(manifest).lower()
