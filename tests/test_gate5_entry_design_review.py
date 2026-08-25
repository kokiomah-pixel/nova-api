from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.validate_gate5_entry_design_review import (
    CANONICAL_AUTHORITY_HASHES,
    DURABLE_LIFECYCLE_PATHS,
    EXPECTED_SCENARIOS,
    EXPECTED_PRECONDITIONS,
    INCORPORATED,
    PROHIBITED_HUMAN_MEANING,
    STALE_LIFECYCLE_MARKERS,
    evaluate_scenario,
    render_human_presentation,
    validate_contract,
    validate_durable_lifecycle_documents,
    validate_fixtures,
    validate_human_presentation,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/gate5_institutional_exposure_contract_v0_1.json"
FIXTURES = ROOT / "fixtures/target-v2/gate5-entry/design_cases.json"
GAPS = ROOT / "specs/review_context_contract_gaps_v0_1.json"


def _contract() -> dict:
    return json.loads(SPEC.read_text(encoding="utf-8"))


def _fixtures() -> dict:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _gaps() -> dict:
    return json.loads(GAPS.read_text(encoding="utf-8"))


def _errors(contract: dict) -> list:
    return validate_contract(contract, _gaps())


def _durable_documents() -> dict[str, str]:
    return {
        path: (ROOT / path).read_text(encoding="utf-8")
        for path in DURABLE_LIFECYCLE_PATHS
    }


def test_gate5_entry_repository_validator_passes() -> None:
    assert validate_repository() == []


def test_canonical_authority_hash_inventory_is_complete() -> None:
    assert set(CANONICAL_AUTHORITY_HASHES) == {
        "docs/architecture/external-review-context-contract-v2.md",
        "specs/review_context_contract_v2.json",
        "docs/target-v2/gate-3-field-derivation-ledger-v0.1.md",
        "specs/review_context_field_derivation_v0_1.json",
        "docs/target-v2/context-proof-canonicalization-v0.1.md",
    }


def test_one_bounded_action_class_only() -> None:
    contract = _contract()
    boundary = contract["action_boundary"]
    assert boundary["permitted_action_classes"] == [
        "agent_prepared_stablecoin_treasury_action"
    ]
    assert boundary["multiple_action_classes_permitted"] is False
    changed = copy.deepcopy(contract)
    changed["action_boundary"]["permitted_action_classes"].append("portfolio_trade")
    assert _errors(changed)


def test_institutional_owner_local_authority_and_profile_owner_are_required() -> None:
    contract = _contract()
    ownership = contract["institutional_ownership"]
    assert ownership["workflow_owner_required"] is True
    assert ownership["local_authority_required"] is True
    assert ownership["review_profile_owner_required"] is True
    assert contract["authority_model"]["local_authority_external_to_Nova"] is True
    for key in (
        "workflow_owner_required",
        "local_authority_required",
        "review_profile_owner_required",
    ):
        changed = copy.deepcopy(contract)
        changed["institutional_ownership"][key] = False
        assert _errors(changed)


def test_profile_lifecycle_is_attributable_versioned_and_nonretroactive() -> None:
    profile = _contract()["review_profile_governance"]
    assert set(profile["lifecycle_authorities"]) == {
        "author",
        "approve",
        "version",
        "activate",
        "replace",
        "retire",
    }
    assert profile["Nova_structural_validation_only"] is True
    assert profile["Nova_may_invent_institutional_requirements"] is False
    assert profile["retroactive_rewrite_of_prior_context"] is False


def test_source_authority_is_scoped_without_new_target_field_or_winner() -> None:
    evidence = _contract()["evidence_boundary"]
    assert set(evidence["state_dimensions"]) == {
        "source_state",
        "context_state",
        "review_completeness",
    }
    model = evidence["source_authority_model"]
    assert model["new_target_v2_semantic_field"] is False
    assert model["global_source_ranking"] is False
    assert model["Nova_selected_winner"] is False
    assert evidence["evidence_categories"]["conflicting"] == (
        "all_material_variants_remain_visible"
    )
    assert evidence["evidence_categories"]["unknown_authority"] == "remains_unknown"


def test_identity_is_not_workflow_authorization_and_cross_tenant_is_prohibited() -> None:
    identity = _contract()["identity_access"]
    assert identity["authentication_equals_workflow_authorization"] is False
    assert identity["payment_equals_institutional_identity"] is False
    assert identity["cross_tenant_access"] == "prohibited"
    assert identity["real_tenant_provisioning"] is False
    assert identity["identity_provider_connected"] is False


def test_support_access_requires_explicit_bounded_controls() -> None:
    support = _contract()["identity_access"]["support_access"]
    assert support == {
        "explicit": True,
        "scoped": True,
        "time_bounded": True,
        "attributable": True,
        "revocable": True,
    }


def test_retention_export_backup_and_withdrawal_architecture_is_present() -> None:
    data = _contract()["data_governance"]
    assert data["retention_policy_required_before_pilot"] is True
    assert data["retention_duration_configuration_required"] is True
    assert data["deletion_triggers_required"] is True
    assert data["export_policy_required_before_pilot"] is True
    assert data["backup_treatment_required"] is True
    assert data["withdrawal_disposition_required_before_pilot"] is True
    assert data["legal_title_claim_made"] is False
    assert len(data["unresolved_legal_or_policy_dependencies"]) == 3


def test_incident_model_is_complete_and_Nova_outage_never_creates_decision() -> None:
    failure = _contract()["failure_incident"]
    assert failure["Nova_failure_creates_decision"] is False
    assert set(failure["prohibited_failure_results"]) == {
        "ALLOW",
        "DENY",
        "HALT",
        "VETO",
    }
    assert failure["cases"]["Nova_unavailable"] == (
        "review_context_unavailable_no_Nova_decision"
    )
    assert len(failure["cases"]) == 11


def test_execution_path_and_production_credentials_are_architecturally_prohibited() -> None:
    integration = _contract()["integration"]
    assert integration["execution_path_through_Nova"] == "prohibited"
    assert integration["execution_credentials_in_Nova"] == "prohibited"
    assert integration["execution_calls_from_Nova"] == "prohibited"
    assert integration["runtime_endpoint_activation"] is False
    assert integration["v2_context_activation"] is False
    assert integration["network_integration_added"] is False


def test_machine_and_human_views_derive_from_one_governed_state() -> None:
    governed = {
        "source_state": "conflicted",
        "context_state": "stale",
        "review_completeness": "partial",
        "authority_effect": "none",
    }
    first = render_human_presentation(governed)
    second = render_human_presentation(dict(reversed(list(governed.items()))))
    assert first == second
    assert validate_human_presentation(governed, first) == []
    assert all(item["source_path"] in governed for item in first)


@pytest.mark.parametrize("marker", PROHIBITED_HUMAN_MEANING)
def test_human_presentation_cannot_add_approval_or_execution_meaning(marker: str) -> None:
    governed = {"authority_effect": "none"}
    statements = render_human_presentation(governed)
    statements[0]["rendered_text"] = marker
    assert validate_human_presentation(governed, statements)


def test_success_metrics_are_context_metrics_with_uninvented_thresholds() -> None:
    measurement = _contract()["measurement"]
    prohibited = set(measurement["prohibited_success_metrics"])
    ids = {metric["metric_id"] for metric in measurement["metrics"]}
    assert not prohibited & ids
    assert len(ids) == 11
    for metric in measurement["metrics"]:
        assert metric["success_threshold"] == "required_pilot_configuration"
        assert metric["falsification_threshold"] == "required_pilot_configuration"
        assert metric["observation_window"] == "required_pilot_configuration"


def test_falsification_conditions_exist_and_stop_advancement() -> None:
    falsification = _contract()["falsification"]
    assert falsification["advancement_on_trigger"] == "prohibited"
    assert len(falsification["conditions"]) == 11
    assert "operators_treat_Nova_as_approval_authority" in falsification["conditions"]
    assert "Nova_requires_execution_credentials" in falsification["conditions"]


def test_withdrawal_preserves_export_revocation_disposition_and_local_continuity() -> None:
    withdrawal = _contract()["withdrawal"]
    assert withdrawal["criteria_required"] is True
    assert withdrawal["active_sessions_revoked"] is True
    assert withdrawal["credentials_and_access_revoked"] is True
    assert withdrawal["integrations_detached"] is True
    assert withdrawal["institution_continuity_without_Nova_required"] is True
    assert withdrawal["Nova_holds_institutional_authority"] is False
    assert "governed_review_context" in withdrawal["export_contents"]


def test_all_termination_states_have_complete_data_disposition_matrix() -> None:
    termination = _contract()["termination"]
    assert set(termination["states"]) == {
        "temporary_suspension",
        "incident_isolation",
        "institution_initiated_withdrawal",
        "Nova_initiated_safety_withdrawal",
        "pilot_completion",
        "pilot_failure",
        "pilot_expiration",
    }
    width = len(termination["matrix_fields"])
    assert width == 7
    assert all(len(behavior) == width for behavior in termination["states"].values())


def test_gate5_and_institutional_pilot_remain_not_started_and_unauthorized() -> None:
    contract = _contract()
    assert contract["status"] == "COMPLETE"
    assert contract["workstream"]["status"] == "COMPLETE"
    assert contract["workstream"]["canonicality_source"] == "authoritative_repository_main"
    assert contract["workstream"]["Gate_5_started"] is False
    assert contract["workstream"]["institutional_pilot_authorized"] is False
    assert contract["institutional_pilot"] == {"authorized": False, "started": False}
    assert contract["Gate_5"] == {"status": "NOT_STARTED", "authority": False}


def test_all_gate5_authorization_preconditions_remain_explicit_and_unevidenced() -> None:
    preconditions = _contract()["Gate_5_authorization_preconditions"]
    assert preconditions["status"] == "NOT_YET_SATISFIED"
    assert preconditions["automatic_authorization_from_Entry_Review_completion"] is False
    assert preconditions["preconditions_not_yet_evidenced"] == 18
    assert preconditions["institution_specific_configuration_requirements"] == 14
    assert preconditions["architectural_constraints"] == 4
    assert preconditions["silently_resolved"] is False
    for category, expected in EXPECTED_PRECONDITIONS.items():
        assert preconditions[category] == expected


@pytest.mark.parametrize(
    ("category", "field"),
    [
        (category, field)
        for category, fields in EXPECTED_PRECONDITIONS.items()
        for field in fields
    ],
)
def test_validator_rejects_disappearing_or_silently_resolved_precondition(
    category: str, field: str
) -> None:
    removed = _contract()
    removed["Gate_5_authorization_preconditions"][category].pop(field)
    assert _errors(removed)
    resolved = _contract()
    resolved["Gate_5_authorization_preconditions"][category][field] = "satisfied"
    assert _errors(resolved)


def test_entry_review_completion_never_automatically_authorizes_gate5() -> None:
    changed = _contract()
    changed["Gate_5_authorization_preconditions"][
        "automatic_authorization_from_Entry_Review_completion"
    ] = True
    changed["Gate_5"]["authority"] = True
    assert _errors(changed)


def test_durable_lifecycle_documents_are_merge_stable() -> None:
    assert validate_durable_lifecycle_documents(_durable_documents()) == []


@pytest.mark.parametrize("marker", STALE_LIFECYCLE_MARKERS)
def test_durable_lifecycle_rejects_stale_premerge_markers(marker: str) -> None:
    documents = _durable_documents()
    documents["CURRENT_STATE.md"] += f"\n{marker}\n"
    assert validate_durable_lifecycle_documents(documents)


def test_PR33_and_unapproved_gate3_semantics_are_absent() -> None:
    contract = _contract()
    assert contract["dependencies"] == {
        "PR_33": "none",
        "unapproved_Gate_3_gaps": [],
        "blocking_dependency": None,
    }
    assert set(contract["canonical_target_contract"]["incorporated_refinements"]) == INCORPORATED
    serialized = json.dumps(contract, sort_keys=True)
    for marker in (
        "authority_scope",
        "treatment_status",
        "applicability_status",
        "applicability_scope",
        "authority_treatment",
        "precedent_treatment",
        "epistemic_status",
        "governed_abstraction",
    ):
        assert marker not in serialized


def test_no_prohibited_implementation_surface_is_enabled() -> None:
    mutations = _contract()["mutation_boundaries"]
    assert mutations
    assert not any(mutations.values())


def test_all_twenty_synthetic_scenarios_validate() -> None:
    fixtures = _fixtures()
    assert validate_fixtures(fixtures) == []
    assert {case["id"] for case in fixtures["scenarios"]} == EXPECTED_SCENARIOS
    assert fixtures["synthetic_only"] is True


@pytest.mark.parametrize(
    ("case_id", "expected_error"),
    [
        ("G5E-007", "cross_tenant_access_prohibited"),
        ("G5E-012", "human_presentation_adds_authority_meaning"),
        ("G5E-013", "execution_path_through_Nova_prohibited"),
        ("G5E-014", "production_credentials_prohibited"),
        ("G5E-018", "PR_33_dependency_prohibited"),
        ("G5E-019", "unapproved_Gate_3_dependency_prohibited"),
        ("G5E-020", "single_action_class_boundary_violated"),
    ],
)
def test_prohibited_synthetic_scenarios_fail_closed(
    case_id: str, expected_error: str
) -> None:
    case = next(case for case in _fixtures()["scenarios"] if case["id"] == case_id)
    assert evaluate_scenario(case) == ("reject", expected_error)


def test_validator_rejects_started_gate_or_pilot() -> None:
    for field in ("Gate_5_started", "institutional_pilot_authorized"):
        changed = _contract()
        changed["workstream"][field] = True
        assert _errors(changed)
    changed = _contract()
    changed["institutional_pilot"]["authorized"] = True
    assert _errors(changed)
    changed = _contract()
    changed["institutional_pilot"]["started"] = True
    assert _errors(changed)


def test_validator_rejects_real_tenant_idp_runtime_and_production_state() -> None:
    mutations = [
        ("workstream", "tenant_created", True),
        ("workstream", "runtime_activated", True),
        ("workstream", "production_active", True),
        ("identity_access", "real_tenant_provisioning", True),
        ("identity_access", "identity_provider_connected", True),
        ("integration", "v2_context_activation", True),
        ("integration", "network_integration_added", True),
    ]
    for section, field, value in mutations:
        changed = _contract()
        changed[section][field] = value
        assert _errors(changed), f"validator accepted {section}.{field}"


def test_validator_rejects_unknown_enabled_production_or_execution_flags() -> None:
    for field in (
        "production_data_added",
        "production_credentials_required",
        "production_crypto_enabled",
        "execution_enabled",
        "settlement_enabled",
        "payment_enabled",
        "x402_enabled",
    ):
        changed = _contract()
        changed[field] = True
        assert _errors(changed), f"validator accepted enabled flag {field}"


def test_validator_rejects_Nova_role_authority() -> None:
    for field in ("approval_authority", "execution_authority"):
        changed = _contract()
        changed["institutional_ownership"]["roles"]["Nova"][field] = True
        assert _errors(changed)


def test_validator_rejects_every_prohibited_mutation_boundary() -> None:
    for field in _contract()["mutation_boundaries"]:
        changed = _contract()
        changed["mutation_boundaries"][field] = True
        assert _errors(changed), f"validator accepted mutation {field}"


def test_validator_rejects_PR33_or_unapproved_gap_dependency() -> None:
    changed = _contract()
    changed["dependencies"]["PR_33"] = "required"
    assert _errors(changed)
    changed = _contract()
    changed["dependencies"]["unapproved_Gate_3_gaps"] = ["G3-R04"]
    assert _errors(changed)


def test_validator_rejects_undefined_data_or_failure_architecture() -> None:
    changed = _contract()
    changed["data_governance"]["retention_policy_required_before_pilot"] = False
    assert _errors(changed)
    changed = _contract()
    changed["failure_incident"]["cases"].pop("security_incident")
    assert _errors(changed)
