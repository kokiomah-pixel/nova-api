from pathlib import Path

import yaml

from scripts.validate_nsf_submission_readiness import (
    CLAIM_MATRIX,
    HYPOTHESIS_MATRIX,
    PROJECT_PITCH,
    SUBMISSION_STATE,
    TECHNICAL_BASELINE,
    _character_counts,
    _extract_pitch_sections,
    full_project_description_has_raw_urls,
    validate_readiness,
)


def _report():
    return validate_readiness()["NSF_submission_readiness"]


def test_Project_Pitch_sections_respect_character_limits():
    counts = _character_counts()

    assert counts["Technology Innovation"]["characters"] <= 3500
    assert counts["Technical Objectives and Challenges"]["characters"] <= 3500
    assert counts["Market Opportunity"]["characters"] <= 1750
    assert counts["Company and Team"]["characters"] <= 1750
    assert all(item["within_limit"] for item in counts.values())


def test_full_proposal_requires_confirmed_invitation():
    state = yaml.safe_load(SUBMISSION_STATE.read_text(encoding="utf-8"))["submission_state"]

    assert state["submission_type"]["value"] == "unknown"
    assert state["Project_Pitch"]["invitation_received"] is False
    assert state["full_proposal"]["submission_authorized"] is False
    assert state["blocking_state"]["value"] == "blocks_full_proposal_submission"


def test_completed_work_separated_from_proposed_research():
    text = TECHNICAL_BASELINE.read_text(encoding="utf-8")

    assert "completed_preliminary_work" in text
    assert "proposed_Phase_I_research" in text
    assert text.index("completed_preliminary_work") < text.index("proposed_Phase_I_research")


def test_unsupported_live_operation_claim_rejected():
    claims = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["claims"]

    assert claims["Nova_operates_in_live_financial_workflows"]["class"] == "prohibited"


def test_production_readiness_claim_rejected():
    claims = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["claims"]

    assert claims["Nova_is_production_ready"]["class"] == "prohibited"


def test_buyer_pull_claim_rejected_without_evidence():
    claims = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["claims"]

    assert claims["Nova_has_buyer_pull"]["class"] == "prohibited"


def test_Stage_B_claim_rejected():
    boundary = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["boundary"]

    assert boundary["Stage_B_activated"] is False


def test_authority_boundary_required():
    boundary = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["boundary"]
    pitch = PROJECT_PITCH.read_text(encoding="utf-8")

    assert boundary["local_authority_remains_responsible"] is True
    assert boundary["Nova_does_not_execute"] is True
    assert "Local authority decides" not in pitch or "Nova does not execute" in pitch


def test_unresolved_thresholds_must_be_labeled():
    matrix = yaml.safe_load(HYPOTHESIS_MATRIX.read_text(encoding="utf-8"))

    assert matrix["research_program"]["threshold_status"] == "to_be_set_from_baseline_experiments"
    assert all(
        item["threshold_status"] == "to_be_set_from_baseline_experiments"
        for item in matrix["hypotheses"].values()
    )


def test_full_Project_Description_rejects_raw_URLs(tmp_path):
    project_description = tmp_path / "project-description.md"
    project_description.write_text("Project description with https://example.com inside.\n", encoding="utf-8")

    assert full_project_description_has_raw_urls(project_description) is True


def test_market_context_does_not_equal_adoption():
    claims = yaml.safe_load(CLAIM_MATRIX.read_text(encoding="utf-8"))["claims"]

    assert claims["agentic_financial_workflows_create_reviewability_pressure"]["class"] == "market_context"
    assert claims["Nova_has_buyer_pull"]["class"] == "prohibited"


def test_Project_Pitch_submission_can_proceed_without_full_proposal_invitation():
    report = _report()
    sections = _extract_pitch_sections(PROJECT_PITCH.read_text(encoding="utf-8"))

    assert report["overall_status"] == "blocked_by_invitation_status"
    assert report["structural_validation"] is True
    assert report["character_limit_validation"] is True
    assert set(sections) == {
        "Technology Innovation",
        "Technical Objectives and Challenges",
        "Market Opportunity",
        "Company and Team",
    }
