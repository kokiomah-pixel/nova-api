from __future__ import annotations

import json
import subprocess
from pathlib import Path

from chronology_common import ROOT

UNKNOWN = {lane: "unknown_report_unavailable" for lane in ("reflex_chronology", "archive_chronology", "operational_chronology", "governance_chronology")}


def load_chronology_status(report_path: Path | None = None) -> dict:
    path = report_path or ROOT / "reports/chronology/chronology-cleanliness.json"
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        if report.get("source_commit") != head:
            return {"current_cleanliness_diagnosis": {lane: "stale_commit_mismatch" for lane in UNKNOWN}}
        if report.get("validation_status") != "passed" or report.get("unsupported_claims") != 0:
            raise ValueError("Report did not pass chronology validation")
        lanes = report["lanes"]
        diagnosis = {}
        for lane in UNKNOWN:
            result = lanes[lane]
            if result["errors"] != 0:
                expected = "not_fully_clean"
            elif result["warnings"] != 0:
                expected = "partially_clean"
            elif result["explicit_unknowns"] != 0:
                expected = "clean_with_explicit_unknowns"
            elif lane == "reflex_chronology":
                expected = "clean_intact"
            else:
                expected = "clean_reconciled"
            if result["state"] != expected:
                raise ValueError("Manual cleanliness override detected")
            diagnosis[lane] = expected
    except FileNotFoundError:
        diagnosis = UNKNOWN.copy()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.SubprocessError):
        diagnosis = {lane: "invalid_report" for lane in UNKNOWN}
    return {"current_cleanliness_diagnosis": diagnosis}
