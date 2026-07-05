from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "reflex_memory"
SCHEMA_DIR = ROOT / "schemas" / "reflex_memory"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_schema_errors(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(instance, dict):
            return errors + [f"{path}: expected object"]

        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}.{key}: missing required property")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}.{key}: additional property is not allowed")

        for key, value in instance.items():
            if key in properties:
                errors.extend(collect_schema_errors(value, properties[key], f"{path}.{key}"))

    elif schema_type == "array":
        if not isinstance(instance, list):
            return errors + [f"{path}: expected array"]

        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} item(s)")

        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(collect_schema_errors(item, item_schema, f"{path}[{index}]"))

    elif schema_type == "string":
        if not isinstance(instance, str):
            return errors + [f"{path}: expected string"]

        min_length = schema.get("minLength")
        if min_length is not None and len(instance) < min_length:
            errors.append(f"{path}: expected minLength {min_length}")

        pattern = schema.get("pattern")
        if pattern and re.search(pattern, instance) is None:
            errors.append(f"{path}: expected pattern {pattern!r}")

    elif schema_type == "boolean" and not isinstance(instance, bool):
        errors.append(f"{path}: expected boolean")

    return errors


def validate_fixture(fixture_name: str, schema_name: str) -> None:
    fixture = load_json(FIXTURE_DIR / fixture_name)
    schema = load_json(SCHEMA_DIR / schema_name)
    errors = collect_schema_errors(fixture, schema)
    assert errors == []


def test_accepted_reflex_memory_entries_match_schema() -> None:
    for fixture_name in [
        "reflex_memory_entry_source_state_conflict.json",
        "reflex_memory_entry_boundary_language_drift.json",
        "reflex_memory_entry_proof_reference_missing.json",
    ]:
        validate_fixture(fixture_name, "reflex_memory_entry_v0_1.schema.json")


def test_chronology_events_match_schema() -> None:
    for fixture_name in [
        "chronology_event_source_state_conflict.json",
        "chronology_event_boundary_language_drift.json",
        "chronology_event_proof_reference_missing.json",
    ]:
        validate_fixture(fixture_name, "chronology_event_v0_1.schema.json")


def test_reflex_memory_schema_rejects_authority_effect_other_than_none() -> None:
    fixture = copy.deepcopy(load_json(FIXTURE_DIR / "reflex_memory_entry_source_state_conflict.json"))
    schema = load_json(SCHEMA_DIR / "reflex_memory_entry_v0_1.schema.json")

    fixture["authority_effect"] = "approve"

    errors = collect_schema_errors(fixture, schema)

    assert errors
    assert any("authority_effect" in error for error in errors)


def test_reflex_memory_schema_rejects_missing_source_chronology() -> None:
    fixture = copy.deepcopy(load_json(FIXTURE_DIR / "reflex_memory_entry_source_state_conflict.json"))
    schema = load_json(SCHEMA_DIR / "reflex_memory_entry_v0_1.schema.json")

    fixture["source_chronology_event_ids"] = []

    errors = collect_schema_errors(fixture, schema)

    assert errors
    assert any("source_chronology_event_ids" in error for error in errors)


def test_reflex_memory_schema_rejects_unsupported_review_posture_effect() -> None:
    fixture = copy.deepcopy(load_json(FIXTURE_DIR / "reflex_memory_entry_source_state_conflict.json"))
    schema = load_json(SCHEMA_DIR / "reflex_memory_entry_v0_1.schema.json")

    fixture["review_posture_effect"] = "authorize_execution"

    errors = collect_schema_errors(fixture, schema)

    assert errors
    assert any("review_posture_effect" in error for error in errors)
