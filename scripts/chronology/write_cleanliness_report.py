#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from chronology_common import (
    ROOT,
    atomic_write_json,
    resolve_ci_checkout_commit,
    resolve_reviewed_source_commit,
)
from validate_chronology import load_and_validate


def _state(lane: str, result: dict) -> str:
    if result["errors"]:
        return "not_fully_clean"
    if result["warnings"]:
        return "partially_clean"
    if result["explicit_unknowns"]:
        return "clean_with_explicit_unknowns"
    return "clean_intact" if lane == "reflex" else "clean_reconciled"


def build_report() -> dict:
    validation = load_and_validate()
    source_commit = resolve_reviewed_source_commit(ROOT)
    ci_checkout_commit = resolve_ci_checkout_commit(ROOT)
    generated_at = datetime.now(timezone.utc).isoformat()
    lanes = {f"{lane if lane != 'operations' else 'operational'}_chronology": {"state": _state(lane, result), "event_count": result["event_count"], "errors": len(result["errors"]), "warnings": len(result["warnings"]), "explicit_unknowns": result["explicit_unknowns"]} for lane, result in validation["lanes"].items()}
    unresolved = [event_id for result in validation["lanes"].values() for event_id in result["explicit_unknown_event_ids"]]
    return {"schema_version": "1.0.0", "generated_at": generated_at, "source_commit": source_commit, "ci_checkout_commit": ci_checkout_commit, "validation_status": validation["status"], "freshness": {"source_commit": source_commit, "generated_at": generated_at, "maximum_age_hours": 24}, "lanes": lanes, "unsupported_claims": validation["unsupported_claims"], "unresolved_items": unresolved + validation["errors"]}


def main() -> None:
    report = build_report()
    path = ROOT / "reports/chronology/chronology-cleanliness.json"
    atomic_write_json(path, report)
    print(f"Chronology cleanliness report written: {path}")
    if report["validation_status"] != "passed": raise SystemExit(1)


if __name__ == "__main__": main()
