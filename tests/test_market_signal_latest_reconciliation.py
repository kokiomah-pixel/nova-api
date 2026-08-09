from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.validate_market_signal_scan_coverage import (
    REGISTER_PATH,
    REPO_ROOT,
    SCHEMA_PATH,
    validate_market_signal_run,
)


RECONCILIATION_PATH = Path("docs/market/runs/2026/MSR-2026-08-09-001.yaml")

EXPECTED_PROVENANCE = {
    "source": "Market_Signal_Agent_brief",
    "status": "specialist_output",
    "independent_repository_verification": False,
}

EXPECTED_RELATIONSHIPS = {
    "Formance_autonomous_finance": {
        "execution_and_ledger_category_compression",
        "agentic_finance_problem_legibility",
    },
    "commercetools_authorization_commentary": {
        "authorization_language_compression",
        "category_confusion_pressure",
    },
    "institutional_AI_governance_analysis": {
        "institutional_governance_problem_legibility",
        "temporal_governance_state_pressure",
    },
}

EXPECTED_AGGREGATE = {
    "environmental_pressure": "increasing",
    "category_compression": "increasing",
    "Nova_problem_legibility": "strengthening",
    "direct_Nova_buyer_evidence": "none",
    "buyer_pull": "none",
    "adoption": "none",
    "workflow_dependency": "none",
}

REQUIRED_NON_CLAIMS = {
    "Arc_watch_escalation_trigger_met",
    "Nova_buyer_pull",
    "Nova_adoption",
    "Nova_pricing_power",
    "Nova_workflow_dependency",
    "institutional_requirement_for_Nova",
    "architecture_change",
    "engineering_authority",
}


def _inputs():
    register = yaml.safe_load((REPO_ROOT / REGISTER_PATH).read_text(encoding="utf-8"))
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    document = yaml.safe_load(
        (REPO_ROOT / RECONCILIATION_PATH).read_text(encoding="utf-8")
    )
    return register, schema, document


def test_august_reconciliation_preserves_historical_content_and_provenance():
    register, schema, document = _inputs()
    report = document["market_signal_report"]

    assert validate_market_signal_run(register, schema, document) == []
    assert report["report_id"] == "MSR-2026-08-09-001"
    assert report["source_provenance"] == EXPECTED_PROVENANCE
    assert report["source_basis"] == "specialist_output"
    assert report["independent_external_reverification"] is False

    actual_relationships = {
        item["observation_id"]: set(item["relationship"])
        for item in report["reconciliation"]["related_to_existing_watch"]
    }
    assert actual_relationships == EXPECTED_RELATIONSHIPS
    assert all(
        item["provenance"] == EXPECTED_PROVENANCE
        for item in report["reconciliation"]["related_to_existing_watch"]
    )
    assert report["aggregate_state"] == EXPECTED_AGGREGATE
    assert REQUIRED_NON_CLAIMS <= set(report["not_established"])


def test_august_reconciliation_does_not_retroactively_claim_direct_scan_coverage():
    _, _, document = _inputs()
    report = document["market_signal_report"]

    assert report["run_mode"] == "retrospective_reconciliation"
    assert report["coverage_record_origin"] == "post_run_governance_reconciliation"
    assert report["original_governed_watch_coverage_explicit"] is False
    assert report["original_run_coverage_compliant"] is False
    assert report["reconciliation_completed"] is True
    assert "evidence_coverage" not in report
    assert "governed_watch_coverage" not in report

    arc_review = report["retrospective_watch_reconciliation"]
    assert len(arc_review) == 1
    assert arc_review[0]["signal_id"] == "ARC_AGENTIC_FINANCE_2026"
    assert arc_review[0]["relationship_review_completed"] is True
    assert arc_review[0]["escalation_review"]["escalation_condition_met"] is False
    assert arc_review[0]["authority_effect"] == "none"
