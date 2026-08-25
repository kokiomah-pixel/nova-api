#!/usr/bin/env python3
"""Validate isolation and scope of the Gate 4 synthetic adapter."""

from __future__ import annotations

import ast
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = Path("nova/harnesses/target_v2_private_synthetic_adapter")
INCORPORATED = {"G3-R01", "G3-R03", "G3-R08", "G3-R11", "G3-Q15"}
REQUIRED_LEGACY_REJECTIONS = {
    "decision_status",
    "decision_admission_record",
    "permission_budget",
    "permission_budget_class",
    "execution_posture",
    "recommended_action",
    "adjusted_size",
    "conditioned_size",
    "halt_release_authority",
    "prevented_action",
    "intervention_type",
}
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
    "README.md",
    "docs/operations/production-readiness-register.md",
    "docs/target-v2/README.md",
    "docs/target-v2/gate-4-private-synthetic-adapter-v0.1.md",
    "fixtures/target-v2/gate4/private_synthetic_adapter_v0_1.json",
    "scripts/validate_gate4_private_synthetic_adapter.py",
    "scripts/validate_public_surface_coherence.py",
    "scripts/validate_target_v2_contract_revision.py",
    "tests/test_gate4_private_synthetic_adapter.py",
}
ALLOWED_BRANCH_PREFIXES = ("nova/harnesses/target_v2_private_synthetic_adapter/",)
DURABLE_GATE4_PATHS = (
    "CURRENT_STATE.md",
    "docs/operations/production-readiness-register.md",
    "docs/target-v2/README.md",
    "docs/target-v2/gate-4-private-synthetic-adapter-v0.1.md",
)
STALE_DURABLE_STATE_MARKERS = (
    "authorized_for_bounded_branch_implementation",
    "candidate_exists_only_on_draft_branch",
    "canonical_private_adapter_implemented: false",
    "private_synthetic_adapter_branch_implemented",
)
DURABLE_REQUIRED_MARKERS = {
    "CURRENT_STATE.md": (
        "canonical_contract: design-v2.1",
        "Gate_3: complete",
        "private_synthetic_reference_adapter:",
        "implemented: true",
        "scope: private_synthetic_reference_only",
        "canonicality_source: authoritative_repository_main",
        "Gate_4: complete",
        "runtime_implemented: false",
        "production_active: false",
        "runtime_implementation_authority: false",
        "production_activation_authority: false",
        "Gate_5_bounded_institutional_pilot:",
        "status: not_started",
        "system_wide_production_readiness: not_established",
    ),
    "docs/operations/production-readiness-register.md": (
        "v2_field_derivation:\n    status: READY",
        "v2_adapter:\n    status: READY",
        "scope: private_synthetic_reference_only",
        "deterministic_synthetic_conformance_verified",
        "Legacy_v1_derivation_dependency_absent",
        "runtime_import_absent",
        "public_route_absent",
        "production_data_dependency_absent",
        "production_credentials_absent",
        "production_crypto_selection_absent",
        "chronology_mutation_absent",
        "Reflex_Memory_mutation_absent",
        "Gate_4:\n    name: private_v2_adapter\n    status: COMPLETE",
        "target_v2_runtime: not_implemented",
        "target_v2_production: not_active",
        "institutional_pilot: not_started",
        "Gate_5:\n    name: bounded_institutional_pilot\n    status: NOT_STARTED",
        "system_wide_production_readiness: not_established",
    ),
    "docs/target-v2/README.md": (
        "field_derivation_complete: true",
        "private_synthetic_reference_adapter_implemented: true",
        "Gate_4_status: complete",
        "runtime_implemented: false",
        "production_active: false",
        "institutional_pilot_started: false",
        "Gate 4 completion does not activate Gate 5.",
    ),
    "docs/target-v2/gate-4-private-synthetic-adapter-v0.1.md": (
        "Gate_4:\n  status: complete\n  artifact: private_synthetic_reference_adapter",
        "canonicality:\n  source: authoritative_repository_main",
        "private_synthetic_reference_adapter:\n  implemented: true",
        "target_v2_runtime_implemented: false",
        "target_v2_production_active: false",
        "system_wide_production_readiness: not_established",
        "authority_effect: none",
        "execution_effect: none",
        "production_activation_authority: false",
        "Gate_5_authority: false",
    ),
}


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


def _assigned_literal(tree: ast.Module, name: str) -> object | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        value = node.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
        ):
            value = value.args[0]
        try:
            return ast.literal_eval(value)
        except (ValueError, TypeError):
            return None
    return None


def validate_durable_merge_state(
    documents: dict[str, str],
) -> list[ValidationError]:
    """Reject branch-relative state from persistent post-merge artifacts."""

    errors: list[ValidationError] = []
    for path in DURABLE_GATE4_PATHS:
        text = documents.get(path, "")
        for marker in STALE_DURABLE_STATE_MARKERS:
            if marker in text:
                errors.append(
                    ValidationError(path, f"stale branch-relative marker: {marker}")
                )
        for marker in DURABLE_REQUIRED_MARKERS[path]:
            if marker not in text:
                errors.append(
                    ValidationError(path, f"missing durable Gate 4 marker: {marker}")
                )
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

    adapter_source = (package / "adapter.py").read_text(encoding="utf-8")
    adapter_tree = ast.parse(adapter_source)
    if _assigned_literal(adapter_tree, "SYNTHETIC_ENVIRONMENT") != "synthetic":
        errors.append(ValidationError("adapter.synthetic_boundary", "must accept only synthetic evidence"))
    legacy_rejections = _assigned_literal(adapter_tree, "PROHIBITED_LEGACY_FIELDS")
    if legacy_rejections != REQUIRED_LEGACY_REJECTIONS:
        errors.append(
            ValidationError(
                "adapter.Legacy_v1_boundary",
                "must reject the complete required Legacy-v1 field inventory",
            )
        )
    if "_validate_request_boundary(request)" not in adapter_source:
        errors.append(
            ValidationError(
                "adapter.request_boundary",
                "request boundary validation must run before target-v2 derivation",
            )
        )

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

    documents = {
        path: (root / path).read_text(encoding="utf-8")
        for path in DURABLE_GATE4_PATHS
    }
    errors.extend(validate_durable_merge_state(documents))
    readiness = documents["docs/operations/production-readiness-register.md"]
    if "canonical_derivation_rules_and_proof_canonicalization_not_yet_completed" in readiness:
        errors.append(ValidationError("governance_state", "stale Gate 3 limitation remains"))
    return errors


def validate_branch_delta(
    base_ref: str, root: Path = REPO_ROOT
) -> list[ValidationError]:
    """Validate local completion scope when the requested base object exists.

    This evidence check is deliberately separate from CI-portable adapter
    safety validation. It is not invoked by the default validator or Makefile.
    """

    root = root.resolve()
    try:
        changed = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        return [ValidationError("branch_scope", f"cannot inspect branch delta: {exc}")]
    return [
        ValidationError(path, "file is outside the bounded Gate 4 branch scope")
        for path in changed
        if path not in ALLOWED_BRANCH_PATHS
        and not path.startswith(ALLOWED_BRANCH_PREFIXES)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-ref",
        help="also validate local branch file scope against an available base ref",
    )
    args = parser.parse_args(argv)
    errors = validate_repository()
    if args.base_ref:
        errors.extend(validate_branch_delta(args.base_ref))
    if errors:
        print("Gate 4 private synthetic adapter validation failed:")
        for error in errors:
            print(f"- {error.format()}")
        return 1
    print("Gate 4 private synthetic adapter validation passed.")
    print("runtime_imported=false route_added=false network_IO=false production_credentials_used=false")
    print("unapproved_Gate_3_gaps_incorporated=[] PR_33_dependency=none")
    print("Gate_4_complete_does_not_mean_runtime=true target_v2_runtime_implemented=false")
    print("target_v2_production_active=false Gate_5_not_started=true")
    print("system_wide_production_readiness_not_established=true")
    if args.base_ref:
        print(f"branch_delta_base={args.base_ref} branch_file_scope=passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
