import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from core.accepted_state_synchronization import (
    ACCEPTED_STATE_ID,
    ARCHIVE_RECORD_PATH,
    CHRONOLOGY_EVENT_ID,
    CHRONOLOGY_PATH,
    REGISTRY_PATH,
    build_action_state,
    classify_repo_movement_acceptance,
    synchronization_state,
)
from scripts.validate_accepted_state_registry import validate_registry
from scripts.validate_archive_record import validate_archive_record


sys.path.insert(0, str(Path("scripts/chronology").resolve()))
from chronology_common import append_jsonl  # noqa: E402
from validate_chronology import validate_events  # noqa: E402


def _registry_entry():
    registry = yaml.safe_load(Path(REGISTRY_PATH).read_text(encoding="utf-8"))
    return next(entry for entry in registry["entries"] if entry["accepted_state_id"] == ACCEPTED_STATE_ID)


def _chronology_event():
    for line in Path(CHRONOLOGY_PATH).read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event["event_id"] == CHRONOLOGY_EVENT_ID:
            return event
    raise AssertionError("chronology event not found")


def _copy_sync_files(tmp_path, *, archive_status="pending_external_write"):
    registry_path = tmp_path / REGISTRY_PATH
    chronology_path = tmp_path / CHRONOLOGY_PATH
    archive_path = tmp_path / ARCHIVE_RECORD_PATH
    registry_path.parent.mkdir(parents=True)
    chronology_path.parent.mkdir(parents=True)
    archive_path.parent.mkdir(parents=True)
    registry_path.write_text(Path(REGISTRY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    chronology_path.write_text(Path(CHRONOLOGY_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    archive = yaml.safe_load(Path(ARCHIVE_RECORD_PATH).read_text(encoding="utf-8"))
    archive["completion"]["status"] = archive_status
    if archive_status == "completed_and_verified":
        archive["completion"]["written_at"] = "2026-07-17T12:30:00Z"
        archive["completion"]["receipt_or_reference"] = "github:commit/example"
        archive["completion"]["verification"] = "external_write_verified"
    archive_path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")


def test_reviewed_repo_movement_can_be_promoted_to_accepted_state():
    entry = _registry_entry()
    result = classify_repo_movement_acceptance(entry)

    assert result["current_repo_movement_reviewed"] is True
    assert result["current_repo_movement_accepted"] is True
    assert result["accepted_remote_head"] == "afeb0fa77b873176a2269a1f7583e5f81b5c244a"


def test_merged_but_unreviewed_repo_movement_remains_unaccepted():
    entry = copy.deepcopy(_registry_entry())
    entry["review_authority"]["Architect_reviewed"] = False
    entry["review_authority"]["CCO_reviewed"] = False

    result = classify_repo_movement_acceptance(entry)

    assert result["current_repo_movement_reviewed"] is False
    assert result["current_repo_movement_accepted"] is False


def test_accepted_stage_a_state_does_not_activate_stage_b():
    entry = _registry_entry()

    assert entry["stage_state"]["Stage_B"]["status"] == "locked"
    assert "Stage_B_activation" in entry["excluded_claims"]


def test_accepted_stage_a_state_does_not_claim_live_operation():
    entry = _registry_entry()

    assert entry["stage_state"]["Stage_A"]["live_operation"] == "not_established"
    assert "Stage A live operation is not established." in entry["accepted_claims"]


def test_accepted_state_entry_preserves_excluded_claims():
    entry = _registry_entry()

    for claim in {
        "production readiness",
        "deployed operator dependency",
        "external comprehension",
        "buyer adoption",
        "Stage_B_activation",
    }:
        assert claim in entry["excluded_claims"]


def test_registry_schema_valid():
    report = validate_registry()

    assert report["status"] == "passed"
    assert report["accepted_state_ids"] == [ACCEPTED_STATE_ID]


def test_chronology_event_written_once():
    events = [
        json.loads(line)
        for line in Path(CHRONOLOGY_PATH).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert [event["event_id"] for event in events].count(CHRONOLOGY_EVENT_ID) == 1


def test_duplicate_chronology_event_rejected_or_reconciled():
    event = _chronology_event()
    result = validate_events(
        {"reflex": [], "archive": [], "operations": [], "governance": [event, event]},
        enforce_gate_state=False,
    )

    assert result["status"] == "failed"
    assert "Duplicate chronology event ID" in result["errors"]


def test_append_jsonl_rejects_duplicate_chronology_event(tmp_path):
    event = _chronology_event()
    ledger = tmp_path / "governance-events.jsonl"
    ledger.write_text(json.dumps(event) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate chronology event ID"):
        append_jsonl(ledger, [event])


def test_archive_local_preparation_not_equal_external_completion(tmp_path):
    archive = yaml.safe_load(Path(ARCHIVE_RECORD_PATH).read_text(encoding="utf-8"))
    archive["completion"] = {
        "status": "pending_external_write",
        "destination": "GitHub repository history",
        "written_at": None,
        "receipt_or_reference": None,
        "verification": "external_write_not_yet_confirmed",
    }
    copied = tmp_path / "archive-record.yaml"
    copied.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    report = validate_archive_record(copied)

    assert report["archive_completion_status"] == "pending_external_write"
    assert report["archive_verified"] is False


def test_system_maintenance_action_distinct_from_Architect_decision(tmp_path):
    _copy_sync_files(tmp_path, archive_status="pending_external_write")

    action_state = build_action_state(tmp_path)

    assert action_state["system_maintenance_action_required"] is True
    assert action_state["Architect_decision_required"] is False
    assert action_state["external_dependency_action_required"] is True
    assert action_state["action_type"] == "archive_write"


def test_completed_synchronization_clears_maintenance_action(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    action_state = build_action_state(tmp_path)

    assert action_state["system_maintenance_action_required"] is False
    assert action_state["Architect_decision_required"] is False
    assert action_state["assigned_to"] == []
    assert action_state["action_type"] == "none"
    assert action_state["external_dependency_action_required"] is False
    assert action_state["blocking_state"] == "non_blocking"
    assert (
        action_state["rationale"]
        == "Stage_A_governance_state_synchronized_and_archive_receipt_verified"
    )


def test_unavailable_local_working_tree_does_not_block_registry_sync(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    state = synchronization_state(tmp_path)

    assert state["repository"]["current_repo_movement_accepted"] is True
    assert state["accepted_state_registry"]["updated"] is True


def test_live_NSF_portal_unavailability_remains_separate():
    action_state = build_action_state()

    assert action_state["Architect_decision_required"] is False
    assert action_state["blocking_state"] != "blocks_Architect_decision"
    assert "NSF" not in action_state["rationale"]


def test_merge_commit_receipt_resolves_on_main():
    receipt = "506ab4d2d7999e46a5cf95f544933ab32c4a545f"

    assert subprocess.run(
        ["git", "cat-file", "-e", f"{receipt}^{{commit}}"],
        check=False,
    ).returncode == 0
    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", receipt, "origin/main"],
        check=False,
    ).returncode == 0


def _archive_copy(tmp_path):
    archive = yaml.safe_load(Path(ARCHIVE_RECORD_PATH).read_text(encoding="utf-8"))
    path = tmp_path / "archive-record.yaml"
    path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")
    return path, archive


def test_completed_archive_requires_receipt(tmp_path):
    path, archive = _archive_copy(tmp_path)
    archive["completion"]["receipt_or_reference"] = None
    path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="requires written_at and receipt_or_reference"):
        validate_archive_record(path)


def test_completed_archive_requires_written_at(tmp_path):
    path, archive = _archive_copy(tmp_path)
    archive["completion"]["written_at"] = None
    path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="requires written_at and receipt_or_reference"):
        validate_archive_record(path)


def test_completed_archive_requires_verified_destination(tmp_path):
    path, archive = _archive_copy(tmp_path)
    archive["completion"]["verification"] = "external_write_not_yet_confirmed"
    path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="requires external write verification"):
        validate_archive_record(path)


def test_pending_external_write_rejected_after_verified_receipt(tmp_path):
    path, archive = _archive_copy(tmp_path)
    archive["completion"]["status"] = "pending_external_write"
    path.write_text(yaml.safe_dump(archive, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="External verification cannot be claimed before completion"):
        validate_archive_record(path)


def test_archive_receipt_closure_clears_related_maintenance_action():
    action_state = build_action_state()

    assert action_state["system_maintenance_action_required"] is False
    assert action_state["Architect_decision_required"] is False
    assert action_state["external_dependency_action_required"] is False
    assert action_state["assigned_to"] == []


def test_archive_receipt_closure_does_not_activate_stage_b():
    state = synchronization_state()

    assert state["runtime_evidence"]["Stage_B"] == "locked"


def test_archive_receipt_closure_does_not_claim_live_operation():
    state = synchronization_state()

    assert state["runtime_evidence"]["Stage_A_live_operation"] == "not_established"


def test_archive_receipt_closure_does_not_claim_production_health():
    state = synchronization_state()

    assert state["runtime_evidence"]["production_health_claim"] == "prohibited"


def test_archive_receipt_closure_does_not_create_duplicate_chronology_event():
    events = [
        json.loads(line)
        for line in Path(CHRONOLOGY_PATH).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert [event["event_id"] for event in events].count(CHRONOLOGY_EVENT_ID) == 1


def test_archive_receipt_closure_does_not_create_duplicate_registry_entry():
    registry = yaml.safe_load(Path(REGISTRY_PATH).read_text(encoding="utf-8"))

    assert [
        entry["accepted_state_id"] for entry in registry["entries"]
    ].count(ACCEPTED_STATE_ID) == 1
