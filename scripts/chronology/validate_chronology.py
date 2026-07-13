#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from chronology_common import LANE_PATHS, ROOT, ChronologyError, load_schema, parse_timestamp, read_jsonl

PREFIXES = {"reflex": "RFX-", "archive": "ARC-", "operations": "OPS-", "governance": "GOV-"}
CORRECTION_TYPES = {"archive_correction_recorded", "operational_correction_recorded", "governance_correction_recorded", "reflex_correction_recorded"}
GOVERNANCE_TRANSITIONS = {
    "proposed": {"reviewed", "rejected", "superseded"},
    "reviewed": {"authorized", "rejected", "superseded"},
    "authorized": {"implemented", "blocked", "superseded"},
    "implemented": {"accepted", "rejected", "superseded"},
    "accepted": {"superseded"},
}


def _error(errors: list[str], event: dict[str, Any], message: str) -> None:
    errors.append(f"{event.get('event_id', '<unknown>')}: {message}")


def validate_events(
    lane_events: dict[str, list[dict[str, Any]]],
    state_path: Path | None = None,
    *,
    enforce_gate_state: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    schema_validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    all_events = [event for events in lane_events.values() for event in events]
    ids = [event.get("event_id") for event in all_events]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate chronology event ID")
    by_id = {event.get("event_id"): event for event in all_events}

    for lane, events in lane_events.items():
        for event in events:
            for issue in schema_validator.iter_errors(event):
                _error(errors, event, issue.message)
            if event.get("chronology_lane") != lane:
                _error(errors, event, f"ledger lane is {lane}")
            if not str(event.get("event_id", "")).startswith(PREFIXES[lane]):
                _error(errors, event, "event ID prefix does not match lane")
            try:
                occurred = parse_timestamp(str(event.get("occurred_at")))
                recorded = parse_timestamp(str(event.get("recorded_at")))
                if recorded < occurred:
                    _error(errors, event, "recorded_at precedes occurred_at")
            except ChronologyError as exc:
                _error(errors, event, str(exc))
            if event.get("confidence") == "verified" and not event.get("evidence_refs"):
                _error(errors, event, "verified event requires evidence")
            if event.get("acceptance_status") == "accepted" and event.get("review_status") != "reviewed":
                _error(errors, event, "accepted event requires reviewed status")
            if event.get("confidence") in {"inferred", "unresolved"} and event.get("acceptance_status") == "accepted":
                _error(errors, event, "uncertain underlying claim cannot be accepted")
            if event.get("event_type") in CORRECTION_TYPES:
                target = event.get("corrects_event_id")
                if not target or target not in by_id:
                    _error(errors, event, "correction target must resolve")
                if not event.get("correction_reason"):
                    _error(errors, event, "correction reason is required")
            for related in event.get("supersedes", []) + event.get("superseded_by", []):
                if related not in by_id:
                    _error(errors, event, f"supersession reference does not resolve: {related}")
            prior = (event.get("prior_state") or {}).get("authority_status")
            resulting = (event.get("resulting_state") or {}).get("authority_status")
            if prior and resulting and resulting not in GOVERNANCE_TRANSITIONS.get(prior, set()):
                _error(errors, event, f"invalid authority transition {prior} -> {resulting}")
            if lane == "reflex":
                if event.get("actor", {}).get("type") in {"CI", "repository"}:
                    _error(errors, event, "CI and repository events cannot enter Reflex chronology")
                if event.get("event_type", "").startswith(("CI_", "commit_", "pull_request_")):
                    _error(errors, event, "operational event cannot enter Reflex chronology")
            if event.get("authority_status") == "executed" and "execution" not in event.get("event_type", ""):
                _error(errors, event, "execution status requires an execution event")

    if enforce_gate_state:
        state_file = state_path or ROOT / "chronology/governance/current-governance-state.yaml"
        state = yaml.safe_load(state_file.read_text(encoding="utf-8"))
        gate4b = state["gates"]["Gate_4B"]
        gate5 = state["gates"]["Gate_5"]
        if gate4b["execution"] == "blocked_no_nonproduction_endpoint" and gate4b["accepted"] is not False:
            errors.append("Gate 4B cannot be accepted while execution is blocked")
        if gate4b["execution"] != "blocked_no_nonproduction_endpoint":
            execution_events = [event for event in all_events if event.get("event_type") == "gate_execution_completed" and "4B" in event.get("event_id", "")]
            if not execution_events:
                errors.append("Gate 4B execution claim lacks execution evidence")
        for gate in (gate4b, gate5):
            for event_id in gate.get("governing_event_ids", []):
                if event_id not in by_id:
                    errors.append(f"Governing event does not resolve: {event_id}")
        if gate5["authorized"] is True:
            authorization = [event for event in lane_events["governance"] if event.get("event_type") == "gate_authorized" and "GATE5" in event.get("event_id", "")]
            if not authorization:
                errors.append("Gate 5 authorization lacks governance event")
        if gate5["authorized"] is False and any("gate_5" in event.get("event_type", "").lower() for event in lane_events["operations"]):
            errors.append("Gate 5 operational event exists before authorization")

    lane_results = {}
    for lane, events in lane_events.items():
        lane_ids = {event.get("event_id") for event in events}
        lane_errors = [error for error in errors if error.split(":", 1)[0] in lane_ids]
        unknown_ids = [event["event_id"] for event in events if event.get("confidence") == "unresolved"]
        lane_results[lane] = {"event_count": len(events), "errors": lane_errors, "warnings": [], "explicit_unknowns": len(unknown_ids), "explicit_unknown_event_ids": unknown_ids}
    return {"status": "passed" if not errors else "failed", "errors": errors, "warnings": warnings, "unsupported_claims": sum("unsupported" in error.lower() for error in errors), "lanes": lane_results, "event_count": len(all_events)}


def load_and_validate() -> dict[str, Any]:
    return validate_events({lane: read_jsonl(path) for lane, path in LANE_PATHS.items()})


def main() -> None:
    report = load_and_validate()
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
