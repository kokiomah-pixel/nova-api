from collections import Counter

from scripts.run_deep_scenario_suite import load_scenarios


def _scenario_by_id(scenario_id: str):
    for record in load_scenarios():
        if record.payload["scenario_id"] == scenario_id:
            return record.payload

    raise AssertionError(f"Scenario not found: {scenario_id}")


def test_suite_contains_non_escalation_outcomes() -> None:
    records = load_scenarios()

    final_postures = Counter(
        record.payload["expected_final_state"]["review_posture"] for record in records
    )

    assert final_postures["ordinary_review"] >= 3
    assert final_postures["reviewable_with_disclosed_uncertainty"] >= 2


def test_complete_context_does_not_create_chronology_candidate() -> None:
    scenario = _scenario_by_id("DSC-013")

    assert all(
        stage["expected_chronology_action"] == "no_candidate"
        for stage in scenario["stages"]
    )
    assert all(
        stage["expected_review_posture"] == "ordinary_review"
        for stage in scenario["stages"]
    )


def test_irrelevant_memory_does_not_condition_posture() -> None:
    scenario = _scenario_by_id("DSC-014")

    assert all(
        stage["expected_reflex_memory_relevance"] == "irrelevant"
        for stage in scenario["stages"]
    )
    assert all(
        stage["expected_review_posture"] == "ordinary_review"
        for stage in scenario["stages"]
    )


def test_routine_review_does_not_require_chronology_candidate() -> None:
    scenario = _scenario_by_id("DSC-015")

    assert all(
        stage["expected_chronology_action"] == "no_candidate"
        for stage in scenario["stages"]
    )


def test_verified_resolution_reduces_posture() -> None:
    scenario = _scenario_by_id("DSC-016")
    postures = [stage["expected_review_posture"] for stage in scenario["stages"]]

    assert postures == [
        "constrained_review",
        "constrained_review",
        "reviewable_with_disclosed_uncertainty",
        "ordinary_review",
    ]


def test_recovery_does_not_rewrite_history() -> None:
    scenario = _scenario_by_id("DSC-016")
    final_stage = scenario["stages"][-1]

    assert final_stage["expected_chronology_action"] == "retain_candidate"
    assert final_stage["expected_review_posture"] == "ordinary_review"
    assert final_stage["expected_authority_effect"] == "none"
