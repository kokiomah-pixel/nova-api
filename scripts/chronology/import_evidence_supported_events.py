#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from chronology_common import LANE_PATHS, ChronologyError, append_jsonl, atomic_write_json, load_schema, read_jsonl


def import_events(*, manifest_path: Path, events_path: Path, approved_by: str, reviewed_by: str, report_path: Path) -> dict:
    if approved_by != "Architect" or reviewed_by != "Jarvis-Nova CCO":
        raise ChronologyError("Exact Architect approval and Jarvis-Nova CCO review are required")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    approval = manifest.get("approval", {})
    if approval.get("reviewed") is not True or approval.get("authorized") is not True:
        raise ChronologyError("Manifest is not reviewed and authorized")
    approved_ids = manifest.get("approved_event_ids", approval.get("approved_event_ids"))
    if not isinstance(approved_ids, list) or not approved_ids or "*" in approved_ids:
        raise ChronologyError("Exact approved event IDs are required; wildcard approval is prohibited")
    proposed = read_jsonl(events_path)
    proposed_by_id = {event["event_id"]: event for event in proposed}
    if set(approved_ids) - set(proposed_by_id):
        raise ChronologyError("Manifest approves an event that is absent from the proposal")
    selected = [proposed_by_id[event_id] for event_id in approved_ids]
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    for event in selected:
        validator.validate(event)
    existing = {event["event_id"] for path in LANE_PATHS.values() for event in read_jsonl(path)}
    if existing.intersection(approved_ids):
        raise ChronologyError("Approved event ID already exists")
    by_lane: dict[str, list[dict]] = {lane: [] for lane in LANE_PATHS}
    for event in selected: by_lane[event["chronology_lane"]].append(event)
    for lane, events in by_lane.items():
        if events: append_jsonl(LANE_PATHS[lane], events)
    report = {"status": "passed", "approved_by": approved_by, "reviewed_by": reviewed_by, "imported_event_ids": approved_ids}
    atomic_write_json(report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--reviewed-by", required=True)
    parser.add_argument("--report", type=Path, default=Path("reports/chronology/import-report.json"))
    args = parser.parse_args()
    try:
        report = import_events(manifest_path=args.manifest, events_path=args.events, approved_by=args.approved_by, reviewed_by=args.reviewed_by, report_path=args.report)
    except (ChronologyError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Chronology import rejected: {exc}")
        raise SystemExit(1) from exc
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__": main()
