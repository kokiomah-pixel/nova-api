#!/usr/bin/env python3
"""Bounded deterministic commands for the internal Jarvis-Nova CCO loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

try:
    from scripts.validate_cco_operating_spine import (
        ValidationIssue,
        review_priority_item_completion_evidence,
        validate_assessment_document,
        validate_priority_register_document,
    )
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repository root.
    from validate_cco_operating_spine import (  # type: ignore[no-redef]
        ValidationIssue,
        review_priority_item_completion_evidence,
        validate_assessment_document,
        validate_priority_register_document,
    )


ASSESSMENT_VALIDATION_SCOPE = [
    "CCO_assessment_schema",
    "CCO_operating_contract",
    "evidence_state_separation",
    "source_accounting",
    "authority_separation",
    "material_delta_semantics",
]

COMPARISON_BLOCKS = (
    "source_scope",
    "source_limitations",
    "source_conclusions",
    "material_delta",
    "binding_uncertainty",
    "work_state",
    "system_need",
    "attention_routing",
    "completion",
    "api_observability",
    "product_generation",
    "observed_state_delta",
    "state_change_evidence",
)


def load_document(path: Path) -> Any:
    """Load a YAML or JSON command input without consulting external systems."""

    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _assessment(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        return {}
    assessment = document.get("cco_system_need_assessment")
    return assessment if isinstance(assessment, dict) else {}


def _live_assessment_issues(document: Any, prefix: str = "") -> list[ValidationIssue]:
    issues = validate_assessment_document(document)
    if prefix:
        issues = [
            ValidationIssue(f"{prefix}.{issue.field}", issue.message)
            for issue in issues
        ]
    assessment = _assessment(document)
    field_prefix = f"{prefix}." if prefix else ""
    if assessment.get("record_source_type") != "operational_assessment":
        issues.append(
            ValidationIssue(
                f"{field_prefix}assessment.record_source_type",
                "live Jarvis-Nova commands require operational_assessment, not a synthetic fixture",
            )
        )
    if assessment.get("operational_evidence_eligible") is not True:
        issues.append(
            ValidationIssue(
                f"{field_prefix}assessment.operational_evidence_eligible",
                "live Jarvis-Nova commands require operational_evidence_eligible: true",
            )
        )
    return issues


def _emit_success(payload: dict[str, Any]) -> int:
    print(yaml.safe_dump(payload, sort_keys=False).rstrip())
    return 0


def _emit_failure(label: str, issues: Sequence[ValidationIssue]) -> int:
    print(f"Jarvis-Nova {label} validation failed:", file=sys.stderr)
    for issue in issues:
        print(f"- {issue.format()}", file=sys.stderr)
    print("assessment_reasoning_may_exist: true", file=sys.stderr)
    print("machine_validation_failed: true", file=sys.stderr)
    return 1


def what_does_system_need(path: Path) -> int:
    document = load_document(path)
    issues = _live_assessment_issues(document)
    if issues:
        return _emit_failure("operational assessment", issues)

    assessment = _assessment(document)
    routing = assessment["attention_routing"]
    effects = assessment["assessment_artifact_effect"]
    return _emit_success(
        {
            "jarvis_nova_command": {
                "command": "what_does_system_need",
                "validation": {
                    "status": "passed",
                    "machine_validated": True,
                    "validation_scope": ASSESSMENT_VALIDATION_SCOPE,
                    "source_truth_independently_verified_by_this_command": False,
                },
                "assessment": {
                    "assessment_id": assessment["assessment_id"],
                    "action_class": assessment["system_need"]["action_class"],
                    "attention_level": routing["level"],
                    "blocking": routing["blocking"],
                    "recommended_owner": routing["recommended_owner"],
                },
                "effects": {
                    "creates_corporate_accepted_state": effects[
                        "creates_corporate_accepted_state"
                    ],
                    "creates_chronology": effects["creates_chronology"],
                    "creates_Reflex_Memory": effects["creates_Reflex_Memory"],
                    "creates_product_implementation_authority": effects[
                        "creates_implementation_authority"
                    ],
                    "creates_production_authority": effects[
                        "creates_production_authority"
                    ],
                    "creates_capital_authority": effects[
                        "creates_capital_authority"
                    ],
                    "creates_pricing_authority": effects[
                        "creates_pricing_authority"
                    ],
                },
            }
        }
    )


def _completion_item_result(item: dict[str, Any]) -> dict[str, Any]:
    review = review_priority_item_completion_evidence(item)
    return {
        "item_id": item["item_id"],
        "prior_status": review["prior_status"],
        "resulting_status": review["resulting_status"],
        "evidence_review": {
            key: review[key]
            for key in (
                "terminal_evidence_contract_satisfied",
                "independent_verification_claim_present",
                "semantic_completion_condition_verified_by_this_command",
                "eligible_for_terminal_review",
            )
        },
    }


def review_completion(path: Path) -> int:
    document = load_document(path)
    issues = validate_priority_register_document(document)
    if issues:
        return _emit_failure("completion evidence", issues)

    items = document["items"]
    result: dict[str, Any] = {
        "command": "review_completion",
        "validation": {
            "status": "passed",
            "machine_validated": True,
            "validation_scope": [
                "CCO_priority_register_schema",
                "completion_evidence_contract",
                "completion_vs_independent_verification",
            ],
            "source_truth_independently_verified_by_this_command": False,
        },
        "authority_effect": "none",
    }
    reviewed_items = [_completion_item_result(item) for item in items]
    if len(reviewed_items) == 1:
        item_result = reviewed_items[0]
        result["item"] = {
            key: item_result[key]
            for key in ("item_id", "prior_status", "resulting_status")
        }
        result["evidence_review"] = item_result["evidence_review"]
    else:
        result["items"] = reviewed_items
    return _emit_success({"jarvis_nova_command": result})


def _different_paths(old: Any, new: Any, prefix: str) -> list[str]:
    if isinstance(old, dict) and isinstance(new, dict):
        paths: list[str] = []
        for key in sorted(set(old) | set(new)):
            child = f"{prefix}.{key}" if prefix else key
            if key not in old or key not in new:
                paths.append(child)
            else:
                paths.extend(_different_paths(old[key], new[key], child))
        return paths
    if old != new:
        return [prefix]
    return []


def _missing_current_evidence(assessment: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    scope = assessment.get("source_scope", {})
    if isinstance(scope, dict):
        for bucket in ("unavailable", "stale", "not_checked"):
            for source_id in scope.get(bucket, []):
                missing.append(f"{source_id}:{bucket}")
    for conclusion in assessment.get("source_conclusions", []):
        if (
            isinstance(conclusion, dict)
            and conclusion.get("conclusion") == "unknown"
        ):
            marker = f"{conclusion.get('source_id')}:unknown_conclusion"
            if marker not in missing:
                missing.append(marker)
    return sorted(missing)


def compare_state(old_path: Path, new_path: Path) -> int:
    old_document = load_document(old_path)
    new_document = load_document(new_path)
    issues = _live_assessment_issues(old_document, "old")
    issues.extend(_live_assessment_issues(new_document, "new"))

    old = _assessment(old_document)
    new = _assessment(new_document)
    new_baseline = new.get("comparison_baseline")
    if isinstance(new_baseline, dict):
        if new_baseline.get("baseline_type") != "prior_verified_assessment":
            issues.append(
                ValidationIssue(
                    "new.comparison_baseline.baseline_type",
                    "current assessment must identify a prior_verified_assessment",
                )
            )
        if old and new_baseline.get("baseline_reference") != old.get("assessment_id"):
            issues.append(
                ValidationIssue(
                    "new.comparison_baseline.baseline_reference",
                    "must equal the prior assessment_id supplied with --old",
                )
            )
    elif new:
        issues.append(
            ValidationIssue(
                "new.comparison_baseline",
                "current assessment must identify the supplied prior verified assessment",
            )
        )

    if issues:
        return _emit_failure("verified-state comparison", issues)

    changed_paths: list[str] = []
    for block in COMPARISON_BLOCKS:
        changed_paths.extend(_different_paths(old.get(block), new.get(block), block))
    changed_paths = sorted(set(changed_paths))
    missing_evidence = _missing_current_evidence(new)
    material_status = new["material_delta"]["status"]
    observed_delta = new["observed_state_delta"]
    return _emit_success(
        {
            "jarvis_nova_command": {
                "command": "compare_state",
                "validation": {
                    "status": "passed",
                    "machine_validated": True,
                    "validation_scope": [
                        "prior_and_current_CCO_assessment_contracts",
                        "verified_baseline_relationship",
                        "deterministic_structural_comparison",
                        "authoritative_state_movement_separation",
                    ],
                    "source_truth_independently_verified_by_this_command": False,
                },
                "comparison": {
                    "prior_assessment_id": old["assessment_id"],
                    "current_assessment_id": new["assessment_id"],
                    "structural_difference_detected": bool(changed_paths),
                    "changed_paths": changed_paths,
                    "current_material_delta_status": material_status,
                    "missing_current_evidence": missing_evidence,
                    "no_material_delta_established": (
                        material_status == "no_material_delta"
                        and not missing_evidence
                    ),
                },
                "authoritative_state_movement": {
                    "inferred_from_structural_difference": False,
                    "canonical_corporate_state_changed": observed_delta[
                        "canonical_corporate_state_changed"
                    ],
                    "accepted_state_change": observed_delta["accepted_state_change"],
                    "chronology_change": observed_delta["chronology_change"],
                    "Reflex_Memory_change": observed_delta["Reflex_Memory_change"],
                    "runtime_change": observed_delta["runtime_change"],
                    "production_change": observed_delta["production_change"],
                },
                "authority_effect": "none",
            }
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate bounded Jarvis-Nova CCO command artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    assess = subparsers.add_parser(
        "what-does-system-need",
        help="Validate a constructed live operational assessment.",
    )
    assess.add_argument("--assessment", required=True, type=Path)

    completion = subparsers.add_parser(
        "review-completion",
        help="Review submitted CCO priority-item completion evidence.",
    )
    completion.add_argument("--items", required=True, type=Path)

    compare = subparsers.add_parser(
        "compare-state",
        help="Compare a prior verified assessment with a current assessment.",
    )
    compare.add_argument("--old", required=True, type=Path)
    compare.add_argument("--new", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "what-does-system-need":
            return what_does_system_need(args.assessment)
        if args.command == "review-completion":
            return review_completion(args.items)
        return compare_state(args.old, args.new)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        return _emit_failure(
            "command input",
            [ValidationIssue("input", f"could not load command document: {exc}")],
        )


if __name__ == "__main__":
    sys.exit(main())
