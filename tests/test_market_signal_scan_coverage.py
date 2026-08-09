from __future__ import annotations

from copy import deepcopy
import json

import yaml

from scripts.validate_market_signal_scan_coverage import (
    DEFAULT_RUN_PATH,
    REGISTER_PATH,
    REPO_ROOT,
    SCHEMA_PATH,
    eligible_governed_watch_ids,
    validate_market_signal_run,
)


def _inputs():
    register = yaml.safe_load((REPO_ROOT / REGISTER_PATH).read_text(encoding="utf-8"))
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    document = yaml.safe_load((REPO_ROOT / DEFAULT_RUN_PATH).read_text(encoding="utf-8"))
    return register, schema, document


def _validate(document, register=None, schema=None):
    loaded_register, loaded_schema, _ = _inputs()
    return validate_market_signal_run(
        register if register is not None else loaded_register,
        schema if schema is not None else loaded_schema,
        document,
    )


def _generic_document():
    _, _, document = _inputs()
    document = deepcopy(document)
    document["market_signal_report"]["report_id"] = "MSR-TEST-001"
    return document


def test_active_governed_watch_present_passes():
    register, schema, document = _inputs()

    assert eligible_governed_watch_ids(register) == {"ARC_AGENTIC_FINANCE_2026"}
    assert validate_market_signal_run(register, schema, document) == []


def test_active_governed_watch_omitted_fails():
    document = _generic_document()
    report = document["market_signal_report"]
    report["governed_watch_coverage"] = []
    report["evidence_coverage"] = "invalid"

    errors = _validate(document)

    assert any("missing mandatory governed-watch coverage" in error.message for error in errors)


def test_watch_checked_no_material_delta_passes():
    document = _generic_document()
    coverage = document["market_signal_report"]["governed_watch_coverage"][0]
    coverage["delta_state"] = "no_material_delta"

    assert _validate(document) == []


def test_watch_source_unavailable_is_valid_source_incomplete_state():
    document = _generic_document()
    report = document["market_signal_report"]
    coverage = report["governed_watch_coverage"][0]
    coverage["scan_status"] = "source_incomplete"
    coverage["delta_state"] = "source_unavailable"
    coverage["source_access"] = {
        "material_sources_available": False,
        "unavailable_sources": ["official_Arc_source"],
    }
    report["evidence_coverage"] = "source_incomplete"

    assert _validate(document) == []


def test_source_unavailable_misrepresented_as_no_change_fails():
    document = _generic_document()
    report = document["market_signal_report"]
    coverage = report["governed_watch_coverage"][0]
    coverage["delta_state"] = "no_material_delta"
    coverage["source_access"] = {
        "material_sources_available": False,
        "unavailable_sources": ["official_Arc_source"],
    }
    report["evidence_coverage"] = "source_incomplete"

    errors = _validate(document)

    assert any("no_material_delta is invalid" in error.message for error in errors)


def test_broad_discovery_cannot_substitute_for_missing_governed_watch():
    document = _generic_document()
    report = document["market_signal_report"]
    assert report["broad_discovery"]["observations_reviewed"]
    report["governed_watch_coverage"] = []
    report["evidence_coverage"] = "invalid"

    errors = _validate(document)

    assert any("missing mandatory governed-watch coverage" in error.message for error in errors)


def test_related_signals_reconcile_to_existing_arc_watch():
    _, _, document = _inputs()
    report = document["market_signal_report"]
    related = report["reconciliation"]["related_to_existing_watch"]

    assert {item["observation_id"] for item in related} == {
        "Formance_autonomous_finance",
        "commercetools_authorization_commentary",
        "institutional_AI_governance_analysis",
    }
    assert {item["watch_signal_id"] for item in related} == {
        "ARC_AGENTIC_FINANCE_2026"
    }
    assert report["reconciliation"]["genuinely_distinct_candidates"] == []
    assert _validate(document) == []


def test_latest_brief_preserves_specialist_output_provenance():
    _, _, document = _inputs()
    report = document["market_signal_report"]

    assert report["run_mode"] == "retrospective_reconciliation"
    assert report["coverage_record_origin"] == "post_run_governance_reconciliation"
    assert report["original_output_watch_coverage_explicit"] is False
    assert report["source_provenance"] == {
        "source": "Market_Signal_Agent_brief",
        "status": "specialist_output",
        "independent_repository_verification": False,
    }
    assert all(
        item["provenance"]["independent_repository_verification"] is False
        for item in report["reconciliation"]["related_to_existing_watch"]
    )


def test_retrospective_reconciliation_cannot_rewrite_original_coverage():
    document = _generic_document()
    report = document["market_signal_report"]
    report["original_output_watch_coverage_explicit"] = True

    errors = _validate(document)

    assert any("preserve that original watch coverage was absent" in error.message for error in errors)


def test_eligible_watch_requires_stored_escalation_conditions():
    register, schema, document = _inputs()
    register = deepcopy(register)
    arc = next(
        item
        for item in register["signals"]
        if item.get("signal_id") == "ARC_AGENTIC_FINANCE_2026"
    )
    arc["thesis_strengthening_triggers"] = []

    errors = validate_market_signal_run(register, schema, document)

    assert any(
        error.field.endswith("thesis_strengthening_triggers")
        and "must preserve stored escalation conditions" in error.message
        for error in errors
    )


def test_market_language_does_not_establish_institutional_behavior_or_escalation():
    _, _, document = _inputs()
    report = document["market_signal_report"]
    coverage = report["governed_watch_coverage"][0]
    stored = coverage["escalation_review"]["stored_escalation_review"]

    assert stored["repeated_institutional_behavior_observed"] is False
    assert stored["structural_category_movement_observed"] is False
    assert stored["material_competitive_compression_observed"] is False
    assert stored["evidence_insufficient_for_trigger"] is True
    assert coverage["escalation_review"]["escalation_condition_met"] is False


def test_watch_scan_creates_no_authority_or_canonical_state():
    _, _, document = _inputs()
    governance = document["market_signal_report"]["governance"]

    assert governance == {
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
