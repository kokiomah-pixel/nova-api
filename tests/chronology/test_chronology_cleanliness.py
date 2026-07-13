import json
import subprocess

from monitoring_console_status import UNKNOWN, load_chronology_status
from write_cleanliness_report import build_report


def test_generated_cleanliness_report_is_validation_derived() -> None:
    report = build_report()
    assert report["validation_status"] == "passed"
    assert report["lanes"]["reflex_chronology"]["state"] == "clean_intact"
    assert report["lanes"]["archive_chronology"]["state"] == "clean_with_explicit_unknowns"
    assert report["unsupported_claims"] == 0
    assert report["unresolved_items"] == ["ARC-20260713-ARCHIVE-INVENTORY-UNKNOWNS"]


def test_console_reads_valid_report(tmp_path) -> None:
    path = tmp_path / "report.json"; path.write_text(json.dumps(build_report()))
    result = load_chronology_status(path)["current_cleanliness_diagnosis"]
    assert result["operational_chronology"] == "clean_reconciled"


def test_console_missing_report_fails_visible(tmp_path) -> None:
    assert load_chronology_status(tmp_path / "missing.json")["current_cleanliness_diagnosis"] == UNKNOWN


def test_console_rejects_manual_clean_override(tmp_path) -> None:
    report = build_report(); report["lanes"]["archive_chronology"]["state"] = "clean_reconciled"
    path = tmp_path / "report.json"; path.write_text(json.dumps(report))
    assert set(load_chronology_status(path)["current_cleanliness_diagnosis"].values()) == {"invalid_report"}


def test_console_rejects_false_cleanliness_with_errors(tmp_path) -> None:
    report = build_report(); report["lanes"]["governance_chronology"]["errors"] = 1
    path = tmp_path / "report.json"; path.write_text(json.dumps(report))
    assert set(load_chronology_status(path)["current_cleanliness_diagnosis"].values()) == {"invalid_report"}


def test_console_marks_commit_mismatch_stale(tmp_path) -> None:
    report = build_report(); report["source_commit"] = "0" * 40
    path = tmp_path / "report.json"; path.write_text(json.dumps(report))
    assert set(load_chronology_status(path)["current_cleanliness_diagnosis"].values()) == {"stale_commit_mismatch"}


def test_console_uses_reviewed_source_commit_during_pr_ci(tmp_path, monkeypatch) -> None:
    reviewed = "1da25a1be3b0408e36bf1411189cf72fa91a1804"
    checkout = "0269e8456e182dd14739ff59c74f86bdc176956a"
    monkeypatch.setenv("NOVA_REVIEWED_SOURCE_COMMIT", reviewed)
    monkeypatch.setenv("NOVA_CI_CHECKOUT_COMMIT", checkout)
    report = build_report()
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report))
    result = load_chronology_status(path)["current_cleanliness_diagnosis"]
    assert result["operational_chronology"] == "clean_reconciled"
    assert report["source_commit"] == reviewed
    assert report["ci_checkout_commit"] == checkout
