from collections import Counter

from scripts.run_deep_scenario_suite import (
    APPROVED_PERSONAS,
    REQUIRED_FAMILIES,
    load_scenarios,
    run_validation,
)


def test_deep_scenario_suite_contains_required_scenarios() -> None:
    records = load_scenarios()

    assert len(records) >= 16
    assert len({record.payload["scenario_id"] for record in records}) == len(records)


def test_deep_scenario_suite_covers_required_families() -> None:
    records = load_scenarios()
    distribution = Counter(record.family for record in records)

    assert set(distribution) == REQUIRED_FAMILIES
    assert all(count >= 1 for count in distribution.values())


def test_deep_scenario_suite_uses_approved_personas() -> None:
    records = load_scenarios()

    for record in records:
        assert record.payload["persona"] in APPROVED_PERSONAS


def test_deep_scenario_suite_has_multi_stage_scenarios() -> None:
    records = load_scenarios()

    assert all(len(record.payload["stages"]) >= 3 for record in records)


def test_deep_scenario_validation_report_passes() -> None:
    report = run_validation()

    assert report["status"] == "passed"
    assert report["scenario_count"] >= 16
    assert report["stage_count"] >= 48
    assert report["authority_effect"] == "none"
    assert report["execution_capability"] is False
