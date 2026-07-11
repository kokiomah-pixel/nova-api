#!/usr/bin/env python3
"""
Offline validator for Sharpe Nova OS deep institutional scenarios.

The runner validates fixture structure, scenario distribution, state transitions,
authority boundaries, chronology behavior, Reflex Memory relevance, and recovery.

It does not execute capital actions or make local decisions.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = ROOT_DIR / "fixtures" / "deep_scenarios"

REQUIRED_FAMILIES = {
    "authority_boundary",
    "incomplete_context",
    "temporal_memory",
    "operator_pressure",
    "neutral_outcomes",
    "recovery",
}

APPROVED_PERSONAS = {
    "treasury_operator",
    "investment_committee_reviewer",
    "risk_officer",
    "governance_operator",
    "technical_integrator",
    "executive_approver",
}

ALLOWED_REVIEW_POSTURES = {
    "ordinary_review",
    "insufficient_context",
    "constrained_review",
    "source_reconciliation_required",
    "chronology_review_required",
    "exception_visibility_required",
    "reviewable_with_disclosed_uncertainty",
}

ALLOWED_CHRONOLOGY_ACTIONS = {
    "no_candidate",
    "candidate",
    "retain_candidate",
}

ALLOWED_MEMORY_RELEVANCE = {
    "none",
    "relevant",
    "irrelevant",
    "uncertain",
    "stale",
    "conflicting",
}

ALLOWED_SOURCE_STATES = {
    "current",
    "incomplete",
    "unverified",
    "conflicting",
    "stale",
    "mixed",
}

PROHIBITED_AUTHORITY_PHRASES = {
    "nova approved",
    "nova rejected",
    "nova authorized",
    "nova blocked",
    "nova allowed",
    "nova denied",
    "nova executed",
    "authority_effect: approved",
    "authority_effect: rejected",
    "authority_effect: authorized",
}

REQUIRED_SCENARIO_FIELDS = {
    "scenario_id",
    "family",
    "title",
    "persona",
    "description",
    "initial_state",
    "stages",
    "expected_final_state",
    "non_claims",
}

REQUIRED_STAGE_FIELDS = {
    "stage_id",
    "event",
    "evidence_delta",
    "expected_review_posture",
    "expected_authority_effect",
    "expected_chronology_action",
    "expected_reflex_memory_relevance",
    "expected_unresolved_items",
    "expected_source_state",
}


class ScenarioValidationError(ValueError):
    """Raised when a deep scenario violates the validation standard."""


@dataclass(frozen=True)
class ScenarioRecord:
    family: str
    source_file: Path
    payload: dict[str, Any]


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ScenarioValidationError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ScenarioValidationError(f"Fixture root must be a mapping: {path}")

    return data


def load_scenarios(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> list[ScenarioRecord]:
    if not fixture_dir.is_dir():
        raise ScenarioValidationError(
            f"Deep scenario fixture directory does not exist: {fixture_dir}"
        )

    records: list[ScenarioRecord] = []

    for path in sorted(fixture_dir.glob("*.yaml")):
        document = load_yaml(path)
        family = document.get("family")
        scenarios = document.get("scenarios")

        if family not in REQUIRED_FAMILIES:
            raise ScenarioValidationError(f"{path}: unknown or missing family: {family!r}")

        if not isinstance(scenarios, list) or not scenarios:
            raise ScenarioValidationError(f"{path}: scenarios must be a non-empty list")

        for payload in scenarios:
            if not isinstance(payload, dict):
                raise ScenarioValidationError(f"{path}: each scenario must be a mapping")

            records.append(
                ScenarioRecord(
                    family=family,
                    source_file=path,
                    payload=payload,
                )
            )

    return records


def require_fields(payload: dict[str, Any], required: set[str], context: str) -> None:
    missing = sorted(required - set(payload))
    if missing:
        raise ScenarioValidationError(
            f"{context}: missing required fields: {', '.join(missing)}"
        )


def validate_evidence_delta(delta: Any, context: str) -> None:
    if not isinstance(delta, dict):
        raise ScenarioValidationError(f"{context}: evidence_delta must be a mapping")

    if set(delta) != {"added", "removed"}:
        raise ScenarioValidationError(
            f"{context}: evidence_delta must contain exactly added and removed"
        )

    for key in ("added", "removed"):
        if not isinstance(delta[key], list):
            raise ScenarioValidationError(
                f"{context}: evidence_delta.{key} must be a list"
            )


def validate_stage(
    stage: dict[str, Any],
    *,
    scenario_id: str,
    stage_index: int,
) -> None:
    context = f"{scenario_id} stage {stage_index}"
    require_fields(stage, REQUIRED_STAGE_FIELDS, context)

    if not isinstance(stage["stage_id"], str) or not stage["stage_id"].strip():
        raise ScenarioValidationError(f"{context}: stage_id must be a non-empty string")

    if stage["expected_review_posture"] not in ALLOWED_REVIEW_POSTURES:
        raise ScenarioValidationError(
            f"{context}: invalid expected_review_posture "
            f"{stage['expected_review_posture']!r}"
        )

    if stage["expected_authority_effect"] != "none":
        raise ScenarioValidationError(f"{context}: expected_authority_effect must be none")

    if stage["expected_chronology_action"] not in ALLOWED_CHRONOLOGY_ACTIONS:
        raise ScenarioValidationError(
            f"{context}: invalid expected_chronology_action "
            f"{stage['expected_chronology_action']!r}"
        )

    if stage["expected_reflex_memory_relevance"] not in ALLOWED_MEMORY_RELEVANCE:
        raise ScenarioValidationError(
            f"{context}: invalid expected_reflex_memory_relevance "
            f"{stage['expected_reflex_memory_relevance']!r}"
        )

    if stage["expected_source_state"] not in ALLOWED_SOURCE_STATES:
        raise ScenarioValidationError(
            f"{context}: invalid expected_source_state "
            f"{stage['expected_source_state']!r}"
        )

    if not isinstance(stage["expected_unresolved_items"], list):
        raise ScenarioValidationError(
            f"{context}: expected_unresolved_items must be a list"
        )

    validate_evidence_delta(stage["evidence_delta"], context)


def validate_scenario(record: ScenarioRecord) -> None:
    scenario = record.payload
    scenario_id = str(scenario.get("scenario_id", "<unknown>"))

    require_fields(scenario, REQUIRED_SCENARIO_FIELDS, scenario_id)

    if not scenario_id.startswith("DSC-"):
        raise ScenarioValidationError(f"{scenario_id}: scenario_id must begin with DSC-")

    if scenario["family"] != record.family:
        raise ScenarioValidationError(
            f"{scenario_id}: scenario family {scenario['family']!r} "
            f"does not match fixture family {record.family!r}"
        )

    if scenario["persona"] not in APPROVED_PERSONAS:
        raise ScenarioValidationError(
            f"{scenario_id}: unsupported persona {scenario['persona']!r}"
        )

    stages = scenario["stages"]

    if not isinstance(stages, list) or len(stages) < 3:
        raise ScenarioValidationError(f"{scenario_id}: at least three stages are required")

    stage_ids: set[str] = set()

    for index, stage in enumerate(stages, start=1):
        if not isinstance(stage, dict):
            raise ScenarioValidationError(
                f"{scenario_id} stage {index}: stage must be a mapping"
            )

        validate_stage(stage, scenario_id=scenario_id, stage_index=index)

        stage_id = stage["stage_id"]

        if stage_id in stage_ids:
            raise ScenarioValidationError(f"{scenario_id}: duplicate stage_id {stage_id!r}")

        stage_ids.add(stage_id)

    expected_final_state = scenario["expected_final_state"]

    if not isinstance(expected_final_state, dict):
        raise ScenarioValidationError(
            f"{scenario_id}: expected_final_state must be a mapping"
        )

    if expected_final_state.get("authority_effect") != "none":
        raise ScenarioValidationError(f"{scenario_id}: final authority_effect must be none")

    if expected_final_state.get("action_decision_owner") != "local_authority":
        raise ScenarioValidationError(
            f"{scenario_id}: action_decision_owner must be local_authority"
        )

    final_posture = expected_final_state.get("review_posture")

    if final_posture not in ALLOWED_REVIEW_POSTURES:
        raise ScenarioValidationError(
            f"{scenario_id}: invalid final review posture {final_posture!r}"
        )

    actual_final_posture = stages[-1]["expected_review_posture"]

    if actual_final_posture != final_posture:
        raise ScenarioValidationError(
            f"{scenario_id}: final stage posture {actual_final_posture!r} "
            f"does not match expected_final_state {final_posture!r}"
        )

    non_claims = scenario["non_claims"]

    if not isinstance(non_claims, list) or not non_claims:
        raise ScenarioValidationError(f"{scenario_id}: non_claims must be a non-empty list")


def validate_unique_scenario_ids(records: Iterable[ScenarioRecord]) -> None:
    seen: set[str] = set()

    for record in records:
        scenario_id = record.payload["scenario_id"]

        if scenario_id in seen:
            raise ScenarioValidationError(f"Duplicate scenario_id: {scenario_id}")

        seen.add(scenario_id)


def validate_distribution(records: list[ScenarioRecord]) -> None:
    families = Counter(record.family for record in records)

    if set(families) != REQUIRED_FAMILIES:
        raise ScenarioValidationError(
            "Scenario fixtures do not cover exactly the required families"
        )

    if len(records) < 16:
        raise ScenarioValidationError(
            f"Expected at least 16 deep scenarios, found {len(records)}"
        )

    final_postures = Counter(
        record.payload["expected_final_state"]["review_posture"] for record in records
    )

    if final_postures["ordinary_review"] < 3:
        raise ScenarioValidationError(
            "At least three scenarios must end in ordinary_review"
        )

    if final_postures["reviewable_with_disclosed_uncertainty"] < 2:
        raise ScenarioValidationError(
            "At least two scenarios must end in reviewable_with_disclosed_uncertainty"
        )

    if final_postures["source_reconciliation_required"] < 2:
        raise ScenarioValidationError(
            "At least two scenarios must end in source_reconciliation_required"
        )


def scan_authority_language(records: Iterable[ScenarioRecord]) -> None:
    for record in records:
        scenario = record.payload
        scenario_id = scenario["scenario_id"]

        expected_payload = {
            "stages": [
                {
                    "expected_review_posture": stage["expected_review_posture"],
                    "expected_authority_effect": stage["expected_authority_effect"],
                    "expected_chronology_action": stage["expected_chronology_action"],
                    "expected_reflex_memory_relevance": stage[
                        "expected_reflex_memory_relevance"
                    ],
                    "expected_unresolved_items": stage["expected_unresolved_items"],
                    "expected_source_state": stage["expected_source_state"],
                }
                for stage in scenario["stages"]
            ],
            "expected_final_state": scenario["expected_final_state"],
        }

        serialized = json.dumps(expected_payload).lower()

        for phrase in PROHIBITED_AUTHORITY_PHRASES:
            if phrase in serialized:
                raise ScenarioValidationError(
                    f"{scenario_id}: prohibited authority phrase found in expected "
                    f"state: {phrase!r}"
                )


def run_validation(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    records = load_scenarios(fixture_dir)

    validate_unique_scenario_ids(records)

    for record in records:
        validate_scenario(record)

    validate_distribution(records)
    scan_authority_language(records)

    family_distribution = Counter(record.family for record in records)
    persona_distribution = Counter(record.payload["persona"] for record in records)
    final_posture_distribution = Counter(
        record.payload["expected_final_state"]["review_posture"] for record in records
    )
    stage_count = sum(len(record.payload["stages"]) for record in records)

    return {
        "status": "passed",
        "scenario_count": len(records),
        "stage_count": stage_count,
        "family_distribution": dict(sorted(family_distribution.items())),
        "persona_distribution": dict(sorted(persona_distribution.items())),
        "final_posture_distribution": dict(sorted(final_posture_distribution.items())),
        "authority_effect": "none",
        "execution_capability": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Sharpe Nova OS deep scenario fixtures."
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the validation report as JSON.",
    )
    args = parser.parse_args()

    try:
        report = run_validation(args.fixture_dir)
    except ScenarioValidationError as exc:
        print(f"Deep scenario validation failed: {exc}")
        raise SystemExit(1) from exc

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print("Deep scenario validation passed.")
    print(f"Scenarios: {report['scenario_count']}")
    print(f"Stages: {report['stage_count']}")
    print(f"Authority effect: {report['authority_effect']}")
    print("Execution capability: false")


if __name__ == "__main__":
    main()
