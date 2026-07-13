#!/usr/bin/env python3
from __future__ import annotations

from chronology_common import LANE_PATHS, ROOT, atomic_write_json, ordered, read_jsonl


def build_index() -> dict:
    lanes = {}
    generated_at = "1970-01-01T00:00:00Z"
    for lane, path in LANE_PATHS.items():
        events = ordered(read_jsonl(path))
        if events:
            generated_at = max(generated_at, max(event["recorded_at"] for event in events))
        latest = events[-1] if events else None
        lanes[lane] = {"path": str(path.relative_to(ROOT)), "event_count": len(events), "latest_event_id": latest["event_id"] if latest else None, "latest_occurred_at": latest["occurred_at"] if latest else None}
    return {"schema_version": "1.0.0", "generated_at": generated_at, "lanes": lanes}


def main() -> None:
    path = ROOT / "chronology/indexes/chronology-master-index.json"
    atomic_write_json(path, build_index())
    print(f"Chronology master index written: {path}")


if __name__ == "__main__": main()
