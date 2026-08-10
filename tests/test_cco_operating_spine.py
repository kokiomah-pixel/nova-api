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


def _operational_assessment() -> dict:
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["record_source_type"] = "operational_assessment"
    assessment["operational_evidence_eligible"] = True
    return document


def test_valid_minimal_system_need_assessment_passes():
    assert validate_assessment_document(_assessment()) == []


def test_observed_plus_recommended_is_representable():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["binding_uncertainty"]["epistemic_state"]["value"] = "observed"
    assessment["work_state"]["recommendation_status"] = "recommended"
    assert validate_assessment_document(document) == []


def test_authorized_but_not_implemented_is_representable():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    routing = assessment["attention_routing"]
    routing["authority_status"] = "externally_granted"
    routing["authority_evidence_reference"] = "governance-record-001"
    routing["authority_evidence_source"] = "external_authority_record"
    assessment["work_state"]["implementation_status"] = "not_started"
    assert validate_assessment_document(document) == []


def test_implemented_but_not_verified_is_representable():
    document = _assessment()
    work_state = document["cco_system_need_assessment"]["work_state"]
    work_state["implementation_status"] = "implemented"
    work_state["verification_status"] = "unverified"
    assert validate_assessment_document(document) == []


def test_completed_but_not_independently_verified_is_representable():
    document = _assessment()
    work_state = document["cco_system_need_assessment"]["work_state"]
    work_state["completion_status"] = "completed"
    work_state["verification_status"] = "unverified"
    assert validate_assessment_document(document) == []


def test_collapsed_current_evidence_state_is_rejected():
    document = _assessment()
    document["cco_system_need_assessment"]["binding_uncertainty"]["current_evidence_state"] = "observed"
    issues = validate_assessment_document(document)
    assert any("current_evidence_state" in issue.message for issue in issues)


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


def _available_external_runtime(document: dict) -> dict:
    observation = document["cco_system_need_assessment"]["api_observability"]["externally_observed_runtime"]
    observation.update(
        {
            "status": "available",
            "observed_at": "2026-08-10T15:03:00Z",
            "endpoint_or_surface": "/health",
            "observation_method": "bounded_HTTP_observation",
            "evidence_references": ["external-observation-001"],
            "limitation": "Does not establish deployed commit or custody.",
        }
    )
    return observation


def _available_control_plane(document: dict) -> dict:
    attestation = document["cco_system_need_assessment"]["api_observability"]["control_plane_attestation"]
    attestation.update(
        {
            "status": "available",
            "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
            "attestation_evidence_reference": "synthetic://independent-control-plane-attestation",
            "environment_identifier": "production-example",
            "observed_at": "2026-08-10T15:03:00Z",
            "observer_or_system": "synthetic-control-plane-observer",
            "evidence_method": "authenticated_control_plane_inspection",
            "control_plane_owner_or_custody": "owner-evidence-001",
            "deployed_commit": "19cfeb341e8d10d223979f40b88d598da5ae1770",
            "evidence_references": ["attestation-record-001"],
            "limitation": None,
        }
    )
    return attestation


def test_external_runtime_available_without_observed_at_fails():
    document = _assessment()
    observation = _available_external_runtime(document)
    del observation["observed_at"]
    assert any("externally_observed_runtime" in field for field in _fields(validate_assessment_document(document)))


def test_external_runtime_available_without_method_fails():
    document = _assessment()
    observation = _available_external_runtime(document)
    del observation["observation_method"]
    assert any("externally_observed_runtime" in field for field in _fields(validate_assessment_document(document)))


def test_external_runtime_available_without_endpoint_or_surface_fails():
    document = _assessment()
    observation = _available_external_runtime(document)
    del observation["endpoint_or_surface"]
    assert any("externally_observed_runtime" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_environment_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["environment_identifier"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_observed_at_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["observed_at"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_owner_or_custody_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["control_plane_owner_or_custody"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_observer_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["observer_or_system"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_evidence_method_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["evidence_method"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_control_plane_available_without_deployed_commit_fails():
    document = _assessment()
    attestation = _available_control_plane(document)
    del attestation["deployed_commit"]
    assert any("control_plane_attestation" in field for field in _fields(validate_assessment_document(document)))


def test_repository_api_evidence_only_passes_without_runtime_inference():
    document = _assessment()
    repository = document["cco_system_need_assessment"]["api_observability"]["repository_implementation"]
    assert repository["treated_as_deployed_runtime"] is False
    assert validate_assessment_document(document) == []


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


def test_production_change_with_arbitrary_string_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["production_change"] = True
    assessment["state_change_evidence"]["production"] = ["some_string"]
    assert any("state_change_evidence.production" in field for field in _fields(validate_assessment_document(document)))


def test_production_change_with_repository_code_only_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["production_change"] = True
    assessment["state_change_evidence"]["production"] = [
        {
            "source_class": "repository_implementation",
            "source_reference": "app.py",
        }
    ]
    assert any("state_change_evidence.production" in field for field in _fields(validate_assessment_document(document)))


def test_corporate_state_change_with_cco_priority_register_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["canonical_corporate_state_changed"] = True
    assessment["state_change_evidence"]["canonical_corporate_state"] = [
        {
            "source_class": "cco_priority_register",
            "source_reference": "docs/operations/cco/current-priority-register.yaml",
        }
    ]
    assert any("state_change_evidence.canonical_corporate_state" in field for field in _fields(validate_assessment_document(document)))


def test_corporate_state_change_with_market_signal_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["canonical_corporate_state_changed"] = True
    assessment["state_change_evidence"]["canonical_corporate_state"] = [
        {
            "source_class": "market_signal",
            "source_reference": "docs/market/market-signal-watch-register.yaml",
        }
    ]
    assert any("state_change_evidence.canonical_corporate_state" in field for field in _fields(validate_assessment_document(document)))


def test_chronology_change_with_cco_recommendation_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["chronology_change"] = True
    assessment["state_change_evidence"]["chronology"] = [
        {
            "source_class": "cco_recommendation",
            "source_reference": "recommendation-001",
        }
    ]
    assert any("state_change_evidence.chronology" in field for field in _fields(validate_assessment_document(document)))


def test_real_accepted_state_registry_entry_can_support_corporate_change():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["canonical_corporate_state_changed"] = True
    assessment["state_change_evidence"]["canonical_corporate_state"] = [
        {
            "source_class": "accepted_state_registry_entry",
            "source_reference": "agent_files/state/accepted-state-registry.yaml",
            "accepted_state_id": "architect_data_operations_stage_a_policy_2026_07_17",
            "observed_or_effective_at": "2026-08-10T15:03:00Z",
        }
    ]
    assert validate_assessment_document(document) == []


def test_synthetic_independent_attestation_structure_passes_without_claiming_current_change():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assert assessment["observed_state_delta"]["production_change"] is False
    assessment["state_change_evidence"]["production"] = [
        {
            "source_class": "production_control_plane_attestation",
            "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
            "attestation_evidence_reference": "synthetic://independent-production-attestation-record",
            "environment_identifier": "production-example",
            "observed_at": "2026-08-10T15:03:00Z",
            "observer_or_system": "synthetic-control-plane-observer",
            "evidence_method": "authenticated_control_plane_inspection",
            "control_plane_owner_or_custody": "owner-evidence-001",
            "deployed_commit": "19cfeb341e8d10d223979f40b88d598da5ae1770",
        }
    ]
    assert validate_assessment_document(document) == []


def test_production_change_with_template_only_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["production_change"] = True
    assessment["state_change_evidence"]["production"] = [
        {
            "source_class": "production_control_plane_attestation",
            "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
        }
    ]
    assert any("state_change_evidence.production" in field for field in _fields(validate_assessment_document(document)))


def test_production_change_without_observer_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["production_change"] = True
    evidence = {
        "source_class": "production_control_plane_attestation",
        "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
        "attestation_evidence_reference": "synthetic://independent-production-attestation-record",
        "environment_identifier": "production-example",
        "observed_at": "2026-08-10T15:03:00Z",
        "evidence_method": "authenticated_control_plane_inspection",
        "control_plane_owner_or_custody": "owner-evidence-001",
        "deployed_commit": "19cfeb341e8d10d223979f40b88d598da5ae1770",
    }
    assessment["state_change_evidence"]["production"] = [evidence]
    assert any("state_change_evidence.production" in field for field in _fields(validate_assessment_document(document)))


def test_production_change_with_cco_assessment_self_reference_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["production_change"] = True
    assessment["state_change_evidence"]["production"] = [
        {
            "source_class": "production_control_plane_attestation",
            "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
            "attestation_evidence_reference": assessment["assessment_id"],
            "environment_identifier": "production-example",
            "observed_at": "2026-08-10T15:03:00Z",
            "observer_or_system": "synthetic-control-plane-observer",
            "evidence_method": "authenticated_control_plane_inspection",
            "control_plane_owner_or_custody": "owner-evidence-001",
            "deployed_commit": "19cfeb341e8d10d223979f40b88d598da5ae1770",
        }
    ]
    assert any("attestation_evidence_reference" in field for field in _fields(validate_assessment_document(document)))


def test_governed_chronology_event_can_support_chronology_change():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["observed_state_delta"]["chronology_change"] = True
    assessment["state_change_evidence"]["chronology"] = [
        {
            "source_class": "chronology_event",
            "source_reference": "chronology/governance/governance-events.jsonl",
            "event_or_record_id": "GOV-20260713-GATE4B-IMPLEMENTATION-ACCEPTED",
        }
    ]
    assert validate_assessment_document(document) == []


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


def test_operational_no_delta_without_baseline_fails():
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    for conclusion in assessment["source_conclusions"]:
        conclusion["conclusion"] = "no_material_delta"
    assessment["material_delta"]["status"] = "no_material_delta"
    assessment["comparison_baseline"] = None
    assert "comparison_baseline" in _fields(validate_assessment_document(document))


def test_observed_change_without_baseline_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "observed_change"
    assessment["material_delta"]["status"] = "observed_change"
    assessment["comparison_baseline"] = None
    assert "comparison_baseline" in _fields(validate_assessment_document(document))


def test_unknown_source_without_baseline_passes():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    for conclusion in assessment["source_conclusions"]:
        conclusion["conclusion"] = "unknown"
    assessment["comparison_baseline"] = None
    assessment["material_delta"]["status"] = "unknown"
    assessment["material_delta"]["summary"] = "Material delta is unknown under stated source limits."
    assert validate_assessment_document(document) == []


def test_all_unknown_sources_with_boolean_false_material_delta_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    for conclusion in assessment["source_conclusions"]:
        conclusion["conclusion"] = "unknown"
    assessment["material_delta"]["changed"] = False
    assert "assessment.cco_system_need_assessment.material_delta" in _fields(
        validate_assessment_document(document)
    )


def test_all_unknown_sources_with_unknown_material_delta_passes():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assert {item["conclusion"] for item in assessment["source_conclusions"]} == {"unknown"}
    assert assessment["material_delta"]["status"] == "unknown"
    assert validate_assessment_document(document) == []


def test_explicit_initial_baseline_with_no_delta_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "no_material_delta"
    assessment["material_delta"]["status"] = "no_material_delta"
    assert "comparison_baseline.baseline_type" in _fields(
        validate_assessment_document(document)
    )


def test_explicit_initial_baseline_with_observed_change_fails():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "observed_change"
    assessment["material_delta"]["status"] = "observed_change"
    assert "comparison_baseline.baseline_type" in _fields(
        validate_assessment_document(document)
    )


def test_prior_verified_assessment_with_no_delta_passes():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "no_material_delta"
    assessment["source_conclusions"][1]["conclusion"] = "no_material_delta"
    assessment["material_delta"]["status"] = "no_material_delta"
    assessment["comparison_baseline"] = {
        "baseline_type": "prior_verified_assessment",
        "baseline_reference": "synthetic://prior-verified-assessment",
        "baseline_observed_at": "2026-08-09T15:00:00Z",
    }
    assert validate_assessment_document(document) == []


def test_verified_repository_snapshot_with_observed_change_passes():
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "observed_change"
    assessment["material_delta"]["status"] = "observed_change"
    assessment["comparison_baseline"] = {
        "baseline_type": "verified_repository_snapshot",
        "baseline_reference": "synthetic://verified-repository-snapshot",
        "baseline_observed_at": "2026-08-09T15:00:00Z",
    }
    assert validate_assessment_document(document) == []


def test_operational_assessment_missing_remote_main_source_fails():
    document = _operational_assessment()
    document["cco_system_need_assessment"]["source_scope"]["available"].remove(
        "repository_remote_main"
    )
    assert "source_scope" in _fields(validate_assessment_document(document))


def test_operational_assessment_missing_cco_priority_register_fails():
    document = _operational_assessment()
    document["cco_system_need_assessment"]["source_scope"]["available"].remove(
        "cco_priority_register"
    )
    assert "source_scope" in _fields(validate_assessment_document(document))


def test_operational_assessment_duplicate_mandatory_source_fails():
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_scope"]["unavailable"].append("production_readiness")
    assessment["source_limitations"].append(
        {
            "source_id": "production_readiness",
            "limitation": "Synthetic duplicate used to prove rejection.",
        }
    )
    assert "source_scope" in _fields(validate_assessment_document(document))


def test_operational_assessment_unavailable_source_with_limitation_passes():
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_scope"]["available"].remove("cco_priority_register")
    assessment["source_scope"]["unavailable"].append("cco_priority_register")
    assessment["source_limitations"].append(
        {
            "source_id": "cco_priority_register",
            "limitation": "Synthetic source-unavailable condition.",
        }
    )
    assert validate_assessment_document(document) == []


def test_synthetic_fixture_does_not_require_live_mandatory_source_set():
    document = _assessment()
    document["cco_system_need_assessment"]["source_scope"]["available"].remove(
        "cco_priority_register"
    )
    assert validate_assessment_document(document) == []


def test_synthetic_fixture_is_marked_synthetic():
    assessment = _assessment()["cco_system_need_assessment"]
    assert assessment["record_source_type"] == "synthetic_fixture"
    assert assessment["operational_evidence_eligible"] is False


def test_synthetic_fixture_treated_as_operational_evidence_fails():
    document = _assessment()
    document["cco_system_need_assessment"]["operational_evidence_eligible"] = True
    assert any("operational_evidence_eligible" in field for field in _fields(validate_assessment_document(document)))


def test_standing_mandate_watch_routes_operator_evidence_separately():
    register = _register()
    item = next(entry for entry in register["items"] if entry["item_id"] == "CCO-WATCH-001")
    assert item["recommended_owner"] == "Architect_or_authorized_operator_research_owner"
