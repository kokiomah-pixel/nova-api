from helpers import event, lanes
from validate_chronology import validate_events


def test_valid_correction_and_supersession() -> None:
    original = event("GOV-20260713-ORIGINAL", "governance", superseded_by=["GOV-20260713-CORRECTION"])
    correction = event("GOV-20260713-CORRECTION", "governance", event_type="governance_correction_recorded", corrects_event_id=original["event_id"], correction_reason="Evidence corrected the reviewed commit.", supersedes=[original["event_id"]])
    assert validate_events(lanes(original, correction), enforce_gate_state=False)["status"] == "passed"


def test_missing_correction_target_and_reason_are_rejected() -> None:
    correction = event("GOV-20260713-BAD-CORRECTION", "governance", event_type="governance_correction_recorded", corrects_event_id="GOV-20260713-MISSING")
    report = validate_events(lanes(correction))
    assert report["status"] == "failed" and len(report["errors"]) >= 2


def test_unresolved_supersession_is_rejected() -> None:
    item = event(supersedes=["OPS-20260713-NOT-PRESENT"])
    assert validate_events(lanes(item))["status"] == "failed"
