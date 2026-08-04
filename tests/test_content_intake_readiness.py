from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from scripts.content.validate_content_intake_readiness import validate_content_intake_readiness
from scripts.content.validate_post_record import validate_post_record
from scripts.content.validation_common import ContentValidationError, ROOT, find_mapping


@pytest.fixture
def readiness_root(tmp_path: Path) -> Path:
    destination = tmp_path / "docs/content"
    destination.parent.mkdir(parents=True)
    shutil.copytree(ROOT / "docs/content", destination)
    return tmp_path


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _current_state(root: Path) -> tuple[Path, dict]:
    path = root / "docs/content/content-current-state.yaml"
    return path, yaml.safe_load(path.read_text(encoding="utf-8"))


def test_repository_is_ready_for_architect_input() -> None:
    result = validate_content_intake_readiness(ROOT)["content_intake_readiness"]

    assert result["overall_status"] == "ready_for_Architect_input"
    assert result["automatic_repository_write"] is False
    assert result["controlled_experiments_active"] == 0
    assert result["automated_ingestion_bridge_present"] is False
    assert result["checks_failed"] == []


def test_merged_content_production_os_is_required(readiness_root: Path) -> None:
    path = readiness_root / "docs/content/content-production-os.md"
    _replace(path, "status: authoritative", "status: proposed")

    with pytest.raises(ContentValidationError, match="status must be authoritative"):
        validate_content_intake_readiness(readiness_root)


def test_initialized_daily_coherence_contract_is_required(readiness_root: Path) -> None:
    path = readiness_root / "docs/content/daily-coherence-content-operating-contract.md"
    _replace(path, "operating_status: initialized", "operating_status: initialized_after_merge")

    with pytest.raises(ContentValidationError, match="operating_status must be initialized"):
        validate_content_intake_readiness(readiness_root)


def test_ready_current_state_is_required(readiness_root: Path) -> None:
    path, payload = _current_state(readiness_root)
    payload["content_current_state"]["content_intake"]["status"] = "not_ready"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentValidationError, match="content_intake.status must be ready"):
        validate_content_intake_readiness(readiness_root)


def test_automatic_repository_write_must_be_false(readiness_root: Path) -> None:
    path, payload = _current_state(readiness_root)
    payload["content_current_state"]["content_intake"]["automatic_repository_write"] = True
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentValidationError, match="automatic_repository_write must be false"):
        validate_content_intake_readiness(readiness_root)


def test_intake_protocol_must_exist(readiness_root: Path) -> None:
    (readiness_root / "docs/content/content-production-engine-august-intake-protocol.md").unlink()

    with pytest.raises(ContentValidationError, match="August_intake_protocol_exists"):
        validate_content_intake_readiness(readiness_root)


def test_post_record_template_must_validate(readiness_root: Path) -> None:
    path = readiness_root / "docs/content/templates/post-record-template.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    del payload["post_record"]["post"]["governed_distinction"]
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentValidationError, match="post record template structural validation failed"):
        validate_content_intake_readiness(readiness_root)


def test_performance_ledgers_must_exist(readiness_root: Path) -> None:
    (readiness_root / "docs/content/performance/content-performance-ledger.csv").unlink()

    with pytest.raises(ContentValidationError, match="performance_ledger_exists"):
        validate_content_intake_readiness(readiness_root)


def test_active_experiments_may_remain_empty(readiness_root: Path) -> None:
    result = validate_content_intake_readiness(readiness_root)["content_intake_readiness"]

    assert result["controlled_experiments_active"] == 0


def test_historical_backfill_is_rescheduled_after_august_cycle() -> None:
    payload = yaml.safe_load(
        (ROOT / "docs/content/content-operational-items.yaml").read_text(encoding="utf-8")
    )
    item = next(entry for entry in payload["operational_items"] if entry["item_id"] == "CONTENT-OPS-001")

    assert item["status"] == "assigned"
    assert item["blocking"] is False
    assert item["activation_condition"] == "August_2026_distribution_cycle_complete"
    assert str(item["not_before"]) == "2026-09-01"
    assert str(item["target_date"]) == "2026-09-05"


def test_automated_ingestion_bridge_must_remain_absent(readiness_root: Path) -> None:
    bridge = readiness_root / "scripts/content/ingest_content_evidence.py"
    bridge.parent.mkdir(parents=True)
    bridge.write_text("# prohibited automated bridge\n", encoding="utf-8")

    with pytest.raises(ContentValidationError, match="automated_ingestion_script_absent"):
        validate_content_intake_readiness(readiness_root)


def test_proposed_until_merge_state_is_rejected(readiness_root: Path) -> None:
    path = readiness_root / "docs/content/daily-coherence-content-operating-contract.md"
    _replace(path, "repository_status: merged", "repository_status: proposed_until_merge")

    with pytest.raises(ContentValidationError, match="repository_status must be merged"):
        validate_content_intake_readiness(readiness_root)


def test_missing_persistence_boundary_is_rejected(readiness_root: Path) -> None:
    path, payload = _current_state(readiness_root)
    del payload["content_current_state"]["content_intake"]["persistence_mode"]
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentValidationError, match="bounded VS Code handoff"):
        validate_content_intake_readiness(readiness_root)


def test_post_record_template_validator_passes() -> None:
    result = validate_post_record(ROOT / "docs/content/templates/post-record-template.yaml")

    assert result["status"] == "passed"
    assert result["template"] is True


def test_synthetic_published_post_only_handoff_is_representable() -> None:
    protocol = ROOT / "docs/content/content-production-engine-august-intake-protocol.md"
    handoff = find_mapping(protocol, "august_content_intake_handoff")
    fixture = find_mapping(protocol, "august_content_intake_acceptance_fixture")

    assert fixture == {
        "intake_type": "published_post_only",
        "publication_month": "2026-08",
        "exact_published_copy": "fixture_only",
        "post_url": "https://www.linkedin.com/posts/example",
        "publication_date": "2026-08-01",
        "experiment_id": None,
        "evidence_role": "baseline_observation",
        "repository_write_performed": False,
    }
    assert "exact_published_copy" in handoff["post"]
    assert "repository_plan" in handoff
    assert handoff["effects"]["canonical_rule_changed"] is False
    assert handoff["status"] == "ready_for_repository_handoff"
