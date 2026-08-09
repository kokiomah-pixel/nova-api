#!/usr/bin/env python3
"""Fail-closed validation for non-authoritative market-signal watches."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = Path("docs/market/market-signal-watch-register.yaml")
ARC_SIGNAL_ID = "ARC_AGENTIC_FINANCE_2026"
ARC_EVIDENCE_ID = "MSE-2026-08-08-035"

EXPECTED_RECORD_PATH = Path(
    "docs/market/signals/2026/MSE-2026-08-08-035-circle-arc-agentic-finance.md"
)
EXPECTED_MEMO_PATH = Path("docs/architecture/arc-circle-compatibility-boundary.md")

REQUIRED_SOURCES = {
    "https://www.arc.io/",
    "https://www.arc.io/blog/arc-mainnet-goes-live-on-september-16-2026",
    "https://developers.circle.com/agent-stack",
}

REQUIRED_NOT_ESTABLISHED = {
    "Nova_buyer_demand",
    "Nova_customer_adoption",
    "Nova_pricing_power",
    "Nova_product_market_fit",
    "Nova_has_pricing_power",
    "Nova_has_product_market_fit",
    "institutional_dependency_on_Nova",
    "Circle_or_Arc_partnership",
    "Arc_integration_requirement",
    "implementation_authority",
    "production_authority",
    "roadmap_change",
    "Arc_creates_demand_for_Nova",
    "Arc_validates_Nova",
    "Circle_requires_Nova",
    "institutions_require_Nova",
    "Nova_should_integrate_with_Arc_now",
    "Nova_should_build_for_Arc",
    "Arc_is_a_customer",
    "Circle_is_a_partner",
}

REQUIRED_THESIS_TRIGGERS = {
    "institutions_insert_contextual_review_between_agent_and_wallet",
    "repeated_pre_execution_evidence_assembly_appears",
    "recurring_manual_exception_handling_appears",
    "decision_reconstruction_problems_repeat",
    "cross_transaction_decision_lineage_becomes_required",
    "institutional_memory_is_required_for_agentic_financial_actions",
    "third_parties_independently_build_Nova_like_decision_context_layers",
}

REQUIRED_COMPRESSION_TRIGGERS = {
    "Circle_moves_beyond_wallet_policy_into_decision_context",
    "Circle_builds_institutional_decision_chronology",
    "Circle_builds_governed_exception_memory",
    "Circle_builds_pre_execution_context_reconstruction",
    "Arc_ecosystem_standardizes_a_competing_upstream_review_layer",
}

NONE_EFFECT_FIELDS = (
    "authority_effect",
    "execution_effect",
    "production_effect",
    "accepted_state_effect",
    "chronology_effect",
    "Reflex_Memory_effect",
    "constraint_effect",
    "policy_effect",
    "product_requirement_effect",
    "roadmap_effect",
)

FALSE_CLAIM_FIELDS = (
    "accepted_state_change",
    "chronology_change",
    "Reflex_Memory_change",
    "runtime_change",
    "production_change",
    "external_integration",
    "authority_change",
    "roadmap_change",
    "implementation_authority_created",
    "production_authority_created",
    "buyer_demand_established",
    "customer_adoption_established",
    "pricing_power_established",
    "product_market_fit_established",
    "product_requirement_established",
    "institutional_dependency_established",
    "Circle_or_Arc_partnership_established",
    "Arc_integration_requirement_established",
)

NONE_ACTION_FIELDS = (
    "engineering_action",
    "production_action",
    "integration_action",
    "chronology_action",
    "Reflex_Memory_action",
    "constraint_action",
    "policy_action",
    "roadmap_action",
)

PROHIBITED_REFERENCE_PATHS = (
    Path("agent_files/state/accepted-state-registry.yaml"),
    Path("chronology"),
    Path("fixtures/reflex_memory"),
)

CANONICAL_BOUNDARY = (
    "Agent prepares action.",
    "Nova structures review context.",
    "Local authority decides.",
    "External systems execute.",
    "Nova does not execute.",
)


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _read_yaml(path: Path, field: str, errors: list[ValidationError]) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(ValidationError(field, f"missing required file: {path}"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(ValidationError(field, f"cannot load YAML: {exc}"))
    return None


def _read_text(path: Path, field: str, errors: list[ValidationError]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(ValidationError(field, f"missing required file: {path}"))
    except (OSError, UnicodeError) as exc:
        errors.append(ValidationError(field, f"cannot read UTF-8 text: {exc}"))
    return ""


def _frontmatter(text: str, field: str, errors: list[ValidationError]) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(ValidationError(field, "missing YAML frontmatter"))
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(ValidationError(field, "unterminated YAML frontmatter"))
        return {}
    try:
        loaded = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        errors.append(ValidationError(field, f"invalid YAML frontmatter: {exc}"))
        return {}
    if not isinstance(loaded, dict):
        errors.append(ValidationError(field, "frontmatter must be a mapping"))
        return {}
    return loaded


def _require_equal(
    errors: list[ValidationError],
    mapping: dict[str, Any],
    key: str,
    expected: Any,
    prefix: str,
) -> None:
    actual = mapping.get(key)
    if actual != expected:
        errors.append(
            ValidationError(
                f"{prefix}.{key}",
                f"expected {expected!r}; found {actual!r}",
            )
        )


def _require_superset(
    errors: list[ValidationError],
    mapping: dict[str, Any],
    key: str,
    expected: set[str],
    prefix: str,
) -> None:
    actual = mapping.get(key)
    if not isinstance(actual, list):
        errors.append(ValidationError(f"{prefix}.{key}", "must be a list"))
        return
    missing = expected - set(actual)
    if missing:
        errors.append(
            ValidationError(
                f"{prefix}.{key}",
                f"missing required values: {sorted(missing)}",
            )
        )


def _iter_files(root: Path, relative: Path) -> Iterable[Path]:
    path = root / relative
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(candidate for candidate in path.rglob("*") if candidate.is_file())


def validate_arc_entry(entry: dict[str, Any]) -> list[ValidationError]:
    """Validate the Arc watch's machine-readable non-authority contract."""

    errors: list[ValidationError] = []
    prefix = f"signals.{ARC_SIGNAL_ID}"

    required_values = {
        "evidence_id": ARC_EVIDENCE_ID,
        "signal_id": ARC_SIGNAL_ID,
        "signal_class": "market_architecture_signal",
        "priority": "high",
        "lifecycle_status": "observed_watch",
        "epistemic_status": "externally_observed",
        "review_state": "governed_watch",
        "record_path": EXPECTED_RECORD_PATH.as_posix(),
        "boundary_memo_path": EXPECTED_MEMO_PATH.as_posix(),
    }
    for key, expected in required_values.items():
        _require_equal(errors, entry, key, expected, prefix)
    for key in NONE_EFFECT_FIELDS:
        _require_equal(errors, entry, key, "none", prefix)
    for key in FALSE_CLAIM_FIELDS:
        _require_equal(errors, entry, key, False, prefix)
    for key in NONE_ACTION_FIELDS:
        _require_equal(errors, entry, key, "none", prefix)

    _require_superset(errors, entry, "not_established", REQUIRED_NOT_ESTABLISHED, prefix)
    _require_superset(
        errors,
        entry,
        "thesis_strengthening_triggers",
        REQUIRED_THESIS_TRIGGERS,
        prefix,
    )
    _require_superset(
        errors,
        entry,
        "category_compression_triggers",
        REQUIRED_COMPRESSION_TRIGGERS,
        prefix,
    )

    sources = entry.get("external_sources")
    source_urls = {
        source.get("url")
        for source in sources or []
        if isinstance(source, dict)
    }
    if source_urls != REQUIRED_SOURCES:
        errors.append(
            ValidationError(
                f"{prefix}.external_sources",
                f"expected exact official source set; found {sorted(source_urls)}",
            )
        )

    escalation = entry.get("escalation_rule")
    if not isinstance(escalation, dict):
        errors.append(ValidationError(f"{prefix}.escalation_rule", "must be a mapping"))
    else:
        expected_escalation = {
            "interesting_event_is_escalation": False,
            "repeated_behavior_requires_Architect_attention": True,
            "structural_category_movement_requires_Architect_attention": True,
            "material_competitive_compression_requires_Architect_attention": True,
        }
        for key, expected in expected_escalation.items():
            _require_equal(errors, escalation, key, expected, f"{prefix}.escalation_rule")

    boundary = entry.get("boundary_assertions")
    if not isinstance(boundary, dict):
        errors.append(ValidationError(f"{prefix}.boundary_assertions", "must be a mapping"))
    else:
        expected_boundary = {
            "Nova_executes": False,
            "Nova_signs": False,
            "Nova_controls_wallet": False,
            "local_authority_decides": True,
            "external_system_executes": True,
        }
        for key, expected in expected_boundary.items():
            _require_equal(errors, boundary, key, expected, f"{prefix}.boundary_assertions")

    return errors


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    """Validate the canonical watch and separation from authoritative namespaces."""

    root = root.resolve()
    errors: list[ValidationError] = []
    register = _read_yaml(root / REGISTER_PATH, "register", errors)
    if not isinstance(register, dict):
        if register is not None:
            errors.append(ValidationError("register", "must be a mapping"))
        return errors

    _require_equal(errors, register, "register_type", "market_signal_watch", "register")
    _require_equal(errors, register, "status", "monitoring_only", "register")
    _require_equal(errors, register, "runtime_authority", "none", "register")
    _require_equal(errors, register, "production_authority", "none", "register")

    signals = register.get("signals")
    if not isinstance(signals, list):
        errors.append(ValidationError("register.signals", "must be a list"))
        return errors

    matching = [entry for entry in signals if isinstance(entry, dict) and entry.get("signal_id") == ARC_SIGNAL_ID]
    if len(matching) != 1:
        errors.append(
            ValidationError(
                "register.signals.ARC_AGENTIC_FINANCE_2026",
                f"expected exactly one Arc watch; found {len(matching)}",
            )
        )
        return errors

    entry = matching[0]
    errors.extend(validate_arc_entry(entry))

    signal_text = _read_text(root / EXPECTED_RECORD_PATH, "Arc_record", errors)
    signal_meta = _frontmatter(signal_text, "Arc_record.frontmatter", errors) if signal_text else {}
    for key, expected in {
        "record_type": "market_signal_evidence",
        "evidence_id": ARC_EVIDENCE_ID,
        "signal_id": ARC_SIGNAL_ID,
        "signal_class": "market_architecture_signal",
        "lifecycle_status": "observed_watch",
        "epistemic_status": "externally_observed",
        "review_state": "governed_watch",
        "authority_effect": "none",
        "execution_effect": "none",
        "production_effect": "none",
        "accepted_state_effect": "none",
        "chronology_effect": "none",
        "Reflex_Memory_effect": "none",
        "accepted_state_change": False,
        "chronology_change": False,
        "Reflex_Memory_change": False,
        "runtime_change": False,
        "production_change": False,
        "external_integration": False,
        "authority_change": False,
        "implementation_authority_created": False,
        "production_authority_created": False,
        "buyer_demand_established": False,
        "product_market_fit_established": False,
        "roadmap_change": False,
    }.items():
        _require_equal(errors, signal_meta, key, expected, "Arc_record.frontmatter")
    for line in CANONICAL_BOUNDARY:
        if line not in signal_text:
            errors.append(ValidationError("Arc_record.boundary", f"missing line: {line}"))

    memo_text = _read_text(root / EXPECTED_MEMO_PATH, "Arc_boundary_memo", errors)
    memo_meta = _frontmatter(memo_text, "Arc_boundary_memo.frontmatter", errors) if memo_text else {}
    for key, expected in {
        "record_type": "architecture_boundary_hypothesis",
        "evidence_state": "externally_observed",
        "review_state": "governed_watch",
        "authority_effect": "none",
        "execution_effect": "none",
        "production_effect": "none",
        "accepted_state_effect": "none",
        "chronology_effect": "none",
        "Reflex_Memory_effect": "none",
        "runtime_implemented": False,
        "external_integration": False,
    }.items():
        _require_equal(errors, memo_meta, key, expected, "Arc_boundary_memo.frontmatter")
    for line in CANONICAL_BOUNDARY:
        if line not in memo_text:
            errors.append(ValidationError("Arc_boundary_memo.boundary", f"missing line: {line}"))

    for required_text in (
        "Nova should govern institutional decision objects, not blockchain",
        "Nova_executes: false",
        "Nova_signs: false",
        "Nova_controls_wallet: false",
        "local_authority_decides: true",
        "external_system_executes: true",
    ):
        if required_text not in memo_text:
            errors.append(
                ValidationError(
                    "Arc_boundary_memo.required_assertions",
                    f"missing assertion: {required_text}",
                )
            )

    identifiers = (ARC_SIGNAL_ID, ARC_EVIDENCE_ID)
    for relative in PROHIBITED_REFERENCE_PATHS:
        for path in _iter_files(root, relative):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(
                    ValidationError(
                        f"separation.{path.relative_to(root)}",
                        f"cannot inspect UTF-8 text: {exc}",
                    )
                )
                continue
            for identifier in identifiers:
                if identifier in text:
                    errors.append(
                        ValidationError(
                            f"separation.{path.relative_to(root)}",
                            f"market-signal identifier entered prohibited state namespace: {identifier}",
                        )
                    )

    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        for error in errors:
            print(error.format(), file=sys.stderr)
        return 1
    print(
        "Market-signal watch validation passed: "
        "ARC_AGENTIC_FINANCE_2026 remains monitoring-only and non-authoritative."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
