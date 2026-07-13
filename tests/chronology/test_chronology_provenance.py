from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from chronology_common import (
    ROOT,
    ChronologyProvenanceError,
    resolve_ci_checkout_commit,
    resolve_reviewed_source_commit,
)
from write_cleanliness_report import build_report


REVIEWED = "ca0ef570fb3aa25e0afc72867a5d8dc896677375"
CHECKOUT = "db6c16f3391a61308df9ecdd5d0d8f21d2e61651"


def test_explicit_reviewed_source_commit_used(monkeypatch) -> None:
    monkeypatch.setenv("NOVA_REVIEWED_SOURCE_COMMIT", REVIEWED)
    assert resolve_reviewed_source_commit(ROOT) == REVIEWED


def test_local_head_fallback_used(monkeypatch) -> None:
    monkeypatch.delenv("NOVA_REVIEWED_SOURCE_COMMIT", raising=False)
    expected = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert resolve_reviewed_source_commit(ROOT) == expected


def test_malformed_reviewed_commit_rejected(monkeypatch) -> None:
    monkeypatch.setenv("NOVA_REVIEWED_SOURCE_COMMIT", "not-a-commit")
    with pytest.raises(ChronologyProvenanceError):
        resolve_reviewed_source_commit(ROOT)


def test_explicit_checkout_commit_recorded(monkeypatch) -> None:
    monkeypatch.setenv("NOVA_CI_CHECKOUT_COMMIT", CHECKOUT)
    assert resolve_ci_checkout_commit(ROOT) == CHECKOUT


def test_malformed_checkout_commit_rejected(monkeypatch) -> None:
    monkeypatch.setenv("NOVA_CI_CHECKOUT_COMMIT", "1234")
    with pytest.raises(ChronologyProvenanceError):
        resolve_ci_checkout_commit(ROOT)


def test_reviewed_source_commit_is_distinct_from_ci_checkout(monkeypatch) -> None:
    monkeypatch.setenv("NOVA_REVIEWED_SOURCE_COMMIT", REVIEWED)
    monkeypatch.setenv("NOVA_CI_CHECKOUT_COMMIT", CHECKOUT)
    report = build_report()
    assert report["source_commit"] == REVIEWED
    assert report["ci_checkout_commit"] == CHECKOUT


def test_report_contains_both_commit_fields(monkeypatch) -> None:
    monkeypatch.delenv("NOVA_REVIEWED_SOURCE_COMMIT", raising=False)
    monkeypatch.delenv("NOVA_CI_CHECKOUT_COMMIT", raising=False)
    report = build_report()
    assert len(report["source_commit"]) == 40
    assert len(report["ci_checkout_commit"]) == 40


def test_make_targets_default_to_repository_python() -> None:
    completed = subprocess.run(
        ["make", "-n", "chronology-verify"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "python3 scripts/chronology" not in completed.stdout
    assert completed.stdout.count(".venv/bin/python scripts/chronology/") == 3


def test_missing_repository_python_fails_with_clear_message(tmp_path: Path) -> None:
    missing = tmp_path / "missing-python"
    completed = subprocess.run(
        ["make", "require-venv", f"PYTHON={missing}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert f"Repository Python not found: {missing}" in completed.stderr
