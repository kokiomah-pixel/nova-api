from jsonschema import Draft202012Validator, FormatChecker

from chronology_common import load_schema
from helpers import event, lanes
from validate_chronology import validate_events


def test_valid_event_schema() -> None:
    Draft202012Validator(load_schema(), format_checker=FormatChecker()).validate(event())


def test_invalid_timestamp_is_rejected() -> None:
    assert validate_events(lanes(event(occurred_at="not-a-time")), enforce_gate_state=False)["status"] == "failed"
