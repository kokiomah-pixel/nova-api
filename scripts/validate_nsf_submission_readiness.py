#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
NSF_ROOT = ROOT / "docs/grants/nsf-seed-fund"
SUBMISSION_STATE = NSF_ROOT / "nsf-submission-state.yaml"
TECHNICAL_BASELINE = NSF_ROOT / "nsf-technical-baseline-2026-07-17.md"
HYPOTHESIS_MATRIX = NSF_ROOT / "nsf-phase-1-research-hypothesis-matrix.yaml"
SCENARIOS = NSF_ROOT / "nsf-phase-1-experimental-scenarios.yaml"
CLAIM_MATRIX = NSF_ROOT / "nsf-claim-evidence-matrix.yaml"
PROJECT_PITCH = NSF_ROOT / "project-pitch/nsf-project-pitch-submission-draft.md"
ARCHITECT_INPUT = NSF_ROOT / "project-pitch/nsf-project-pitch-Architect-input.yaml"
CONTROL_MATRIX = NSF_ROOT / "nsf-phase-1-proposal-control-matrix.md"

PROJECT_PITCH_LIMITS = {
    "Technology Innovation": 3500,
    "Technical Objectives and Challenges": 3500,
    "Market Opportunity": 1750,
    "Company and Team": 1750,
}

PROHIBITED_ESTABLISHED_CLAIMS = {
    "Nova is " + "production ready": "production_readiness_not_claimed",
    "Nova is deployed across " + "institutional workflows": "live_operation_not_claimed",
    "Nova has demonstrated " + "buyer demand": "buyer_pull_not_claimed",
    "Nova improves " + "financial decisions": "decision_quality_not_established",
    "Nova guarantees compliant " + "execution": "compliance_execution_not_claimed",
    "Nova " + "authorizes transactions": "authority_boundary_preserved",
    "Nova blocks " + "unauthorized transactions": "authority_boundary_preserved",
}

BOUNDARY_ALLOWED_MARKERS = (
    "not ",
    "not_",
    "not-",
    "no ",
    "does not ",
    "do not ",
    "must not ",
    "has not ",
    "will test",
    "research will",
    "proposed_research",
    "prohibited",
    "absent",
    "future research",
    "not established",
)

REQUIRED_MEASURES = {
    "material_context_recall",
    "irrelevant_context_inclusion_rate",
    "prohibited_payload_exposure_count",
    "stale_source_detection_rate",
    "contradiction_detection_rate",
    "unsafe_reconstruction_detection_rate",
    "reconstruction_success_rate",
    "inter_reviewer_agreement",
    "authority_role_confusion_rate",
    "execution_effect_violation_count",
}

REQUIRED_ARCHITECT_INPUT_FIELDS = {
    ("applicant_company", "legal_name"),
    ("applicant_company", "state_of_formation"),
    ("applicant_company", "formation_date"),
    ("applicant_company", "principal_place_of_business"),
    ("applicant_company", "US_owned_and_operated"),
    ("principal_investigator", "full_name"),
    ("principal_investigator", "role"),
    ("principal_investigator", "employment_status"),
    ("principal_investigator", "planned_Phase_I_employment_commitment"),
    ("principal_investigator", "technical_qualifications"),
    ("principal_investigator", "prior_relevant_work"),
    ("company_history", "founded_date"),
    ("submission", "active_target"),
    ("submission", "Project_Pitch_previously_submitted"),
    ("submission", "invitation_received"),
    ("submission", "portal_status"),
}


class NSFReadinessError(ValueError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise NSFReadinessError(f"Expected YAML object: {path}")
    return payload


def _extract_pitch_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    pattern = re.compile(r"^## \d+\. (?P<title>.+?)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        marker = "### Submission Text"
        validation = "### Section Validation"
        if marker not in block or validation not in block:
            sections[title] = ""
            continue
        body = block.split(marker, 1)[1].split(validation, 1)[0].strip()
        sections[title] = body
    return sections


def _character_counts(path: Path = PROJECT_PITCH) -> dict[str, dict[str, Any]]:
    sections = _extract_pitch_sections(path.read_text(encoding="utf-8"))
    return {
        title: {
            "characters": len(sections.get(title, "")),
            "within_limit": len(sections.get(title, "")) <= limit,
            "limit": limit,
        }
        for title, limit in PROJECT_PITCH_LIMITS.items()
    }


def _line_allowed(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in BOUNDARY_ALLOWED_MARKERS)


def _scan_prohibited_claims(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for phrase in PROHIBITED_ESTABLISHED_CLAIMS:
                if phrase.lower() in lowered and not _line_allowed(line):
                    findings.append(f"{path.relative_to(ROOT)}:{line_no}: {phrase}")
    return findings


def _full_project_description_paths() -> list[Path]:
    candidates = [
        NSF_ROOT / "project-description.md",
        NSF_ROOT / "phase-i-project-description.md",
        NSF_ROOT / "full-phase-i-project-description.md",
    ]
    return [path for path in candidates if path.exists()]


def full_project_description_has_raw_urls(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return bool(re.search(r"https?://|www\.", text))


def _has_value(value: Any) -> bool:
    return value is not None and value != "" and value != []


def _architect_input_status() -> dict[str, Any]:
    if not ARCHITECT_INPUT.exists():
        return {
            "file_present": False,
            "Architect_confirmed": False,
            "verified_company_facts_present": False,
            "verified_PI_facts_present": False,
            "verified_team_facts_present": False,
            "missing_fields": ["Architect_input_file_missing"],
        }

    payload = _load_yaml(ARCHITECT_INPUT).get("Architect_input", {})
    missing = [
        ".".join(path)
        for path in sorted(REQUIRED_ARCHITECT_INPUT_FIELDS)
        if not _has_value(payload.get(path[0], {}).get(path[1]))
    ]
    team = payload.get("team", {})
    if not team.get("members"):
        missing.append("team.members")
    if not team.get("technical_roles"):
        missing.append("team.technical_roles")
    if not team.get("commercialization_roles"):
        missing.append("team.commercialization_roles")

    return {
        "file_present": True,
        "Architect_confirmed": payload.get("verification", {}).get("Architect_confirmed") is True,
        "verified_company_facts_present": not any(item.startswith("applicant_company.") for item in missing),
        "verified_PI_facts_present": not any(item.startswith("principal_investigator.") for item in missing),
        "verified_team_facts_present": not any(item.startswith("team.") for item in missing),
        "missing_fields": missing,
    }


def validate_readiness() -> dict[str, Any]:
    blocking: list[str] = []
    warnings: list[str] = []

    required_paths = [
        SUBMISSION_STATE,
        TECHNICAL_BASELINE,
        HYPOTHESIS_MATRIX,
        SCENARIOS,
        CLAIM_MATRIX,
        PROJECT_PITCH,
        ARCHITECT_INPUT,
    ]
    for path in required_paths:
        if not path.exists():
            blocking.append(f"missing_required_file:{path.relative_to(ROOT)}")

    if blocking:
        return _result(
            active_target="unknown",
            invitation_confirmed=False,
            Project_Pitch_invitation_required=False,
            Project_Pitch_structurally_prepared=False,
            portal_blocking=[],
            full_proposal_blocking=[],
            architect_input={},
            structural=False,
            claim_boundary=False,
            character_counts={},
            blocking=blocking,
            warnings=warnings,
        )

    state = _load_yaml(SUBMISSION_STATE)["submission_state"]
    active_target = state["active_target"]["value"]
    invitation_confirmed = bool(state["full_Phase_I_proposal"].get("invitation_confirmed"))
    full_authorized = bool(state["full_Phase_I_proposal"].get("submission_authorized"))
    Project_Pitch_invitation_required = bool(state["Project_Pitch"].get("invitation_required"))
    Project_Pitch_structurally_prepared = bool(state["Project_Pitch"].get("structurally_prepared"))

    if active_target not in state["active_target"]["allowed_values"]:
        blocking.append("active_target_not_allowed")
    if Project_Pitch_invitation_required:
        blocking.append("Project_Pitch_must_not_require_invitation")
    if active_target == "invited_full_Phase_I_proposal" and not invitation_confirmed:
        blocking.append("full_proposal_requires_confirmed_invitation")
    if full_authorized and not invitation_confirmed:
        blocking.append("full_proposal_authorized_without_confirmed_invitation")

    counts = _character_counts()
    for title, result in counts.items():
        if not result["within_limit"]:
            blocking.append(f"Project_Pitch_character_limit_exceeded:{title}")

    sections = _extract_pitch_sections(PROJECT_PITCH.read_text(encoding="utf-8"))
    for title in PROJECT_PITCH_LIMITS:
        if not sections.get(title):
            blocking.append(f"missing_Project_Pitch_section:{title}")

    architect_input = _architect_input_status()
    portal_blocking = list(state["Project_Pitch"].get("blocking_findings", []))
    full_proposal_blocking = list(state["full_Phase_I_proposal"].get("blocking_findings", []))
    if active_target == "unknown":
        portal_blocking.append("active_target_unknown")
    if not architect_input["Architect_confirmed"]:
        portal_blocking.append("Architect_verified_facts_missing")
    if not architect_input["verified_company_facts_present"]:
        portal_blocking.append("verified_company_facts_missing")
    if not architect_input["verified_PI_facts_present"]:
        portal_blocking.append("verified_PI_facts_missing")
    if not architect_input["verified_team_facts_present"]:
        portal_blocking.append("verified_team_facts_missing")
    if "[Do not copy into portal.]" in sections.get("Company and Team", ""):
        portal_blocking.append("placeholder_company_text_not_portal_ready")

    baseline = TECHNICAL_BASELINE.read_text(encoding="utf-8")
    if "completed_preliminary_work" not in baseline or "proposed_Phase_I_research" not in baseline:
        blocking.append("completed_and_proposed_research_not_separated")

    hypotheses = _load_yaml(HYPOTHESIS_MATRIX)
    measure_names = {
        measure
        for hypothesis in hypotheses.get("hypotheses", {}).values()
        for measure in hypothesis.get("measures", [])
    }
    missing_measures = sorted(REQUIRED_MEASURES - measure_names)
    if missing_measures:
        blocking.append(f"missing_quantitative_measure_names:{','.join(missing_measures)}")
    if hypotheses.get("research_program", {}).get("threshold_status") != "to_be_set_from_baseline_experiments":
        blocking.append("program_threshold_status_not_baseline_dependent")
    for hypothesis_id, hypothesis in hypotheses.get("hypotheses", {}).items():
        if hypothesis.get("threshold_status") != "to_be_set_from_baseline_experiments":
            blocking.append(f"threshold_status_not_baseline_dependent:{hypothesis_id}")

    claim_matrix = _load_yaml(CLAIM_MATRIX)
    claims = claim_matrix.get("claims", {})
    if claims.get("Nova_operates_in_live_financial_workflows", {}).get("class") != "prohibited":
        blocking.append("unsupported_live_operation_claim_not_rejected")
    if claims.get("Nova_is_production_ready", {}).get("class") != "prohibited":
        blocking.append("production_readiness_claim_not_rejected")
    if claims.get("Nova_has_buyer_pull", {}).get("class") != "prohibited":
        blocking.append("buyer_pull_claim_not_rejected")
    boundary = claim_matrix.get("boundary", {})
    if boundary.get("Stage_B_activated") is not False:
        blocking.append("Stage_B_claim_rejected")
    if boundary.get("local_authority_remains_responsible") is not True or boundary.get("Nova_does_not_execute") is not True:
        blocking.append("authority_boundary_required")

    prohibited_findings = _scan_prohibited_claims([TECHNICAL_BASELINE, PROJECT_PITCH])
    blocking.extend(f"prohibited_established_claim:{finding}" for finding in prohibited_findings)

    for path in _full_project_description_paths():
        if full_project_description_has_raw_urls(path):
            blocking.append(f"raw_URLs_in_full_Project_Description:{path.relative_to(ROOT)}")
    if not _full_project_description_paths():
        warnings.append("full_Project_Description_not_present; no raw_URL scan applied")

    if "market_context" not in CLAIM_MATRIX.read_text(encoding="utf-8"):
        blocking.append("market_context_does_not_equal_adoption")

    structural = not any(
        item.startswith("missing_required_file") or item.startswith("missing_Project_Pitch_section")
        for item in blocking
    )
    claim_boundary = not any("claim" in item or "Stage_B" in item or "authority_boundary" in item for item in blocking)
    return _result(
        active_target=active_target,
        invitation_confirmed=invitation_confirmed,
        Project_Pitch_invitation_required=Project_Pitch_invitation_required,
        Project_Pitch_structurally_prepared=Project_Pitch_structurally_prepared,
        portal_blocking=sorted(set(portal_blocking)),
        full_proposal_blocking=sorted(set(full_proposal_blocking)),
        architect_input=architect_input,
        structural=structural,
        claim_boundary=claim_boundary,
        character_counts=counts,
        blocking=blocking,
        warnings=warnings,
    )


def _overall_status(blocking: list[str], active_target: str) -> str:
    if any("character_limit" in item for item in blocking):
        return "blocked_by_character_limit"
    if any("missing" in item or "section" in item for item in blocking):
        return "blocked_by_missing_section"
    if any("claim" in item or "Stage_B" in item or "authority_boundary" in item for item in blocking):
        return "blocked_by_claim_boundary"
    if active_target == "unknown":
        return "ready_for_Architect_Project_Pitch_review"
    return "ready_for_Architect_content_review"


def _result(
    *,
    active_target: str,
    invitation_confirmed: bool,
    Project_Pitch_invitation_required: bool = False,
    Project_Pitch_structurally_prepared: bool = False,
    portal_blocking: list[str] | None = None,
    full_proposal_blocking: list[str] | None = None,
    architect_input: dict[str, Any] | None = None,
    structural: bool,
    claim_boundary: bool,
    character_counts: dict[str, dict[str, Any]],
    blocking: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "NSF_submission_readiness": {
            "active_target": active_target,
            "Project_Pitch_invitation_required": Project_Pitch_invitation_required,
            "Project_Pitch_structurally_prepared": Project_Pitch_structurally_prepared,
            "Project_Pitch_portal_ready": not portal_blocking,
            "Project_Pitch_portal_blocking_findings": portal_blocking or [],
            "full_proposal_invitation_confirmed": invitation_confirmed,
            "full_proposal_submission_ready": invitation_confirmed and not (full_proposal_blocking or []),
            "full_proposal_blocking_findings": full_proposal_blocking or [],
            "Architect_input": architect_input or {},
            "structural_validation": structural,
            "claim_boundary_validation": claim_boundary,
            "character_limit_validation": all(item["within_limit"] for item in character_counts.values()) if character_counts else False,
            "character_counts": character_counts,
            "research_engineering_separation": not any(
                item == "completed_and_proposed_research_not_separated" for item in blocking
            ),
            "blocking_findings": blocking,
            "warning_findings": warnings,
            "internal_content_review_allowed": structural and not blocking,
            "overall_status": _overall_status(blocking, active_target),
        }
    }


def main() -> int:
    report = validate_readiness()
    print(json.dumps(report, indent=2, sort_keys=True))
    overall = report["NSF_submission_readiness"]["overall_status"]
    return 0 if overall in {"ready_for_Architect_content_review", "ready_for_Architect_Project_Pitch_review"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
