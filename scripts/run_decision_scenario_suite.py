from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = REPO_ROOT / "docs" / "decision-intake" / "decision-scenario-library.md"
REPORT_PATH = REPO_ROOT / "docs" / "decision-intake" / "month-two-decision-pressure-log.md"

SEVERITY_LEVELS = {"low", "moderate", "elevated", "severe"}
PULSE_LEVELS = {"stable", "unstable", "elevated"}
SCENARIO_CATEGORIES = {
    "capital_movement",
    "pacing",
    "interoperability",
    "governance",
    "security",
    "gtm",
    "orchestration",
}
MEMORY_TYPES = {
    "decision_context",
    "failure_pattern",
    "semantic_drift",
    "interoperability_event",
    "security_event",
    "pacing_event",
}
PROHIBITED_RESPONSE_LANGUAGE = {
    "execute " + "now",
    "approv" + "ed",
    "authoriz" + "ed",
    "authoriz" + "es",
    "recommends trades",
    "recommend trades",
    "sovereign " + "reasoning",
    "policy " + "weights",
}

RISK_TO_ENVIRONMENT = {
    "coordination_risk": "fragmentation",
    "sovereignty_risk": "drift",
    "retry_escalation_risk": "timing_pressure",
    "semantic_drift_risk": "drift",
    "interoperability_risk": "constraint_pressure",
}

CATEGORY_MEMORY_TYPE = {
    "capital_movement": "decision_context",
    "pacing": "pacing_event",
    "interoperability": "interoperability_event",
    "governance": "semantic_drift",
    "security": "security_event",
    "gtm": "semantic_drift",
    "orchestration": "decision_context",
}

CATEGORY_ASSESSMENT = {
    "capital_movement": "Nova surfaces capital-movement pressure as an environmental admissibility condition, with chronology preserved before any local action path changes.",
    "pacing": "Nova classifies timing pressure and coordination cadence as environmental conditions that should be stabilized before downstream systems change pace.",
    "interoperability": "Nova distinguishes payload validity from acceptance by surrounding settlement infrastructure and records the replayable interoperability chronology.",
    "governance": "Nova flags doctrine continuity and sovereignty-boundary pressure while preserving the audit trail for review.",
    "security": "Nova classifies developer-environment integrity as governance pressure and preserves a security chronology without exposing sensitive material.",
    "gtm": "Nova identifies narrative drift and category-collapse pressure that could weaken environmental-governance positioning.",
    "orchestration": "Nova surfaces dependency formation and orchestration trust pressure before integration choices harden into operating assumptions.",
}

CATEGORY_GUIDANCE = {
    "capital_movement": "Conditioning guidance: emit risk posture, increase context validation depth, and keep capital-moving responsibility with the consuming system.",
    "pacing": "Conditioning guidance: normalize cadence, widen timing observation, and suppress blind retry loops until the environment is less congested.",
    "interoperability": "Conditioning guidance: separate construction success from facilitator acceptance, preserve failure chronology, and require replayable diagnostics.",
    "governance": "Conditioning guidance: protect canonical framing, classify category drift, and route unresolved doctrine pressure into review chronology.",
    "security": "Conditioning guidance: preserve event order, apply credential hygiene outside the report surface, and avoid storing raw secret material.",
    "gtm": "Conditioning guidance: choose language that reinforces environmental governance and log second-order market interpretation risk.",
    "orchestration": "Conditioning guidance: protect sovereign internals, constrain field expansion, and prioritize orchestration conditioning over feature sprawl.",
}


class ScenarioSuiteError(ValueError):
    pass


def _extract_json_block(markdown: str) -> Any:
    match = re.search(r"```json\s*(.*?)\s*```", markdown, flags=re.DOTALL)
    if not match:
        raise ScenarioSuiteError("scenario library must contain a fenced json block")
    return json.loads(match.group(1))


def load_scenario_library(path: Path = LIBRARY_PATH) -> list[dict[str, Any]]:
    raw = _extract_json_block(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "categories" not in raw:
        raise ScenarioSuiteError("scenario library json must contain a categories object")

    scenarios: list[dict[str, Any]] = []
    for category, prompts in raw["categories"].items():
        if category not in SCENARIO_CATEGORIES:
            raise ScenarioSuiteError(f"unknown scenario category: {category}")
        if not isinstance(prompts, list):
            raise ScenarioSuiteError(f"category {category} must contain a list of prompts")
        for index, prompt in enumerate(prompts, start=1):
            scenario = {
                "scenario_id": f"{category}_{index:02d}",
                "scenario_category": category,
                "decision_context": prompt["decision_context"],
                "primary_risks": prompt["primary_risks"],
                "intensity": prompt.get("intensity", "elevated"),
                "unresolved_class": prompt.get("unresolved_class"),
            }
            scenarios.append(scenario)
    return scenarios


def _empty_environment() -> dict[str, str]:
    return {
        "constraint_pressure": "low",
        "drift": "low",
        "fragmentation": "low",
        "pulse": "stable",
        "timing_pressure": "low",
    }


def _empty_risks() -> dict[str, str]:
    return {
        "coordination_risk": "low",
        "sovereignty_risk": "low",
        "retry_escalation_risk": "low",
        "semantic_drift_risk": "low",
        "interoperability_risk": "low",
    }


def _pulse_for(environment: dict[str, str]) -> str:
    if "severe" in environment.values():
        return "unstable"
    if "elevated" in environment.values():
        return "elevated"
    return "stable"


def process_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    category = scenario["scenario_category"]
    intensity = scenario.get("intensity", "elevated")
    if intensity not in SEVERITY_LEVELS:
        raise ScenarioSuiteError(f"invalid intensity for {scenario['scenario_id']}: {intensity}")

    environment = _empty_environment()
    risks = _empty_risks()
    primary_risks = scenario.get("primary_risks", [])
    if not primary_risks:
        raise ScenarioSuiteError(f"scenario must classify at least one risk: {scenario['scenario_id']}")

    for risk_name in primary_risks:
        if risk_name not in risks:
            raise ScenarioSuiteError(f"unknown risk surface {risk_name} in {scenario['scenario_id']}")
        risks[risk_name] = intensity
        environment[RISK_TO_ENVIRONMENT[risk_name]] = intensity

    if category == "pacing":
        environment["timing_pressure"] = intensity
    if category == "interoperability":
        risks["interoperability_risk"] = max([risks["interoperability_risk"], intensity], key=_severity_rank)
    if category == "security":
        environment["drift"] = max([environment["drift"], "moderate"], key=_severity_rank)
    if category == "gtm":
        risks["semantic_drift_risk"] = max([risks["semantic_drift_risk"], intensity], key=_severity_rank)
    if category == "orchestration":
        risks["coordination_risk"] = max([risks["coordination_risk"], intensity], key=_severity_rank)

    environment["pulse"] = _pulse_for(environment)

    output = {
        "scenario_id": scenario["scenario_id"],
        "scenario_category": category,
        "decision_context": scenario["decision_context"],
        "environmental_conditions": environment,
        "risk_surfaces": risks,
        "nova_response": {
            "environmental_assessment": CATEGORY_ASSESSMENT[category],
            "conditioning_guidance": CATEGORY_GUIDANCE[category],
            "non_authority_boundary": "Nova emits environmental telemetry only; the consuming operator or orchestration system retains execution responsibility.",
            "required_chronology_entry": f"Record {scenario['scenario_id']} as {category} pressure with observed risks: {', '.join(primary_risks)}.",
        },
        "reflex_memory_update": {
            "should_record": True,
            "memory_type": CATEGORY_MEMORY_TYPE[category],
            "reason": f"Decision pressure contributes to environment -> behavior -> outcome chronology for {category} scenarios.",
        },
    }
    validate_scenario_output(output, scan_response_only=True)
    return output


def _severity_rank(level: str) -> int:
    return {"low": 0, "moderate": 1, "elevated": 2, "severe": 3}[level]


def _contains_prohibited_response_language(output: dict[str, Any], scan_response_only: bool) -> list[str]:
    scanned = output["nova_response"] if scan_response_only else output
    serialized = json.dumps(scanned, sort_keys=True).lower()
    return sorted(term for term in PROHIBITED_RESPONSE_LANGUAGE if term in serialized)


def validate_scenario_output(output: dict[str, Any], *, scan_response_only: bool = False) -> None:
    required_top_level = {
        "scenario_id",
        "scenario_category",
        "decision_context",
        "environmental_conditions",
        "risk_surfaces",
        "nova_response",
        "reflex_memory_update",
    }
    missing = required_top_level - set(output)
    if missing:
        raise ScenarioSuiteError(f"scenario output missing keys: {sorted(missing)}")

    if output["scenario_category"] not in SCENARIO_CATEGORIES:
        raise ScenarioSuiteError(f"unknown scenario category: {output['scenario_category']}")

    environmental_conditions = output["environmental_conditions"]
    for key in ("constraint_pressure", "drift", "fragmentation", "timing_pressure"):
        if environmental_conditions.get(key) not in SEVERITY_LEVELS:
            raise ScenarioSuiteError(f"invalid environmental level for {output['scenario_id']}: {key}")
    if environmental_conditions.get("pulse") not in PULSE_LEVELS:
        raise ScenarioSuiteError(f"invalid pulse level for {output['scenario_id']}")

    risks = output["risk_surfaces"]
    if set(risks) != set(_empty_risks()):
        raise ScenarioSuiteError(f"risk surfaces do not match contract for {output['scenario_id']}")
    if not any(level != "low" for level in risks.values()):
        raise ScenarioSuiteError(f"scenario must classify at least one risk: {output['scenario_id']}")
    if any(level not in SEVERITY_LEVELS for level in risks.values()):
        raise ScenarioSuiteError(f"invalid risk level in {output['scenario_id']}")

    response = output["nova_response"]
    for key in (
        "environmental_assessment",
        "conditioning_guidance",
        "non_authority_boundary",
        "required_chronology_entry",
    ):
        if not response.get(key):
            raise ScenarioSuiteError(f"missing nova_response.{key} for {output['scenario_id']}")
    if "retains execution responsibility" not in response["non_authority_boundary"]:
        raise ScenarioSuiteError(f"consumer execution responsibility boundary missing for {output['scenario_id']}")

    memory = output["reflex_memory_update"]
    if not isinstance(memory.get("should_record"), bool):
        raise ScenarioSuiteError(f"reflex memory decision missing for {output['scenario_id']}")
    if memory.get("memory_type") not in MEMORY_TYPES:
        raise ScenarioSuiteError(f"invalid reflex memory type for {output['scenario_id']}")
    if not memory.get("reason"):
        raise ScenarioSuiteError(f"reflex memory reason missing for {output['scenario_id']}")

    prohibited = _contains_prohibited_response_language(output, scan_response_only)
    if prohibited:
        raise ScenarioSuiteError(
            f"prohibited response language in {output['scenario_id']}: {', '.join(prohibited)}"
        )


def process_scenarios(scenarios: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [process_scenario(scenario) for scenario in scenarios]


def summarize_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    category_distribution = Counter(output["scenario_category"] for output in outputs)
    risk_distribution: dict[str, Counter[str]] = defaultdict(Counter)
    elevated_surfaces = Counter()
    for output in outputs:
        for surface, level in output["risk_surfaces"].items():
            risk_distribution[surface][level] += 1
            if level in {"elevated", "severe"}:
                elevated_surfaces[surface] += 1

    return {
        "total_scenarios": len(outputs),
        "category_distribution": dict(sorted(category_distribution.items())),
        "risk_distribution": {
            surface: dict(sorted(levels.items()))
            for surface, levels in sorted(risk_distribution.items())
        },
        "most_common_elevated_risk_surfaces": elevated_surfaces.most_common(),
        "reflex_memory_update_count": sum(
            1 for output in outputs if output["reflex_memory_update"]["should_record"]
        ),
        "semantic_drift_flags": sum(
            1 for output in outputs
            if output["risk_surfaces"]["semantic_drift_risk"] in {"elevated", "severe"}
        ),
        "interoperability_risk_flags": sum(
            1 for output in outputs
            if output["risk_surfaces"]["interoperability_risk"] in {"elevated", "severe"}
        ),
        "retry_escalation_flags": sum(
            1 for output in outputs
            if output["risk_surfaces"]["retry_escalation_risk"] in {"elevated", "severe"}
        ),
        "sovereignty_risk_flags": sum(
            1 for output in outputs
            if output["risk_surfaces"]["sovereignty_risk"] in {"elevated", "severe"}
        ),
        "unresolved_scenario_classes": sorted(
            {
                output["scenario_category"]
                for output in outputs
                if "severe" in output["risk_surfaces"].values()
            }
        ),
    }


def _markdown_table(mapping: dict[str, Any], *, headers: tuple[str, str]) -> str:
    lines = [f"| {headers[0]} | {headers[1]} |", "| --- | --- |"]
    for key, value in mapping.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_report(outputs: list[dict[str, Any]], path: Path = REPORT_PATH) -> dict[str, Any]:
    summary = summarize_outputs(outputs)
    risk_rows = []
    for surface, distribution in summary["risk_distribution"].items():
        risk_rows.append(
            "| {surface} | {low} | {moderate} | {elevated} | {severe} |".format(
                surface=surface,
                low=distribution.get("low", 0),
                moderate=distribution.get("moderate", 0),
                elevated=distribution.get("elevated", 0),
                severe=distribution.get("severe", 0),
            )
        )

    common_rows = [
        f"| {surface} | {count} |"
        for surface, count in summary["most_common_elevated_risk_surfaces"]
    ]
    if not common_rows:
        common_rows = ["| none | 0 |"]

    unresolved = ", ".join(summary["unresolved_scenario_classes"]) or "none"
    content = "\n".join(
        [
            "# Month Two Decision Pressure Log",
            "",
            "Generated by `scripts/run_decision_scenario_suite.py`.",
            "",
            "## Total Scenarios Processed",
            "",
            str(summary["total_scenarios"]),
            "",
            "## Category Distribution",
            "",
            _markdown_table(summary["category_distribution"], headers=("Category", "Count")),
            "",
            "## Risk Distribution",
            "",
            "| Risk Surface | Low | Moderate | Elevated | Severe |",
            "| --- | ---: | ---: | ---: | ---: |",
            *risk_rows,
            "",
            "## Most Common Elevated Risk Surfaces",
            "",
            "| Risk Surface | Count |",
            "| --- | ---: |",
            *common_rows,
            "",
            "## Reflex Memory Update Count",
            "",
            str(summary["reflex_memory_update_count"]),
            "",
            "## Flag Counts",
            "",
            _markdown_table(
                {
                    "semantic_drift_flags": summary["semantic_drift_flags"],
                    "interoperability_risk_flags": summary["interoperability_risk_flags"],
                    "retry_escalation_flags": summary["retry_escalation_flags"],
                    "sovereignty_risk_flags": summary["sovereignty_risk_flags"],
                },
                headers=("Flag", "Count"),
            ),
            "",
            "## Unresolved Scenario Classes",
            "",
            unresolved,
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Nova decision intake scenario suite.")
    parser.add_argument("--library", type=Path, default=LIBRARY_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args(argv)

    scenarios = load_scenario_library(args.library)
    outputs = process_scenarios(scenarios)
    for output in outputs:
        validate_scenario_output(output, scan_response_only=True)
    summary = write_report(outputs, args.report)
    print(f"processed {summary['total_scenarios']} decision scenarios")
    print(f"report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
