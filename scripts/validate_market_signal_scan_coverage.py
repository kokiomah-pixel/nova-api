#!/usr/bin/env python3
"""Validate governed-watch continuity in a bounded market-signal scan."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = Path("docs/market/market-signal-watch-register.yaml")
SCHEMA_PATH = Path("schemas/market/market_signal_run_v0_1.schema.json")
DEFAULT_RUN_PATH = Path("docs/market/runs/2026/MSR-2026-08-09-001.yaml")

ELIGIBILITY_VERSION = "governed_watch_eligibility_v0_1"
ELIGIBLE_REVIEW_STATE = "governed_watch"
ELIGIBLE_LIFECYCLE_STATUSES = {"observed_watch"}
LATEST_RECONCILIATION_ID = "MSR-2026-08-09-001"

REQUIRED_LATEST_RELATIONSHIPS = {
    "Formance_autonomous_finance": {
        "execution_and_ledger_category_compression",
        "agentic_finance_problem_legibility",
    },
    "commercetools_authorization_commentary": {
        "authorization_language_compression",
        "category_confusion_pressure",
    },
    "institutional_AI_governance_analysis": {
        "institutional_governance_problem_legibility",
        "temporal_governance_state_pressure",
    },
}

REQUIRED_LATEST_NON_CLAIMS = {
    "Arc_watch_escalation_trigger_met",
    "Nova_buyer_pull",
    "Nova_adoption",
    "Nova_pricing_power",
    "Nova_workflow_dependency",
    "institutional_requirement_for_Nova",
    "architecture_change",
    "engineering_authority",
}

EXPECTED_LATEST_AGGREGATE = {
    "environmental_pressure": "increasing",
    "category_compression": "increasing",
    "Nova_problem_legibility": "strengthening",
    "direct_Nova_buyer_evidence": "none",
    "buyer_pull": "none",
    "adoption": "none",
    "workflow_dependency": "none",
}


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
        for error in sorted(validator.iter_errors(normalized), key=lambda item: list(item.absolute_path))
    ]


def _validate_coverage_semantics(
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
    for signal_id in sorted(eligible_ids & set(by_id)):
        item = by_id[signal_id]
        prefix = f"market_signal_report.governed_watch_coverage.{signal_id}"
        if item.get("required_this_run") is not True:
            errors.append(ValidationError(f"{prefix}.required_this_run", "must be true"))
        if item.get("scan_attempted") is not True:
            errors.append(ValidationError(f"{prefix}.scan_attempted", "must be true"))
        if item.get("authority_effect") != "none":
            errors.append(ValidationError(f"{prefix}.authority_effect", "must be none"))

        review = item.get("escalation_review")
        if isinstance(review, dict):
            if review.get("thesis_strengthening_triggers_checked") is not True:
                errors.append(
                    ValidationError(
                        f"{prefix}.escalation_review.thesis_strengthening_triggers_checked",
                        "must be true",
                    )
                )
            if review.get("category_compression_triggers_checked") is not True:
                errors.append(
                    ValidationError(
                        f"{prefix}.escalation_review.category_compression_triggers_checked",
                        "must be true",
                    )
                )

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
    discovery_complete = (
        discovery.get("completed_within_stated_scope")
        if isinstance(discovery, dict)
        else None
    )
    if discovery_complete is not True:
        incomplete = True

    aggregate = report.get("evidence_coverage")
    if missing or any(error.field.endswith("scan_attempted") for error in errors):
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
    report: dict[str, Any],
    eligible_ids: set[str],
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


def _validate_run_origin(report: dict[str, Any]) -> list[ValidationError]:
    mode = report.get("run_mode")
    origin = report.get("coverage_record_origin")
    original_explicit = report.get("original_output_watch_coverage_explicit")
    if mode == "retrospective_reconciliation":
        if origin != "post_run_governance_reconciliation" or original_explicit is not False:
            return [
                ValidationError(
                    "market_signal_report.run_mode",
                    "retrospective reconciliation must preserve that original watch coverage was absent",
                )
            ]
    elif mode == "direct_market_signal_run":
        if origin != "contemporaneous_scan" or original_explicit is not True:
            return [
                ValidationError(
                    "market_signal_report.run_mode",
                    "direct runs require contemporaneous explicit governed-watch coverage",
                )
            ]
    return []


def _validate_latest_reconciliation(report: dict[str, Any]) -> list[ValidationError]:
    if report.get("report_id") != LATEST_RECONCILIATION_ID:
        return []

    errors: list[ValidationError] = []
    provenance = report.get("source_provenance")
    expected_provenance = {
        "source": "Market_Signal_Agent_brief",
        "status": "specialist_output",
        "independent_repository_verification": False,
    }
    if provenance != expected_provenance:
        errors.append(
            ValidationError(
                "market_signal_report.source_provenance",
                "latest brief must remain unverified specialist output",
            )
        )

    reconciliation = report.get("reconciliation", {})
    actual: dict[str, set[str]] = {}
    for item in reconciliation.get("related_to_existing_watch", []):
        if not isinstance(item, dict):
            continue
        observation_id = item.get("observation_id")
        if isinstance(observation_id, str):
            actual[observation_id] = set(item.get("relationship", []))
        if item.get("provenance") != expected_provenance:
            errors.append(
                ValidationError(
                    f"market_signal_report.reconciliation.{observation_id}.provenance",
                    "related context must preserve specialist-output provenance",
                )
            )
    if actual != REQUIRED_LATEST_RELATIONSHIPS:
        errors.append(
            ValidationError(
                "market_signal_report.reconciliation.related_to_existing_watch",
                "latest brief relationship map is incomplete or changed",
            )
        )

    if report.get("aggregate_state") != EXPECTED_LATEST_AGGREGATE:
        errors.append(
            ValidationError(
                "market_signal_report.aggregate_state",
                "latest brief aggregate interpretation is incomplete or changed",
            )
        )

    not_established = set(report.get("not_established", []))
    missing_non_claims = REQUIRED_LATEST_NON_CLAIMS - not_established
    if missing_non_claims:
        errors.append(
            ValidationError(
                "market_signal_report.not_established",
                f"missing required non-claims: {sorted(missing_non_claims)}",
            )
        )

    coverage = report.get("governed_watch_coverage", [])
    arc = next(
        (
            item
            for item in coverage
            if isinstance(item, dict) and item.get("signal_id") == "ARC_AGENTIC_FINANCE_2026"
        ),
        None,
    )
    review = arc.get("escalation_review") if isinstance(arc, dict) else None
    if not isinstance(review, dict) or review.get("escalation_condition_met") is not False:
        errors.append(
            ValidationError(
                "market_signal_report.governed_watch_coverage.ARC_AGENTIC_FINANCE_2026.escalation_condition_met",
                "latest brief does not establish an Arc escalation trigger",
            )
        )

    return errors


def validate_market_signal_run(
    register: Any,
    schema: dict[str, Any],
    document: Any,
) -> list[ValidationError]:
    """Validate schema, watch coverage, reconciliation, and non-authority."""

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
    errors.extend(_validate_coverage_semantics(report, eligible_ids, registered_ids))
    errors.extend(_validate_run_origin(report))
    errors.extend(_validate_reconciliation(report, eligible_ids))
    errors.extend(_validate_latest_reconciliation(report))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate mandatory governed-watch coverage in a market-signal run."
    )
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN_PATH)
    args = parser.parse_args(argv)

    try:
        register = _load_yaml(REPO_ROOT / args.register)
        schema = _load_json(REPO_ROOT / args.schema)
        document = _load_yaml(REPO_ROOT / args.run)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"market-signal scan input error: {exc}", file=sys.stderr)
        return 2

    errors = validate_market_signal_run(register, schema, document)
    if errors:
        for error in errors:
            print(error.format(), file=sys.stderr)
        return 1

    report = document["market_signal_report"]
    active = sorted(eligible_governed_watch_ids(register))
    print("Governed-watch scan coverage validation passed.")
    print(f"active_watches: {','.join(active)}")
    print(f"evidence_coverage: {report['evidence_coverage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
