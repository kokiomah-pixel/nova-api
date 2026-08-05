#!/usr/bin/env python3
"""Fail-closed validation for Sharpe Nova OS public-surface coherence."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "CURRENT_STATE.md",
    "docs/legacy-v1/README.md",
    "docs/legacy-v1/quickstart.md",
    "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md",
    "docs/target-v2/README.md",
    "docs/go-to-market/system-class-comparator.md",
    "docs/go-to-market/commercialization-sequence.md",
    "docs/operations/public-surface-coherence-standard.md",
)

BOUNDARY_LINES = (
    "Agent prepares an action.",
    "Nova structures review context.",
    "Local authority decides.",
    "External systems execute.",
    "Nova does not execute.",
)

FIRST_SCREEN_PROHIBITED = (
    "coordination_state",
    "constraint_pressure",
    "drift_score",
    "epoch",
    "policy b",
    "feed metering",
    "x402",
    "circle marketplace",
    "circle agent marketplace",
    "nsf",
    "environmental conditioning",
    "environmental coordination",
)

CURRENT_SURFACES = (
    "CURRENT_STATE.md",
    "README.md",
    "PROJECT_REPORT.md",
    "docs/start-here.md",
    "docs/target-v2/README.md",
    "docs/operations/production-readiness-register.md",
)


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str

    def format(self) -> str:
        return f"{self.field}: {self.message}"


def _read(root: Path, relative: str, errors: list[ValidationError]) -> str:
    path = root / relative
    if not path.is_file():
        errors.append(ValidationError(f"canonical_files.{relative}", "missing required file"))
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(ValidationError(f"canonical_files.{relative}", f"cannot read UTF-8 text: {exc}"))
        return ""


def _require(
    errors: list[ValidationError],
    condition: bool,
    field: str,
    message: str,
) -> None:
    if not condition:
        errors.append(ValidationError(field, message))


def _contains_yaml_value(text: str, key: str, value: str) -> bool:
    pattern = rf"(?m)^\s*{re.escape(key)}:\s*{re.escape(value)}\s*$"
    return re.search(pattern, text) is not None


def _check_links(
    root: Path,
    source_relative: str,
    text: str,
    errors: list[ValidationError],
) -> None:
    source = root / source_relative
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (source.parent / target_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(
                ValidationError(
                    f"links.{source_relative}",
                    f"local link escapes repository: {target}",
                )
            )
            continue
        if not resolved.exists():
            errors.append(
                ValidationError(
                    f"links.{source_relative}",
                    f"unresolved local link: {target}",
                )
            )


def _has_unqualified_production_ready_claim(text: str) -> bool:
    pattern = re.compile(
        r"\b(?:Sharpe Nova OS|Nova|the system|system[- ]wide)\b"
        r"[^\n.]{0,40}\b(?:is|is currently|remains)\s+"
        r"(?:system[- ]wide\s+)?(?:institutionally\s+)?production[- ]ready\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        sentence_start = text.rfind(".", 0, match.start()) + 1
        context = text[sentence_start : match.end()].lower()
        if any(
            qualifier in context
            for qualifier in (
                "not ",
                "does not ",
                "must not ",
                "without evidence",
                "cannot conclude",
                "no claim",
            )
        ):
            continue
        return True
    return False


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    """Return all public-surface coherence failures for *root*."""

    root = root.resolve()
    errors: list[ValidationError] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(ValidationError(f"canonical_files.{relative}", "missing required file"))

    readme = _read(root, "README.md", errors)
    current = _read(root, "CURRENT_STATE.md", errors)
    project_report = _read(root, "PROJECT_REPORT.md", errors)
    historical = _read(
        root,
        "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md",
        errors,
    )
    legacy = _read(root, "docs/legacy-v1/README.md", errors)
    target = _read(root, "docs/target-v2/README.md", errors)
    comparator = _read(root, "docs/go-to-market/system-class-comparator.md", errors)
    commercialization = _read(
        root,
        "docs/go-to-market/commercialization-sequence.md",
        errors,
    )
    readiness = _read(
        root,
        "docs/operations/production-readiness-register.md",
        errors,
    )
    reviewer_paths = _read(root, "docs/reviewer-paths.md", errors)

    # Root README entry path.
    _require(errors, "CURRENT_STATE.md" in readme, "root_README.links_to_CURRENT_STATE", "missing CURRENT_STATE.md link")
    _require(errors, "docs/legacy-v1/README.md" in readme, "root_README.links_to_Legacy_v1", "missing Legacy v1 entry link")
    _require(errors, "docs/target-v2/README.md" in readme, "root_README.links_to_target_v2", "missing target v2 entry link")
    _require(errors, all(line in readme for line in BOUNDARY_LINES), "root_README.canonical_boundary_present", "canonical five-line boundary is incomplete")
    _require(errors, "agent-prepared stablecoin treasury action" in readme.lower(), "root_README.first_workflow_present", "first bounded workflow is missing")
    _require(errors, "## Current state" in readme and "runtime and private adapter are not yet implemented" in readme, "root_README.current_state_summary_present", "bounded current-state summary is missing")
    quickstart_markers = ("NOVA_API_KEY=mytestkey", "/v1/context?intent=", "## Quick Local Check")
    _require(errors, not any(marker in readme for marker in quickstart_markers), "root_README.Legacy_v1_quickstart_absent", "Legacy v1 startup commands remain in the root README")

    first_screen = "\n".join(readme.splitlines()[:100]).lower().replace("_", " ")
    for term in FIRST_SCREEN_PROHIBITED:
        normalized = term.lower().replace("_", " ")
        _require(errors, normalized not in first_screen, f"root_README.first_screen_terminology.{term}", f"prohibited term appears in first 100 lines: {term}")

    # Root compatibility report and historical archive.
    _require(errors, "retained for compatibility" in project_report, "root_PROJECT_REPORT.superseded_pointer_present", "compatibility/supersession pointer is missing")
    _require(errors, "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md" in project_report, "root_PROJECT_REPORT.historical_report_link_present", "historical report link is missing")
    _require(errors, "CURRENT_STATE.md" in project_report, "root_PROJECT_REPORT.current_state_link_present", "current-state link is missing")
    _require(errors, re.search(r"(?im)^\*\*Status:\*\*\s*GTM[- ]Ready", project_report) is None, "root_PROJECT_REPORT.current_GTM_ready_claim_absent", "current GTM-Ready status claim is present")
    _require(errors, re.search(r"(?i)\b(?:system|API)\s+is\s+\*\*?operationally live", project_report) is None, "root_PROJECT_REPORT.current_operationally_live_claim_absent", "current operationally-live claim is present")

    first_40_historical = "\n".join(historical.splitlines()[:40])
    _require(errors, "Superseded current-state notice" in first_40_historical, "historical_report.supersession_banner_in_first_40_lines", "supersession banner is missing from first 40 lines")
    _require(errors, "March 20, 2026" in first_40_historical, "historical_report.historical_date_present", "historical evidence date is missing")
    _require(errors, "CURRENT_STATE.md" in first_40_historical, "historical_report.current_state_link_present", "current-state reference is missing from banner")

    # Product generations.
    _require(errors, _contains_yaml_value(legacy, "implemented", "true"), "product_generation.Legacy_v1_implemented_true", "Legacy v1 must remain implemented")
    _require(errors, _contains_yaml_value(legacy, "canonical_future_external_model", "false"), "product_generation.Legacy_v1_canonical_future_false", "Legacy v1 cannot be the canonical future model")
    _require(errors, _contains_yaml_value(target, "contract_approved", "true"), "product_generation.target_v2_contract_approved_true", "target v2 contract approval is missing")
    _require(errors, _contains_yaml_value(target, "runtime_implemented", "false"), "product_generation.target_v2_runtime_implemented_false", "target v2 runtime must remain not implemented")
    _require(errors, _contains_yaml_value(target, "production_active", "false"), "product_generation.target_v2_production_active_false", "target v2 production must remain inactive")

    # Readiness claims.
    combined_current = "\n".join(
        _read(root, relative, errors)
        for relative in CURRENT_SURFACES
        if (root / relative).is_file()
    )
    _require(errors, not _has_unqualified_production_ready_claim(combined_current), "production_claims.unqualified_system_wide_production_ready_claim_absent", "unqualified system-wide production-ready claim is present")
    _require(errors, _contains_yaml_value(readiness, "system_wide_production_readiness", "not_established"), "production_claims.system_wide_production_readiness_not_established", "system-wide readiness must be not established")
    _require(errors, _contains_yaml_value(readiness, "institutional_pilot", "not_started"), "production_claims.institutional_pilot_not_started", "institutional pilot must be not started")
    _require(errors, _contains_yaml_value(readiness, "production_custody_attestation", "not_complete"), "production_claims.custody_attestation_not_complete", "custody attestation must be incomplete")

    # Commercialization authority.
    _require(errors, _contains_yaml_value(commercialization, "new_pricing_expansion", "false"), "commercialization.new_pricing_expansion_false", "pricing expansion cannot be authorized")
    _require(errors, _contains_yaml_value(commercialization, "marketplace_activation", "false"), "commercialization.marketplace_activation_false", "marketplace activation cannot be authorized")
    _require(errors, _contains_yaml_value(commercialization, "x402_activation", "false"), "commercialization.x402_activation_false", "x402 activation cannot be authorized")
    _require(errors, "bounded_pricing_research" in commercialization and "operator_discovery" in commercialization, "commercialization.bounded_research_permitted", "bounded research permissions are incomplete")

    # Existing system classes and hypothesis boundary.
    comparator_lower = comparator.lower()
    classes = {
        "pre_trade_controls_present": "pre-trade or transaction control",
        "policy_engines_present": "policy engine",
        "compliance_gates_present": "compliance gate",
        "approval_workflows_present": "approval workflow",
        "audit_logs_present": "audit or event log",
        "agent_frameworks_present": "agent framework",
    }
    for field, phrase in classes.items():
        _require(errors, phrase in comparator_lower, f"comparator.{field}", f"missing system class: {phrase}")
    _require(errors, "differentiation is a hypothesis" in comparator_lower and "does not establish that existing systems lack" in comparator_lower, "comparator.differentiation_labeled_hypothesis", "hypothesis and existing-capability boundary are incomplete")
    _require(errors, re.search(r"(?i)\bNova\s+(?:has|possesses|establishes)\s+(?:a\s+)?moat\b", comparator) is None, "comparator.moat_claim_absent", "positive moat claim is present")

    # Entry links and default reviewer order.
    _check_links(root, "CURRENT_STATE.md", current, errors)
    ten_minute = reviewer_paths.split("## Ten-Minute Path", 1)[-1].split("\n---", 1)[0]
    expected_order = (
        "README.md",
        "CURRENT_STATE.md",
        "docs/go-to-market/first-use-case-agent-prepared-treasury-action.md",
        "docs/target-v2/README.md",
        "docs/operations/production-readiness-register.md",
    )
    positions = [ten_minute.find(item) for item in expected_order]
    numbered_start = "1. `README.md`\n2. `CURRENT_STATE.md`"
    _require(errors, numbered_start in ten_minute and all(position >= 0 for position in positions) and positions == sorted(positions), "reviewer_paths.default_path_starts_with_CURRENT_STATE", "ten-minute path must move from README directly to CURRENT_STATE before workflow and readiness detail")

    return errors


def main() -> int:
    errors = validate_repository(REPO_ROOT)
    if errors:
        print("public_surface_coherence:")
        print("  overall_status: incoherent")
        print("  errors:")
        for error in errors:
            escaped = error.format().replace('"', '\\"')
            print(f'    - "{escaped}"')
        return 1

    print("public_surface_coherence:")
    print("  overall_status: coherent")
    print("  canonical_current_state: CURRENT_STATE.md")
    print("  canonical_product_direction: target_v2_non_authority_review_context")
    print("  Legacy_v1_isolated: true")
    print("  target_v2_status_explicit: true")
    print("  conflicting_current_readiness_claims: 0")
    print("  commercialization_sequence_explicit: true")
    print("  public_comprehension_path_ready: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
