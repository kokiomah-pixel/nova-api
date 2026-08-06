#!/usr/bin/env python3
"""Validate governed-abstraction schemas, fixtures, and non-authority boundaries."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "reflex_memory"
FIXTURE_DIR = ROOT / "fixtures" / "reflex_memory"

CANDIDATE_SCHEMA = "reflex_memory_candidate_v0_2.schema.json"
ENTRY_SCHEMA = "reflex_memory_entry_v0_2.schema.json"
RETRIEVAL_SCHEMA = "reflex_memory_retrieval_explanation_v0_1.schema.json"

NEW_FIXTURES = {
    "reflex_memory_candidate_implicit_policy_conversion.json": CANDIDATE_SCHEMA,
    "reflex_memory_candidate_exception_only.json": CANDIDATE_SCHEMA,
    "reflex_memory_entry_governed_abstraction_v0_2.json": ENTRY_SCHEMA,
    "reflex_memory_retrieval_comparison_limits.json": RETRIEVAL_SCHEMA,
}

V0_1_FIXTURES = {
    "chronology_event_source_state_conflict.json": "chronology_event_v0_1.schema.json",
    "chronology_event_boundary_language_drift.json": "chronology_event_v0_1.schema.json",
    "chronology_event_proof_reference_missing.json": "chronology_event_v0_1.schema.json",
    "reflex_memory_entry_source_state_conflict.json": "reflex_memory_entry_v0_1.schema.json",
    "reflex_memory_entry_boundary_language_drift.json": "reflex_memory_entry_v0_1.schema.json",
    "reflex_memory_entry_proof_reference_missing.json": "reflex_memory_entry_v0_1.schema.json",
}

V0_1_SCHEMA_HASHES = {
    "chronology_event_v0_1.schema.json": "7f220e61e27ddc1eed42b498972249e0814dca4c042639f51ec24a14345bc621",
    "reflex_memory_entry_v0_1.schema.json": "8cbc9ac0d5078b4ce0457b71550e47df6a15fa28d0a0e58cb7bbfe86afb0a1ff",
}

LIFECYCLE_VALUES = {"candidate", "reviewed", "accepted", "rejected", "archived"}
EPISTEMIC_VALUES = {"source_supported", "source_limited", "disputed", "contradicted", "unverified", "superseded"}
AUTHORITY_VALUES = {"reference_only", "accepted_for_review_use", "exception_only", "formally_adopted_by_local_authority", "superseded"}
PRECEDENT_VALUES = {"none", "analogous", "materially_distinguishable", "exception_only", "contradicted", "superseded"}

PROHIBITED_FIELDS = {
    "approve", "deny", "authorize", "permission", "execute", "settle", "sign",
    "route", "block_execution", "policy_update", "constraint_update",
    "automatic_policy_update", "automatic_constraint_update",
    "authority_update", "automatic_acceptance", "automatic_learning",
    "binding_precedent", "active_reflex_memory_entry", "runtime_activation",
}

IMPLICIT_POLICY_PATTERNS = {
    "unbounded 'always require' language": re.compile(r"\balways\s+require\b", re.I),
    "automatic policy conversion": re.compile(r"\bautomatically?\s+(?:becomes?|creates?|updates?|changes?)\s+(?:an?\s+)?(?:policy|rule|constraint)\b", re.I),
    "binding precedent": re.compile(r"\bbinding\s+precedent\b", re.I),
    "future permission": re.compile(r"\bfuture\s+actions?\s+may\s+proceed\b", re.I),
    "automatic approval or denial": re.compile(r"\bautomatically?\s+(?:approve|deny|authorize)\b", re.I),
}

RETRIEVAL_RECOMMENDATION_PATTERNS = {
    "approval recommendation": re.compile(r"\brecommend(?:s|ed|ation)?\s+(?:approval|approving|approve)\b", re.I),
    "denial recommendation": re.compile(r"\brecommend(?:s|ed|ation)?\s+(?:denial|denying|deny)\b", re.I),
    "execution recommendation": re.compile(r"\brecommend(?:s|ed|ation)?\s+(?:execution|executing|execute)\b", re.I),
    "permission recommendation": re.compile(r"\brecommend(?:s|ed|ation)?\s+(?:permission|permitting|permit)\b", re.I),
}


class AbstractionValidationError(ValueError):
    """Raised when a governed-abstraction object fails closed."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _path(error: Any) -> str:
    parts = [str(part) for part in error.absolute_path]
    return "$" + ("." + ".".join(parts) if parts else "")


def schema_errors(instance: dict[str, Any], schema_name: str) -> list[str]:
    schema = load_json(SCHEMA_DIR / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{_path(error)}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]


def _all_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_keys(child)


def _texts(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _texts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _texts(child)


def _require_no_prohibited_fields(instance: dict[str, Any]) -> list[str]:
    return [f"$.{key}: authority-bearing or runtime field is prohibited" for key in sorted(set(_all_keys(instance)) & PROHIBITED_FIELDS)]


def _require_non_authority(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if instance.get("authority_effect") != "none":
        errors.append("$.authority_effect: must be 'none'")
    if "precedent_effect" in instance and instance.get("precedent_effect") != "none":
        errors.append("$.precedent_effect: must be 'none'")
    return errors


def _require_state_separation(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lifecycle = instance.get("lifecycle_status")
    epistemic = instance.get("epistemic_status")
    authority = instance.get("authority_treatment")
    precedent = instance.get("precedent_treatment")
    if lifecycle is not None and lifecycle not in LIFECYCLE_VALUES:
        errors.append("$.lifecycle_status: must express lifecycle only")
    if epistemic is not None and epistemic not in EPISTEMIC_VALUES:
        errors.append("$.epistemic_status: must express epistemic treatment only")
    if authority is not None and authority not in AUTHORITY_VALUES:
        errors.append("$.authority_treatment: must express authority treatment only")
    if precedent is None:
        errors.append("$.precedent_treatment: is required")
    elif precedent not in PRECEDENT_VALUES:
        errors.append("$.precedent_treatment: must express precedent treatment only")
    return errors


def _phrase_errors(texts: Iterable[str], patterns: dict[str, re.Pattern[str]], path: str) -> list[str]:
    errors: list[str] = []
    for text in texts:
        for label, pattern in patterns.items():
            if pattern.search(text):
                errors.append(f"{path}: prohibited {label}")
    return sorted(set(errors))


def validate_candidate(instance: dict[str, Any]) -> list[str]:
    errors = schema_errors(instance, CANDIDATE_SCHEMA)
    errors += _require_no_prohibited_fields(instance)
    errors += _require_non_authority(instance)
    errors += _require_state_separation(instance)
    errors += _phrase_errors([instance.get("proposed_lesson", "")], IMPLICIT_POLICY_PATTERNS, "$.proposed_lesson")

    if "reflex_id" in instance or instance.get("status") == "accepted":
        errors.append("$: candidate must not be represented as an active Reflex Memory entry")

    exception_only = instance.get("authority_treatment") == "exception_only" or instance.get("precedent_treatment") == "exception_only"
    if exception_only and not instance.get("known_exceptions"):
        errors.append("$.known_exceptions: exception-only treatment requires preserved exceptions")

    if instance.get("epistemic_status") in {"disputed", "contradicted"}:
        if not instance.get("contradictory_cases"):
            errors.append("$.contradictory_cases: disputed or contradicted propositions require a contradictory case")
        if not instance.get("material_distinctions") and not instance.get("unresolved_conditions"):
            errors.append("$: disputed or contradicted propositions require limitations")
        if re.search(r"\b(?:universally established|always true|applies universally)\b", instance.get("proposed_lesson", ""), re.I):
            errors.append("$.proposed_lesson: disputed or contradicted proposition cannot be universalized")

    if instance.get("lifecycle_status") == "accepted":
        for field in ("reviewed_by", "reviewed_at", "accepted_by", "accepted_at", "converted_entry_id"):
            if not instance.get(field):
                errors.append(f"$.{field}: accepted candidate requires acceptance evidence")
    if instance.get("authority_treatment") == "formally_adopted_by_local_authority":
        for field in ("accepted_by", "accepted_at", "supporting_evidence_refs"):
            if not instance.get(field):
                errors.append(f"$.{field}: formal adoption requires explicit evidence")

    if "superseded" in {instance.get("epistemic_status"), instance.get("authority_treatment"), instance.get("precedent_treatment")}:
        for field in ("candidate_id", "superseded_by", "source_chronology_event_ids"):
            if not instance.get(field):
                errors.append(f"$.{field}: supersession requires identity and source lineage")
    return sorted(set(errors))


def validate_entry(instance: dict[str, Any]) -> list[str]:
    errors = schema_errors(instance, ENTRY_SCHEMA)
    errors += _require_no_prohibited_fields(instance)
    errors += _require_non_authority(instance)
    errors += _require_state_separation(instance)

    for field in ("source_candidate_id", "source_chronology_event_ids", "reviewed_by", "reviewed_at", "accepted_by", "accepted_at", "evidence_refs"):
        if not instance.get(field):
            errors.append(f"$.{field}: accepted memory requires review, acceptance, and source evidence")

    if instance.get("epistemic_status") in {"disputed", "contradicted"}:
        if not instance.get("contradictory_cases"):
            errors.append("$.contradictory_cases: disputed or contradicted memory requires a contradictory case")
        if not instance.get("unresolved_conditions") and not instance.get("material_distinctions"):
            errors.append("$: disputed or contradicted memory requires limitations")
        if re.search(r"\b(?:universally established|always true|applies universally)\b", " ".join(_texts(instance)), re.I):
            errors.append("$: disputed or contradicted memory cannot be presented as universal truth")

    exception_only = instance.get("authority_treatment") == "exception_only" or instance.get("precedent_treatment") == "exception_only"
    if exception_only and not instance.get("known_exceptions"):
        errors.append("$.known_exceptions: exception-only treatment requires preserved exceptions")

    if "superseded" in {instance.get("epistemic_status"), instance.get("authority_treatment"), instance.get("precedent_treatment")}:
        for field in ("reflex_id", "superseded_by", "source_chronology_event_ids"):
            if not instance.get(field):
                errors.append(f"$.{field}: supersession requires identity and source lineage")
    return sorted(set(errors))


def validate_retrieval(instance: dict[str, Any]) -> list[str]:
    errors = schema_errors(instance, RETRIEVAL_SCHEMA)
    errors += _require_no_prohibited_fields(instance)
    errors += _require_non_authority(instance)
    errors += _require_state_separation(instance)
    for field in ("surfaced_because", "comparison_dimensions", "comparison_limits", "source_chronology_event_ids"):
        if not instance.get(field):
            errors.append(f"$.{field}: retrieval explanation requires transparent comparison lineage")
    errors += _phrase_errors(_texts(instance), RETRIEVAL_RECOMMENDATION_PATTERNS, "$: retrieval explanation")
    return sorted(set(errors))


def validate_runtime_activation_claim(text: str) -> list[str]:
    pattern = re.compile(r"\bv0\.2\b.{0,80}\b(?:is|as)\s+(?:active|loaded|production|runtime-enabled)\b", re.I | re.S)
    return ["$: v0.2 runtime activation claim is prohibited"] if pattern.search(text) else []


def _validate_v0_1_compatibility() -> list[str]:
    errors: list[str] = []
    for schema_name, expected_hash in V0_1_SCHEMA_HASHES.items():
        actual_hash = hashlib.sha256((SCHEMA_DIR / schema_name).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"schemas/reflex_memory/{schema_name}: existing v0.1 schema changed")
    for fixture_name, schema_name in V0_1_FIXTURES.items():
        for error in schema_errors(load_json(FIXTURE_DIR / fixture_name), schema_name):
            errors.append(f"fixtures/reflex_memory/{fixture_name} {error}")
    return errors


def _changed_paths() -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "origin/main"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    paths = set(tracked.stdout.splitlines()) | set(untracked.stdout.splitlines())
    return sorted(path for path in paths if path and not path.startswith("artifacts/"))


def _schema_boundary_errors() -> list[str]:
    errors: list[str] = []
    for schema_name in (CANDIDATE_SCHEMA, ENTRY_SCHEMA, RETRIEVAL_SCHEMA):
        schema = load_json(SCHEMA_DIR / schema_name)
        properties = schema.get("properties", {})
        prohibited = sorted(set(properties) & PROHIBITED_FIELDS)
        for field in prohibited:
            errors.append(f"schemas/reflex_memory/{schema_name} $.properties.{field}: prohibited field")
        if properties.get("authority_effect", {}).get("const") != "none":
            errors.append(f"schemas/reflex_memory/{schema_name} $.properties.authority_effect: must be const 'none'")
        if "precedent_effect" in properties and properties["precedent_effect"].get("const") != "none":
            errors.append(f"schemas/reflex_memory/{schema_name} $.properties.precedent_effect: must be const 'none'")
    return errors


def _boundary_errors() -> list[str]:
    errors: list[str] = []
    runtime_prefixes = ("app.py", "core/", "nova/", "services/", "routes/", "middleware/", "migrations/")
    state_patterns = ("accepted-state", "accepted_state", "chronology/events/", "active_reflex", "production_data/")
    for path in _changed_paths():
        if path == runtime_prefixes[0] or path.startswith(runtime_prefixes[1:]):
            errors.append(f"{path}: runtime change detected")
        if any(pattern in path.lower() for pattern in state_patterns):
            errors.append(f"{path}: accepted-state or chronology event change detected")
    return errors


def validate_repository() -> list[str]:
    errors: list[str] = []
    required_docs = [
        ROOT / "docs/market/signals/2026/MSE-2026-08-06-038-plugmem-governed-abstraction.md",
        ROOT / "docs/governance/governed-abstraction-boundary.md",
    ]
    for path in required_docs:
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: required document is missing")

    validators = {
        CANDIDATE_SCHEMA: validate_candidate,
        ENTRY_SCHEMA: validate_entry,
        RETRIEVAL_SCHEMA: validate_retrieval,
    }
    for fixture_name, schema_name in NEW_FIXTURES.items():
        instance = load_json(FIXTURE_DIR / fixture_name)
        for error in validators[schema_name](instance):
            errors.append(f"fixtures/reflex_memory/{fixture_name} {error}")

    errors += _validate_v0_1_compatibility()
    errors += _schema_boundary_errors()
    errors += _boundary_errors()
    for path in (
        ROOT / "docs/governance/governed-abstraction-boundary.md",
        ROOT / "docs/governance/reflex-memory-specification.md",
        ROOT / "docs/governance/reflex-memory-v0-1-fixture.md",
    ):
        for error in validate_runtime_activation_claim(path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(ROOT)} {error}")
    return sorted(set(errors))


def _success_output() -> str:
    return """reflex_memory_abstraction_validation:
  overall_status: coherent

  market_signal_record: present
  governed_abstraction_boundary: present

  candidate_schema_v0_2: passed
  entry_schema_v0_2: passed
  retrieval_explanation_schema_v0_1: passed

  implicit_policy_conversion_guard: passed
  exception_preservation: passed
  contradiction_preservation: passed
  acceptance_evidence: passed
  retrieval_comparison_limits: passed
  supersession_lineage: passed
  non_authority_boundary: passed

  existing_v0_1_compatibility: passed
  runtime_change_detected: false
  accepted_state_change_detected: false
  chronology_event_detected: false"""


def main() -> int:
    errors = validate_repository()
    if errors:
        print("reflex_memory_abstraction_validation:", file=sys.stderr)
        print("  overall_status: blocked", file=sys.stderr)
        print("  errors:", file=sys.stderr)
        for error in errors:
            print(f"    - {error}", file=sys.stderr)
        return 1
    print(_success_output())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
