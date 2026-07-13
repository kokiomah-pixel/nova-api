import json
from pathlib import Path

import pytest
import yaml

import import_evidence_supported_events as importer
from chronology_common import ChronologyError, read_jsonl
from helpers import event


def _lane_paths(tmp_path: Path) -> dict[str, Path]:
    paths = {lane: tmp_path / f"{lane}.jsonl" for lane in ("reflex", "archive", "operations", "governance")}
    for path in paths.values(): path.write_text("")
    return paths


def test_controlled_import_appends_only_exact_approved_ids(tmp_path, monkeypatch) -> None:
    paths = _lane_paths(tmp_path); monkeypatch.setattr(importer, "LANE_PATHS", paths)
    proposed = tmp_path / "proposed.jsonl"; proposed.write_text(json.dumps(event()) + "\n")
    manifest = tmp_path / "manifest.yaml"; manifest.write_text(yaml.safe_dump({"approval": {"reviewed": True, "authorized": True}, "approved_event_ids": ["OPS-20260713-TEST-EVENT"]}))
    report = importer.import_events(manifest_path=manifest, events_path=proposed, approved_by="Architect", reviewed_by="Jarvis-Nova CCO", report_path=tmp_path / "report.json")
    assert report["imported_event_ids"] == ["OPS-20260713-TEST-EVENT"]
    assert len(read_jsonl(paths["operations"])) == 1


def test_wildcard_approval_is_rejected(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(importer, "LANE_PATHS", _lane_paths(tmp_path))
    proposed = tmp_path / "proposed.jsonl"; proposed.write_text(json.dumps(event()) + "\n")
    manifest = tmp_path / "manifest.yaml"; manifest.write_text(yaml.safe_dump({"approval": {"reviewed": True, "authorized": True}, "approved_event_ids": ["*"]}))
    with pytest.raises(ChronologyError, match="wildcard"):
        importer.import_events(manifest_path=manifest, events_path=proposed, approved_by="Architect", reviewed_by="Jarvis-Nova CCO", report_path=tmp_path / "report.json")
