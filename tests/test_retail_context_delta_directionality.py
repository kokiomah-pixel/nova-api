from __future__ import annotations

import copy

from test_retail_context_delta import DELTA_GENERATED_AT, build_ping_case
from retail_context.context_delta import build_context_delta


def _material(delta: dict, category: str, change_type: str) -> dict:
    return next(
        item
        for item in delta["material_changes"]
        if item["category"] == category and item["change_type"] == change_type
    )


def test_reversing_evidence_status_transition_changes_identity() -> None:
    observed = build_ping_case("single_verified_positive")
    contradicted = copy.deepcopy(observed)
    contradicted["evidence"][0]["evidence_status"] = "contradicted"

    forward = build_context_delta(observed, contradicted, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(contradicted, observed, generated_at=DELTA_GENERATED_AT)

    forward_change = next(
        item for item in forward["evidence_state_changes"] if item["change_type"] == "status_changed"
    )
    reverse_change = next(
        item for item in reverse["evidence_state_changes"] if item["change_type"] == "status_changed"
    )
    assert forward_change["change_id"] != reverse_change["change_id"]
    assert _material(forward, "evidence", "status_changed")["change_id"] != _material(
        reverse, "evidence", "status_changed"
    )["change_id"]


def test_reversing_context_status_transition_changes_material_identity() -> None:
    resolved = build_ping_case("multiple_positive")
    partial = build_ping_case("single_unverified")
    partial["subject"] = copy.deepcopy(resolved["subject"])
    partial["resource_type"] = resolved["resource_type"]

    forward = build_context_delta(resolved, partial, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(partial, resolved, generated_at=DELTA_GENERATED_AT)

    assert _material(forward, "context_status", "status_changed")["change_id"] != _material(
        reverse, "context_status", "status_changed"
    )["change_id"]


def test_reversing_contradiction_status_transition_changes_identity() -> None:
    unresolved = build_ping_case("contradictory")
    resolved = copy.deepcopy(unresolved)
    resolved["contradictions"][0]["status"] = "resolved"
    resolved["contradictions"][0]["resolution_basis"] = "Fixture-only explicit resolution basis."

    forward = build_context_delta(unresolved, resolved, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(resolved, unresolved, generated_at=DELTA_GENERATED_AT)

    forward_change = next(
        item for item in forward["contradiction_changes"] if item["change_type"] == "status_changed"
    )
    reverse_change = next(
        item for item in reverse["contradiction_changes"] if item["change_type"] == "status_changed"
    )
    assert forward_change["change_id"] != reverse_change["change_id"]


def test_reversing_unresolved_status_transition_changes_identity() -> None:
    unresolved = build_ping_case("single_unverified")
    changed = copy.deepcopy(unresolved)
    changed["unresolved_evidence"][0]["status"] = "missing"

    forward = build_context_delta(unresolved, changed, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(changed, unresolved, generated_at=DELTA_GENERATED_AT)

    forward_change = next(
        item for item in forward["unresolved_evidence_changes"] if item["change_type"] == "status_changed"
    )
    reverse_change = next(
        item for item in reverse["unresolved_evidence_changes"] if item["change_type"] == "status_changed"
    )
    assert forward_change["change_id"] != reverse_change["change_id"]


def test_reversing_limitation_impact_transition_changes_identity() -> None:
    limited = build_ping_case("multiple_positive")
    limited["limitations"] = [
        {
            "limitation_id": "fixture-directional-limitation",
            "description": "Fixture-only bounded limitation.",
            "impact": "limited_scope",
        }
    ]
    material = copy.deepcopy(limited)
    material["limitations"][0]["impact"] = "material"

    forward = build_context_delta(limited, material, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(material, limited, generated_at=DELTA_GENERATED_AT)

    forward_change = next(
        item for item in forward["limitation_changes"] if item["change_type"] == "impact_changed"
    )
    reverse_change = next(
        item for item in reverse["limitation_changes"] if item["change_type"] == "impact_changed"
    )
    assert forward_change["change_id"] != reverse_change["change_id"]


def test_content_change_exposes_bounded_before_after_and_reverses_identity() -> None:
    before = build_ping_case("single_verified_positive")
    after = copy.deepcopy(before)
    after["evidence"][0]["claim_or_observation"] = "A different bounded fixture observation."

    forward = build_context_delta(before, after, generated_at=DELTA_GENERATED_AT)
    reverse = build_context_delta(after, before, generated_at=DELTA_GENERATED_AT)

    forward_material = _material(forward, "evidence", "content_changed")
    reverse_material = _material(reverse, "evidence", "content_changed")
    assert "previous_value" in forward_material
    assert "current_value" in forward_material
    assert forward_material["previous_value"] != forward_material["current_value"]
    assert forward_material["change_id"] != reverse_material["change_id"]
