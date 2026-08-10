from __future__ import annotations

import yaml

from scripts.validate_cco_operating_spine import (
    PRIORITY_REGISTER_PATH,
    REPO_ROOT,
    validate_assessment_document,
    validate_priority_register_document,
    validate_repository,
)


ASSESSMENT_FIXTURE = (
    REPO_ROOT / "tests/fixtures/cco/valid-minimal-system-need-assessment.yaml"
)


def _assessment() -> dict:
    return yaml.safe_load(ASSESSMENT_FIXTURE.read_text(encoding="utf-8"))


def _register() -> dict:
    return yaml.safe_load((REPO_ROOT / PRIORITY_REGISTER_PATH).read_text(encoding="utf-8"))


def _fields(issues) -> set[str]:
    return {issue.field for issue in issues}


def test_valid_minimal_system_need_assessment_passes():
    assert validate_assessment_document(_assessment()) == []


def test_valid_priority_register_passes():
    assert validate_priority_register_document(_register()) == []


def test_repository_operating_spine_passes():
    assert validate_repository() == []


def test_missing_repository_verification_fails_for_available_source():
    document = _assessment()
    del document["cco_system_need_assessment"]["repository_verification"]
    assert any("repository_verification" in field for field in _fields(validate_assessment_document(document)))


def test_stale_repository_verification_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["repository_verified_at"] = "2026-08-10T14:00:00Z"
    assessment["repository_verification"]["verified_at"] = "2026-08-10T14:00:00Z"
    assert "repository_verified_at" in _fields(validate_assessment_document(document))


def test_explicit_repository_source_unavailable_passes_with_limitation():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_scope"]["available"].remove("repository_remote_main")
    assessment["source_scope"]["unavailable"].append("repository_remote_main")
    assessment["repository_verified_at"] = None
    assessment["repository_verification"] = {
        "status": "unavailable",
        "verified_at": None,
        "remote_main_sha": None,
        "limitation": "Remote repository source could not be reached.",
    }
    assessment["source_conclusions"][0]["availability"] = "unavailable"
    assessment["source_conclusions"][0]["conclusion"] = "unknown"
    assert validate_assessment_document(document) == []


def test_invalid_action_class_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["system_need"]["action_class"] = "approve"
    assert any("action_class" in field for field in _fields(validate_assessment_document(document)))


def test_wait_without_review_trigger_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["system_need"]["action_class"] = "wait"
    assert any("system_need" in field for field in _fields(validate_assessment_document(document)))


def test_stop_without_reopen_condition_fails():
    document = _assessment()
    need = document["cco_system_need_assessment"]["system_need"]
    need["action_class"] = "stop"
    need["stop_reason"] = "Evidence cannot support continued work."
    assert any("system_need" in field for field in _fields(validate_assessment_document(document)))


def test_authority_required_without_authority_owner_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["attention_routing"]["authority_owner"] = None
    assert any("authority_owner" in field for field in _fields(validate_assessment_document(document)))


def test_externally_granted_authority_without_evidence_fails():
    document = _assessment()
    routing = document["cco_system_need_assessment"]["attention_routing"]
    routing["authority_status"] = "externally_granted"
    assert any("authority_evidence_reference" in field for field in _fields(validate_assessment_document(document)))


def test_recommendation_treated_as_authority_fails():
    document = _assessment()
    routing = document["cco_system_need_assessment"]["attention_routing"]
    routing["authority_status"] = "externally_granted"
    routing["authority_evidence_reference"] = "CCO recommendation"
    routing["authority_evidence_source"] = "cco_recommendation"
    assert any("authority_evidence_source" in field for field in _fields(validate_assessment_document(document)))


def test_action_required_without_material_trigger_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["attention_routing"]["material_trigger"] = None
    assert any("material_trigger" in field for field in _fields(validate_assessment_document(document)))


def test_active_action_without_owner_fails():
    register = _register()
    register["items"][0]["recommended_owner"] = ""
    assert any("recommended_owner" in field for field in _fields(validate_priority_register_document(register)))


def test_active_action_without_blocking_state_fails():
    register = _register()
    del register["items"][0]["blocking"]
    assert any("blocking" in field for field in _fields(validate_priority_register_document(register)))


def test_active_action_without_completion_condition_fails():
    register = _register()
    register["items"][0]["completion_condition"] = ""
    assert any("completion_condition" in field for field in _fields(validate_priority_register_document(register)))


def test_terminal_priority_without_completion_evidence_fails():
    register = _register()
    register["items"][0]["status"] = "verified_complete"
    assert any("completion_evidence" in field for field in _fields(validate_priority_register_document(register)))


def test_completion_evidence_with_silent_overwrite_fails():
    register = _register()
    register["items"][0]["completion_evidence"]["silent_overwrite_detected"] = True
    assert any("silent_overwrite_detected" in field for field in _fields(validate_priority_register_document(register)))


def test_unavailable_source_treated_as_no_change_fails():
    document = _assessment()
    conclusion = document["cco_system_need_assessment"]["source_conclusions"][2]
    conclusion["conclusion"] = "no_material_delta"
    assert any("source_conclusions.2.conclusion" in field for field in _fields(validate_assessment_document(document)))


def test_not_checked_source_treated_as_no_change_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["source_conclusions"].append(
        {
            "source_id": "specialist_agent_outputs",
            "availability": "not_checked",
            "conclusion": "no_material_delta",
        }
    )
    assert any("source_conclusions.3.conclusion" in field for field in _fields(validate_assessment_document(document)))


def test_repository_api_treated_as_deployed_runtime_fails():
    document = _assessment()
    repository = document["cco_system_need_assessment"]["api_observability"]["repository_implementation"]
    repository["treated_as_deployed_runtime"] = True
    assert any("treated_as_deployed_runtime" in field for field in _fields(validate_assessment_document(document)))


def test_target_v2_contract_treated_as_runtime_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["product_generation"]["target_v2_contract_treated_as_runtime"] = True
    assert any("target_v2_contract_treated_as_runtime" in field for field in _fields(validate_assessment_document(document)))


def test_cco_artifact_creates_accepted_state_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["assessment_artifact_effect"]["creates_corporate_accepted_state"] = True
    assert any("creates_corporate_accepted_state" in field for field in _fields(validate_assessment_document(document)))


def test_cco_artifact_creates_chronology_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["assessment_artifact_effect"]["creates_chronology"] = True
    assert any("creates_chronology" in field for field in _fields(validate_assessment_document(document)))


def test_cco_artifact_creates_reflex_memory_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["assessment_artifact_effect"]["creates_Reflex_Memory"] = True
    assert any("creates_Reflex_Memory" in field for field in _fields(validate_assessment_document(document)))


def test_cco_artifact_creates_production_authority_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["assessment_artifact_effect"]["creates_production_authority"] = True
    assert any("creates_production_authority" in field for field in _fields(validate_assessment_document(document)))


def test_cco_artifact_creates_capital_authority_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["assessment_artifact_effect"]["creates_capital_authority"] = True
    assert any("creates_capital_authority" in field for field in _fields(validate_assessment_document(document)))


def test_current_priority_register_preserves_non_authority():
    register = _register()
    assert register["authority_effect"] == "none"
    assert register["accepted_state_effect"] == "none"
    assert register["chronology_effect"] == "none"
    assert register["Reflex_Memory_effect"] == "none"
    assert register["product_runtime_effect"] == "none"


def test_observed_production_change_requires_attestation_evidence():
    document = _assessment()
    document["cco_system_need_assessment"]["observed_state_delta"]["production_change"] = True
    assert any("state_change_evidence.production" in field for field in _fields(validate_assessment_document(document)))


def test_observed_corporate_state_change_requires_authoritative_evidence():
    document = _assessment()
    document["cco_system_need_assessment"]["observed_state_delta"]["canonical_corporate_state_changed"] = True
    assert any("state_change_evidence.canonical_corporate_state" in field for field in _fields(validate_assessment_document(document)))


def test_observed_chronology_change_requires_authorized_evidence():
    document = _assessment()
    document["cco_system_need_assessment"]["observed_state_delta"]["chronology_change"] = True
    assert any("state_change_evidence.chronology" in field for field in _fields(validate_assessment_document(document)))


def test_duplicate_priority_rank_fails():
    register = _register()
    register["items"][1]["priority_rank"] = register["items"][0]["priority_rank"]
    assert any("priority_rank" in field for field in _fields(validate_priority_register_document(register)))


def test_terminal_priority_with_complete_evidence_passes():
    register = _register()
    item = register["items"][0]
    item["status"] = "verified_complete"
    item["completion_evidence"] = {
        "artifact_or_registry_path": "docs/operations/example-attestation.md",
        "resulting_commit_or_record_id": "record-001",
        "completed_at": "2026-08-10T16:00:00Z",
        "writer_authority": "Architect",
        "historical_entries_preserved": True,
        "provenance_preserved": True,
        "silent_overwrite_detected": False,
        "independently_verified_at": "2026-08-10T16:05:00Z",
    }
    assert validate_priority_register_document(register) == []
