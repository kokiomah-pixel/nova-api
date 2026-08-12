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
    Path("docs/operations/cco/jarvis-nova-command-contract-v0.1.md"),
    SOURCE_MANIFEST_PATH,
    PRIORITY_REGISTER_PATH,
    Path("docs/operations/cco/nova-api-observability-boundary.md"),
    ASSESSMENT_SCHEMA_PATH,
    PRIORITY_SCHEMA_PATH,
    Path("scripts/validate_cco_operating_spine.py"),
    Path("scripts/jarvis_nova_commands.py"),
    Path("tests/test_cco_operating_spine.py"),
    Path("tests/test_jarvis_nova_commands.py"),
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
COMPLETION_EVIDENCE_REQUIREMENTS = (
    (
        "artifact_or_registry_path",
        lambda value: isinstance(value, str) and bool(value.strip()),
    ),
    (
        "resulting_commit_or_record_id",
        lambda value: isinstance(value, str) and bool(value.strip()),
    ),
    ("completed_at", lambda value: isinstance(value, str) and bool(value.strip())),
    ("writer_authority", lambda value: isinstance(value, str) and bool(value.strip())),
    ("historical_entries_preserved", lambda value: value is True),
    ("provenance_preserved", lambda value: value is True),
    ("silent_overwrite_detected", lambda value: value is False),
    (
        "independently_verified_at",
        lambda value: isinstance(value, str) and bool(value.strip()),
    ),
)
MANDATORY_OPERATIONAL_SOURCES = (
    "repository_remote_main",
    "material_open_prs",
    "current_product_state",
    "production_readiness",
    "target_v2_contract",
    "cco_priority_register",
)
PRODUCTION_ATTESTATION_CONTRACT = (
    "docs/operations/production-control-plane-attestation.md"
)
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
    "jarvis-nova " + "authorizes capital",
    "jarvis-nova " + "authorizes production",
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


def _attestation_reference_issues(
    evidence_reference: Any,
    assessment_id: Any,
    field: str,
) -> list[ValidationIssue]:
    """Reject a template or the current CCO assessment as production evidence."""

    if not isinstance(evidence_reference, str):
        return []
    normalized = evidence_reference.strip().lower()
    normalized_assessment_id = (
        assessment_id.strip().lower() if isinstance(assessment_id, str) else ""
    )
    self_references = {
        normalized_assessment_id,
        f"cco_assessment:{normalized_assessment_id}",
        f"cco-assessment:{normalized_assessment_id}",
    }
    if (
        normalized == PRODUCTION_ATTESTATION_CONTRACT.lower()
        or normalized in self_references
        or "cco_system_need_assessment" in normalized
        or "cco-system-need-assessment" in normalized
        or "system-need-assessment" in normalized
        or normalized.startswith("cco-assessment")
    ):
        return [
            ValidationIssue(
                field,
                "must identify independent production evidence outside the CCO assessment and its contract template",
            )
        ]
    return []


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

        limitation_entries = assessment.get("source_limitations", [])
        limitation_counts: dict[str, int] = {}
        for entry in limitation_entries:
            if isinstance(entry, dict) and isinstance(entry.get("source_id"), str):
                source_id = entry["source_id"]
                limitation_counts[source_id] = limitation_counts.get(source_id, 0) + 1
        for source_id, count in limitation_counts.items():
            if count > 1:
                issues.append(
                    ValidationIssue(
                        "source_limitations",
                        f"source {source_id!r} has more than one limitation entry",
                    )
                )

        if assessment.get("record_source_type") == "operational_assessment":
            for source_id in MANDATORY_OPERATIONAL_SOURCES:
                states = [
                    state
                    for state in ("available", "unavailable", "stale", "not_checked")
                    if source_id in (source_scope.get(state) or [])
                ]
                if len(states) != 1:
                    issues.append(
                        ValidationIssue(
                            "source_scope",
                            f"mandatory operational source {source_id!r} must appear in exactly one availability bucket",
                        )
                    )
                    continue
                if states[0] != "available" and limitation_counts.get(source_id, 0) != 1:
                    issues.append(
                        ValidationIssue(
                            "source_limitations",
                            f"mandatory operational source {source_id!r} in state {states[0]!r} requires one explicit limitation",
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

    comparison_baseline = assessment.get("comparison_baseline")
    comparison_claims = {
        conclusion.get("conclusion")
        for conclusion in assessment.get("source_conclusions", [])
        if isinstance(conclusion, dict)
    }
    material_delta = assessment.get("material_delta", {})
    material_status = (
        material_delta.get("status") if isinstance(material_delta, dict) else None
    )
    baseline_type = (
        comparison_baseline.get("baseline_type")
        if isinstance(comparison_baseline, dict)
        else None
    )
    if "observed_change" in comparison_claims:
        expected_material_status = "observed_change"
    elif "no_material_delta" in comparison_claims:
        expected_material_status = "no_material_delta"
    else:
        expected_material_status = "unknown"
    if material_status != expected_material_status:
        issues.append(
            ValidationIssue(
                "material_delta.status",
                f"must be {expected_material_status!r} for the recorded source conclusions",
            )
        )
    if baseline_type == "explicit_initial_baseline":
        if material_status != "unknown" or comparison_claims & {
            "observed_change",
            "no_material_delta",
        }:
            issues.append(
                ValidationIssue(
                    "comparison_baseline.baseline_type",
                    "an explicit initial baseline cannot support observed-change or no-material-delta claims",
                )
            )
    if material_status in {"observed_change", "no_material_delta"}:
        if baseline_type not in {
            "prior_verified_assessment",
            "verified_repository_snapshot",
        }:
            issues.append(
                ValidationIssue(
                    "comparison_baseline",
                    "observed change and no-material-delta require a distinct prior verified assessment or repository snapshot",
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
            authority_reference = routing.get("authority_evidence_reference")
            if isinstance(authority_reference, str) and authority_reference.strip().lower() in {
                "jarvis-nova",
                "jarvis_nova",
                "jarvis-nova cco",
                "jarvis_nova_cco",
                "cco recommendation",
            }:
                issues.append(
                    ValidationIssue(
                        "attention_routing.authority_evidence_reference",
                        "Jarvis-Nova and its recommendation cannot serve as authority evidence",
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

        accepted_registry = yaml.safe_load(
            (REPO_ROOT / "agent_files/state/accepted-state-registry.yaml").read_text(
                encoding="utf-8"
            )
        )
        accepted_ids = {
            entry.get("accepted_state_id")
            for entry in accepted_registry.get("entries", [])
            if isinstance(entry, dict)
        }
        for index, reference in enumerate(evidence.get("canonical_corporate_state", [])):
            if isinstance(reference, dict) and reference.get("accepted_state_id") not in accepted_ids:
                issues.append(
                    ValidationIssue(
                        f"state_change_evidence.canonical_corporate_state.{index}.accepted_state_id",
                        "must identify an entry in the canonical accepted-state registry",
                    )
                )

        chronology_ids: set[str] = set()
        for chronology_file in (REPO_ROOT / "chronology").rglob("*.jsonl"):
            for line in chronology_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    chronology_ids.add(json.loads(line).get("event_id"))
        for index, reference in enumerate(evidence.get("chronology", [])):
            if isinstance(reference, dict) and reference.get("event_or_record_id") not in chronology_ids:
                issues.append(
                    ValidationIssue(
                        f"state_change_evidence.chronology.{index}.event_or_record_id",
                        "must identify an existing governed chronology event",
                    )
                )

        for index, reference in enumerate(evidence.get("production", [])):
            if isinstance(reference, dict):
                issues.extend(
                    _attestation_reference_issues(
                        reference.get("attestation_evidence_reference"),
                        assessment.get("assessment_id"),
                        f"state_change_evidence.production.{index}.attestation_evidence_reference",
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
        attestation = api.get("control_plane_attestation", {})
        if isinstance(attestation, dict) and attestation.get("status") == "available":
            issues.extend(
                _attestation_reference_issues(
                    attestation.get("attestation_evidence_reference"),
                    assessment.get("assessment_id"),
                    "api_observability.control_plane_attestation.attestation_evidence_reference",
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


def review_priority_item_completion_evidence(item: Any) -> dict[str, Any]:
    """Review terminal-evidence structure without deciding semantic completion."""

    if not isinstance(item, dict):
        return {
            "prior_status": None,
            "resulting_status": None,
            "terminal_evidence_contract_satisfied": False,
            "independent_verification_claim_present": False,
            "semantic_completion_condition_verified_by_this_command": False,
            "eligible_for_terminal_review": False,
        }

    evidence = item.get("completion_evidence")
    if not isinstance(evidence, dict):
        evidence = {}
    requirement_results = {
        field: predicate(evidence.get(field))
        for field, predicate in COMPLETION_EVIDENCE_REQUIREMENTS
    }
    terminal_evidence_contract_satisfied = all(requirement_results.values())
    independent_verification_claim_present = requirement_results[
        "independently_verified_at"
    ]
    prior_status = item.get("status")
    return {
        "prior_status": prior_status,
        "resulting_status": prior_status,
        "terminal_evidence_contract_satisfied": terminal_evidence_contract_satisfied,
        "independent_verification_claim_present": independent_verification_claim_present,
        "semantic_completion_condition_verified_by_this_command": False,
        "eligible_for_terminal_review": terminal_evidence_contract_satisfied,
    }


def validate_terminal_completion_evidence(
    item: Any, prefix: str
) -> list[ValidationIssue]:
    """Validate the evidence required for an item that claims terminal status."""

    if not isinstance(item, dict):
        return []
    evidence = item.get("completion_evidence")
    if not isinstance(evidence, dict):
        return []
    issues: list[ValidationIssue] = []
    for field, predicate in COMPLETION_EVIDENCE_REQUIREMENTS:
        if not predicate(evidence.get(field)):
            issues.append(
                ValidationIssue(
                    f"{prefix}.completion_evidence.{field}",
                    "terminal item lacks valid completion evidence",
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
        if item.get("status") in TERMINAL_PRIORITY_STATUSES:
            issues.extend(validate_terminal_completion_evidence(item, prefix))

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
        declared_mandatory_sources = manifest.get("mandatory_operational_sources")
        if declared_mandatory_sources != list(MANDATORY_OPERATIONAL_SOURCES):
            issues.append(
                ValidationIssue(
                    "source_manifest.mandatory_operational_sources",
                    "must declare the canonical mandatory operational source set in order",
                )
            )
        declared_source_ids = {
            source.get("source_id")
            for source in manifest.get("sources", [])
            if isinstance(source, dict)
        }
        for source_id in MANDATORY_OPERATIONAL_SOURCES:
            if source_id not in declared_source_ids:
                issues.append(
                    ValidationIssue(
                        "source_manifest.sources",
                        f"missing mandatory operational source definition {source_id!r}",
                    )
                )
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
