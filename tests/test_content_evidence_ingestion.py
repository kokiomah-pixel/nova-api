from __future__ import annotations

import csv
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.content.content_evidence_store import (
    AUDIENCE_HEADER,
    PERFORMANCE_HEADER,
    ContentEvidenceStore,
    validate_receipt_mapping,
)
from scripts.content.validate_content_evidence_intake import validate_intake_mapping
from scripts.content.validation_common import ContentValidationError


EVIDENCE_BRANCH = "ops/content-evidence-2026-08"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _seed_evidence_repo(root: Path) -> Path:
    _write(
        root / "docs/content/performance/content-performance-ledger.csv",
        ",".join(PERFORMANCE_HEADER) + "\n",
    )
    _write(
        root / "docs/content/performance/audience-engagement-ledger.csv",
        ",".join(AUDIENCE_HEADER) + "\n",
    )
    _write(
        root / "docs/content/content-current-state.yaml",
        yaml.safe_dump(
            {
                "content_current_state": {
                    "published_posts": [],
                    "metrics_due": [],
                    "last_content_evidence_ingestion": None,
                    "pending_evidence_resolution": [],
                    "content_evidence_ingestion": {
                        "last_intake_id": None,
                        "last_ingested_at": None,
                        "pending_intakes": [],
                        "unresolved_intakes": [],
                        "evidence_branch": None,
                        "evidence_pull_request": None,
                    },
                }
            },
            sort_keys=False,
        ),
    )
    _write(
        root / "docs/content/content-experiment-register.yaml",
        yaml.safe_dump({"experiments": []}, sort_keys=False),
    )
    _write(root / "docs/content/content-production-os.md", "canonical sentinel\n")
    return root


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def evidence_repo(tmp_path: Path) -> Path:
    return _seed_evidence_repo(tmp_path)


@pytest.fixture
def publish_repo(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    worktree = tmp_path / "worktree"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    worktree.mkdir()
    _git(worktree, "init", "-b", "main")
    _git(worktree, "config", "user.name", "Content Evidence Test")
    _git(worktree, "config", "user.email", "content-evidence@example.invalid")
    _seed_evidence_repo(worktree)
    _git(worktree, "add", "docs")
    _git(worktree, "commit", "-m", "test: establish content evidence baseline")
    _git(worktree, "remote", "add", "origin", str(remote))
    _git(worktree, "push", "-u", "origin", "main")
    _write(worktree / "artifacts/untouched.txt", "pre-existing untracked artifact\n")
    return worktree, remote


def _intake(
    *,
    intake_id: str = "INTAKE-20260804T180000-ABCDEF01",
    source_reference: str = "architect://linkedin/screenshot/one",
    explicit_window: str | None = "24_hours",
    post_url: str = "https://www.linkedin.com/posts/example-one",
    publication_date: str = "2026-08-03",
) -> dict:
    return {
        "schema_version": "1.0.0",
        "intake_id": intake_id,
        "received_at": "2026-08-04T18:00:00Z",
        "supplied_by_role": "Architect",
        "post_identifier": {
            "post_id": None,
            "post_url": post_url,
            "publication_date": publication_date,
            "title_or_working_name": "A governed review context",
        },
        "post_creation_context": {
            "allow_create_post_record": True,
            "exact_published_copy": "A proposal is not an approval. Context precedes execution.",
            "intended_audience": "institutional_treasury_operators",
            "audience_stage": "problem_aware",
            "narrative_pillar": "institutional_review_problems",
            "governed_distinction": "proposal_vs_approval",
            "hook_type": "scenario",
            "content_pattern": "scenario_to_consequence",
            "experiment_id": None,
        },
        "measurement": {
            "explicit_window": explicit_window,
            "measured_at": "2026-08-04T17:30:00Z",
            "publication_timestamp": "2026-08-03T17:30:00Z",
            "calculated_age_hours": None,
            "classified_window": None,
        },
        "source": {
            "source_type": "LinkedIn_screenshot",
            "source_reference": source_reference,
            "source_fingerprint": None,
            "raw_evidence_committed": False,
        },
        "evidence_action": {
            "record_action": "observation",
            "supersedes_record_id": None,
            "correction_reason": None,
        },
        "observed_metrics": {
            "impressions": 1284,
            "reactions": 31,
            "comments": 0,
            "reposts": 2,
            "saves": None,
            "profile_views": None,
            "new_followers": None,
            "link_clicks": None,
            "inbound_messages": None,
        },
        "unavailable_metrics": [
            "saves",
            "profile_views",
            "new_followers",
            "link_clicks",
            "inbound_messages",
        ],
        "audience_observations": [],
        "qualitative_observations": {
            "strongest_line": None,
            "weakest_section": None,
            "misunderstanding_signals": [],
            "notes": [],
        },
        "extraction": {"status": "complete", "uncertain_fields": [], "unresolved_fields": []},
        "authority": {
            "interpretation_authorized": False,
            "canonical_rule_change_authorized": False,
            "publication_authorized": False,
        },
    }


def _apply(repo: Path, intake: dict, **kwargs: object) -> dict:
    return ContentEvidenceStore(repo).ingest(
        intake,
        apply=True,
        allow_create_post=True,
        current_branch=EVIDENCE_BRANCH,
        expected_branch=EVIDENCE_BRANCH,
        **kwargs,
    )


def _first_apply(repo: Path) -> tuple[dict, dict[str, str]]:
    result = _apply(repo, _intake())
    return result, _rows(repo / "docs/content/performance/content-performance-ledger.csv")[0]


def test_dry_run_makes_no_changes_and_prepared_receipt_is_truthful(evidence_repo: Path) -> None:
    before = {path: path.read_bytes() for path in evidence_repo.rglob("*") if path.is_file()}

    result = ContentEvidenceStore(evidence_repo).ingest(_intake(), allow_create_post=True)

    after = {path: path.read_bytes() for path in evidence_repo.rglob("*") if path.is_file()}
    receipt = result["content_evidence_receipt"]
    assert before == after
    assert result["ingestion_preview"]["persistence_ready"] is True
    assert result["ingestion_preview"]["writes_performed"] is False
    assert receipt["status"] == "prepared_not_persisted"
    assert receipt["missing_capabilities"] == []
    assert receipt["transaction"]["transaction_reference"] is None
    assert receipt["repository"]["local_commit"] is None
    assert receipt["repository"]["remote_commit"] is None
    assert receipt["repository_state"]["persisted_to_monthly_branch"] is False


def test_cli_defaults_to_dry_run(evidence_repo: Path, tmp_path: Path) -> None:
    intake_path = tmp_path / "intake.yaml"
    _write(
        intake_path,
        yaml.safe_dump({"content_evidence_intake": _intake()}, sort_keys=False),
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/content/ingest_content_evidence.py",
            str(intake_path),
            "--repo-root",
            str(evidence_repo),
            "--allow-create-post",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    output = yaml.safe_load(result.stdout)
    assert output["content_evidence_receipt"]["status"] == "prepared_not_persisted"
    assert output["ingestion_preview"]["writes_performed"] is False


def test_valid_first_intake_creates_post_evidence_and_truthful_receipt(evidence_repo: Path) -> None:
    result = _apply(evidence_repo, _intake())
    receipt = result["content_evidence_receipt"]
    rows = _rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")

    assert receipt["status"] == "validated_worktree_write"
    assert receipt["repository"]["branch"] == EVIDENCE_BRANCH
    assert receipt["transaction"]["transaction_reference"].startswith("transaction:")
    assert receipt["repository"]["local_commit"] is None
    assert receipt["repository"]["remote_commit"] is None
    assert receipt["repository"]["remote_branch_verified"] is False
    assert receipt["repository_state"] == {
        "persisted_to_monthly_branch": False,
        "merged_to_main": False,
    }
    assert receipt["rows"] == {"performance_rows_added": 1, "audience_rows_added": 0}
    assert len(rows) == 1
    assert rows[0]["comments"] == "0"
    assert rows[0]["saves"] == "unavailable"
    state = yaml.safe_load(
        (evidence_repo / "docs/content/content-current-state.yaml").read_text(encoding="utf-8")
    )["content_current_state"]
    assert state["metrics_due"] == [
        {
            "post_id": receipt["post_id"],
            "window": "7_days",
            "due_date": "2026-08-10",
        },
        {
            "post_id": receipt["post_id"],
            "window": "30_days",
            "due_date": "2026-09-02",
        },
    ]
    post_path = evidence_repo / next(
        path for path in receipt["files"]["created"] if path.startswith("docs/content/posts/")
    )
    assert post_path.exists()
    assert "A proposal is not an approval" in post_path.read_text(encoding="utf-8")
    receipt_path = evidence_repo / "docs/content/receipts/2026/08/INTAKE-20260804T180000-ABCDEF01.yaml"
    assert receipt_path.exists()
    persisted = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))["content_evidence_receipt"]
    validate_receipt_mapping(persisted)


def test_existing_post_appends_seven_day_row_and_preserves_24_hour_row(evidence_repo: Path) -> None:
    first, first_row = _first_apply(evidence_repo)
    second = _intake(
        intake_id="INTAKE-20260810T180000-ABCDEF02",
        source_reference="architect://linkedin/screenshot/seven-day",
        explicit_window="7_days",
    )
    second["received_at"] = "2026-08-10T18:00:00Z"
    second["measurement"]["measured_at"] = "2026-08-10T17:30:00Z"
    second["post_identifier"]["post_id"] = first["content_evidence_receipt"]["post_id"]

    result = _apply(evidence_repo, second)
    rows = _rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")

    assert result["content_evidence_receipt"]["status"] == "validated_worktree_write"
    assert len(rows) == 2
    assert rows[0] == first_row
    assert [row["measurement_window"] for row in rows] == ["24_hours", "7_days"]


def test_duplicate_intake_and_duplicate_source_hash_are_noops(evidence_repo: Path) -> None:
    _first_apply(evidence_repo)
    duplicate_intake = _apply(evidence_repo, _intake())
    same_source = _intake(intake_id="INTAKE-20260804T190000-ABCDEF03")
    duplicate_source = _apply(evidence_repo, same_source)

    assert duplicate_intake["content_evidence_receipt"]["status"] == "duplicate_noop"
    assert duplicate_source["content_evidence_receipt"]["status"] == "duplicate_noop"
    assert len(_rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")) == 1


def test_ambiguous_post_resolution_blocks_write(evidence_repo: Path) -> None:
    first, _ = _first_apply(evidence_repo)
    original_post = evidence_repo / next(
        path for path in first["content_evidence_receipt"]["files"]["created"]
        if path.startswith("docs/content/posts/")
    )
    duplicate_post = original_post.with_name("POST-2026-08-03-FFFFFFFF.md")
    text = original_post.read_text(encoding="utf-8").replace(
        first["content_evidence_receipt"]["post_id"], "POST-2026-08-03-FFFFFFFF"
    )
    _write(duplicate_post, text)
    intake = _intake(intake_id="INTAKE-20260804T200000-ABCDEF04", source_reference="ambiguous")
    intake["post_identifier"]["post_url"] = None
    intake["post_identifier"]["post_id"] = None
    before = (evidence_repo / "docs/content/performance/content-performance-ledger.csv").read_bytes()

    result = ContentEvidenceStore(evidence_repo).ingest(intake, allow_create_post=False)

    assert result["content_evidence_receipt"]["status"] == "needs_post_resolution"
    assert result["ingestion_preview"]["writes_performed"] is False
    assert (evidence_repo / "docs/content/performance/content-performance-ledger.csv").read_bytes() == before


@pytest.mark.parametrize("window", ["ad_hoc", "historical_unknown_age"])
def test_noncontrolled_evidence_is_preserved_but_not_experiment_eligible(
    evidence_repo: Path, window: str
) -> None:
    intake = _intake(explicit_window=window)
    result = _apply(evidence_repo, intake)
    row = _rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")[0]

    assert row["measurement_window"] == window
    assert result["ingestion_preview"]["measurement"]["controlled_experiment_eligible"] is False


def test_correction_appends_lineage_and_preserves_previous_record(evidence_repo: Path) -> None:
    _, first_row = _first_apply(evidence_repo)
    correction = _intake(
        intake_id="INTAKE-20260804T210000-ABCDEF05",
        source_reference="architect://linkedin/corrected-export",
    )
    correction["source"]["source_type"] = "LinkedIn_export"
    correction["observed_metrics"]["impressions"] = 1291
    correction["evidence_action"] = {
        "record_action": "correction",
        "supersedes_record_id": first_row["evidence_record_id"],
        "correction_reason": "LinkedIn export supersedes the screenshot transcription.",
    }

    result = _apply(evidence_repo, correction)
    rows = _rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")

    assert result["content_evidence_receipt"]["status"] == "validated_worktree_write"
    assert len(rows) == 2
    assert rows[0] == first_row
    assert rows[1]["record_action"] == "correction"
    assert rows[1]["supersedes_record_id"] == first_row["evidence_record_id"]


def test_conflicting_values_without_correction_are_blocked(evidence_repo: Path) -> None:
    _first_apply(evidence_repo)
    conflict = _intake(
        intake_id="INTAKE-20260804T220000-ABCDEF06",
        source_reference="architect://linkedin/second-source",
    )
    conflict["observed_metrics"]["impressions"] = 999

    result = _apply(evidence_repo, conflict)

    assert result["content_evidence_receipt"]["status"] == "conflict_requires_review"
    assert len(_rows(evidence_repo / "docs/content/performance/content-performance-ledger.csv")) == 1


def test_audience_row_requires_material_observation(evidence_repo: Path) -> None:
    intake = _intake()
    intake["audience_observations"] = [
        {"engagement_type": "comment", "relevance_basis": "workflow-specific comment"},
        {
            "engagement_type": "comment",
            "role": "treasury_operator",
            "target_market_relevance": "high",
            "relevance_basis": "described proposal-version review",
            "content_understanding": "correct_Nova_understanding",
            "qualified_conversation": False,
            "notes": "No demand inference.",
        },
    ]

    result = _apply(evidence_repo, intake)
    rows = _rows(evidence_repo / "docs/content/performance/audience-engagement-ledger.csv")

    assert result["content_evidence_receipt"]["rows"]["audience_rows_added"] == 1
    assert len(rows) == 1
    assert rows[0]["relevance_basis"] == "described proposal-version review"


def test_active_experiment_receives_only_controlled_measurement_reference(evidence_repo: Path) -> None:
    experiment = {
        "experiment_id": "CONTENT-EXP-TEST",
        "status": "active",
        "hypothesis": "Scenario opening improves qualified comprehension.",
        "target_audience": ["institutional_treasury_operators"],
        "narrative_pillar": "institutional_review_problems",
        "variable_changed": "opening_frame",
        "control_pattern": "definition",
        "test_pattern": "scenario",
        "posts_included": [],
        "measurement_windows": ["24_hours", "7_days", "30_days"],
        "primary_metric": "comments",
        "audience_quality_metric": "target_role_engagements",
        "narrative_accuracy_metric": "correct_Nova_understanding",
        "result": None,
        "measurement_evidence": [],
        "evidence_strength": "insufficient_evidence",
        "interpretation": None,
        "recommended_action": "continue",
        "promotion_status": "observation_only",
    }
    register_path = evidence_repo / "docs/content/content-experiment-register.yaml"
    _write(register_path, yaml.safe_dump({"experiments": [experiment]}, sort_keys=False))
    intake = _intake()
    intake["post_creation_context"]["experiment_id"] = experiment["experiment_id"]

    _apply(evidence_repo, intake)
    persisted = yaml.safe_load(register_path.read_text(encoding="utf-8"))["experiments"][0]

    assert persisted["posts_included"]
    assert persisted["measurement_evidence"][0]["measurement_window"] == "24_hours"
    assert persisted["result"] is None
    assert persisted["interpretation"] is None
    assert persisted["evidence_strength"] == "insufficient_evidence"
    assert persisted["promotion_status"] == "observation_only"


def test_inactive_experiment_evidence_is_rejected(evidence_repo: Path) -> None:
    register_path = evidence_repo / "docs/content/content-experiment-register.yaml"
    _write(
        register_path,
        yaml.safe_dump({"experiments": [{"experiment_id": "CONTENT-EXP-INACTIVE", "status": "approved"}]}),
    )
    intake = _intake()
    intake["post_creation_context"]["experiment_id"] = "CONTENT-EXP-INACTIVE"

    result = _apply(evidence_repo, intake)

    assert result["content_evidence_receipt"]["status"] == "conflict_requires_review"
    assert "not active" in result["ingestion_preview"]["blockers"][0]


def test_canonical_os_is_unchanged_by_ingestion(evidence_repo: Path) -> None:
    canonical = evidence_repo / "docs/content/content-production-os.md"
    before = canonical.read_bytes()

    _apply(evidence_repo, _intake())

    assert canonical.read_bytes() == before


def test_transaction_rolls_back_and_cannot_issue_success_receipt(evidence_repo: Path) -> None:
    before = {path: path.read_bytes() for path in evidence_repo.rglob("*") if path.is_file()}

    result = _apply(evidence_repo, _intake(), fail_after_writes=1)
    after = {path: path.read_bytes() for path in evidence_repo.rglob("*") if path.is_file()}

    receipt = result["content_evidence_receipt"]
    assert receipt["status"] == "rolled_back"
    assert receipt["transaction"]["transaction_reference"] is None
    assert receipt["repository"]["local_commit"] is None
    assert receipt["repository"]["remote_commit"] is None
    assert receipt["repository_state"]["persisted_to_monthly_branch"] is False
    assert receipt["transaction_result"]["repository_changed"] is False
    assert before == after


def _receipt_for_validation(status: str = "persisted_to_evidence_branch") -> dict:
    return {
        "schema_version": "1.0.0",
        "intake_id": "INTAKE-1",
        "processed_at": "2026-08-04T18:00:00Z",
        "status": status,
        "transaction": {
            "transaction_reference": "transaction:" + "a" * 64,
            "validated_at": "2026-08-04T18:00:01Z",
        },
        "repository": {
            "repository": "test",
            "branch": EVIDENCE_BRANCH,
            "local_commit": "1" * 40,
            "remote_commit": "1" * 40,
            "pull_request": "local-pr://29",
            "remote_branch_verified": True,
            "main_merge_verified": False,
        },
        "repository_state": {"persisted_to_monthly_branch": True, "merged_to_main": False},
        "files": {"created": ["docs/content/intake/example.yaml"], "updated": []},
        "validators": {
            "intake": "passed",
            "post_record": "passed",
            "performance_ledger": "passed",
            "audience_ledger": "passed",
            "experiment_register": "passed",
            "current_state": "passed",
        },
    }


@pytest.mark.parametrize("commit_field", ["local_commit", "remote_commit"])
def test_transaction_hash_is_not_a_git_commit(commit_field: str) -> None:
    receipt = _receipt_for_validation()
    receipt["repository"][commit_field] = "transaction:" + "a" * 64

    with pytest.raises(ContentValidationError, match="must be a Git commit"):
        validate_receipt_mapping(receipt)


def test_persisted_status_requires_real_commit_sha() -> None:
    receipt = _receipt_for_validation()
    receipt["repository"]["remote_commit"] = None

    with pytest.raises(ContentValidationError, match="real remote Git commit SHA"):
        validate_receipt_mapping(receipt)


def test_persisted_status_requires_remote_verification() -> None:
    receipt = _receipt_for_validation()
    receipt["repository"]["remote_branch_verified"] = False

    with pytest.raises(ContentValidationError, match="remote branch verification"):
        validate_receipt_mapping(receipt)


def test_publish_rejects_dirty_tracked_worktree(publish_repo: tuple[Path, Path]) -> None:
    repo, _ = publish_repo
    _write(repo / "docs/content/content-production-os.md", "unrelated tracked edit\n")

    with pytest.raises(ContentValidationError, match="unrelated tracked modifications"):
        ContentEvidenceStore(repo).publish(
            _intake(), expected_branch=EVIDENCE_BRANCH, allow_create_post=True
        )


def test_publish_rejects_unrelated_staged_file(publish_repo: tuple[Path, Path]) -> None:
    repo, _ = publish_repo
    _write(repo / "docs/content/content-production-os.md", "unrelated staged edit\n")
    _git(repo, "add", "docs/content/content-production-os.md")

    with pytest.raises(ContentValidationError, match="unrelated staged files"):
        ContentEvidenceStore(repo).publish(
            _intake(), expected_branch=EVIDENCE_BRANCH, allow_create_post=True
        )


def test_publish_rejects_detached_head(publish_repo: tuple[Path, Path]) -> None:
    repo, _ = publish_repo
    _git(repo, "checkout", "--detach")

    with pytest.raises(ContentValidationError, match="detached HEAD"):
        ContentEvidenceStore(repo).publish(
            _intake(), expected_branch=EVIDENCE_BRANCH, allow_create_post=True
        )


def test_publish_rejects_wrong_monthly_branch(publish_repo: tuple[Path, Path]) -> None:
    repo, _ = publish_repo
    _git(repo, "switch", "-c", "ops/content-evidence-2026-07")

    with pytest.raises(ContentValidationError, match="wrong monthly evidence branch"):
        ContentEvidenceStore(repo).publish(
            _intake(), expected_branch=EVIDENCE_BRANCH, allow_create_post=True
        )


def test_new_monthly_branch_rejects_head_behind_remote_main(
    publish_repo: tuple[Path, Path], tmp_path: Path
) -> None:
    repo, remote = publish_repo
    updater = tmp_path / "updater"
    subprocess.run(
        ["git", "clone", "--branch", "main", str(remote), str(updater)],
        check=True,
        capture_output=True,
    )
    _git(updater, "config", "user.name", "Remote Main Test")
    _git(updater, "config", "user.email", "remote-main@example.invalid")
    _write(updater / "remote-main-update.txt", "new remote main\n")
    _git(updater, "add", "remote-main-update.txt")
    _git(updater, "commit", "-m", "test: advance remote main")
    _git(updater, "push", "origin", "main")

    with pytest.raises(ContentValidationError, match="initialize from current remote main"):
        ContentEvidenceStore(repo).publish(
            _intake(), expected_branch=EVIDENCE_BRANCH, allow_create_post=True
        )


def test_commit_failure_keeps_validated_worktree_state(publish_repo: tuple[Path, Path]) -> None:
    repo, remote = publish_repo
    hook = repo / ".git/hooks/pre-commit"
    _write(hook, "#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)

    result = ContentEvidenceStore(repo).publish(
        _intake(),
        expected_branch=EVIDENCE_BRANCH,
        allow_create_post=True,
        pr_manager=lambda _repo, _branch: "local-pr://29",
    )
    receipt = result["content_evidence_receipt"]

    assert receipt["status"] == "validated_worktree_write"
    assert receipt["repository"]["local_commit"] is None
    assert receipt["repository"]["remote_commit"] is None
    assert receipt["repository_state"]["persisted_to_monthly_branch"] is False
    assert _git(repo, "diff", "--cached", "--name-only").stdout == ""
    assert _git(remote, "rev-parse", "--verify", f"refs/heads/{EVIDENCE_BRANCH}", check=False).returncode != 0


def test_push_failure_returns_committed_locally(publish_repo: tuple[Path, Path]) -> None:
    repo, remote = publish_repo
    hook = remote / "hooks/pre-receive"
    _write(hook, "#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)

    result = ContentEvidenceStore(repo).publish(
        _intake(),
        expected_branch=EVIDENCE_BRANCH,
        allow_create_post=True,
        pr_manager=lambda _repo, _branch: "local-pr://29",
    )
    receipt = result["content_evidence_receipt"]

    assert receipt["status"] == "committed_locally"
    assert len(receipt["repository"]["local_commit"]) == 40
    assert receipt["repository"]["remote_commit"] is None
    assert receipt["repository"]["remote_branch_verified"] is False
    assert receipt["repository_state"]["persisted_to_monthly_branch"] is False


def test_successful_publish_pushes_verifies_scope_and_resolves_rolling_pr(
    publish_repo: tuple[Path, Path]
) -> None:
    repo, remote = publish_repo
    pr_calls: list[tuple[Path, str]] = []

    def resolve_pr(repo_root: Path, branch: str) -> str:
        pr_calls.append((repo_root, branch))
        return "local-pr://29"

    result = ContentEvidenceStore(repo).publish(
        _intake(),
        expected_branch=EVIDENCE_BRANCH,
        allow_create_post=True,
        pr_manager=resolve_pr,
    )
    receipt = result["content_evidence_receipt"]
    local_commit = receipt["repository"]["local_commit"]
    intended = set(receipt["files"]["created"] + receipt["files"]["updated"])
    committed = set(
        _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", local_commit).stdout.splitlines()
    )
    remote_commit = _git(remote, "rev-parse", f"refs/heads/{EVIDENCE_BRANCH}").stdout.strip()

    assert receipt["status"] == "persisted_to_evidence_branch"
    assert receipt["transaction"]["transaction_reference"].startswith("transaction:")
    assert local_commit == remote_commit == receipt["repository"]["remote_commit"]
    assert receipt["repository"]["remote_branch_verified"] is True
    assert receipt["repository"]["pull_request"] == "local-pr://29"
    assert receipt["repository_state"]["persisted_to_monthly_branch"] is True
    assert committed == intended
    assert pr_calls == [(repo, EVIDENCE_BRANCH)]
    assert _git(repo, "status", "--short").stdout.strip() == "?? artifacts/"
    validate_receipt_mapping(receipt)


def test_pr_failure_preserves_verified_remote_persistence(publish_repo: tuple[Path, Path]) -> None:
    repo, _ = publish_repo

    def fail_pr(_repo: Path, _branch: str) -> str:
        raise RuntimeError("simulated PR connector failure")

    result = ContentEvidenceStore(repo).publish(
        _intake(),
        expected_branch=EVIDENCE_BRANCH,
        allow_create_post=True,
        pr_manager=fail_pr,
    )
    receipt = result["content_evidence_receipt"]

    assert receipt["status"] == "persisted_to_evidence_branch"
    assert receipt["repository"]["remote_branch_verified"] is True
    assert receipt["repository"]["pull_request"] is None
    assert "rolling_evidence_PR" in receipt["unresolved_fields"]


def test_raw_screenshot_and_personal_data_are_not_required_or_committed(evidence_repo: Path) -> None:
    intake = _intake()
    validate_intake_mapping(intake)

    result = _apply(evidence_repo, intake)
    written = result["content_evidence_receipt"]["files"]["created"] + result["content_evidence_receipt"]["files"]["updated"]

    assert intake["source"]["raw_evidence_committed"] is False
    assert not any(path.lower().endswith((".png", ".jpg", ".jpeg")) for path in written)
    assert all("person" not in path.lower() for path in written)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda item: item.update({"intake_id": None}), "intake_id"),
        (lambda item: item.update({"received_at": None}), "received_at"),
        (lambda item: item.update({"supplied_by_role": None}), "supplied_by_role"),
        (
            lambda item: item.update(
                {"post_identifier": {"post_id": None, "post_url": None, "publication_date": None}}
            ),
            "post identifier",
        ),
        (lambda item: item["source"].update({"source_type": "unsupported"}), "source type"),
        (lambda item: item["observed_metrics"].update({"impressions": -1}), "cannot be negative"),
        (lambda item: item["observed_metrics"].update({"impressions": 1.5}), "integer count"),
        (lambda item: item["unavailable_metrics"].append("impressions"), "both observed and unavailable"),
        (lambda item: item["measurement"].update({"explicit_window": "48_hours"}), "window"),
        (
            lambda item: item["authority"].update({"interpretation_authorized": True}),
            "cannot authorize",
        ),
        (
            lambda item: item["authority"].update({"canonical_rule_change_authorized": True}),
            "cannot authorize",
        ),
        (
            lambda item: item["authority"].update({"publication_authorized": True}),
            "cannot authorize",
        ),
        (
            lambda item: item["audience_observations"].append(
                {"target_market_relevance": "certainly_a_buyer"}
            ),
            "audience relevance",
        ),
    ],
)
def test_intake_validator_rejects_invalid_evidence(mutate, message: str) -> None:
    intake = _intake()
    mutate(intake)

    with pytest.raises(ContentValidationError, match=message):
        validate_intake_mapping(intake)


def test_controlled_classification_without_time_evidence_is_rejected() -> None:
    intake = _intake(explicit_window=None)
    intake["measurement"].update(
        {
            "classified_window": "24_hours",
            "measured_at": None,
            "publication_timestamp": None,
        }
    )

    with pytest.raises(ContentValidationError, match="timestamp evidence"):
        validate_intake_mapping(intake)


def test_correction_without_explanation_is_rejected() -> None:
    intake = _intake()
    intake["evidence_action"] = {
        "record_action": "correction",
        "supersedes_record_id": "EVID-PRIOR",
        "correction_reason": None,
    }

    with pytest.raises(ContentValidationError, match="correction_reason"):
        validate_intake_mapping(intake)


def test_nondeterministic_intake_id_is_rejected() -> None:
    intake = _intake()
    intake["intake_id"] = "../../intake"

    with pytest.raises(ContentValidationError, match="INTAKE-YYYYMMDDTHHMMSS-HASH8"):
        validate_intake_mapping(intake)


@pytest.mark.parametrize(
    ("measurement", "expected"),
    [
        (
            {
                "explicit_window": None,
                "measured_at": "2026-08-04T17:30:00Z",
                "publication_timestamp": "2026-08-03T17:30:00Z",
                "calculated_age_hours": None,
                "classified_window": None,
            },
            "24_hours",
        ),
        (
            {
                "explicit_window": None,
                "measured_at": "2026-08-06T17:30:00Z",
                "publication_timestamp": "2026-08-03T17:30:00Z",
                "calculated_age_hours": None,
                "classified_window": None,
            },
            "ad_hoc",
        ),
        (
            {
                "explicit_window": None,
                "measured_at": None,
                "publication_timestamp": None,
                "calculated_age_hours": None,
                "classified_window": "historical_unknown_age",
            },
            "historical_unknown_age",
        ),
    ],
)
def test_acceptance_window_dry_runs(evidence_repo: Path, measurement: dict, expected: str) -> None:
    intake = _intake(explicit_window=None)
    intake["measurement"] = measurement

    result = ContentEvidenceStore(evidence_repo).ingest(intake, allow_create_post=True)

    assert result["content_evidence_receipt"]["status"] == "prepared_not_persisted"
    assert result["ingestion_preview"]["measurement"]["classified_window"] == expected


def test_acceptance_duplicate_ambiguous_and_correction_dry_runs(evidence_repo: Path) -> None:
    _, first_row = _first_apply(evidence_repo)
    duplicate = ContentEvidenceStore(evidence_repo).ingest(_intake(), allow_create_post=True)
    correction = _intake(
        intake_id="INTAKE-20260804T230000-ABCDEF07",
        source_reference="architect://linkedin/dry-correction",
    )
    correction["observed_metrics"]["impressions"] = 1300
    correction["evidence_action"] = {
        "record_action": "correction",
        "supersedes_record_id": first_row["evidence_record_id"],
        "correction_reason": "corrected source",
    }
    correction_preview = ContentEvidenceStore(evidence_repo).ingest(correction, allow_create_post=True)
    ambiguous = deepcopy(correction)
    ambiguous["intake_id"] = "INTAKE-20260804T230001-ABCDEF08"
    ambiguous["post_identifier"] = {
        "post_id": None,
        "post_url": None,
        "publication_date": "2026-08-03",
        "title_or_working_name": "unknown title",
    }
    ambiguous["post_creation_context"]["exact_published_copy"] = None
    ambiguous_preview = ContentEvidenceStore(evidence_repo).ingest(ambiguous, allow_create_post=False)

    assert duplicate["content_evidence_receipt"]["status"] == "duplicate_noop"
    assert correction_preview["content_evidence_receipt"]["status"] == "prepared_not_persisted"
    assert ambiguous_preview["content_evidence_receipt"]["status"] == "needs_post_resolution"
