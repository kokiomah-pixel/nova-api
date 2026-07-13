#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from chronology_common import LANE_PATHS, ROOT, read_jsonl, sha256


def inventory() -> dict:
    archive_files = sorted(path for path in (ROOT / "archive").rglob("*") if path.is_file())
    return {
        "schema_version": "1.0.0",
        "mode": "read_only_inventory",
        "ledgers": {lane: {"path": str(path.relative_to(ROOT)), "event_count": len(read_jsonl(path))} for lane, path in LANE_PATHS.items()},
        "archive_sources": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "manifest_status": "unresolved_no_canonical_manifest"} for path in archive_files],
        "duplicate_summary": {"canonical": 0, "mirrored": 0, "superseded": 0, "conflicting": 0, "unresolved": len(archive_files)},
        "unresolved_fields": ["archive creation timestamps", "archive custody chain", "canonical archive manifest"],
    }


def proposal() -> dict:
    data = inventory()
    data["mode"] = "review_only_proposal"
    data["reconciliation_items"] = [{"source": item["path"], "proposed_lane": "archive", "proposed_event_type": "archive_integrity_verified", "evidence_quality": "partially_supported", "authority_status": "informational", "review_status": "pending", "acceptance_status": "pending", "confidence": "unresolved", "duplicate_status": "unresolved", "unresolved_fields": ["occurred_at", "custody_status", "manifest"], "proposed_event": None} for item in data["archive_sources"]]
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--propose", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = proposal() if args.propose else inventory()
    rendered = yaml.safe_dump(result, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Chronology reconciliation output written: {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__": main()
