import json
from pathlib import Path

import pytest
import yaml

from chronology_common import ChronologyError, read_jsonl
from helpers import event, lanes
from validate_chronology import validate_events


def test_duplicate_event_id_rejected() -> None:
    item = event()
    assert validate_events(lanes(item, dict(item)))["status"] == "failed"


def test_lane_prefix_mismatch_rejected() -> None:
    assert validate_events(lanes(event("GOV-20260713-WRONG-LANE")))["status"] == "failed"


def test_verified_without_evidence_rejected() -> None:
    assert validate_events(lanes(event(evidence_refs=[])))["status"] == "failed"


def test_execution_without_execution_event_rejected() -> None:
    assert validate_events(lanes(event(authority_status="executed")))["status"] == "failed"


def test_ci_cannot_auto_import_to_reflex() -> None:
    item = event("RFX-20260713-CI-IMPORT", "reflex", actor={"type": "CI", "identifier": "test"}, event_type="CI_passed")
    assert validate_events(lanes(item))["status"] == "failed"


def test_gate4b_false_acceptance_rejected(tmp_path: Path) -> None:
    state = {"schema_version": "1.0.0", "gates": {"Gate_4B": {"implementation": "merged", "execution": "blocked_no_nonproduction_endpoint", "accepted": True, "governing_event_ids": []}, "Gate_5": {"authorized": False, "governing_event_ids": []}}}
    path = tmp_path / "state.yaml"; path.write_text(yaml.safe_dump(state))
    assert validate_events(lanes(), state_path=path)["status"] == "failed"


def test_gate5_false_authorization_rejected(tmp_path: Path) -> None:
    state = {"schema_version": "1.0.0", "gates": {"Gate_4B": {"implementation": "merged", "execution": "blocked_no_nonproduction_endpoint", "accepted": False, "governing_event_ids": []}, "Gate_5": {"authorized": True, "governing_event_ids": []}}}
    path = tmp_path / "state.yaml"; path.write_text(yaml.safe_dump(state))
    assert validate_events(lanes(), state_path=path)["status"] == "failed"


def test_malformed_jsonl_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"; path.write_text("{bad json}\n")
    with pytest.raises(ChronologyError): read_jsonl(path)
