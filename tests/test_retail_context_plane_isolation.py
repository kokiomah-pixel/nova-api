from pathlib import Path

import pytest

from retail_context.boundaries import (
    RetailIsolationViolation,
    assert_retail_module_allowed,
    assert_retail_path_allowed,
    validate_retail_package_imports,
)
from retail_context.config import (
    DEFAULT_RETAIL_ENDPOINT_PREFIX,
    RETAIL_ENV_PREFIX,
    RetailContextConfig,
)


def test_retail_package_has_no_forbidden_non_retail_imports():
    package_dir = Path(__file__).resolve().parents[1] / "retail_context"
    assert validate_retail_package_imports(package_dir) == []


@pytest.mark.parametrize(
    "module_name",
    [
        "core.accepted_state_synchronization",
        "core.reflex_governance_runtime",
        "core.reflex_governance_runtime.runtime",
        "core.governance_identity",
    ],
)
def test_institutional_state_modules_are_denied(module_name):
    with pytest.raises(RetailIsolationViolation):
        assert_retail_module_allowed(module_name)


@pytest.mark.parametrize(
    "module_name",
    [
        "core.x402_config",
        "core.x402_middleware",
        "core.feed_pricing",
        "core.feed_metering",
        "core.feed_identity",
        "core.bazaar_metadata",
        "core.billing_config",
        "core.billing_state",
    ],
)
def test_legacy_runtime_modules_are_denied_as_direct_retail_dependencies(module_name):
    with pytest.raises(RetailIsolationViolation):
        assert_retail_module_allowed(module_name)


@pytest.mark.parametrize(
    "path",
    [
        "agent_files/state/accepted-state-registry.yaml",
        "agent_files/state/accepted-state-checkpoint.yaml",
        "docs/chronology/accepted-entry.yaml",
        "data/reflex_memory/accepted.json",
        "specs/institutional_exposure_contract_v0.1.json",
    ],
)
def test_institutional_state_paths_are_denied(path):
    with pytest.raises(RetailIsolationViolation):
        assert_retail_path_allowed(path)


def test_unrelated_authority_neutral_module_is_not_denied():
    assert_retail_module_allowed("core.environmental_state_engine")


def test_retail_configuration_uses_separate_namespace(monkeypatch, tmp_path):
    monkeypatch.setenv(f"{RETAIL_ENV_PREFIX}STATE_DIR", str(tmp_path / "retail"))
    monkeypatch.setenv(f"{RETAIL_ENV_PREFIX}ENDPOINT_PREFIX", "/retail/v1/context")
    config = RetailContextConfig.from_env()

    assert config.state_dir == tmp_path / "retail"
    assert config.endpoint_prefix == DEFAULT_RETAIL_ENDPOINT_PREFIX
    assert config.telemetry_namespace == "retail_context"
    assert config.source_namespace == "retail_public_sources"
    assert config.credential_namespace == "retail_context"
