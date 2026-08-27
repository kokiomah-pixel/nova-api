from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from retail_context.context_delta import (
    build_context_delta,
    load_context_delta_schema,
    validate_context_delta,
)
from retail_context.state_ping import build_state_ping


REPO_ROOT = Path(__file__).resolve().parents[1]
DELTA_CASE_PATH = (
    REPO_ROOT / "fixtures" / "retail_context" / "context_delta" / "cases.json"
)
PING_CASE_PATH = (
    REPO_ROOT / "fixtures" / "retail_context" / "state_ping" / "cases.json"
)
SOURCE_FIXTURE_DIR = REPO_ROOT / "fixtures" / "retail_context" / "sources"
DELTA_GENERATED_AT = "2026-08-27T15:00:00Z"


def _merge(base: dict, overrides: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _eligible_source_entry(source_id: str) -> dict:
    return {
        "source_id": source_id,
        "source_type": "fixture_test_source",
        "display_name": f"Eligible test source {source_id}",
        "source_namespace": "retail_public_sources",
        "access_class": "public",
        "authorization_state": "authorized",
        "licensing_state": "public",
        "configuration_state": "configured",
        "credential_requirement": "none",
        "credential_namespace": "none",
        "freshness_policy_reference": "fixture-policy:no-production-threshold",
        "provenance_requirement": "required",
        "enabled": True,
        "authority_effect": "none",
    }


def build_ping_case(name: str) -> dict:
    cases = json.loads(PING_CASE_PATH.read_text(encoding="utf-8"))
    case = copy.deepcopy(cases[name])
    observations = []
    for specification in case["observations"]:
        observation = json.loads(
            (SOURCE_FIXTURE_DIR / specification["fixture"]).read_text(
                encoding="utf-8"
            )
        )
        observations.append(_merge(observation, specification.get("overrides", {})))
    source_entries = [
        _eligible_source_entry(source_id)
        for source_id in sorted({item["source_id"] for item in observations})
    ]
    return build_state_ping(
        case["subject"],
        observations,
        source_entries,
        generated_at=case["generated_at"],
    )


def load_delta_contexts(name: str) -> tuple[dict, dict]:
    cases = json.loads(DELTA_CASE_PATH.read_text(encoding="utf-8"))
    case = cases[name]
    return (
        build_ping_case(case["previous_state_ping_case"]),
        build_ping_case(case["current_state_ping_case"]),
    )


def build_delta_case(name: str) -> dict:
    previous, current = load_delta_contexts(name)
    return build_context_delta(
        previous,
        current,
        generated_at=DELTA_GENERATED_AT,
    )


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_identical_contexts_are_unchanged() -> None:
    delta = build_delta_case("identical")
    assert delta["delta_status"] == "unchanged"
    assert delta["material_changes"] == []


def test_reordered_identity_arrays_are_unchanged() -> None:
    previous = build_ping_case("contradictory")
    current = copy.deepcopy(previous)
    for field in (
        "provenance",
        "evidence",
        "contradictions",
        "unresolved_evidence",
        "limitations",
    ):
        current[field].reverse()
    for item in current["provenance"]:
        item["contribution_scope"].reverse()
    for item in current["contradictions"]:
        item["evidence_ids"].reverse()
    for item in current["unresolved_evidence"]:
        if "related_source_ids" in item:
            item["related_source_ids"].reverse()

    delta = build_context_delta(
        previous,
        current,
        generated_at=DELTA_GENERATED_AT,
    )
    assert delta["delta_status"] == "unchanged"
    assert delta["material_changes"] == []


def test_subject_mismatch_fails_closed() -> None:
    previous, current = load_delta_contexts("subject_mismatch")
    with pytest.raises(ValueError, match="same subject"):
        build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)


@pytest.mark.parametrize("invalid_side", ["previous", "current"])
def test_invalid_input_context_fails(invalid_side: str) -> None:
    previous, current = load_delta_contexts("identical")
    target = previous if invalid_side == "previous" else current
    del target["schema_version"]
    with pytest.raises(ValidationError):
        build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)


@pytest.mark.parametrize("invalid_side", ["previous", "current"])
def test_authority_effect_other_than_none_fails(invalid_side: str) -> None:
    previous, current = load_delta_contexts("identical")
    target = previous if invalid_side == "previous" else current
    target["authority_effect"] = "approval"
    with pytest.raises(ValidationError):
        build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)


def test_context_status_change_is_recorded() -> None:
    delta = build_delta_case("status_and_evidence_removed")
    assert delta["delta_status"] == "changed"
    change = next(
        item
        for item in delta["material_changes"]
        if item["category"] == "context_status"
    )
    assert change["change_type"] == "status_changed"
    assert change["previous_value"] == "resolved"
    assert change["current_value"] == "partially_resolved"


def test_evidence_added_is_recorded() -> None:
    delta = build_delta_case("evidence_added")
    assert any(
        item["change_type"] == "added"
        for item in delta["evidence_state_changes"]
    )


def test_evidence_removed_is_recorded() -> None:
    delta = build_delta_case("status_and_evidence_removed")
    assert any(
        item["change_type"] == "removed"
        for item in delta["evidence_state_changes"]
    )


def test_evidence_status_change_preserves_both_states() -> None:
    previous = build_ping_case("single_verified_positive")
    current = copy.deepcopy(previous)
    current["evidence"][0]["evidence_status"] = "contradicted"
    delta = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    change = next(
        item
        for item in delta["evidence_state_changes"]
        if item["change_type"] == "status_changed"
    )
    assert change["previous_status"] == "observed"
    assert change["current_status"] == "contradicted"


def test_contradiction_added_is_recorded() -> None:
    delta = build_delta_case("contradiction_added")
    assert any(
        item["change_type"] == "added"
        for item in delta["contradiction_changes"]
    )


def test_contradiction_removed_does_not_claim_resolution() -> None:
    delta = build_delta_case("contradiction_removed")
    removed = next(
        item
        for item in delta["contradiction_changes"]
        if item["change_type"] == "removed"
    )
    assert removed["current_status"] is None
    assert removed["treatment"] == "removed_from_current_bounded_context"


def test_unresolved_evidence_added_and_removed_are_recorded() -> None:
    base = build_ping_case("multiple_positive")
    with_gap = copy.deepcopy(base)
    with_gap["unresolved_evidence"].append(
        {
            "issue_id": "fixture-gap-added",
            "status": "unresolved",
            "claim_scope": "fixture comparison scope",
            "reason": "The fixture leaves one bounded item unresolved.",
        }
    )
    added = build_context_delta(base, with_gap, generated_at=DELTA_GENERATED_AT)
    removed = build_context_delta(with_gap, base, generated_at=DELTA_GENERATED_AT)
    assert any(
        item["change_type"] == "added"
        for item in added["unresolved_evidence_changes"]
    )
    removed_change = next(
        item
        for item in removed["unresolved_evidence_changes"]
        if item["change_type"] == "removed"
    )
    assert removed_change["treatment"] == "removed_from_current_bounded_context"


def test_freshness_status_change_is_recorded() -> None:
    delta = build_delta_case("freshness_changed")
    change = next(
        item for item in delta["freshness_changes"] if item["field"] == "freshness_status"
    )
    assert change["previous_value"] == "unknown"
    assert change["current_value"] == "stale"


def test_source_age_change_is_recorded_without_interpretation() -> None:
    previous = build_ping_case("single_verified_positive")
    current = copy.deepcopy(previous)
    current["freshness"]["source_age_seconds"] += 1
    delta = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    change = next(
        item
        for item in delta["freshness_changes"]
        if item["field"] == "source_age_seconds"
    )
    assert change["previous_value"] == 5
    assert change["current_value"] == 6


def test_confidence_level_change_is_recorded() -> None:
    previous = build_ping_case("single_verified_positive")
    current = copy.deepcopy(previous)
    current["confidence"]["level"] = "low"
    delta = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    change = next(
        item for item in delta["confidence_changes"] if item["field"] == "level"
    )
    assert change["previous_value"] == "medium"
    assert change["current_value"] == "low"


def test_provenance_source_added_and_removed_are_recorded() -> None:
    added = build_delta_case("evidence_added")
    removed = build_delta_case("status_and_evidence_removed")
    assert any(item["change_type"] == "added" for item in added["provenance_changes"])
    assert any(
        item["change_type"] == "removed" for item in removed["provenance_changes"]
    )


def test_provenance_source_status_change_is_explicit() -> None:
    previous = build_ping_case("single_verified_positive")
    current = copy.deepcopy(previous)
    current["provenance"][0]["source_status"] = "verification_failed"
    delta = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    change = next(
        item
        for item in delta["provenance_changes"]
        if item["change_type"] == "source_status_changed"
    )
    assert change["previous_value"] == "verified"
    assert change["current_value"] == "verification_failed"


def test_limitation_added_and_removed_are_recorded() -> None:
    base = build_ping_case("multiple_positive")
    with_limitation = copy.deepcopy(base)
    with_limitation["limitations"].append(
        {
            "limitation_id": "fixture-comparison-limitation",
            "description": "Fixture comparison has an explicit bounded limitation.",
            "impact": "limited_scope",
        }
    )
    added = build_context_delta(
        base, with_limitation, generated_at=DELTA_GENERATED_AT
    )
    removed = build_context_delta(
        with_limitation, base, generated_at=DELTA_GENERATED_AT
    )
    assert any(item["change_type"] == "added" for item in added["limitation_changes"])
    assert any(
        item["change_type"] == "removed" for item in removed["limitation_changes"]
    )


def test_no_economic_or_directional_fields_are_emitted() -> None:
    delta = build_delta_case("evidence_added")
    for field in (
        "signal",
        "prediction",
        "recommendation",
        "execution",
        "opportunity",
        "bullish",
        "bearish",
    ):
        assert field not in delta


def test_deterministic_ordering_produces_byte_equivalent_output() -> None:
    previous, current = load_delta_contexts("contradiction_added")
    reordered_previous = copy.deepcopy(previous)
    reordered_current = copy.deepcopy(current)
    for context in (reordered_previous, reordered_current):
        for field in (
            "provenance",
            "evidence",
            "contradictions",
            "unresolved_evidence",
            "limitations",
        ):
            context[field].reverse()
    first = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    second = build_context_delta(
        reordered_previous,
        reordered_current,
        generated_at=DELTA_GENERATED_AT,
    )
    assert _canonical(first) == _canonical(second)


def test_explicit_generated_at_is_preserved() -> None:
    delta = build_delta_case("identical")
    assert delta["generated_at"] == DELTA_GENERATED_AT


def test_swapping_contexts_reverses_add_remove_semantics() -> None:
    previous, current = load_delta_contexts("evidence_added")
    forward = build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(current, previous, generated_at=DELTA_GENERATED_AT)
    added_ids = {
        item["evidence_id"]
        for item in forward["evidence_state_changes"]
        if item["change_type"] == "added"
    }
    removed_ids = {
        item["evidence_id"]
        for item in reverse["evidence_state_changes"]
        if item["change_type"] == "removed"
    }
    assert added_ids
    assert added_ids == removed_ids
    assert forward["resource_id"] != reverse["resource_id"]


def test_output_and_schema_validate_under_draft_2020_12() -> None:
    delta = build_delta_case("evidence_added")
    validate_context_delta(delta)
    Draft202012Validator.check_schema(load_context_delta_schema())


def test_identical_insufficient_contexts_are_indeterminate() -> None:
    delta = build_delta_case("indeterminate")
    assert delta["delta_status"] == "indeterminate"
    assert delta["material_changes"] == []
    assert delta["limitations"][0]["impact"] == "indeterminate"


def test_incompatible_resource_types_fail_closed() -> None:
    previous, current = load_delta_contexts("identical")
    current["resource_type"] = "full_context"
    with pytest.raises(ValueError, match="resource types"):
        build_context_delta(previous, current, generated_at=DELTA_GENERATED_AT)
