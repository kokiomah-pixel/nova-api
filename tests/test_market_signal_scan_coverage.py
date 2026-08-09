from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import yaml

from scripts.validate_market_signal_scan_coverage import (
    REGISTER_PATH,
    REPO_ROOT,
    SCHEMA_PATH,
    discover_market_signal_run_paths,
    eligible_governed_watch_ids,
    validate_market_signal_run,
    validate_market_signal_run_artifacts,
)


RETROSPECTIVE_PATH = Path("docs/market/runs/2026/MSR-2026-08-09-001.yaml")


def _inputs():
    register = yaml.safe_load((REPO_ROOT / REGISTER_PATH).read_text(encoding="utf-8"))
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    retrospective = yaml.safe_load(
        (REPO_ROOT / RETROSPECTIVE_PATH).read_text(encoding="utf-8")
    )
    return register, schema, retrospective


def _governance_non_effects():
    return {
        "accepted_state_change": False,
        "chronology_event_required": False,
        "chronology_change": False,
        "Reflex_Memory_effect": "none",
        "Reflex_Memory_change": False,
        "constraint_change": False,
        "policy_change": False,
        "roadmap_authority": False,
        "roadmap_change": False,
        "architecture_change": False,
        "architecture_authority_created": False,
        "engineering_authority": False,
        "engineering_authority_created": False,
        "runtime_change": False,
        "production_change": False,
        "external_integration": False,
        "buyer_demand_established": False,
    }


def _escalation_review():
    return {
        "thesis_strengthening_triggers_checked": True,
        "category_compression_triggers_checked": True,
        "stored_escalation_review": {
            "repeated_institutional_behavior_observed": False,
            "structural_category_movement_observed": False,
            "material_competitive_compression_observed": False,
            "evidence_insufficient_for_trigger": True,
        },
        "escalation_condition_met": False,
    }


def _direct_document():
    return {
        "market_signal_report": {
            "report_id": "MSR-TEST-DIRECT-001",
            "contract_version": "market_signal_run_v0_1",
            "run_mode": "direct_market_signal_run",
            "coverage_record_origin": "contemporaneous_scan",
            "original_governed_watch_coverage_explicit": True,
            "observed_date": "2026-08-10",
            "reporting_window": {
                "start": "2026-08-10",
                "end": "2026-08-10",
                "source_scope": ["bounded_external_research"],
                "source_limits": [],
            },
            "evidence_coverage": "sufficient",
            "governed_watch_coverage": [
                {
                    "signal_id": "ARC_AGENTIC_FINANCE_2026",
                    "required_this_run": True,
                    "scan_attempted": True,
                    "scan_status": "completed",
                    "delta_state": "no_material_delta",
                    "source_access": {
                        "material_sources_available": True,
                        "unavailable_sources": [],
                    },
                    "escalation_review": _escalation_review(),
                    "authority_effect": "none",
                }
            ],
            "broad_discovery": {
                "completed_within_stated_scope": True,
                "observations_reviewed": [],
                "new_signals": [],
            },
            "reconciliation": {
                "related_to_existing_watch": [],
                "genuinely_distinct_candidates": [],
            },
            "aggregate_state": {
                "environmental_pressure": "unchanged",
                "category_compression": "unchanged",
                "Nova_problem_legibility": "unchanged",
                "direct_Nova_buyer_evidence": "none",
                "buyer_pull": "none",
                "adoption": "none",
                "workflow_dependency": "none",
            },
            "not_established": ["engineering_authority"],
            "source_provenance": {
                "source": "bounded_external_research",
                "status": "direct_scan_output",
                "independent_repository_verification": True,
            },
            "governance": _governance_non_effects(),
        }
    }


def _validate(document, register=None, schema=None):
    loaded_register, loaded_schema, _ = _inputs()
    return validate_market_signal_run(
        register if register is not None else loaded_register,
        schema if schema is not None else loaded_schema,
        document,
    )


def _write_run(root: Path, name: str, document: dict) -> Path:
    path = root / "docs" / "market" / "runs" / "2026" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_active_governed_watch_present_in_direct_run_passes():
    register, schema, _ = _inputs()

    assert eligible_governed_watch_ids(register) == {"ARC_AGENTIC_FINANCE_2026"}
    assert validate_market_signal_run(register, schema, _direct_document()) == []


def test_active_governed_watch_omitted_from_direct_run_fails():
    document = _direct_document()
    report = document["market_signal_report"]
    report["governed_watch_coverage"] = []
    report["evidence_coverage"] = "invalid"

    errors = _validate(document)

    assert any("missing mandatory governed-watch coverage" in error.message for error in errors)


def test_watch_checked_no_material_delta_passes():
    assert _validate(_direct_document()) == []


def test_watch_source_unavailable_is_valid_source_incomplete_state():
    document = _direct_document()
    report = document["market_signal_report"]
    coverage = report["governed_watch_coverage"][0]
    coverage["scan_status"] = "source_incomplete"
    coverage["delta_state"] = "source_unavailable"
    coverage["source_access"] = {
        "material_sources_available": False,
        "unavailable_sources": ["material_watch_source"],
    }
    report["evidence_coverage"] = "source_incomplete"

    assert _validate(document) == []


def test_source_unavailable_misrepresented_as_no_change_fails():
    document = _direct_document()
    report = document["market_signal_report"]
    coverage = report["governed_watch_coverage"][0]
    coverage["scan_status"] = "source_incomplete"
    coverage["delta_state"] = "no_material_delta"
    coverage["source_access"] = {
        "material_sources_available": False,
        "unavailable_sources": ["material_watch_source"],
    }
    report["evidence_coverage"] = "source_incomplete"

    errors = _validate(document)

    assert any("no_material_delta is invalid" in error.message for error in errors)


def test_broad_discovery_cannot_substitute_for_missing_governed_watch():
    document = _direct_document()
    report = document["market_signal_report"]
    report["broad_discovery"]["observations_reviewed"] = ["new_observation"]
    report["broad_discovery"]["new_signals"] = ["new_observation"]
    report["reconciliation"]["genuinely_distinct_candidates"] = ["new_observation"]
    report["governed_watch_coverage"] = []
    report["evidence_coverage"] = "invalid"

    errors = _validate(document)

    assert any("missing mandatory governed-watch coverage" in error.message for error in errors)


def test_related_signal_reconciled_to_existing_watch_passes():
    document = _direct_document()
    report = document["market_signal_report"]
    report["broad_discovery"]["observations_reviewed"] = ["related_observation"]
    report["reconciliation"]["related_to_existing_watch"] = [
        {
            "observation_id": "related_observation",
            "watch_signal_id": "ARC_AGENTIC_FINANCE_2026",
            "relationship": ["supporting_context"],
            "provenance": {
                "source": "bounded_external_research",
                "status": "direct_scan_output",
                "independent_repository_verification": True,
            },
            "canonical_watch_record_mutated": False,
        }
    ]

    assert _validate(document) == []


def test_retrospective_reconciliation_is_valid_but_has_no_direct_scan_coverage():
    register, schema, document = _inputs()
    report = document["market_signal_report"]

    assert validate_market_signal_run(register, schema, document) == []
    assert report["run_mode"] == "retrospective_reconciliation"
    assert report["original_governed_watch_coverage_explicit"] is False
    assert report["original_run_coverage_compliant"] is False
    assert "governed_watch_coverage" not in report
    assert "evidence_coverage" not in report


def test_retrospective_reconciliation_cannot_claim_direct_scan_fields():
    _, _, document = _inputs()
    report = document["market_signal_report"]
    report["governed_watch_coverage"] = deepcopy(_direct_document()["market_signal_report"]["governed_watch_coverage"])

    errors = _validate(document)

    assert any(error.field.startswith("schema.") for error in errors)


def test_retrospective_reconciliation_cannot_rewrite_original_compliance():
    _, _, document = _inputs()
    document["market_signal_report"]["original_run_coverage_compliant"] = True

    errors = _validate(document)

    assert any("original_run_coverage_compliant" in error.field or error.field.startswith("schema.") for error in errors)


def test_future_bad_direct_run_makes_canonical_artifact_validation_fail(tmp_path):
    register, schema, retrospective = _inputs()
    _write_run(tmp_path, "MSR-EXISTING-RETROSPECTIVE.yaml", retrospective)
    future = _direct_document()
    future["market_signal_report"]["report_id"] = "MSR-FUTURE-BAD"
    future["market_signal_report"]["governed_watch_coverage"] = []
    future["market_signal_report"]["evidence_coverage"] = "invalid"
    _write_run(tmp_path, "MSR-FUTURE-BAD.yaml", future)

    paths = discover_market_signal_run_paths(tmp_path)
    errors = validate_market_signal_run_artifacts(register, schema, paths)

    assert len(paths) == 2
    assert any(
        "MSR-FUTURE-BAD.yaml" in error.field
        and "missing mandatory governed-watch coverage" in error.message
        for error in errors
    )


def test_future_compliant_direct_run_keeps_canonical_artifact_validation_green(tmp_path):
    register, schema, retrospective = _inputs()
    _write_run(tmp_path, "MSR-EXISTING-RETROSPECTIVE.yaml", retrospective)
    future = _direct_document()
    future["market_signal_report"]["report_id"] = "MSR-FUTURE-GOOD"
    _write_run(tmp_path, "MSR-FUTURE-GOOD.yaml", future)

    paths = discover_market_signal_run_paths(tmp_path)

    assert len(paths) == 2
    assert validate_market_signal_run_artifacts(register, schema, paths) == []


def test_eligible_watch_requires_stored_escalation_conditions():
    register, schema, _ = _inputs()
    register = deepcopy(register)
    arc = next(
        item
        for item in register["signals"]
        if item.get("signal_id") == "ARC_AGENTIC_FINANCE_2026"
    )
    arc["thesis_strengthening_triggers"] = []

    errors = validate_market_signal_run(register, schema, _direct_document())

    assert any(
        error.field.endswith("thesis_strengthening_triggers")
        and "must preserve stored escalation conditions" in error.message
        for error in errors
    )


def test_watch_scan_creates_no_authority_or_canonical_state():
    governance = _direct_document()["market_signal_report"]["governance"]

    assert governance == _governance_non_effects()
