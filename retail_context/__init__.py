"""Isolated retail-agent context plane for Nova Context Network.

This package is intentionally separate from institutional target-v2 review
context, accepted chronology, accepted-state synchronization, institutional
constraints, and institutional Reflex Memory.
"""

from .boundaries import assert_retail_module_allowed, validate_retail_package_imports
from .config import RetailContextConfig
from .context_delta import (
    build_context_delta,
    load_context_delta_schema,
    validate_context_delta,
)
from .schema import (
    SCHEMA_VERSION,
    load_retail_context_schema,
    retail_context_validator,
    validate_retail_context_object,
)
from .sources import (
    FixtureRetailSourceAdapter,
    RetailSourceAdapter,
    is_source_usable,
    load_source_observation_schema,
    load_source_registry_schema,
    validate_source_observation,
    validate_source_registry,
)
from .state_ping import build_state_ping

__all__ = [
    "RetailContextConfig",
    "FixtureRetailSourceAdapter",
    "RetailSourceAdapter",
    "SCHEMA_VERSION",
    "assert_retail_module_allowed",
    "build_context_delta",
    "build_state_ping",
    "is_source_usable",
    "load_retail_context_schema",
    "load_context_delta_schema",
    "load_source_observation_schema",
    "load_source_registry_schema",
    "retail_context_validator",
    "validate_retail_context_object",
    "validate_context_delta",
    "validate_retail_package_imports",
    "validate_source_observation",
    "validate_source_registry",
]
