#!/usr/bin/env python3
"""Validate governed-watch continuity across market-signal run artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = Path("docs/market/market-signal-watch-register.yaml")
SCHEMA_PATH = Path("schemas/market/market_signal_run_v0_1.schema.json")
RUN_ARTIFACT_GLOB = "docs/market/runs/**/*.yaml"

ELIGIBILITY_VERSION = "governed_watch_eligibility_v0_1"
ELIGIBLE_REVIEW_STATE = "governed_watch"
ELIGIBLE_LIFECYCLE_STATUSES = {"observed_watch"}


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_compatible(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    return value


def _path(parts: Any) -> str:
    return ".".join(str(part) for part in parts) or "$"


def _resolve_from_repo(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def discover_market_signal_run_paths(root: Path = REPO_ROOT) -> list[Path]:
    """Return every governed YAML artifact in the market-signal runs surface."""

    return sorted(path for path in root.glob(RUN_ARTIFACT_GLOB) if path.is_file())


def validate_eligibility_contract(register: Any) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not isinstance(register, dict):
        return [ValidationError("register", "must be a mapping")]

    contract = register.get("governed_watch_eligibility")
    if not isinstance(contract, dict):
        return [
            ValidationError(
                "register.governed_watch_eligibility",
                "missing governed-watch eligibility contract",
            )
        ]

    expected = {
        "contract_version": ELIGIBILITY_VERSION,
        "source_path": REGISTER_PATH.as_posix(),
        "scan_requirement": "mandatory_for_every_applicable_market_signal_run",
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            errors.append(
                ValidationError(
                    f"register.governed_watch_eligibility.{key}",
                    f"expected {value!r}; found {contract.get(key)!r}",
                )
            )

    include = contract.get("eligible_when_all")
    if not isinstance(include, dict):
        errors.append(
            ValidationError(
                "register.governed_watch_eligibility.eligible_when_all",
                "must be a mapping",
            )
        )
    else:
        if include.get("review_state") != ELIGIBLE_REVIEW_STATE:
            errors.append(
                ValidationError(
                    "register.governed_watch_eligibility.eligible_when_all.review_state",
                    f"must be {ELIGIBLE_REVIEW_STATE!r}",
                )
            )
        statuses = include.get("lifecycle_status")
        if not isinstance(statuses, list) or set(statuses) != ELIGIBLE_LIFECYCLE_STATUSES:
            errors.append(
                ValidationError(
                    "register.governed_watch_eligibility.eligible_when_all.lifecycle_status",
                    f"must be {sorted(ELIGIBLE_LIFECYCLE_STATUSES)!r}",
                )
            )

    boundary = contract.get("lifecycle_boundary")
    if not isinstance(boundary, dict):
        errors.append(
            ValidationError(
                "register.governed_watch_eligibility.lifecycle_boundary",
                "must be a mapping",
            )
        )
    else:
        if boundary.get("implicit_expiration_allowed") is not False:
            errors.append(
                ValidationError(
                    "register.governed_watch_eligibility.lifecycle_boundary.implicit_expiration_allowed",
                    "must remain false",
                )
            )
        if boundary.get("exclusion_requires_explicit_governed_lifecycle_state") is not True:
            errors.append(
                ValidationError(
                    "register.governed_watch_eligibility.lifecycle_boundary.exclusion_requires_explicit_governed_lifecycle_state",
                    "must remain true",
                )
            )
        if boundary.get("inactive_lifecycle_values_defined_by_this_contract") != []:
            errors.append(
                ValidationError(
                    "register.governed_watch_eligibility.lifecycle_boundary.inactive_lifecycle_values_defined_by_this_contract",
                    "this contract must not invent inactive lifecycle values",
                )
            )

    return errors


def eligible_governed_watch_ids(register: dict[str, Any]) -> set[str]:
    """Return signal IDs matching the register's positive eligibility rule."""

    eligible: set[str] = set()
    for signal in register.get("signals", []):
        if not isinstance(signal, dict):
            continue
        if signal.get("review_state") != ELIGIBLE_REVIEW_STATE:
            continue
        if signal.get("lifecycle_status") not in ELIGIBLE_LIFECYCLE_STATUSES:
            continue
        signal_id = signal.get("signal_id")
        if isinstance(signal_id, str) and signal_id:
            eligible.add(signal_id)
    return eligible


def _schema_errors(schema: dict[str, Any], document: Any) -> list[ValidationError]:
    validator = Draft202012Validator(schema)
    normalized = _json_compatible(document)
    return [
        ValidationError(f"schema.{_path(error.absolute_path)}", error.message)
        for error in sorted(
            validator.iter_errors(normalized), key=lambda item: list(item.absolute_path)
        )
    ]


def _validate_registered_escalation_conditions(
    register: dict[str, Any], eligible_ids: set[str]
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for signal in register.get("signals", []):
        if not isinstance(signal, dict) or signal.get("signal_id") not in eligible_ids:
            continue
        signal_id = signal["signal_id"]
        for trigger_field in (
            "thesis_strengthening_triggers",
            "category_compression_triggers",
        ):
            triggers = signal.get(trigger_field)
            if not isinstance(triggers, list) or not triggers:
                errors.append(
                    ValidationError(
                        f"register.signals.{signal_id}.{trigger_field}",
                        "eligible governed watches must preserve stored escalation conditions",
                    )
                )
    return errors


def _validate_escalation_review(review: Any, prefix: str) -> list[ValidationError]:
    if not isinstance(review, dict):
        return [ValidationError(prefix, "must be a mapping")]

    errors: list[ValidationError] = []
    if review.get("thesis_strengthening_triggers_checked") is not True:
        errors.append(
            ValidationError(
                f"{prefix}.thesis_strengthening_triggers_checked", "must be true"
            )
        )
    if review.get("category_compression_triggers_checked") is not True:
        errors.append(
            ValidationError(
                f"{prefix}.category_compression_triggers_checked", "must be true"
            )
        )
    stored = review.get("stored_escalation_review")
    if not isinstance(stored, dict):
        errors.append(ValidationError(f"{prefix}.stored_escalation_review", "must be a mapping"))
    else:
        required = (
            "repeated_institutional_behavior_observed",
            "structural_category_movement_observed",
            "material_competitive_compression_observed",
            "evidence_insufficient_for_trigger",
        )
        for field in required:
            if not isinstance(stored.get(field), bool):
                errors.append(
                    ValidationError(f"{prefix}.stored_escalation_review.{field}", "must be boolean")
                )
    if not isinstance(review.get("escalation_condition_met"), bool):
        errors.append(ValidationError(f"{prefix}.escalation_condition_met", "must be boolean"))
    return errors


def _validate_direct_coverage(
    report: dict[str, Any],
    eligible_ids: set[str],
    registered_ids: set[str],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    coverage = report.get("governed_watch_coverage")
    if not isinstance(coverage, list):
        return [ValidationError("market_signal_report.governed_watch_coverage", "must be a list")]

    by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(coverage):
        if not isinstance(item, dict):
            continue
        signal_id = item.get("signal_id")
        if not isinstance(signal_id, str):
            continue
        if signal_id in by_id:
            errors.append(
                ValidationError(
                    f"market_signal_report.governed_watch_coverage.{index}.signal_id",
                    f"duplicate coverage for {signal_id}",
                )
            )
        by_id[signal_id] = item
        if signal_id not in registered_ids:
            errors.append(
                ValidationError(
                    f"market_signal_report.governed_watch_coverage.{index}.signal_id",
                    f"unknown register signal_id: {signal_id}",
                )
            )

    missing = eligible_ids - set(by_id)
    if missing:
        errors.append(
            ValidationError(
                "market_signal_report.governed_watch_coverage",
                f"missing mandatory governed-watch coverage: {sorted(missing)}",
            )
        )

    incomplete = False
    unattempted = False
    for signal_id in sorted(eligible_ids & set(by_id)):
        item = by_id[signal_id]
        prefix = f"market_signal_report.governed_watch_coverage.{signal_id}"
        if item.get("required_this_run") is not True:
            errors.append(ValidationError(f"{prefix}.required_this_run", "must be true"))
        if item.get("scan_attempted") is not True:
            unattempted = True
            errors.append(ValidationError(f"{prefix}.scan_attempted", "must be true"))
        if item.get("authority_effect") != "none":
            errors.append(ValidationError(f"{prefix}.authority_effect", "must be none"))

        errors.extend(_validate_escalation_review(item.get("escalation_review"), f"{prefix}.escalation_review"))

        status = item.get("scan_status")
        delta = item.get("delta_state")
        source_access = item.get("source_access")
        available = source_access.get("material_sources_available") if isinstance(source_access, dict) else None
        unavailable = source_access.get("unavailable_sources") if isinstance(source_access, dict) else None

        if available is True and unavailable:
            errors.append(
                ValidationError(
                    f"{prefix}.source_access",
                    "available material sources cannot also be listed as unavailable",
                )
            )
        if available is False and not unavailable:
            errors.append(
                ValidationError(
                    f"{prefix}.source_access.unavailable_sources",
                    "must identify unavailable material sources",
                )
            )

        if status == "completed":
            if delta not in {"no_material_delta", "material_delta_observed"}:
                errors.append(
                    ValidationError(
                        f"{prefix}.delta_state",
                        "completed scans require a material-delta classification",
                    )
                )
            if available is not True:
                errors.append(
                    ValidationError(
                        f"{prefix}.source_access.material_sources_available",
                        "completed scans require available material sources",
                    )
                )
        elif status == "source_incomplete":
            incomplete = True
            if delta not in {"source_incomplete", "source_unavailable"}:
                errors.append(
                    ValidationError(
                        f"{prefix}.delta_state",
                        "source-incomplete scans cannot claim no change or material change",
                    )
                )
            if available is not False:
                errors.append(
                    ValidationError(
                        f"{prefix}.source_access.material_sources_available",
                        "source-incomplete scans must preserve unavailable material sources",
                    )
                )

        if delta == "no_material_delta" and (available is not True or unavailable):
            errors.append(
                ValidationError(
                    f"{prefix}.delta_state",
                    "no_material_delta is invalid when material sources were unavailable",
                )
            )

    discovery = report.get("broad_discovery")
    if not isinstance(discovery, dict) or discovery.get("completed_within_stated_scope") is not True:
        incomplete = True

    aggregate = report.get("evidence_coverage")
    if missing or unattempted:
        if aggregate != "invalid":
            errors.append(
                ValidationError(
                    "market_signal_report.evidence_coverage",
                    "omitted or unattempted mandatory coverage requires invalid classification",
                )
            )
    elif incomplete:
        if aggregate != "source_incomplete":
            errors.append(
                ValidationError(
                    "market_signal_report.evidence_coverage",
                    "source limitations require source_incomplete classification",
                )
            )
    elif aggregate != "sufficient":
        errors.append(
            ValidationError(
                "market_signal_report.evidence_coverage",
                "complete mandatory coverage and discovery require sufficient classification",
            )
        )

    return errors


def _validate_reconciliation(
    report: dict[str, Any], eligible_ids: set[str]
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    discovery = report.get("broad_discovery")
    reconciliation = report.get("reconciliation")
    if not isinstance(discovery, dict) or not isinstance(reconciliation, dict):
        return errors

    observations = set(discovery.get("observations_reviewed", []))
    related_items = reconciliation.get("related_to_existing_watch", [])
    distinct = set(reconciliation.get("genuinely_distinct_candidates", []))
    new_signals = set(discovery.get("new_signals", []))

    related_ids: set[str] = set()
    for index, item in enumerate(related_items):
        if not isinstance(item, dict):
            continue
        observation_id = item.get("observation_id")
        watch_id = item.get("watch_signal_id")
        if isinstance(observation_id, str):
            if observation_id in related_ids:
                errors.append(
                    ValidationError(
                        f"market_signal_report.reconciliation.related_to_existing_watch.{index}.observation_id",
                        f"duplicate related observation: {observation_id}",
                    )
                )
            related_ids.add(observation_id)
        if watch_id not in eligible_ids:
            errors.append(
                ValidationError(
                    f"market_signal_report.reconciliation.related_to_existing_watch.{index}.watch_signal_id",
                    f"related evidence must reference an active governed watch: {watch_id!r}",
                )
            )

    overlap = related_ids & distinct
    if overlap:
        errors.append(
            ValidationError(
                "market_signal_report.reconciliation",
                f"observations cannot be both related and distinct: {sorted(overlap)}",
            )
        )

    unreconciled = observations - related_ids - distinct
    if unreconciled:
        errors.append(
            ValidationError(
                "market_signal_report.reconciliation",
                f"broad-discovery observations were not reconciled: {sorted(unreconciled)}",
            )
        )

    if new_signals != distinct:
        errors.append(
            ValidationError(
                "market_signal_report.broad_discovery.new_signals",
                "new signals must equal genuinely distinct reconciled candidates",
            )
        )

    return errors


def _validate_retrospective_reconciliation(
    report: dict[str, Any], eligible_ids: set[str]
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    expected = {
        "coverage_record_origin": "post_run_governance_reconciliation",
        "original_governed_watch_coverage_explicit": False,
        "original_run_coverage_compliant": False,
        "reconciliation_completed": True,
        "independent_external_reverification": False,
    }
    for field, value in expected.items():
        if report.get(field) != value:
            errors.append(
                ValidationError(
                    f"market_signal_report.{field}",
                    f"retrospective reconciliation requires {value!r}",
                )
            )

    provenance = report.get("source_provenance")
    if isinstance(provenance, dict):
        if report.get("source_basis") != provenance.get("status"):
            errors.append(
                ValidationError(
                    "market_signal_report.source_basis",
                    "must match the preserved source-provenance status",
                )
            )
        if provenance.get("independent_repository_verification") is not False:
            errors.append(
                ValidationError(
                    "market_signal_report.source_provenance.independent_repository_verification",
                    "retrospective specialist output must not claim repository verification",
                )
            )

    related = report.get("reconciliation", {}).get("related_to_existing_watch", [])
    related_watch_ids = {
        item.get("watch_signal_id") for item in related if isinstance(item, dict)
    }
    reviews = report.get("retrospective_watch_reconciliation")
    if not isinstance(reviews, list):
        return errors + [
            ValidationError(
                "market_signal_report.retrospective_watch_reconciliation", "must be a list"
            )
        ]

    by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(reviews):
        if not isinstance(item, dict):
            continue
        signal_id = item.get("signal_id")
        if not isinstance(signal_id, str):
            continue
        if signal_id in by_id:
            errors.append(
                ValidationError(
                    f"market_signal_report.retrospective_watch_reconciliation.{index}.signal_id",
                    f"duplicate retrospective review for {signal_id}",
                )
            )
        by_id[signal_id] = item
        if signal_id not in eligible_ids:
            errors.append(
                ValidationError(
                    f"market_signal_report.retrospective_watch_reconciliation.{index}.signal_id",
                    f"retrospective review must reference an active governed watch: {signal_id!r}",
                )
            )
        if item.get("relationship_review_completed") is not True:
            errors.append(
                ValidationError(
                    f"market_signal_report.retrospective_watch_reconciliation.{signal_id}.relationship_review_completed",
                    "must be true",
                )
            )
        if item.get("authority_effect") != "none":
            errors.append(
                ValidationError(
                    f"market_signal_report.retrospective_watch_reconciliation.{signal_id}.authority_effect",
                    "must be none",
                )
            )
        errors.extend(
            _validate_escalation_review(
                item.get("escalation_review"),
                f"market_signal_report.retrospective_watch_reconciliation.{signal_id}.escalation_review",
            )
        )

    missing_reviews = related_watch_ids - set(by_id)
    if missing_reviews:
        errors.append(
            ValidationError(
                "market_signal_report.retrospective_watch_reconciliation",
                f"missing reconciliation review for related watches: {sorted(missing_reviews)}",
            )
        )
    return errors


def validate_market_signal_run(
    register: Any,
    schema: dict[str, Any],
    document: Any,
) -> list[ValidationError]:
    """Validate one direct run or retrospective reconciliation artifact."""

    errors = validate_eligibility_contract(register)
    errors.extend(_schema_errors(schema, document))
    if not isinstance(register, dict) or not isinstance(document, dict):
        return errors

    report = document.get("market_signal_report")
    if not isinstance(report, dict):
        return errors

    eligible_ids = eligible_governed_watch_ids(register)
    if not eligible_ids:
        errors.append(
            ValidationError(
                "register.governed_watch_eligibility",
                "no eligible governed watches detected; lifecycle state requires review",
            )
        )

    registered_ids = {
        signal.get("signal_id")
        for signal in register.get("signals", [])
        if isinstance(signal, dict) and isinstance(signal.get("signal_id"), str)
    }
    errors.extend(_validate_registered_escalation_conditions(register, eligible_ids))
    errors.extend(_validate_reconciliation(report, eligible_ids))

    mode = report.get("run_mode")
    if mode == "direct_market_signal_run":
        errors.extend(_validate_direct_coverage(report, eligible_ids, registered_ids))
    elif mode == "retrospective_reconciliation":
        errors.extend(_validate_retrospective_reconciliation(report, eligible_ids))
    return errors


def validate_market_signal_run_artifacts(
    register: Any,
    schema: dict[str, Any],
    run_paths: Iterable[Path],
) -> list[ValidationError]:
    """Validate every supplied artifact independently and prefix errors by path."""

    paths = list(run_paths)
    if not paths:
        return [
            ValidationError(
                "market_signal_run_artifacts",
                f"no artifacts found for {RUN_ARTIFACT_GLOB}",
            )
        ]

    errors: list[ValidationError] = []
    for path in paths:
        try:
            document = _load_yaml(path)
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(ValidationError(path.as_posix(), f"input error: {exc}"))
            continue
        for error in validate_market_signal_run(register, schema, document):
            errors.append(
                ValidationError(f"{path.as_posix()}::{error.field}", error.message)
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate all governed market-signal run artifacts, or one artifact with --run."
        )
    )
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument(
        "--run",
        type=Path,
        help="validate one run artifact instead of discovering the canonical run surface",
    )
    args = parser.parse_args(argv)

    try:
        register = _load_yaml(_resolve_from_repo(args.register))
        schema = _load_json(_resolve_from_repo(args.schema))
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"market-signal scan input error: {exc}", file=sys.stderr)
        return 2

    run_paths = (
        [_resolve_from_repo(args.run)]
        if args.run is not None
        else discover_market_signal_run_paths()
    )
    errors = validate_market_signal_run_artifacts(register, schema, run_paths)
    if errors:
        for error in errors:
            print(error.format(), file=sys.stderr)
        return 1

    active = sorted(eligible_governed_watch_ids(register))
    print("Governed-watch scan artifact validation passed.")
    print(f"active_watches: {','.join(active)}")
    print(f"artifacts_validated: {len(run_paths)}")
    for path in run_paths:
        try:
            display = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            display = path.as_posix()
        print(f"validated: {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
