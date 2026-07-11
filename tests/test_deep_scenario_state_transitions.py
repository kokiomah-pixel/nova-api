from scripts.run_deep_scenario_suite import load_scenarios


def _scenario_by_id(scenario_id: str):
    for record in load_scenarios():
        if record.payload["scenario_id"] == scenario_id:
            return record.payload

    raise AssertionError(f"Scenario not found: {scenario_id}")


def _postures(scenario_id: str) -> list[str]:
    scenario = _scenario_by_id(scenario_id)

    return [stage["expected_review_posture"] for stage in scenario["stages"]]


def test_missing_source_can_recover_to_ordinary_review() -> None:
    assert _postures("DSC-004") == [
        "insufficient_context",
        "constrained_review",
        "ordinary_review",
    ]


def test_stale_source_requires_reconciliation_before_recovery() -> None:
    assert _postures("DSC-006") == [
        "constrained_review",
        "source_reconciliation_required",
        "ordinary_review",
    ]


def test_urgency_does_not_reduce_missing_context_constraint() -> None:
    scenario = _scenario_by_id("DSC-010")
    stages = scenario["stages"]

    assert stages[0]["expected_review_posture"] == "insufficient_context"
    assert stages[1]["expected_review_posture"] == "insufficient_context"
    assert "urgency_pressure" in stages[1]["expected_unresolved_items"]


def test_repeated_request_does_not_create_permission() -> None:
    scenario = _scenario_by_id("DSC-012")
    stages = scenario["stages"]

    assert stages[0]["expected_authority_effect"] == "none"
    assert stages[1]["expected_authority_effect"] == "none"
    assert stages[1]["expected_review_posture"] == "exception_visibility_required"


def test_recovery_requires_evidence_change() -> None:
    scenario = _scenario_by_id("DSC-016")
    stages = scenario["stages"]

    assert stages[0]["expected_review_posture"] == "constrained_review"
    assert stages[1]["expected_review_posture"] == "constrained_review"
    assert "verified_resolution" in stages[2]["evidence_delta"]["added"]
    assert stages[2]["expected_review_posture"] == (
        "reviewable_with_disclosed_uncertainty"
    )
    assert stages[3]["expected_review_posture"] == "ordinary_review"


def test_historical_context_can_remain_visible_without_controlling_posture() -> None:
    scenario = _scenario_by_id("DSC-008")
    stages = scenario["stages"]

    assert stages[0]["expected_reflex_memory_relevance"] == "uncertain"
    assert stages[1]["expected_reflex_memory_relevance"] == "stale"
    assert stages[2]["expected_reflex_memory_relevance"] == "irrelevant"
    assert stages[2]["expected_review_posture"] == "ordinary_review"
