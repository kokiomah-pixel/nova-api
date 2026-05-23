from collections import Counter

from scripts.run_decision_scenario_suite import (
    SCENARIO_CATEGORIES,
    load_scenario_library,
    process_scenarios,
    validate_scenario_output,
)


def test_decision_scenario_library_contains_required_distribution():
    scenarios = load_scenario_library()
    distribution = Counter(scenario["scenario_category"] for scenario in scenarios)

    assert len(scenarios) >= 70
    assert set(distribution) == SCENARIO_CATEGORIES
    assert all(count >= 10 for count in distribution.values())


def test_decision_scenario_outputs_match_required_shape():
    outputs = process_scenarios(load_scenario_library())

    for output in outputs:
        validate_scenario_output(output, scan_response_only=True)
        assert output["nova_response"]["environmental_assessment"]
        assert output["nova_response"]["required_chronology_entry"]
        assert any(level != "low" for level in output["risk_surfaces"].values())
        assert isinstance(output["reflex_memory_update"]["should_record"], bool)
