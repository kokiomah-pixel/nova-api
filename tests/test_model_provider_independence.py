from pathlib import Path

from scripts.doctrine_lint import scan_text
from scripts.run_decision_scenario_suite import (
    load_scenario_library,
    process_scenarios,
    validate_scenario_output,
)
from nova_api.telemetry.x402_observability import structured_event


def test_core_governance_tools_remain_usable_without_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    lint_findings = scan_text(
        path=Path("continuity-sample.md"),
        text="Nova emits environmental governance context; operators retain local responsibility.",
        root=Path("."),
    )
    assert lint_findings == []

    scenarios = load_scenario_library()
    outputs = process_scenarios(scenarios[:3])
    assert outputs
    for output in outputs:
        validate_scenario_output(output, scan_response_only=True)

    event = structured_event(
        "x402.interoperability.failure",
        resource="/v1/feeds/constraint_pressure",
        failure_reason="provider-independent-continuity-check",
    )
    assert event.to_dict()["event"] == "x402.interoperability.failure"
