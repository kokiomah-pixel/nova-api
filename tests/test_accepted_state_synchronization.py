import copy
import json
import sys
from pathlib import Path

import pytest
import yaml

from core.accepted_state_synchronization import (
    ACCEPTED_STATE_ID,
    ARCHIVE_RECORD_PATH,
    CHRONOLOGY_EVENT_ID,
    CHRONOLOGY_PATH,
    REGISTRY_CHECKPOINT_PATH,
    REGISTRY_PATH,
    advance_accepted_state_checkpoint,
    build_action_state,
    classify_repo_movement_acceptance,
    load_archive_record,
    refresh_local_mirror,
    resolve_registry_source,
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


def _registry_payload():
    return yaml.safe_load(Path(REGISTRY_PATH).read_text(encoding="utf-8"))


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


def _write_checkpoint(root, *, acknowledged=None, commit="fixture-commit"):
    path = root / REGISTRY_CHECKPOINT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "accepted_state_checkpoint": {
                    "schema_version": "1.0.0",
                    "checkpoint_type": "observation_cursor",
                    "canonical_registry_commit": commit,
                    "latest_acknowledged_entry_ids": acknowledged or [],
                    "observed_at": "2026-07-18T00:00:00Z",
                    "authority_effect": "none",
                    "execution_effect": "none",
                    "independent_governance_claims": False,
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _write_stale_mirror(root):
    registry = yaml.safe_load(Path(REGISTRY_PATH).read_text(encoding="utf-8"))
    registry["entries"] = []
    mirror = root / REGISTRY_PATH
    mirror.parent.mkdir(parents=True)
    mirror.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    metadata = root / "agent_files/state/accepted-state-registry.mirror-metadata.yaml"
    metadata.write_text(
        yaml.safe_dump(
            {
                "mirror_metadata": {
                    "canonical_repository": "kokiomah-pixel/sharpe-nova-os",
                    "canonical_commit": "0000000000000000000000000000000000000000",
                    "synchronized_at": "2026-07-15T00:00:00Z",
                    "registry_content_hash": "stale",
                    "schema_version": "1.0.0",
                    "sync_status": "lag_detected",
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return mirror


def _verified_repository_state(commit="1111111111111111111111111111111111111111"):
    return {
        "checkout_commit": commit,
        "canonical_main_commit": commit,
        "canonical_main_verified": True,
    }


def _feature_branch_repository_state():
    return {
        "checkout_commit": "2222222222222222222222222222222222222222",
        "canonical_main_commit": "1111111111111111111111111111111111111111",
        "canonical_main_verified": True,
    }


def _unverified_repository_state():
    return {
        "checkout_commit": "2222222222222222222222222222222222222222",
        "canonical_main_commit": None,
        "canonical_main_verified": False,
    }


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
    report = validate_registry(require_resolvable_commits=False)

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

    action_state = build_action_state(
        tmp_path,
        repository_state_override=_verified_repository_state(),
    )

    assert action_state["system_maintenance_action_required"] is True
    assert action_state["Architect_decision_required"] is False
    assert action_state["external_dependency_action_required"] is True
    assert action_state["action_type"] == "archive_write"


def test_completed_synchronization_clears_maintenance_action(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    action_state = build_action_state(
        tmp_path,
        repository_state_override=_verified_repository_state(),
    )

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

    state = synchronization_state(
        tmp_path,
        repository_state_override=_verified_repository_state(),
    )

    assert state["repository"]["current_repo_movement_accepted"] is True
    assert state["accepted_state_registry"]["updated"] is True


def test_live_NSF_portal_unavailability_remains_separate():
    action_state = build_action_state()

    assert action_state["Architect_decision_required"] is False
    assert action_state["blocking_state"] != "blocks_Architect_decision"
    assert "NSF" not in action_state["rationale"]


def test_completed_archive_records_approved_merge_receipt():
    record = load_archive_record()

    assert record["completion"]["status"] == "completed_and_verified"
    assert (
        record["completion"]["receipt_or_reference"]
        == "506ab4d2d7999e46a5cf95f544933ab32c4a545f"
    )
    assert record["completion"]["verification"] == "merge_commit_resolved_in_main"

    report = validate_archive_record()
    assert report["archive_verified"] is True
    assert report["archive_package_hash_valid"] is True


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


def test_archive_receipt_closure_clears_related_maintenance_action(tmp_path):
    _copy_sync_files(
        tmp_path,
        archive_status="completed_and_verified",
    )

    action_state = build_action_state(
        tmp_path,
        repository_state_override=_verified_repository_state(),
    )

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


def test_canonical_registry_preferred_over_stale_local_mirror(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    mirror_root = tmp_path / "mirror"
    _write_stale_mirror(mirror_root)

    state = resolve_registry_source(
        tmp_path,
        local_mirror_root=mirror_root,
        repository_state_override=_verified_repository_state(),
    )

    assert state["registry_state"]["canonical_source_available"] is True
    assert state["registry_state"]["selected_registry_path"] == str(tmp_path / REGISTRY_PATH)
    assert state["registry_state"]["mirror_lag_detected"] is True
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is True


def test_stale_mirror_not_presented_as_current_state(tmp_path):
    mirror_root = tmp_path / "mirror"
    _write_stale_mirror(mirror_root)

    state = resolve_registry_source(tmp_path / "missing-canonical", local_mirror_root=mirror_root)

    assert state["registry_state"]["canonical_source_available"] is False
    assert state["registry_usage"]["allowed"] == "bounded_historical_context_only"
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is False


def test_canonical_source_unavailable_reports_source_incomplete(tmp_path):
    mirror_root = tmp_path / "mirror"
    _write_stale_mirror(mirror_root)

    state = synchronization_state(tmp_path / "missing-canonical", local_mirror_root=mirror_root)

    assert state["operating_state"] == "source_incomplete"
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is False


def test_mirror_refresh_requires_schema_validation(tmp_path):
    invalid = tmp_path / "invalid-registry.yaml"
    invalid.write_text("schema_version: wrong\nentries: []\n", encoding="utf-8")
    mirror = tmp_path / "mirror" / REGISTRY_PATH

    result = refresh_local_mirror(
        canonical_registry_path=invalid,
        mirror_registry_path=mirror,
        metadata_path=tmp_path / "mirror/agent_files/state/accepted-state-registry.mirror-metadata.yaml",
        canonical_repository="kokiomah-pixel/sharpe-nova-os",
        canonical_commit="fixture",
        synchronized_at="2026-07-18T00:00:00Z",
    )

    assert result["sync_status"] == "failed_schema_validation"
    assert mirror.exists() is False


def test_failed_refresh_preserves_last_valid_mirror(tmp_path):
    mirror_root = tmp_path / "mirror"
    mirror = _write_stale_mirror(mirror_root)
    original = mirror.read_text(encoding="utf-8")
    invalid = tmp_path / "invalid-registry.yaml"
    invalid.write_text("schema_version: wrong\nentries: []\n", encoding="utf-8")

    result = refresh_local_mirror(
        canonical_registry_path=invalid,
        mirror_registry_path=mirror,
        metadata_path=mirror_root / "agent_files/state/accepted-state-registry.mirror-metadata.yaml",
        canonical_repository="kokiomah-pixel/sharpe-nova-os",
        canonical_commit="fixture",
        synchronized_at="2026-07-18T00:00:00Z",
    )

    assert result["sync_status"] == "failed_schema_validation"
    assert result["mirror_preserved"] is True
    assert mirror.read_text(encoding="utf-8") == original


def test_local_mirror_cannot_create_accepted_state(tmp_path):
    mirror_root = tmp_path / "mirror"
    mirror = mirror_root / REGISTRY_PATH
    mirror.parent.mkdir(parents=True)
    mirror.write_text(Path(REGISTRY_PATH).read_text(encoding="utf-8"), encoding="utf-8")

    state = resolve_registry_source(tmp_path / "missing-canonical", local_mirror_root=mirror_root)

    assert ACCEPTED_STATE_ID in yaml.safe_load(mirror.read_text(encoding="utf-8"))["entries"][0]["accepted_state_id"]
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is False


def test_acknowledged_entry_not_repeated_as_new_delta(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    _write_checkpoint(tmp_path, acknowledged=[ACCEPTED_STATE_ID])

    state = resolve_registry_source(
        tmp_path,
        repository_state_override=_verified_repository_state(),
    )

    assert state["accepted_state_delta"]["newly_accepted"] == "none"
    assert state["accepted_state_delta"]["stable_accepted_state"] == [ACCEPTED_STATE_ID]


def test_mirror_refresh_does_not_create_chronology_event(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    mirror_root = tmp_path / "mirror"
    before = (tmp_path / CHRONOLOGY_PATH).read_text(encoding="utf-8")

    refresh_local_mirror(
        canonical_registry_path=tmp_path / REGISTRY_PATH,
        mirror_registry_path=mirror_root / REGISTRY_PATH,
        metadata_path=mirror_root / "agent_files/state/accepted-state-registry.mirror-metadata.yaml",
        canonical_repository="kokiomah-pixel/sharpe-nova-os",
        canonical_commit="fixture",
        synchronized_at="2026-07-18T00:00:00Z",
    )

    assert (tmp_path / CHRONOLOGY_PATH).read_text(encoding="utf-8") == before


def test_registry_sync_action_does_not_require_Architect_decision(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    mirror_root = tmp_path / "mirror"
    _write_stale_mirror(mirror_root)

    action_state = build_action_state(
        tmp_path,
        local_mirror_root=mirror_root,
        repository_state_override=_verified_repository_state(),
    )

    assert action_state["system_maintenance_action_required"] is True
    assert action_state["Architect_decision_required"] is False
    assert action_state["action_type"] == "registry_synchronization"
    assert action_state["blocking_state"] == "non_blocking"


def test_registry_sync_preserves_Stage_B_locked(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    mirror_root = tmp_path / "mirror"
    _write_stale_mirror(mirror_root)

    state = synchronization_state(
        tmp_path,
        local_mirror_root=mirror_root,
        repository_state_override=_verified_repository_state(),
    )

    assert state["runtime_evidence"]["Stage_B"] == "locked"


def test_feature_branch_HEAD_not_labeled_canonical_main(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    state = resolve_registry_source(
        tmp_path,
        repository_state_override=_feature_branch_repository_state(),
    )

    assert state["repository_state"]["checkout_commit"] == "2222222222222222222222222222222222222222"
    assert state["repository_state"]["canonical_main_commit"] == "1111111111111111111111111111111111111111"
    assert state["repository_state"]["checkout_is_canonical_main"] is False
    assert state["registry_ingestion"]["canonical_commit"] == "1111111111111111111111111111111111111111"


def test_verified_origin_main_used_as_canonical_commit(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    state = resolve_registry_source(
        tmp_path,
        repository_state_override=_feature_branch_repository_state(),
    )

    assert state["registry_state"]["canonical_source_state"] == "verified_repository_main"
    assert state["registry_state"]["canonical_commit"] == "1111111111111111111111111111111111111111"
    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is True


def test_missing_origin_main_reports_unverified_checkout(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    state = resolve_registry_source(
        tmp_path,
        repository_state_override=_unverified_repository_state(),
    )

    assert state["registry_state"]["canonical_source_state"] == "unverified_repository_checkout"
    assert state["registry_ingestion"]["canonical_main_verified"] is False
    assert state["registry_ingestion"]["canonical_main_commit"] is None
    assert state["registry_usage"]["allowed"] == "bounded_checkout_context"


def test_unverified_checkout_cannot_make_current_accepted_state_claim(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")

    state = synchronization_state(
        tmp_path,
        repository_state_override=_unverified_repository_state(),
    )

    assert state["registry_usage"]["current_accepted_state_claim_allowed"] is False
    assert state["repository"]["current_repo_movement_accepted"] is False
    assert state["accepted_state_registry"]["updated"] is False


def test_checkpoint_advances_only_from_verified_canonical_registry(tmp_path):
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])

    unverified = advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit=None,
        canonical_main_verified=False,
        observed_at="2026-07-18T12:00:00Z",
        successful_daily_run=True,
    )
    verified = advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit="1111111111111111111111111111111111111111",
        canonical_main_verified=True,
        observed_at="2026-07-18T12:01:00Z",
        successful_daily_run=True,
    )

    assert unverified["advanced"] is False
    assert verified["advanced"] is True
    assert ACCEPTED_STATE_ID in verified["acknowledged_entry_ids"]


def test_failed_daily_run_does_not_advance_checkpoint(tmp_path):
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])

    result = advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit="1111111111111111111111111111111111111111",
        canonical_main_verified=True,
        observed_at="2026-07-18T12:00:00Z",
        successful_daily_run=False,
    )

    stored = yaml.safe_load(checkpoint.read_text(encoding="utf-8"))["accepted_state_checkpoint"]
    assert result["advanced"] is False
    assert stored["latest_acknowledged_entry_ids"] == []


def test_checkpoint_write_is_atomic(tmp_path):
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])
    temporary = checkpoint.with_suffix(checkpoint.suffix + ".tmp")

    result = advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit="1111111111111111111111111111111111111111",
        canonical_main_verified=True,
        observed_at="2026-07-18T12:00:00Z",
        successful_daily_run=True,
    )

    assert result["advanced"] is True
    assert temporary.exists() is False
    stored = yaml.safe_load(checkpoint.read_text(encoding="utf-8"))["accepted_state_checkpoint"]
    assert stored["canonical_registry_commit"] == "1111111111111111111111111111111111111111"


def test_checkpoint_cannot_acknowledge_unknown_entry_id(tmp_path):
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])

    with pytest.raises(ValueError, match="unknown accepted_state_id"):
        advance_accepted_state_checkpoint(
            registry=_registry_payload(),
            checkpoint_path=checkpoint,
            canonical_main_commit="1111111111111111111111111111111111111111",
            canonical_main_verified=True,
            observed_at="2026-07-18T12:00:00Z",
            successful_daily_run=True,
            acknowledge_entry_ids=["not_in_registry"],
        )


def test_runtime_checkpoint_does_not_create_governance_state(tmp_path):
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])
    advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit="1111111111111111111111111111111111111111",
        canonical_main_verified=True,
        observed_at="2026-07-18T12:00:00Z",
        successful_daily_run=True,
    )

    stored = yaml.safe_load(checkpoint.read_text(encoding="utf-8"))["accepted_state_checkpoint"]
    assert stored["checkpoint_type"] == "observation_cursor"
    assert stored["storage_model"]["runtime_checkpoint_authoritative"] is False
    assert stored["independent_governance_claims"] is False
    assert stored["authority_effect"] == "none"


def test_repeated_entry_not_reported_after_successful_checkpoint_advance(tmp_path):
    _copy_sync_files(tmp_path, archive_status="completed_and_verified")
    checkpoint = _write_checkpoint(tmp_path, acknowledged=[])
    advance_accepted_state_checkpoint(
        registry=_registry_payload(),
        checkpoint_path=checkpoint,
        canonical_main_commit="1111111111111111111111111111111111111111",
        canonical_main_verified=True,
        observed_at="2026-07-18T12:00:00Z",
        successful_daily_run=True,
    )

    state = resolve_registry_source(
        tmp_path,
        checkpoint_path=checkpoint,
        repository_state_override=_verified_repository_state(),
    )

    assert state["accepted_state_delta"]["newly_accepted"] == "none"
    assert state["accepted_state_delta"]["stable_accepted_state"] == [ACCEPTED_STATE_ID]
