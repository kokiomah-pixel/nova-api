from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .schema import _FORMAT_CHECKER, validate_retail_context_object


SCHEMA_VERSION = "0.1.0"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "retail_context_delta_v0_1.schema.json"
)
_MISSING = object()


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _stable_id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256(_canonical_json(parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def _identity_value(value: object) -> dict[str, object]:
    if value is _MISSING:
        return {"present": False}
    return {"present": True, "value": value}


def load_context_delta_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def context_delta_validator() -> Draft202012Validator:
    return Draft202012Validator(load_context_delta_schema(), format_checker=_FORMAT_CHECKER)


def validate_context_delta(delta: Mapping[str, Any]) -> None:
    context_delta_validator().validate(delta)


def _index_by_id(
    items: Sequence[Mapping[str, Any]], identity_field: str, category: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        identity = item[identity_field]
        if identity in indexed:
            raise ValueError(f"duplicate {category} identity: {identity}")
        indexed[identity] = copy.deepcopy(dict(item))
    return indexed


def _without(item: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key not in fields}


def _normalized_contradiction_content(item: Mapping[str, Any]) -> dict[str, Any]:
    content = _without(item, "status")
    content["evidence_ids"] = sorted(content["evidence_ids"])
    return content


def _normalized_unresolved_content(item: Mapping[str, Any]) -> dict[str, Any]:
    content = _without(item, "status")
    if "related_source_ids" in content:
        content["related_source_ids"] = sorted(content["related_source_ids"])
    return content


def build_context_delta(
    previous_context: Mapping[str, Any],
    current_context: Mapping[str, Any],
    *,
    generated_at: str,
) -> dict[str, Any]:
    """Compare two valid retail contexts without reacquiring or interpreting evidence."""

    previous = copy.deepcopy(dict(previous_context))
    current = copy.deepcopy(dict(current_context))
    validate_retail_context_object(previous)
    validate_retail_context_object(current)

    if previous["subject"] != current["subject"]:
        raise ValueError("previous and current contexts must have the same subject")
    if previous["schema_version"] != current["schema_version"]:
        raise ValueError("previous and current schema versions are incompatible")
    if previous["resource_type"] != current["resource_type"]:
        raise ValueError("previous and current resource types are incompatible")

    material_changes: list[dict[str, Any]] = []
    evidence_changes: list[dict[str, Any]] = []
    contradiction_changes: list[dict[str, Any]] = []
    unresolved_changes: list[dict[str, Any]] = []
    freshness_changes: list[dict[str, Any]] = []
    confidence_changes: list[dict[str, Any]] = []
    provenance_changes: list[dict[str, Any]] = []
    limitation_changes: list[dict[str, Any]] = []

    def add_material(
        category: str,
        change_type: str,
        item_id: str | None,
        field: str,
        previous_value: object = _MISSING,
        current_value: object = _MISSING,
    ) -> None:
        change_id = _stable_id(
            "material-change",
            category,
            change_type,
            item_id,
            field,
            _identity_value(previous_value),
            _identity_value(current_value),
        )
        change = {
            "change_id": change_id,
            "category": category,
            "change_type": change_type,
            "item_id": item_id,
            "field": field,
        }
        if previous_value is not _MISSING:
            change["previous_value"] = previous_value
        if current_value is not _MISSING:
            change["current_value"] = current_value
        material_changes.append(change)

    if previous["context_status"] != current["context_status"]:
        add_material(
            "context_status",
            "status_changed",
            None,
            "context_status",
            previous["context_status"],
            current["context_status"],
        )

    previous_evidence = _index_by_id(previous["evidence"], "evidence_id", "evidence")
    current_evidence = _index_by_id(current["evidence"], "evidence_id", "evidence")
    for evidence_id in sorted(previous_evidence.keys() | current_evidence.keys()):
        before = previous_evidence.get(evidence_id)
        after = current_evidence.get(evidence_id)
        if before is None or after is None:
            change_type = "added" if before is None else "removed"
            item = after if after is not None else before
            evidence_changes.append(
                {
                    "change_id": _stable_id("evidence-change", evidence_id, change_type),
                    "evidence_id": evidence_id,
                    "source_id": item["source_id"],
                    "change_type": change_type,
                    "previous_status": None if before is None else before["evidence_status"],
                    "current_status": None if after is None else after["evidence_status"],
                }
            )
            add_material("evidence", change_type, evidence_id, "evidence")
            continue

        if before["evidence_status"] != after["evidence_status"]:
            before_status = before["evidence_status"]
            after_status = after["evidence_status"]
            evidence_changes.append(
                {
                    "change_id": _stable_id(
                        "evidence-change",
                        evidence_id,
                        "status_changed",
                        before_status,
                        after_status,
                    ),
                    "evidence_id": evidence_id,
                    "source_id": after["source_id"],
                    "change_type": "status_changed",
                    "previous_status": before_status,
                    "current_status": after_status,
                }
            )
            add_material(
                "evidence",
                "status_changed",
                evidence_id,
                "evidence_status",
                before_status,
                after_status,
            )

        before_content = _without(before, "evidence_status")
        after_content = _without(after, "evidence_status")
        if before_content != after_content:
            evidence_changes.append(
                {
                    "change_id": _stable_id(
                        "evidence-change",
                        evidence_id,
                        "content_changed",
                        before_content,
                        after_content,
                    ),
                    "evidence_id": evidence_id,
                    "source_id": after["source_id"],
                    "change_type": "content_changed",
                    "previous_status": before["evidence_status"],
                    "current_status": after["evidence_status"],
                }
            )
            add_material(
                "evidence",
                "content_changed",
                evidence_id,
                "content",
                _canonical_json(before_content),
                _canonical_json(after_content),
            )

    previous_contradictions = _index_by_id(
        previous["contradictions"], "contradiction_id", "contradiction"
    )
    current_contradictions = _index_by_id(
        current["contradictions"], "contradiction_id", "contradiction"
    )
    for contradiction_id in sorted(
        previous_contradictions.keys() | current_contradictions.keys()
    ):
        before = previous_contradictions.get(contradiction_id)
        after = current_contradictions.get(contradiction_id)
        change_types: list[str] = []
        if before is None:
            change_types.append("added")
        elif after is None:
            change_types.append("removed")
        else:
            if before["status"] != after["status"]:
                change_types.append("status_changed")
            if _normalized_contradiction_content(before) != _normalized_contradiction_content(after):
                change_types.append("content_changed")
        for change_type in change_types:
            if change_type == "status_changed":
                before_identity = before["status"]
                after_identity = after["status"]
            elif change_type == "content_changed":
                before_identity = _normalized_contradiction_content(before)
                after_identity = _normalized_contradiction_content(after)
            else:
                before_identity = None
                after_identity = None
            contradiction_changes.append(
                {
                    "change_id": _stable_id(
                        "contradiction-change",
                        contradiction_id,
                        change_type,
                        before_identity,
                        after_identity,
                    ),
                    "contradiction_id": contradiction_id,
                    "change_type": change_type,
                    "previous_status": None if before is None else before["status"],
                    "current_status": None if after is None else after["status"],
                    "treatment": (
                        "removed_from_current_bounded_context"
                        if change_type == "removed"
                        else "structural_change_only"
                    ),
                }
            )
            add_material(
                "contradiction",
                change_type,
                contradiction_id,
                "status" if change_type == "status_changed" else "contradiction",
                (
                    before["status"]
                    if change_type == "status_changed"
                    else _canonical_json(_normalized_contradiction_content(before))
                    if change_type == "content_changed"
                    else _MISSING
                ),
                (
                    after["status"]
                    if change_type == "status_changed"
                    else _canonical_json(_normalized_contradiction_content(after))
                    if change_type == "content_changed"
                    else _MISSING
                ),
            )

    previous_unresolved = _index_by_id(
        previous["unresolved_evidence"], "issue_id", "unresolved evidence"
    )
    current_unresolved = _index_by_id(
        current["unresolved_evidence"], "issue_id", "unresolved evidence"
    )
    for issue_id in sorted(previous_unresolved.keys() | current_unresolved.keys()):
        before = previous_unresolved.get(issue_id)
        after = current_unresolved.get(issue_id)
        change_types: list[str] = []
        if before is None:
            change_types.append("added")
        elif after is None:
            change_types.append("removed")
        else:
            if before["status"] != after["status"]:
                change_types.append("status_changed")
            if _normalized_unresolved_content(before) != _normalized_unresolved_content(after):
                change_types.append("content_changed")
        for change_type in change_types:
            if change_type == "status_changed":
                before_identity = before["status"]
                after_identity = after["status"]
            elif change_type == "content_changed":
                before_identity = _normalized_unresolved_content(before)
                after_identity = _normalized_unresolved_content(after)
            else:
                before_identity = None
                after_identity = None
            unresolved_changes.append(
                {
                    "change_id": _stable_id(
                        "unresolved-change",
                        issue_id,
                        change_type,
                        before_identity,
                        after_identity,
                    ),
                    "issue_id": issue_id,
                    "change_type": change_type,
                    "previous_status": None if before is None else before["status"],
                    "current_status": None if after is None else after["status"],
                    "treatment": (
                        "removed_from_current_bounded_context"
                        if change_type == "removed"
                        else "structural_change_only"
                    ),
                }
            )
            add_material(
                "unresolved_evidence",
                change_type,
                issue_id,
                "status" if change_type == "status_changed" else "unresolved_evidence",
                (
                    before["status"]
                    if change_type == "status_changed"
                    else _canonical_json(_normalized_unresolved_content(before))
                    if change_type == "content_changed"
                    else _MISSING
                ),
                (
                    after["status"]
                    if change_type == "status_changed"
                    else _canonical_json(_normalized_unresolved_content(after))
                    if change_type == "content_changed"
                    else _MISSING
                ),
            )

    for field in ("freshness_status", "observed_at", "source_age_seconds"):
        before = previous["freshness"][field]
        after = current["freshness"][field]
        if before == after:
            continue
        freshness_changes.append(
            {
                "change_id": _stable_id("freshness-change", field, before, after),
                "field": field,
                "previous_value": before,
                "current_value": after,
            }
        )
        add_material("freshness", "value_changed", None, field, before, after)

    for field in ("level", "basis"):
        before = previous["confidence"][field]
        after = current["confidence"][field]
        if before == after:
            continue
        confidence_changes.append(
            {
                "change_id": _stable_id("confidence-change", field, before, after),
                "field": field,
                "previous_value": before,
                "current_value": after,
            }
        )
        add_material("confidence", "value_changed", None, field, before, after)

    previous_provenance = _index_by_id(previous["provenance"], "source_id", "provenance")
    current_provenance = _index_by_id(current["provenance"], "source_id", "provenance")
    provenance_fields = (
        ("source_status", "source_status_changed", "status_changed"),
        ("claim_reconciliation_status", "claim_reconciliation_status_changed", "status_changed"),
        ("contribution_scope", "contribution_scope_changed", "scope_changed"),
        ("source_type", "source_type_changed", "content_changed"),
        ("observed_at", "observed_at_changed", "value_changed"),
    )
    for source_id in sorted(previous_provenance.keys() | current_provenance.keys()):
        before = previous_provenance.get(source_id)
        after = current_provenance.get(source_id)
        if before is None or after is None:
            change_type = "added" if before is None else "removed"
            provenance_changes.append(
                {
                    "change_id": _stable_id("provenance-change", source_id, change_type),
                    "source_id": source_id,
                    "change_type": change_type,
                    "field": "source",
                    "previous_value": None if before is None else source_id,
                    "current_value": None if after is None else source_id,
                }
            )
            add_material("provenance", change_type, source_id, "source")
            continue
        for field, change_type, material_type in provenance_fields:
            before_value = before[field]
            after_value = after[field]
            if field == "contribution_scope":
                before_value = sorted(before_value)
                after_value = sorted(after_value)
            if before_value == after_value:
                continue
            provenance_changes.append(
                {
                    "change_id": _stable_id(
                        "provenance-change", source_id, field, before_value, after_value
                    ),
                    "source_id": source_id,
                    "change_type": change_type,
                    "field": field,
                    "previous_value": before_value,
                    "current_value": after_value,
                }
            )
            add_material(
                "provenance", material_type, source_id, field, before_value, after_value
            )

    previous_limitations = _index_by_id(
        previous["limitations"], "limitation_id", "limitation"
    )
    current_limitations = _index_by_id(
        current["limitations"], "limitation_id", "limitation"
    )
    for limitation_id in sorted(previous_limitations.keys() | current_limitations.keys()):
        before = previous_limitations.get(limitation_id)
        after = current_limitations.get(limitation_id)
        change_types: list[str] = []
        if before is None:
            change_types.append("added")
        elif after is None:
            change_types.append("removed")
        else:
            if before["impact"] != after["impact"]:
                change_types.append("impact_changed")
            if before["description"] != after["description"]:
                change_types.append("content_changed")
        for change_type in change_types:
            if change_type == "impact_changed":
                before_identity = before["impact"]
                after_identity = after["impact"]
            elif change_type == "content_changed":
                before_identity = before["description"]
                after_identity = after["description"]
            else:
                before_identity = None
                after_identity = None
            limitation_changes.append(
                {
                    "change_id": _stable_id(
                        "limitation-change",
                        limitation_id,
                        change_type,
                        before_identity,
                        after_identity,
                    ),
                    "limitation_id": limitation_id,
                    "change_type": change_type,
                    "previous_impact": None if before is None else before["impact"],
                    "current_impact": None if after is None else after["impact"],
                    "treatment": (
                        "removed_from_current_bounded_context"
                        if change_type == "removed"
                        else "structural_change_only"
                    ),
                }
            )
            add_material(
                "limitation",
                "value_changed" if change_type == "impact_changed" else change_type,
                limitation_id,
                "impact" if change_type == "impact_changed" else "limitation",
                (
                    before["impact"]
                    if change_type == "impact_changed"
                    else before["description"]
                    if change_type == "content_changed"
                    else _MISSING
                ),
                (
                    after["impact"]
                    if change_type == "impact_changed"
                    else after["description"]
                    if change_type == "content_changed"
                    else _MISSING
                ),
            )

    for changes in (
        material_changes,
        evidence_changes,
        contradiction_changes,
        unresolved_changes,
        freshness_changes,
        confidence_changes,
        provenance_changes,
        limitation_changes,
    ):
        changes.sort(key=lambda item: item["change_id"])

    comparison_limitations: list[dict[str, Any]] = []
    insufficient_basis = "insufficient_evidence" in {
        previous["context_status"],
        current["context_status"],
    }
    if insufficient_basis:
        limitation_id = _stable_id(
            "limit",
            "insufficient-comparison-basis",
            previous["resource_id"],
            current["resource_id"],
        )
        comparison_limitations.append(
            {
                "limitation_id": limitation_id,
                "description": "At least one input context has insufficient evidence; the delta reports bounded structural differences only.",
                "impact": "indeterminate",
            }
        )

    if material_changes:
        delta_status = "changed"
    elif insufficient_basis:
        delta_status = "indeterminate"
    else:
        delta_status = "unchanged"

    resource_material = {
        "subject": previous["subject"],
        "previous_context_id": previous["resource_id"],
        "current_context_id": current["resource_id"],
        "generated_at": generated_at,
        "delta_status": delta_status,
        "material_changes": material_changes,
        "evidence_state_changes": evidence_changes,
        "contradiction_changes": contradiction_changes,
        "unresolved_evidence_changes": unresolved_changes,
        "freshness_changes": freshness_changes,
        "confidence_changes": confidence_changes,
        "provenance_changes": provenance_changes,
        "limitation_changes": limitation_changes,
        "limitations": comparison_limitations,
    }
    result = {
        "resource_id": _stable_id("context-delta", resource_material),
        "resource_type": "context_delta",
        "schema_version": SCHEMA_VERSION,
        "subject": copy.deepcopy(previous["subject"]),
        "generated_at": generated_at,
        "previous_context_id": previous["resource_id"],
        "current_context_id": current["resource_id"],
        "delta_status": delta_status,
        "material_changes": material_changes,
        "evidence_state_changes": evidence_changes,
        "contradiction_changes": contradiction_changes,
        "unresolved_evidence_changes": unresolved_changes,
        "freshness_changes": freshness_changes,
        "confidence_changes": confidence_changes,
        "provenance_changes": provenance_changes,
        "limitation_changes": limitation_changes,
        "limitations": comparison_limitations,
        "authority_effect": "none",
    }
    validate_context_delta(result)
    return result
