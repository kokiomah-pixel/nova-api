from scripts.run_decision_scenario_suite import load_scenario_library, process_scenarios


def _outputs_by_category():
    outputs = process_scenarios(load_scenario_library())
    grouped = {}
    for output in outputs:
        grouped.setdefault(output["scenario_category"], []).append(output)
    return grouped


def test_environmental_governance_classifies_category_specific_pressure():
    grouped = _outputs_by_category()

    assert any(
        output["environmental_conditions"]["constraint_pressure"] in {"elevated", "severe"}
        or output["risk_surfaces"]["retry_escalation_risk"] in {"elevated", "severe"}
        for output in grouped["capital_movement"]
    )
    assert all(
        output["environmental_conditions"]["timing_pressure"] != "low"
        for output in grouped["pacing"]
    )
    assert all(
        output["risk_surfaces"]["interoperability_risk"] != "low"
        for output in grouped["interoperability"]
    )
    assert all(
        output["risk_surfaces"]["semantic_drift_risk"] != "low"
        or output["risk_surfaces"]["sovereignty_risk"] != "low"
        for output in grouped["governance"]
    )
    assert all(
        output["risk_surfaces"]["sovereignty_risk"] != "low"
        for output in grouped["security"]
    )
    assert all(
        output["risk_surfaces"]["semantic_drift_risk"] != "low"
        for output in grouped["gtm"]
    )
    assert all(
        output["risk_surfaces"]["coordination_risk"] != "low"
        for output in grouped["orchestration"]
    )


def test_nova_response_preserves_consumer_execution_responsibility():
    outputs = process_scenarios(load_scenario_library())

    for output in outputs:
        boundary = output["nova_response"]["non_authority_boundary"]
        assert "retains execution responsibility" in boundary
        assert "sovereign " + "reasoning" not in str(output["nova_response"]).lower()
        assert "policy " + "weights" not in str(output["nova_response"]).lower()
