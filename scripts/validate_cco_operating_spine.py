#!/usr/bin/env python3
"""Deterministic offline validation for the Jarvis-Nova CCO Operating Spine."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT_SCHEMA_PATH = Path(
    "schemas/operations/cco_system_need_assessment_v0_1.schema.json"
)
PRIORITY_SCHEMA_PATH = Path(
    "schemas/operations/cco_priority_register_v0_1.schema.json"
)
PRIORITY_REGISTER_PATH = Path("docs/operations/cco/current-priority-register.yaml")
SOURCE_MANIFEST_PATH = Path("docs/operations/cco/operating-source-manifest.yaml")
ASSESSMENT_FIXTURE_DIR = Path("tests/fixtures/cco")

REQUIRED_ARTIFACTS = (
    Path("docs/operations/cco/README.md"),
    Path("docs/operations/cco/operating-contract-v0.1.md"),
    SOURCE_MANIFEST_PATH,
    PRIORITY_REGISTER_PATH,
    Path("docs/operations/cco/nova-api-observability-boundary.md"),
    ASSESSMENT_SCHEMA_PATH,
    PRIORITY_SCHEMA_PATH,
    Path("scripts/validate_cco_operating_spine.py"),
    Path("tests/test_cco_operating_spine.py"),
)

REQUIRED_ARTIFACT_EFFECTS = (
    "creates_corporate_accepted_state",
    "creates_chronology",
    "creates_Reflex_Memory",
    "creates_implementation_authority",
    "creates_production_authority",
    "creates_capital_authority",
    "creates_pricing_authority",
)

TERMINAL_PRIORITY_STATUSES = {"verified_complete", "closed"}
ACTIVE_PRIORITY_STATUSES = {
    "observed",
    "review_required",
    "due",
    "assigned",
    "in_progress",
    "evidence_submitted",
    "blocked",
}

PROHIBITED_POSITIVE_AUTHORITY_PHRASES = (
    "jarvis-nova authorizes capital",
    "jarvis-nova authorizes production",
    "jarvis-nova approves transactions",
    "jarvis-nova executes transactions",
    "jarvis-nova creates accepted state",
    "jarvis-nova creates pricing authority",
    "jarvis-nova may merge without external authority",
)


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))


def _load_json(path: Path) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _schema_issues(
    document: Any, schema: dict[str, Any], prefix: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path)
        field = f"{prefix}.{location}" if location else prefix
        issues.append(ValidationIssue(field, error.message))
    return issues


def _parse_timestamp(value: Any, field: str, issues: list[ValidationIssue]) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        issues.append(ValidationIssue(field, "must be an ISO-8601 date-time"))
        return None


def _freshness_issues(
    assessment: dict[str, Any],
    source_name: str,
    block_name: str,
    timestamp_name: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    block = assessment.get(block_name, {})
    if not isinstance(block, dict) or block.get("status") != "verified":
        return issues

    created = _parse_timestamp(assessment.get("created_at"), "created_at", issues)
    verified = _parse_timestamp(
        assessment.get(timestamp_name), timestamp_name, issues
    )
    nested_verified = block.get("verified_at")
    if nested_verified != assessment.get(timestamp_name):
        issues.append(
            ValidationIssue(
                timestamp_name,
                f"must equal {block_name}.verified_at for {source_name}",
            )
        )
    if created is not None and verified is not None:
        age_seconds = (created - verified).total_seconds()
        if age_seconds < 0 or age_seconds > 300:
            issues.append(
                ValidationIssue(
                    timestamp_name,
                    "verified dynamic source must be within five minutes of assessment",
                )
            )
    return issues


def validate_assessment_document(document: Any) -> list[ValidationIssue]:
    """Validate one machine-readable CCO assessment."""

    schema = _load_json(ASSESSMENT_SCHEMA_PATH)
    issues = _schema_issues(document, schema, "assessment")
    if not isinstance(document, dict):
        return issues
    assessment = document.get("cco_system_need_assessment")
    if not isinstance(assessment, dict):
        return issues

    source_scope = assessment.get("source_scope", {})
    repo_verification = assessment.get("repository_verification", {})
    pr_verification = assessment.get("open_pr_verification", {})

    if isinstance(source_scope, dict):
        repo_locations = {
            state: "repository_remote_main" in (source_scope.get(state) or [])
            for state in ("available", "unavailable", "stale", "not_checked")
        }
        expected_repo_status = {
            "available": "verified",
            "unavailable": "unavailable",
            "stale": "stale",
            "not_checked": "not_checked",
        }
        for state, present in repo_locations.items():
            if present and isinstance(repo_verification, dict):
                if repo_verification.get("status") != expected_repo_status[state]:
                    issues.append(
                        ValidationIssue(
                            "repository_verification.status",
                            f"must reflect repository_remote_main source state {state}",
                        )
                    )

        pr_locations = {
            state: "material_open_prs" in (source_scope.get(state) or [])
            for state in ("available", "unavailable", "stale", "not_checked")
        }
        for state, present in pr_locations.items():
            if present and isinstance(pr_verification, dict):
                if pr_verification.get("status") != expected_repo_status[state]:
                    issues.append(
                        ValidationIssue(
                            "open_pr_verification.status",
                            f"must reflect material_open_prs source state {state}",
                        )
                    )

    for index, conclusion in enumerate(assessment.get("source_conclusions", [])):
        if not isinstance(conclusion, dict):
            continue
        availability = conclusion.get("availability")
        result = conclusion.get("conclusion")
        if availability in {"unavailable", "not_checked", "stale"} and result != "unknown":
            issues.append(
                ValidationIssue(
                    f"source_conclusions.{index}.conclusion",
                    f"{availability} source must remain unknown, not {result!r}",
                )
            )

    issues.extend(
        _freshness_issues(
            assessment,
            "repository remote main",
            "repository_verification",
            "repository_verified_at",
        )
    )
    issues.extend(
        _freshness_issues(
            assessment,
            "material open PRs",
            "open_pr_verification",
            "open_prs_verified_at",
        )
    )

    routing = assessment.get("attention_routing", {})
    if isinstance(routing, dict):
        if routing.get("authority_required") is True and routing.get("authority_owner") != "Architect":
            issues.append(
                ValidationIssue(
                    "attention_routing.authority_owner",
                    "current canonical authority owner must be Architect",
                )
            )
        if routing.get("authority_status") == "externally_granted":
            if not routing.get("authority_evidence_reference"):
                issues.append(
                    ValidationIssue(
                        "attention_routing.authority_evidence_reference",
                        "externally granted authority requires evidence",
                    )
                )
            if routing.get("authority_evidence_source") != "external_authority_record":
                issues.append(
                    ValidationIssue(
                        "attention_routing.authority_evidence_source",
                        "a CCO recommendation cannot serve as authority evidence",
                    )
                )

    effects = assessment.get("assessment_artifact_effect", {})
    if isinstance(effects, dict):
        for key in REQUIRED_ARTIFACT_EFFECTS:
            if effects.get(key) is not False:
                issues.append(
                    ValidationIssue(
                        f"assessment_artifact_effect.{key}",
                        "CCO assessment artifacts must have this effect set to false",
                    )
                )

    observed = assessment.get("observed_state_delta", {})
    evidence = assessment.get("state_change_evidence", {})
    if isinstance(observed, dict) and isinstance(evidence, dict):
        evidence_rules = (
            ("canonical_corporate_state_changed", "canonical_corporate_state"),
            ("production_change", "production"),
            ("chronology_change", "chronology"),
        )
        for change_field, evidence_field in evidence_rules:
            if observed.get(change_field) is True and not evidence.get(evidence_field):
                issues.append(
                    ValidationIssue(
                        f"state_change_evidence.{evidence_field}",
                        f"required when {change_field} is true",
                    )
                )

    api = assessment.get("api_observability", {})
    if isinstance(api, dict):
        repository = api.get("repository_implementation", {})
        if isinstance(repository, dict) and repository.get("treated_as_deployed_runtime") is not False:
            issues.append(
                ValidationIssue(
                    "api_observability.repository_implementation.treated_as_deployed_runtime",
                    "repository implementation cannot be treated as deployed runtime",
                )
            )

    generation = assessment.get("product_generation", {})
    if isinstance(generation, dict) and generation.get("target_v2_contract_treated_as_runtime") is not False:
        issues.append(
            ValidationIssue(
                "product_generation.target_v2_contract_treated_as_runtime",
                "target-v2 contract approval does not establish target-v2 runtime",
            )
        )

    return issues


def validate_priority_register_document(document: Any) -> list[ValidationIssue]:
    """Validate the CCO priority register and terminal-state integrity."""

    schema = _load_json(PRIORITY_SCHEMA_PATH)
    issues = _schema_issues(document, schema, "priority_register")
    if not isinstance(document, dict):
        return issues

    seen_ids: set[str] = set()
    seen_ranks: set[int] = set()
    for index, item in enumerate(document.get("items", [])):
        if not isinstance(item, dict):
            continue
        prefix = f"priority_register.items.{index}"
        item_id = item.get("item_id")
        rank = item.get("priority_rank")
        if item_id in seen_ids:
            issues.append(ValidationIssue(f"{prefix}.item_id", "must be unique"))
        if isinstance(item_id, str):
            seen_ids.add(item_id)
        if rank in seen_ranks:
            issues.append(ValidationIssue(f"{prefix}.priority_rank", "must be unique"))
        if isinstance(rank, int):
            seen_ranks.add(rank)

        if item.get("status") in ACTIVE_PRIORITY_STATUSES:
            for field in ("recommended_owner", "blocking", "completion_condition"):
                value = item.get(field)
                if value is None or (isinstance(value, str) and not value.strip()):
                    issues.append(
                        ValidationIssue(
                            f"{prefix}.{field}",
                            "active action requires this field",
                        )
                    )

        evidence = item.get("completion_evidence", {})
        if item.get("status") in TERMINAL_PRIORITY_STATUSES and isinstance(evidence, dict):
            terminal_values = {
                "artifact_or_registry_path": lambda value: isinstance(value, str) and bool(value.strip()),
                "resulting_commit_or_record_id": lambda value: isinstance(value, str) and bool(value.strip()),
                "completed_at": lambda value: isinstance(value, str) and bool(value.strip()),
                "writer_authority": lambda value: isinstance(value, str) and bool(value.strip()),
                "historical_entries_preserved": lambda value: value is True,
                "provenance_preserved": lambda value: value is True,
                "silent_overwrite_detected": lambda value: value is False,
                "independently_verified_at": lambda value: isinstance(value, str) and bool(value.strip()),
            }
            for field, predicate in terminal_values.items():
                if not predicate(evidence.get(field)):
                    issues.append(
                        ValidationIssue(
                            f"{prefix}.completion_evidence.{field}",
                            "terminal item lacks valid completion evidence",
                        )
                    )

        if isinstance(evidence, dict) and evidence.get("silent_overwrite_detected") is True:
            issues.append(
                ValidationIssue(
                    f"{prefix}.completion_evidence.silent_overwrite_detected",
                    "completion evidence cannot contain a silent overwrite",
                )
            )

    return issues


def _iter_assessment_fixtures() -> Iterable[Path]:
    fixture_root = REPO_ROOT / ASSESSMENT_FIXTURE_DIR
    yield from sorted(fixture_root.glob("*.yaml"))
    yield from sorted(fixture_root.glob("*.yml"))
    yield from sorted(fixture_root.glob("*.json"))


def validate_repository() -> list[ValidationIssue]:
    """Validate all CCO spine artifacts without network or runtime access."""

    issues: list[ValidationIssue] = []
    for path in REQUIRED_ARTIFACTS:
        if not (REPO_ROOT / path).is_file():
            issues.append(ValidationIssue("required_artifact", f"missing {path}"))

    for schema_path in (ASSESSMENT_SCHEMA_PATH, PRIORITY_SCHEMA_PATH):
        try:
            Draft202012Validator.check_schema(_load_json(schema_path))
        except (OSError, json.JSONDecodeError, SchemaError) as exc:
            issues.append(ValidationIssue(str(schema_path), f"invalid schema: {exc}"))

    try:
        manifest = _load_yaml(SOURCE_MANIFEST_PATH)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        issues.append(ValidationIssue(str(SOURCE_MANIFEST_PATH), f"cannot load: {exc}"))
        manifest = {}

    if isinstance(manifest, dict):
        for index, source in enumerate(manifest.get("sources", [])):
            if not isinstance(source, dict):
                continue
            repository_path = source.get("repository_path")
            if repository_path and not (REPO_ROOT / repository_path).exists():
                issues.append(
                    ValidationIssue(
                        f"source_manifest.sources.{index}.repository_path",
                        f"claimed repository path does not exist: {repository_path}",
                    )
                )

    try:
        priority_register = _load_yaml(PRIORITY_REGISTER_PATH)
        issues.extend(validate_priority_register_document(priority_register))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        issues.append(ValidationIssue(str(PRIORITY_REGISTER_PATH), f"cannot load: {exc}"))

    fixtures = list(_iter_assessment_fixtures())
    if not fixtures:
        issues.append(ValidationIssue("assessment_fixtures", "no assessment fixture found"))
    for path in fixtures:
        try:
            if path.suffix == ".json":
                document = json.loads(path.read_text(encoding="utf-8"))
            else:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
            issues.extend(validate_assessment_document(document))
        except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
            issues.append(ValidationIssue(str(path.relative_to(REPO_ROOT)), f"cannot load: {exc}"))

    for path in (
        Path("docs/operations/cco/README.md"),
        Path("docs/operations/cco/operating-contract-v0.1.md"),
        Path("docs/operations/cco/nova-api-observability-boundary.md"),
    ):
        try:
            lowered = (REPO_ROOT / path).read_text(encoding="utf-8").lower()
        except (OSError, UnicodeError):
            continue
        for phrase in PROHIBITED_POSITIVE_AUTHORITY_PHRASES:
            if phrase in lowered:
                issues.append(
                    ValidationIssue(
                        str(path),
                        f"prohibited positive authority claim: {phrase!r}",
                    )
                )

    return issues


def main() -> int:
    issues = validate_repository()
    if issues:
        print("CCO operating spine validation failed:")
        for issue in issues:
            print(f"- {issue.format()}")
        return 1
    print("CCO operating spine validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
