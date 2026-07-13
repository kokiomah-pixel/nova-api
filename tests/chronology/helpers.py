from __future__ import annotations

from typing import Any


def event(event_id: str = "OPS-20260713-TEST-EVENT", lane: str = "operations", **updates: Any) -> dict[str, Any]:
    value = {
        "schema_version": "1.0.0", "event_id": event_id, "event_type": "local_verification_passed", "chronology_lane": lane,
        "occurred_at": "2026-07-13T01:00:00Z", "recorded_at": "2026-07-13T02:00:00Z", "effective_at": None,
        "actor": {"type": "operator", "identifier": "test"}, "repository": "test/repository", "branch": "test", "commit": None,
        "artifact_refs": [], "evidence_refs": [{"type": "file", "value": "test-evidence"}], "prior_state": None, "resulting_state": None,
        "authority_status": "informational", "review_status": "not_required", "acceptance_status": "not_applicable", "confidence": "verified",
        "supersedes": [], "superseded_by": [], "corrects_event_id": None, "correction_reason": None, "notes": None,
    }
    value.update(updates)
    return value


def lanes(*events: dict) -> dict[str, list[dict]]:
    result = {"reflex": [], "archive": [], "operations": [], "governance": []}
    for item in events: result[item["chronology_lane"]].append(item)
    return result
