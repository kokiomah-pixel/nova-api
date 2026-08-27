from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from retail_context.schema import (
    load_retail_context_schema,
    validate_retail_context_object,
)


FIXTURE_DIR = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "retail_context"
    / "context_object"
)


def load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def assert_invalid(context: dict) -> None:
    with pytest.raises(ValidationError):
        validate_retail_context_object(context)


def test_valid_resolved_context_object_passes() -> None:
    validate_retail_context_object(load_fixture("resolved.json"))


def test_valid_unresolved_context_object_passes() -> None:
    validate_retail_context_object(load_fixture("unresolved.json"))


def test_valid_partially_resolved_context_object_passes() -> None:
    validate_retail_context_object(load_fixture("partially_resolved.json"))


def test_valid_insufficient_evidence_context_object_passes() -> None:
    validate_retail_context_object(load_fixture("insufficient_evidence.json"))


@pytest.mark.parametrize("field", ["schema_version", "generated_at"])
def test_missing_structurally_mandatory_field_fails(field: str) -> None:
    context = load_fixture("resolved.json")
    del context[field]
    assert_invalid(context)


def test_unsupported_context_status_fails() -> None:
    context = load_fixture("resolved.json")
    context["context_status"] = "approved"
    assert_invalid(context)


def test_unsupported_confidence_level_fails() -> None:
    context = load_fixture("resolved.json")
    context["confidence"]["level"] = "certain"
    assert_invalid(context)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_id", None),
        ("source_type", "Public API"),
        ("observed_at", "not-a-timestamp"),
        ("source_status", "trusted"),
        ("claim_reconciliation_status", "approved"),
        ("contribution_scope", []),
    ],
)
def test_malformed_provenance_fails(field: str, value: object) -> None:
    context = load_fixture("resolved.json")
    context["provenance"][0][field] = value
    assert_invalid(context)


def test_additional_unexpected_top_level_property_fails() -> None:
    context = load_fixture("resolved.json")
    context["unexpected"] = True
    assert_invalid(context)


def test_authority_effect_other_than_none_fails() -> None:
    context = load_fixture("resolved.json")
    context["authority_effect"] = "approval"
    assert_invalid(context)


def test_object_with_unresolved_contradiction_passes() -> None:
    context = load_fixture("unresolved.json")
    assert context["contradictions"][0]["status"] == "unresolved"
    validate_retail_context_object(context)


def test_insufficient_evidence_does_not_require_fabricated_positive_evidence() -> None:
    context = load_fixture("insufficient_evidence.json")
    assert context["provenance"] == []
    assert context["evidence"] == []
    validate_retail_context_object(context)


def test_insufficient_evidence_requires_explicit_evidence_gap() -> None:
    context = load_fixture("insufficient_evidence.json")
    context["unresolved_evidence"] = []
    assert_invalid(context)


@pytest.mark.parametrize(
    "institutional_field",
    [
        "institutional_tenant_id",
        "institutional_chronology_id",
        "institutional_reflex_memory_id",
        "institutional_credentials",
        "institutional_accepted_state",
    ],
)
def test_institutional_state_bearing_fields_are_rejected(
    institutional_field: str,
) -> None:
    context = copy.deepcopy(load_fixture("resolved.json"))
    context[institutional_field] = "prohibited"
    assert_invalid(context)


def test_schema_itself_validates_under_draft_2020_12() -> None:
    schema = load_retail_context_schema()
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:  # pragma: no cover - assertion gives useful failure
        pytest.fail(f"invalid Draft 2020-12 schema: {exc}")
