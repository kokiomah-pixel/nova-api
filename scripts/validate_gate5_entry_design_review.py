#!/usr/bin/env python3
"""Validate the bounded Gate 5 Entry institutional-exposure design."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = Path("specs/gate5_institutional_exposure_contract_v0_1.json")
FIXTURE_PATH = Path("fixtures/target-v2/gate5-entry/design_cases.json")
REVIEW_PATH = Path("docs/target-v2/gate-5-entry-design-review-v0.1.md")
CONTRACT_PATH = Path("docs/target-v2/institutional-exposure-contract-v0.1.md")
GAP_PATH = Path("specs/review_context_contract_gaps_v0_1.json")
INCORPORATED = {"G3-R01", "G3-R03", "G3-R08", "G3-R11", "G3-Q15"}
EXPECTED_SCENARIOS = {f"G5E-{index:03d}" for index in range(1, 21)}
EXPECTED_REJECTIONS = {
    "G5E-007": "cross_tenant_access_prohibited",
    "G5E-012": "human_presentation_adds_authority_meaning",
    "G5E-013": "execution_path_through_Nova_prohibited",
    "G5E-014": "production_credentials_prohibited",
    "G5E-018": "PR_33_dependency_prohibited",
    "G5E-019": "unapproved_Gate_3_dependency_prohibited",
    "G5E-020": "single_action_class_boundary_violated",
}
CANONICAL_AUTHORITY_HASHES = {
    "docs/architecture/external-review-context-contract-v2.md": "12818bcc0b800b681aec7883c26e80491bd56bcab2d826e691fbe76a90dc1874",
    "specs/review_context_contract_v2.json": "2204b622643f4c88d4112099d66d46a2e4c5e28b4e84ffc70a71eafa32c2e6d9",
    "docs/target-v2/gate-3-field-derivation-ledger-v0.1.md": "36afbea1c0c0d1e1c896095008e2b60208c9c25329e91a89534240498f9a0bcf",
    "specs/review_context_field_derivation_v0_1.json": "0b026284f2d9839e4ca68a52efb5c1e64073129983466ee4b17d16022011bb0a",
    "docs/target-v2/context-proof-canonicalization-v0.1.md": "3565677d0208b4222f3e1031bd7b0653d2ea1063291ef830a1b3c381adb192f0",
}
REQUIRED_DOMAINS = {
    "action_boundary",
    "authority_model",
    "institutional_ownership",
    "review_profile_governance",
    "evidence_boundary",
    "identity_access",
    "data_governance",
    "failure_incident",
    "integration",
    "presentation",
    "measurement",
    "falsification",
    "withdrawal",
    "termination",
    "Gate_5_authorization_preconditions",
}
EXPECTED_PRECONDITIONS = {
    "institutional_configuration": {
        "institution_and_workflow_owner_identified": "required",
        "local_decision_authority_identified": "required",
        "review_profile_owner_identified": "required",
        "external_identity_authority_defined": "required",
    },
    "data_and_legal": {
        "legal_title_and_license_terms_resolved": "required",
        "jurisdiction_specific_retention_duration_defined": "required",
        "backup_deletion_timing_defined": "required",
        "export_and_post_withdrawal_disposition_approved": "required",
    },
    "measurement": {
        "success_thresholds_agreed": "required",
        "falsification_thresholds_agreed": "required",
        "observation_windows_agreed": "required",
    },
    "operations": {
        "support_access_model_approved": "required",
        "incident_and_degradation_process_approved": "required",
        "withdrawal_requesters_and_process_approved": "required",
    },
    "architecture": {
        "one_action_class_only": "required",
        "local_authority_external_to_Nova": "required",
        "execution_path_through_Nova": "prohibited",
        "production_execution_credentials_in_Nova": "prohibited",
    },
}
REQUIRED_FAILURES = {
    "Nova_unavailable",
    "required_source_unavailable",
    "source_conflict",
    "stale_evidence",
    "identity_access_failure",
    "tenant_isolation_concern",
    "context_reconstruction_failure",
    "suspected_integrity_failure",
    "security_incident",
    "export_failure",
    "withdrawal_request",
}
REQUIRED_TERMINATION_STATES = {
    "temporary_suspension",
    "incident_isolation",
    "institution_initiated_withdrawal",
    "Nova_initiated_safety_withdrawal",
    "pilot_completion",
    "pilot_failure",
    "pilot_expiration",
}
REQUIRED_METRIC_FIELDS = {
    "metric_id",
    "definition",
    "measurement_source",
    "numerator_denominator_or_method",
    "success_threshold",
    "falsification_threshold",
    "observation_window",
    "owner",
}
PROHIBITED_HUMAN_MEANING = (
    "nova approved",
    "nova authorized",
    "nova recommends",
    "permission granted",
    "execute this action",
)
UNAPPROVED_SEMANTICS = {
    "authority_scope": "G3-R04",
    "treatment_status": "G3-R10",
    "applicability_status": "G3-R10",
    "applicability_scope": "unapproved_or_undefined",
    "authority_treatment": "PR_33_or_unapproved",
    "precedent_treatment": "PR_33_or_unapproved",
    "epistemic_status": "PR_33_or_unapproved",
    "governed_abstraction": "PR_33",
}
ALLOWED_BRANCH_PATHS = {
    "CURRENT_STATE.md",
    "Makefile",
    "docs/operations/production-readiness-register.md",
    str(REVIEW_PATH),
    str(CONTRACT_PATH),
    str(SPEC_PATH),
    str(FIXTURE_PATH),
    "scripts/validate_gate5_entry_design_review.py",
    "tests/test_gate5_entry_design_review.py",
}
DURABLE_LIFECYCLE_PATHS = (
    "CURRENT_STATE.md",
    "docs/operations/production-readiness-register.md",
    str(REVIEW_PATH),
    str(CONTRACT_PATH),
    str(SPEC_PATH),
)
STALE_LIFECYCLE_MARKERS = (
    "authorized_design_workstream",
    "architecture_reviewable_when_validated",
    "candidate_complete",
    "candidate only",
    "draft branch",
    "not canonical until merge",
)


@dataclass(frozen=True)
class ValidationError:
    location: str
    message: str

    def format(self) -> str:
        return f"{self.location}: {self.message}"


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _require(condition: bool, location: str, message: str) -> list[ValidationError]:
    return [] if condition else [ValidationError(location, message)]


def _reject_enabled_prohibited_flags(value: Any, path: str = "contract") -> list[ValidationError]:
    """Fail closed when an extra flag attempts to activate prohibited scope."""

    errors: list[ValidationError] = []
    prohibited_fragments = (
        "gate_5_started",
        "institutional_pilot_authorized",
        "institution_onboarded",
        "tenant_created",
        "real_tenant",
        "identity_provider_connected",
        "runtime_activated",
        "runtime_endpoint",
        "v2_context",
        "production_active",
        "production_data",
        "production_credential",
        "production_crypto",
        "execution_enabled",
        "execution_call",
        "settlement_enabled",
        "payment_enabled",
        "x402_enabled",
        "chronology_mutation",
        "reflex_memory_mutation",
    )
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            child_path = f"{path}.{key}"
            if child is True and any(fragment in lowered for fragment in prohibited_fragments):
                errors.append(ValidationError(child_path, "prohibited Gate 5 scope enabled"))
            errors.extend(_reject_enabled_prohibited_flags(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_reject_enabled_prohibited_flags(child, f"{path}[{index}]"))
    return errors


def render_human_presentation(governed_state: dict[str, Any]) -> list[dict[str, str]]:
    """Render only declared governed fields; this is design-validation code."""

    declarations = (
        ("source_state", "Source state", "state-v0.1"),
        ("context_state", "Context state", "state-v0.1"),
        ("review_completeness", "Review completeness", "state-v0.1"),
        ("authority_effect", "Nova authority effect", "authority-v0.1"),
    )
    return [
        {
            "statement_id": key,
            "source_path": key,
            "template_id": template,
            "rendered_text": f"{label}: {governed_state[key]}.",
        }
        for key, label, template in declarations
        if key in governed_state
    ]


def validate_human_presentation(
    governed_state: dict[str, Any], statements: list[dict[str, str]]
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if statements != render_human_presentation(governed_state):
        errors.append(ValidationError("presentation", "human view diverges from governed state"))
    for statement in statements:
        rendered = statement.get("rendered_text", "").lower()
        if any(marker in rendered for marker in PROHIBITED_HUMAN_MEANING):
            errors.append(ValidationError("presentation", "human view adds prohibited authority meaning"))
        if statement.get("source_path") not in governed_state:
            errors.append(ValidationError("presentation", "human statement lacks a governed source path"))
    return errors


def evaluate_scenario(case: dict[str, Any]) -> tuple[str, str | None]:
    """Evaluate the twenty design cases without implementing a pilot or runtime."""

    case_id = case.get("id")
    data = case.get("input", {})
    attempt = case.get("attempt", {})
    if case_id == "G5E-001" and (
        data.get("action_class") != "agent_prepared_stablecoin_treasury_action"
        or data.get("action_prepared_externally") is not True
    ):
        return "reject", "single_action_class_boundary_violated"
    if case_id == "G5E-002" and not (
        data.get("local_authority_external_to_Nova") is True
        and data.get("Nova_approval_authority") is False
    ):
        return "reject", "local_authority_boundary_missing"
    if case_id == "G5E-003" and (
        not data.get("revision_attributed_to") or data.get("retroactive_rewrite") is not False
    ):
        return "reject", "profile_revision_governance_missing"
    if case_id == "G5E-004" and (
        len(data.get("variants", [])) < 2 or data.get("Nova_selected_winner") is not False
    ):
        return "reject", "conflict_visibility_missing"
    if case_id == "G5E-005" and data.get("context_state") != "stale":
        return "reject", "stale_state_not_explicit"
    if case_id == "G5E-006" and data.get("authorization_inferred") is not False:
        return "reject", "authentication_inferred_as_authorization"
    if case_id == "G5E-007" and attempt.get("cross_tenant_access") is True:
        return "reject", "cross_tenant_access_prohibited"
    if case_id == "G5E-008" and not all(
        data.get(key) for key in ("scope", "expires_at", "attributable_to", "revocable")
    ):
        return "reject", "support_access_scope_missing"
    if case_id == "G5E-009" and not (
        data.get("context_state") == "unavailable" and data.get("Nova_decision") is None
    ):
        return "reject", "outage_created_domain_decision"
    if case_id == "G5E-010" and data.get("source_state") != "unavailable":
        return "reject", "unavailable_source_not_explicit"
    if case_id == "G5E-011":
        if validate_human_presentation(
            case.get("governed_state", {}), case.get("expected_human_statements", [])
        ):
            return "reject", "machine_human_semantic_divergence"
    if case_id == "G5E-012":
        addition = attempt.get("additional_human_statement", "").lower()
        if any(marker in addition for marker in PROHIBITED_HUMAN_MEANING):
            return "reject", "human_presentation_adds_authority_meaning"
    if case_id == "G5E-013" and (
        attempt.get("execution_call") or attempt.get("Nova_execution_target")
    ):
        return "reject", "execution_path_through_Nova_prohibited"
    if case_id == "G5E-014" and attempt.get("production_credential_required"):
        return "reject", "production_credentials_prohibited"
    if case_id == "G5E-015" and not (
        data.get("export_format") and data.get("includes_audit_manifest") is True
    ):
        return "reject", "export_contract_incomplete"
    if case_id == "G5E-016" and not all(
        data.get(key) is True
        for key in (
            "sessions_revoked",
            "new_context_stopped",
            "export_completed",
            "disposition_policy_applied",
            "integration_detached",
            "institution_can_continue_without_Nova",
        )
    ):
        return "reject", "withdrawal_contract_incomplete"
    if case_id == "G5E-017" and not (
        data.get("advancement_stopped") is True
        and data.get("termination_state") == "pilot_failure"
        and data.get("data_disposition_defined") is True
    ):
        return "reject", "falsification_did_not_stop_advancement"
    if case_id == "G5E-018" and attempt.get("dependency") == "PR_33":
        return "reject", "PR_33_dependency_prohibited"
    if case_id == "G5E-019" and attempt.get("dependency") not in INCORPORATED:
        return "reject", "unapproved_Gate_3_dependency_prohibited"
    if case_id == "G5E-020" and len(attempt.get("action_classes", [])) != 1:
        return "reject", "single_action_class_boundary_violated"
    return "accept", None


def validate_contract(
    contract: dict[str, Any], gap_registry: dict[str, Any]
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    location = str(SPEC_PATH)
    errors.extend(_reject_enabled_prohibited_flags(contract))
    errors += _require(REQUIRED_DOMAINS <= contract.keys(), location, "institutional domains missing")
    errors += _require(contract.get("schema_version") == "0.1", location, "schema version must be 0.1")
    errors += _require(contract.get("status") == "COMPLETE", location, "Entry Design Review status must be COMPLETE")
    errors += _require(contract.get("scope") == "institutional_exposure_contract_only", location, "Entry Design Review scope changed")
    errors += _require(contract.get("canonicality_source") == "authoritative_repository_main", location, "merge-stable canonicality source missing")
    canonical = contract.get("canonical_target_contract", {})
    errors += _require(canonical.get("version") == "design-v2.1", location, "canonical contract changed")
    errors += _require(set(canonical.get("incorporated_refinements", [])) == INCORPORATED, location, "incorporated set changed")
    errors += _require(canonical.get("unapproved_refinements_used") == [], location, "unapproved refinement used")
    workstream = contract.get("workstream", {})
    errors += _require(
        workstream.get("status") == "COMPLETE"
        and workstream.get("artifact") == "institutional_exposure_contract_v0.1"
        and workstream.get("canonicality_source") == "authoritative_repository_main",
        location,
        "durable Entry Design Review lifecycle is incomplete",
    )
    for key in ("Gate_5_started", "institutional_pilot_authorized", "institution_onboarded", "tenant_created", "runtime_activated", "production_active"):
        errors += _require(workstream.get(key) is False, f"{location}.workstream.{key}", "must remain false")
    errors += _require(
        contract.get("institutional_pilot") == {"authorized": False, "started": False},
        location,
        "institutional pilot must remain unauthorized and not started",
    )
    preconditions = contract.get("Gate_5_authorization_preconditions", {})
    errors += _require(
        preconditions.get("status") == "NOT_YET_SATISFIED",
        location,
        "Gate 5 authorization preconditions must remain not yet satisfied",
    )
    errors += _require(
        preconditions.get("automatic_authorization_from_Entry_Review_completion") is False,
        location,
        "Entry Review completion must not automatically authorize Gate 5",
    )
    errors += _require(
        preconditions.get("preconditions_not_yet_evidenced") == 18
        and preconditions.get("institution_specific_configuration_requirements") == 14
        and preconditions.get("architectural_constraints") == 4
        and preconditions.get("silently_resolved") is False,
        location,
        "Gate 5 precondition counts or unresolved state changed",
    )
    for category, expected in EXPECTED_PRECONDITIONS.items():
        errors += _require(
            preconditions.get(category) == expected,
            f"{location}.Gate_5_authorization_preconditions.{category}",
            "required authorization precondition disappeared or was silently resolved",
        )
    action = contract.get("action_boundary", {})
    errors += _require(action.get("permitted_action_classes") == ["agent_prepared_stablecoin_treasury_action"], location, "exactly one bounded action class required")
    errors += _require(action.get("multiple_action_classes_permitted") is False, location, "multiple action classes prohibited")
    errors += _require(action.get("action_prepared_externally") is True and action.get("Nova_prepares_action") is False and action.get("Nova_executes_action") is False, location, "prepared-action boundary invalid")
    authority = contract.get("authority_model", {})
    errors += _require(authority.get("Nova_authority_effect") == "none" and authority.get("Nova_execution_effect") == "none" and authority.get("local_authority_external_to_Nova") is True, location, "authority boundary invalid")
    owners = contract.get("institutional_ownership", {})
    for key in ("workflow_owner_required", "local_authority_required", "review_profile_owner_required"):
        errors += _require(owners.get(key) is True, location, f"{key} must be true")
    nova_role = owners.get("roles", {}).get("Nova", {})
    errors += _require(
        nova_role.get("approval_authority") is False
        and nova_role.get("execution_authority") is False,
        location,
        "Nova role acquired institutional authority",
    )
    profile = contract.get("review_profile_governance", {})
    errors += _require(set(profile.get("lifecycle_authorities", {})) == {"author", "approve", "version", "activate", "replace", "retire"}, location, "profile lifecycle authority incomplete")
    errors += _require(profile.get("Nova_may_invent_institutional_requirements") is False and profile.get("retroactive_rewrite_of_prior_context") is False, location, "profile boundary invalid")
    evidence = contract.get("evidence_boundary", {})
    errors += _require(set(evidence.get("state_dimensions", [])) == {"source_state", "context_state", "review_completeness"}, location, "Gate 3 state separation missing")
    source_model = evidence.get("source_authority_model", {})
    errors += _require(source_model.get("new_target_v2_semantic_field") is False and source_model.get("global_source_ranking") is False and source_model.get("Nova_selected_winner") is False, location, "source authority overreaches canonical semantics")
    identity = contract.get("identity_access", {})
    errors += _require(identity.get("real_tenant_provisioning") is False and identity.get("identity_provider_connected") is False, location, "real identity infrastructure prohibited")
    errors += _require(identity.get("cross_tenant_access") == "prohibited" and identity.get("authentication_equals_workflow_authorization") is False, location, "identity boundary invalid")
    data = contract.get("data_governance", {})
    for key in ("retention_policy_required_before_pilot", "export_policy_required_before_pilot", "withdrawal_disposition_required_before_pilot", "backup_treatment_required"):
        errors += _require(data.get(key) is True, location, f"{key} must be defined")
    failures = contract.get("failure_incident", {})
    errors += _require(REQUIRED_FAILURES <= failures.get("cases", {}).keys(), location, "failure/incident cases incomplete")
    errors += _require(failures.get("Nova_failure_creates_decision") is False and set(failures.get("prohibited_failure_results", [])) == {"ALLOW", "DENY", "HALT", "VETO"}, location, "failure creates authority")
    integration = contract.get("integration", {})
    errors += _require(integration.get("execution_path_through_Nova") == "prohibited" and integration.get("execution_credentials_in_Nova") == "prohibited" and integration.get("execution_calls_from_Nova") == "prohibited", location, "no-execution architecture missing")
    errors += _require(integration.get("runtime_endpoint_activation") is False and integration.get("v2_context_activation") is False and integration.get("network_integration_added") is False, location, "runtime or network activation prohibited")
    presentation = contract.get("presentation", {})
    errors += _require(presentation.get("single_governed_state") is True and presentation.get("machine_human_semantic_parity_required") is True and presentation.get("hidden_human_judgment_layer") is False, location, "presentation parity boundary invalid")
    measurement = contract.get("measurement", {})
    metric_ids: set[str] = set()
    for index, metric in enumerate(measurement.get("metrics", [])):
        errors += _require(REQUIRED_METRIC_FIELDS <= metric.keys(), f"{location}.measurement.metrics[{index}]", "metric contract fields missing")
        errors += _require(metric.get("success_threshold") == "required_pilot_configuration" and metric.get("falsification_threshold") == "required_pilot_configuration", f"{location}.measurement.metrics[{index}]", "threshold must remain required pilot configuration")
        metric_ids.add(metric.get("metric_id", ""))
    errors += _require(len(metric_ids) == 11, location, "required measurement inventory incomplete")
    errors += _require(REQUIRED_TERMINATION_STATES == contract.get("termination", {}).get("states", {}).keys(), location, "termination state inventory incomplete")
    matrix_width = len(contract.get("termination", {}).get("matrix_fields", []))
    for state, behavior in contract.get("termination", {}).get("states", {}).items():
        errors += _require(len(behavior) == matrix_width, f"{location}.termination.{state}", "termination matrix incomplete")
    dependencies = contract.get("dependencies", {})
    errors += _require(dependencies == {"PR_33": "none", "unapproved_Gate_3_gaps": [], "blocking_dependency": None}, location, "dependency boundary changed")
    mutations = contract.get("mutation_boundaries", {})
    errors += _require(mutations and not any(mutations.values()), location, "prohibited implementation mutation enabled")
    errors += _require(contract.get("Gate_5") == {"status": "NOT_STARTED", "authority": False}, location, "Gate 5 must remain not started and unauthorized")

    approved_from_registry = {
        item["id"]
        for item in gap_registry.get("contract_refinements", [])
        if item.get("canonical_contract_status") == "incorporated_in_design_v2.1_contract"
    }
    errors += _require(approved_from_registry == INCORPORATED, str(GAP_PATH), "canonical incorporated gap inventory changed")

    serialized = json.dumps(contract, sort_keys=True)
    for semantic, gap in UNAPPROVED_SEMANTICS.items():
        if semantic in serialized:
            errors.append(ValidationError(location, f"unapproved semantic dependency {semantic} ({gap})"))
    return errors


def validate_fixtures(fixtures: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    location = str(FIXTURE_PATH)
    errors += _require(fixtures.get("synthetic_only") is True, location, "fixtures must be synthetic only")
    scenarios = fixtures.get("scenarios", [])
    by_id = {case.get("id"): case for case in scenarios}
    errors += _require(set(by_id) == EXPECTED_SCENARIOS and len(scenarios) == 20, location, "G5E-001 through G5E-020 required exactly once")
    for case_id, case in by_id.items():
        actual, error = evaluate_scenario(case)
        expected = case.get("expected")
        errors += _require(actual == expected, f"{location}.{case_id}", f"expected {expected}, got {actual}")
        expected_error = EXPECTED_REJECTIONS.get(case_id)
        errors += _require(error == expected_error, f"{location}.{case_id}", f"expected error {expected_error!r}, got {error!r}")
        if expected == "reject":
            errors += _require(case.get("error") == expected_error, f"{location}.{case_id}", "fixture rejection label mismatch")
    return errors


def validate_durable_lifecycle_documents(documents: dict[str, str]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required = {
        str(REVIEW_PATH): ("status: COMPLETE", "canonicality_source: authoritative_repository_main", "Gate_5_authorization_preconditions:", "preconditions_not_yet_evidenced: 18", "PR_33_dependency: none", "unapproved_Gate_3_gaps: []"),
        str(CONTRACT_PATH): ("Entry_Design_Review_status: COMPLETE", "canonicality_source: authoritative_repository_main", "Gate_5_authorization_preconditions:", "preconditions_not_yet_evidenced: 18", "Exactly one action class", "Authentication is not workflow authorization", "Nova does not select", "template only"),
        "CURRENT_STATE.md": ("Gate_5_Entry_Design_Review:", "status: COMPLETE", "canonicality_source: authoritative_repository_main", "Gate_5_authorization_preconditions:", "preconditions_not_yet_evidenced: 18", "Gate_5_bounded_institutional_pilot:", "status: NOT_STARTED", "authorized: false", "started: false"),
        "docs/operations/production-readiness-register.md": ("Gate_5_Entry_Design_Review:", "status: COMPLETE", "canonicality_source: authoritative_repository_main", "Gate_5_authorization_preconditions:", "preconditions_not_yet_evidenced: 18", "Gate_5:", "status: NOT_STARTED", "authorized: false", "started: false"),
        str(SPEC_PATH): ('"status": "COMPLETE"', '"canonicality_source": "authoritative_repository_main"', '"Gate_5_authorization_preconditions"', '"preconditions_not_yet_evidenced": 18', '"status": "NOT_STARTED"', '"authorized": false', '"started": false'),
    }
    for path, markers in required.items():
        text = documents.get(path, "")
        for marker in markers:
            errors += _require(marker in text, path, f"required marker missing: {marker}")
    for path in DURABLE_LIFECYCLE_PATHS:
        text = documents.get(path, "")
        lowered = text.lower()
        for marker in STALE_LIFECYCLE_MARKERS:
            if marker.lower() in lowered:
                errors.append(ValidationError(path, f"stale pre-merge lifecycle marker: {marker}"))
    return errors


def validate_documents(root: Path) -> list[ValidationError]:
    documents = {
        path: (root / path).read_text(encoding="utf-8") if (root / path).exists() else ""
        for path in DURABLE_LIFECYCLE_PATHS
    }
    return validate_durable_lifecycle_documents(documents)


def validate_canonical_authorities(root: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for relative, expected in CANONICAL_AUTHORITY_HASHES.items():
        path = root / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
        errors += _require(actual == expected, relative, "canonical design-v2.1 semantic authority changed")
    return errors


def validate_repository(root: Path = REPO_ROOT) -> list[ValidationError]:
    root = root.resolve()
    errors: list[ValidationError] = []
    try:
        contract = _load_json(root, SPEC_PATH)
        fixtures = _load_json(root, FIXTURE_PATH)
        gaps = _load_json(root, GAP_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        return [ValidationError("repository", f"cannot load Gate 5 design inputs: {exc}")]
    errors.extend(validate_contract(contract, gaps))
    errors.extend(validate_fixtures(fixtures))
    errors.extend(validate_documents(root))
    errors.extend(validate_canonical_authorities(root))
    return errors


def validate_branch_delta(base_ref: str, root: Path = REPO_ROOT) -> list[ValidationError]:
    """Optional local completion evidence; default CI validation needs no history."""

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return [ValidationError("git", f"cannot inspect branch delta from {base_ref}: {result.stderr.strip()}")]
    return [
        ValidationError(path, "file is outside the Gate 5 Entry design allowlist")
        for path in result.stdout.splitlines()
        if path and path not in ALLOWED_BRANCH_PATHS
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", help="also validate local branch file scope")
    args = parser.parse_args()
    errors = validate_repository()
    if args.base_ref:
        errors.extend(validate_branch_delta(args.base_ref))
    if errors:
        for error in errors:
            print(f"FAIL: {error.format()}")
        return 1
    print("PASS: Gate 5 Entry institutional-exposure design is bounded and complete")
    if args.base_ref:
        print(f"PASS: branch delta from {args.base_ref} is design-only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
