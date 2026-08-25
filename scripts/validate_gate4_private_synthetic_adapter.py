#!/usr/bin/env python3
"""Validate isolation and scope of the Gate 4 synthetic adapter."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_MAIN_SHA = "bde8e8578c871caeefa962dd8bfbfe72528ff6fe"
ADAPTER_ROOT = Path("nova/harnesses/target_v2_private_synthetic_adapter")
INCORPORATED = {"G3-R01", "G3-R03", "G3-R08", "G3-R11", "G3-Q15"}
FORBIDDEN_IMPORT_PREFIXES = (
    "app",
    "main",
    "fastapi",
    "requests",
    "httpx",
    "socket",
    "urllib",
    "asyncio",
    "threading",
    "multiprocessing",
    "subprocess",
    "os",
    "boto",
    "stripe",
    "x402",
    "cdp",
    "nova_api",
    "scripts.gate3_reference_semantics",
)
FORBIDDEN_SOURCE_MARKERS = (
    "os.getenv",
    "os.environ",
    "load_dotenv",
    "@app.",
    "@router.",
    "FastAPI(",
    "APIRouter(",
    "decision_admission_record",
    "PR_33",
    "PR #33",
    "append_chronology",
    "write_chronology",
    "mutate_chronology",
    "write_reflex_memory",
    "mutate_reflex_memory",
    "authority_scope",
    "treatment_status",
    "applicability_status",
    "applicability_scope",
)
RUNTIME_ENTRYPOINTS = (
    Path("app.py"),
    Path("main.py"),
    Path("nova_api"),
)
ALLOWED_BRANCH_PATHS = {
    "CURRENT_STATE.md",
    "Makefile",
    "docs/operations/production-readiness-register.md",
    "docs/target-v2/gate-4-private-synthetic-adapter-v0.1.md",
    "fixtures/target-v2/gate4/private_synthetic_adapter_v0_1.json",
    "scripts/validate_gate4_private_synthetic_adapter.py",
    "tests/test_gate4_private_synthetic_adapter.py",
}
ALLOWED_BRANCH_PREFIXES = ("nova/harnesses/target_v2_private_synthetic_adapter/",)


@dataclass(frozen=True)
class ValidationError:
    location: str
    message: str

    def format(self) -> str:
        return f"{self.location}: {self.message}"


def validate_implementation_source(source: str, location: str = "adapter") -> list[ValidationError]:
    errors: list[ValidationError] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [ValidationError(location, f"invalid Python: {exc}")]
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                errors.append(ValidationError(location, "external file I/O is prohibited"))
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "connect",
                "read_bytes",
                "read_text",
                "send",
                "urlopen",
                "write_bytes",
                "write_text",
            }:
                errors.append(ValidationError(location, f"external I/O call is prohibited: {node.func.attr}"))
    for imported in imports:
        if any(imported == prefix or imported.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
            errors.append(ValidationError(location, f"forbidden dependency import: {imported}"))
    for marker in FORBIDDEN_SOURCE_MARKERS:
        if marker in source:
            errors.append(ValidationError(location, f"forbidden implementation marker: {marker}"))
    return errors


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    root = root.resolve()
    errors: list[ValidationError] = []
    package = root / ADAPTER_ROOT
    required = {"__init__.py", "adapter.py", "canonicalization.py"}
    present = {path.name for path in package.glob("*.py")}
    if not required <= present:
        errors.append(ValidationError(str(ADAPTER_ROOT), f"missing files: {sorted(required - present)}"))
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        errors.extend(validate_implementation_source(source, str(path.relative_to(root))))

    token = "target_v2_private_synthetic_adapter"
    for entry in RUNTIME_ENTRYPOINTS:
        target = root / entry
        paths = [target] if target.is_file() else list(target.rglob("*.py")) if target.is_dir() else []
        for path in paths:
            if token in path.read_text(encoding="utf-8"):
                errors.append(ValidationError(str(path.relative_to(root)), "runtime imports Gate 4 adapter"))

    contract = json.loads((root / "specs/review_context_contract_v2.json").read_text(encoding="utf-8"))
    gaps = json.loads((root / "specs/review_context_contract_gaps_v0_1.json").read_text(encoding="utf-8"))
    incorporated = set(contract.get("incorporated_Gate_3_refinements", []))
    if incorporated != INCORPORATED:
        errors.append(ValidationError("contract", "incorporated refinement set changed"))
    records = {record["id"]: record for record in gaps["contract_refinements"]}
    if len(records) != 26 or len(set(records) - INCORPORATED) != 21:
        errors.append(ValidationError("gap_register", "expected five incorporated and 21 unapproved gaps"))
    for gap_id in set(records) - INCORPORATED:
        if not records[gap_id].get("requires_CCO_review") or not records[gap_id].get("requires_Architect_review"):
            errors.append(ValidationError(f"gap_register.{gap_id}", "unapproved refinement became approved"))

    try:
        changed = subprocess.run(
            ["git", "diff", "--name-only", BASE_MAIN_SHA],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(ValidationError("branch_scope", f"cannot inspect branch delta: {exc}"))
        changed = []
    for path in changed:
        if path not in ALLOWED_BRANCH_PATHS and not path.startswith(ALLOWED_BRANCH_PREFIXES):
            errors.append(ValidationError(path, "file is outside the bounded Gate 4 branch scope"))

    state = (root / "CURRENT_STATE.md").read_text(encoding="utf-8")
    readiness = (root / "docs/operations/production-readiness-register.md").read_text(encoding="utf-8")
    required_state = (
        "Gate_3: complete",
        "canonical_contract: design-v2.1",
        "Gate_4: authorized_for_bounded_branch_implementation",
        "target_v2_runtime: not_implemented",
        "target_v2_production: not_active",
        "system_wide_production_readiness: not_established",
    )
    combined = state + "\n" + readiness
    for marker in required_state:
        if marker not in combined:
            errors.append(ValidationError("governance_state", f"missing marker: {marker}"))
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Gate 4 private synthetic adapter validation failed:")
        for error in errors:
            print(f"- {error.format()}")
        return 1
    print("Gate 4 private synthetic adapter validation passed.")
    print("runtime_imported=false route_added=false network_IO=false production_credentials_used=false")
    print("unapproved_Gate_3_gaps_incorporated=[] PR_33_dependency=none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
