from helpers import event, lanes
from validate_chronology import validate_events


def test_valid_governance_transition() -> None:
    item = event("GOV-20260713-VALID-TRANSITION", "governance", event_type="doctrine_authorized", authority_status="authorized", review_status="reviewed", acceptance_status="pending", prior_state={"authority_status": "reviewed"}, resulting_state={"authority_status": "authorized"})
    assert validate_events(lanes(item), enforce_gate_state=False)["status"] == "passed"


def test_proposed_to_accepted_is_rejected() -> None:
    item = event("GOV-20260713-INVALID-TRANSITION", "governance", event_type="doctrine_accepted", authority_status="accepted", review_status="reviewed", acceptance_status="accepted", prior_state={"authority_status": "proposed"}, resulting_state={"authority_status": "accepted"})
    assert validate_events(lanes(item))["status"] == "failed"


def test_accepted_without_review_is_rejected() -> None:
    item = event("GOV-20260713-NO-REVIEW", "governance", acceptance_status="accepted", review_status="pending")
    assert validate_events(lanes(item))["status"] == "failed"
