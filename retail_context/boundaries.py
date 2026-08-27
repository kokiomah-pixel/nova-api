from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List


# Retail may reuse authority-neutral primitives, but it must not import or read
# institutional state-bearing modules. Legacy v1 payment, pricing, metering, and
# billing modules are also denied as direct dependencies because they carry the
# wrong product contract or institutional semantics. Reuse requires extraction
# into a new authority-neutral primitive first.
FORBIDDEN_IMPORT_PREFIXES = (
    "core.accepted_state_synchronization",
    "core.reflex_governance_runtime",
    "core.governance_identity",
    "core.x402_config",
    "core.x402_middleware",
    "core.feed_pricing",
    "core.feed_metering",
    "core.feed_identity",
    "core.bazaar_metadata",
    "core.billing_config",
    "core.billing_state",
    "core.telemetry_engine",
    "core.usage_meter",
    "core.cdp_auth",
    "app",
    "key_manager",
)

FORBIDDEN_PATH_FRAGMENTS = (
    "accepted-state-registry",
    "accepted-state-checkpoint",
    "chronology",
    "reflex-memory",
    "reflex_memory",
    "institutional",
)


class RetailIsolationViolation(RuntimeError):
    pass


def assert_retail_module_allowed(module_name: str) -> None:
    normalized = str(module_name or "").strip()
    if any(
        normalized == prefix or normalized.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_IMPORT_PREFIXES
    ):
        raise RetailIsolationViolation(
            f"retail context plane cannot import non-retail module directly: {normalized}"
        )


def assert_retail_path_allowed(path: str | Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_PATH_FRAGMENTS):
        raise RetailIsolationViolation(
            f"retail context plane cannot access institutional state path: {path}"
        )


def _imports_from_source(source: str) -> Iterable[str]:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def validate_retail_package_imports(package_dir: str | Path) -> List[str]:
    """Return isolation violations found by static import inspection.

    This is intentionally deterministic and suitable for CI. It checks only the
    retail package and does not infer production state or institutional authority.
    """

    root = Path(package_dir)
    violations: List[str] = []
    for path in sorted(root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for module_name in _imports_from_source(source):
            try:
                assert_retail_module_allowed(module_name)
            except RetailIsolationViolation as exc:
                violations.append(f"{path}: {exc}")
    return violations
