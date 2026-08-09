from __future__ import annotations

from copy import deepcopy

import yaml

from scripts.validate_arc_market_signal_watch import (
    ARC_EVIDENCE_ID,
    ARC_SIGNAL_ID,
    PROHIBITED_REFERENCE_PATHS,
    REPO_ROOT,
    validate_arc_entry,
    validate_arc_watch_repository,
)


REGISTER = REPO_ROOT / "docs/market/market-signal-watch-register.yaml"


def _arc_entry() -> dict:
    register = yaml.safe_load(REGISTER.read_text(encoding="utf-8"))
    return next(item for item in register["signals"] if item.get("signal_id") == ARC_SIGNAL_ID)


def test_arc_market_signal_repository_contract_passes():
    assert validate_arc_watch_repository() == []


def test_arc_market_signal_is_non_authoritative():
    entry = _arc_entry()

    assert entry["lifecycle_status"] == "observed_watch"
    assert entry["epistemic_status"] == "externally_observed"
    assert entry["review_state"] == "governed_watch"
    assert entry["authority_effect"] == "none"
    assert entry["implementation_authority_created"] is False
    assert entry["production_authority_created"] is False
    assert entry["runtime_change"] is False
    assert entry["production_change"] is False
    assert entry["external_integration"] is False


def test_arc_market_signal_creates_no_accepted_state_memory_or_chronology():
    entry = _arc_entry()

    assert entry["accepted_state_change"] is False
    assert entry["accepted_state_effect"] == "none"
    assert entry["chronology_effect"] == "none"
    assert entry["chronology_action"] == "none"
    assert entry["Reflex_Memory_effect"] == "none"
    assert entry["Reflex_Memory_action"] == "none"
    assert entry["constraint_effect"] == "none"
    assert entry["constraint_action"] == "none"
    assert entry["policy_effect"] == "none"
    assert entry["policy_action"] == "none"
    assert entry["product_requirement_effect"] == "none"
    assert entry["roadmap_effect"] == "none"
    assert entry["roadmap_action"] == "none"

    for relative in PROHIBITED_REFERENCE_PATHS:
        target = REPO_ROOT / relative
        files = [target] if target.is_file() else [path for path in target.rglob("*") if path.is_file()]
        for path in files:
            text = path.read_text(encoding="utf-8")
            assert ARC_SIGNAL_ID not in text
            assert ARC_EVIDENCE_ID not in text


def test_arc_boundary_preserves_local_authority_and_external_execution():
    assertions = _arc_entry()["boundary_assertions"]

    assert assertions == {
        "Nova_executes": False,
        "Nova_signs": False,
        "Nova_controls_wallet": False,
        "local_authority_decides": True,
        "external_system_executes": True,
    }


def test_validator_fails_if_market_signal_gains_authority():
    entry = deepcopy(_arc_entry())
    entry["authority_effect"] = "implementation"
    entry["implementation_authority_created"] = True

    errors = validate_arc_entry(entry)

    fields = {error.field for error in errors}
    assert f"signals.{ARC_SIGNAL_ID}.authority_effect" in fields
    assert f"signals.{ARC_SIGNAL_ID}.implementation_authority_created" in fields


def test_validator_fails_if_single_event_becomes_escalation():
    entry = deepcopy(_arc_entry())
    entry["escalation_rule"]["interesting_event_is_escalation"] = True

    errors = validate_arc_entry(entry)

    assert any(
        error.field.endswith("escalation_rule.interesting_event_is_escalation")
        for error in errors
    )


def test_validator_fails_if_required_non_claim_is_removed():
    entry = deepcopy(_arc_entry())
    entry["not_established"].remove("Nova_product_market_fit")

    errors = validate_arc_entry(entry)

    assert any(error.field.endswith("not_established") for error in errors)
