from scripts.run_decision_scenario_suite import (
    MEMORY_TYPES,
    load_scenario_library,
    process_scenarios,
    summarize_outputs,
    write_report,
)


def test_reflex_memory_update_is_decided_for_every_scenario():
    outputs = process_scenarios(load_scenario_library())

    assert all(output["reflex_memory_update"]["should_record"] is True for output in outputs)
    assert all(output["reflex_memory_update"]["memory_type"] in MEMORY_TYPES for output in outputs)
    assert all(output["reflex_memory_update"]["reason"] for output in outputs)


def test_reflex_memory_growth_summary_tracks_required_flags():
    outputs = process_scenarios(load_scenario_library())
    summary = summarize_outputs(outputs)

    assert summary["total_scenarios"] >= 70
    assert summary["reflex_memory_update_count"] == summary["total_scenarios"]
    assert summary["semantic_drift_flags"] > 0
    assert summary["interoperability_risk_flags"] > 0
    assert summary["retry_escalation_flags"] > 0
    assert summary["sovereignty_risk_flags"] > 0


def test_decision_pressure_report_can_be_emitted(tmp_path):
    outputs = process_scenarios(load_scenario_library())
    report_path = tmp_path / "month-two-decision-pressure-log.md"

    summary = write_report(outputs, report_path)
    report = report_path.read_text(encoding="utf-8")

    assert summary["total_scenarios"] >= 70
    assert "Total Scenarios Processed" in report
    assert "Risk Distribution" in report
    assert "Unresolved Scenario Classes" in report
