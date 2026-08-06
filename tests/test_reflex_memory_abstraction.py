from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

import pytest

from scripts.validate_reflex_memory_abstraction import (
    FIXTURE_DIR,
    V0_1_FIXTURES,
    _boundary_errors,
    _changed_paths,
    _validate_v0_1_compatibility,
    load_json,
    validate_candidate,
    validate_candidate_to_entry,
    validate_entry,
    validate_entry_to_retrieval,
    validate_lineage_registry,
    validate_retrieval,
    validate_runtime_activation_claim,
)


ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict[str, Any]:
    return load_json(FIXTURE_DIR / name)


def assert_fails(errors: list[str], field: str) -> None:
    assert errors
    assert any(field in error for error in errors), errors


@pytest.mark.parametrize(
    ("fixture_name", "validator"),
    [
        ("reflex_memory_candidate_implicit_policy_conversion.json", validate_candidate),
        ("reflex_memory_candidate_exception_only.json", validate_candidate),
        ("reflex_memory_candidate_governed_abstraction_accepted.json", validate_candidate),
        ("reflex_memory_entry_governed_abstraction_v0_2.json", validate_entry),
        ("reflex_memory_entry_exception_only_v0_2.json", validate_entry),
        ("reflex_memory_retrieval_comparison_limits.json", validate_retrieval),
    ],
)
def test_versioned_fixtures_pass(
    fixture_name: str,
    validator: Callable[[dict[str, Any]], list[str]],
) -> None:
    assert validator(fixture(fixture_name)) == []


def test_existing_v0_1_fixtures_still_pass() -> None:
    assert len(V0_1_FIXTURES) == 6
    assert _validate_v0_1_compatibility() == []


def test_disputed_accepted_memory_can_exist_when_dispute_is_preserved() -> None:
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    entry["epistemic_status"] = "disputed"
    entry["contradictory_cases"] = ["synthetic_counter_case"]
    entry["unresolved_conditions"] = ["dispute_requires_future_review"]
    assert validate_entry(entry) == []


def test_reference_only_candidate_passes() -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    assert candidate["authority_treatment"] == "reference_only"
    assert validate_candidate(candidate) == []


def test_materially_distinguishable_prior_case_passes() -> None:
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    retrieval["precedent_treatment"] = "materially_distinguishable"
    assert validate_retrieval(retrieval) == []


def test_governed_abstraction_candidate_to_entry_chain_passes() -> None:
    candidate = fixture("reflex_memory_candidate_governed_abstraction_accepted.json")
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    assert validate_candidate_to_entry(candidate, entry) == []


def test_exception_candidate_entry_retrieval_chain_passes() -> None:
    candidate = fixture("reflex_memory_candidate_exception_only.json")
    entry = fixture("reflex_memory_entry_exception_only_v0_2.json")
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    assert validate_candidate_to_entry(candidate, entry) == []
    assert validate_entry_to_retrieval(entry, retrieval) == []


def lineage_objects() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = [
        fixture("reflex_memory_candidate_governed_abstraction_accepted.json"),
        fixture("reflex_memory_candidate_exception_only.json"),
    ]
    entries = [
        fixture("reflex_memory_entry_governed_abstraction_v0_2.json"),
        fixture("reflex_memory_entry_exception_only_v0_2.json"),
    ]
    retrievals = [fixture("reflex_memory_retrieval_comparison_limits.json")]
    return candidates, entries, retrievals


def test_accepted_entry_with_unknown_candidate_fails() -> None:
    candidates, entries, retrievals = lineage_objects()
    entries[0]["source_candidate_id"] = "RMC-9999"
    assert_fails(validate_lineage_registry(candidates, entries, retrievals), "unknown candidate")


def test_candidate_converted_entry_id_mismatch_fails() -> None:
    candidate = fixture("reflex_memory_candidate_governed_abstraction_accepted.json")
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    candidate["converted_entry_id"] = "RM-9999"
    assert_fails(validate_candidate_to_entry(candidate, entry), "converted_entry_id")


def test_candidate_entry_chronology_mismatch_fails() -> None:
    candidate = fixture("reflex_memory_candidate_governed_abstraction_accepted.json")
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    candidate["source_chronology_event_ids"] = ["CHR-2026-08-06-999"]
    assert_fails(validate_candidate_to_entry(candidate, entry), "source_chronology_event_ids")


def test_candidate_entry_authority_treatment_mismatch_fails() -> None:
    candidate = fixture("reflex_memory_candidate_governed_abstraction_accepted.json")
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    candidate["authority_treatment"] = "reference_only"
    assert_fails(validate_candidate_to_entry(candidate, entry), "authority_treatment")


def test_candidate_entry_acceptance_timestamp_mismatch_fails() -> None:
    candidate = fixture("reflex_memory_candidate_governed_abstraction_accepted.json")
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    candidate["accepted_at"] = "2026-08-06T16:21:00Z"
    assert_fails(validate_candidate_to_entry(candidate, entry), "accepted_at")


def test_retrieval_with_unknown_reflex_id_fails() -> None:
    candidates, entries, retrievals = lineage_objects()
    retrievals[0]["reflex_id"] = "RM-9999"
    assert_fails(validate_lineage_registry(candidates, entries, retrievals), "unknown Reflex Memory entry")


def retrieval_mismatch_errors(field: str, value: Any) -> list[str]:
    entry = fixture("reflex_memory_entry_exception_only_v0_2.json")
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    retrieval[field] = value
    return validate_entry_to_retrieval(entry, retrieval)


def test_retrieval_chronology_not_in_entry_lineage_fails() -> None:
    errors = retrieval_mismatch_errors(
        "source_chronology_event_ids",
        ["CHR-2026-08-06-999"],
    )
    assert_fails(errors, "source_chronology_event_ids")


def test_retrieval_authority_treatment_mismatch_fails() -> None:
    assert_fails(
        retrieval_mismatch_errors("authority_treatment", "reference_only"),
        "authority_treatment",
    )


def test_retrieval_precedent_treatment_mismatch_fails() -> None:
    assert_fails(
        retrieval_mismatch_errors("precedent_treatment", "none"),
        "precedent_treatment",
    )


@pytest.mark.parametrize(
    ("field", "validator", "fixture_name"),
    [
        ("source_chronology_event_ids", validate_candidate, "reflex_memory_candidate_implicit_policy_conversion.json"),
        ("supporting_evidence_refs", validate_candidate, "reflex_memory_candidate_implicit_policy_conversion.json"),
        ("applicability_conditions", validate_candidate, "reflex_memory_candidate_implicit_policy_conversion.json"),
    ],
)
def test_required_candidate_lineage_fails_when_empty(
    field: str,
    validator: Callable[[dict[str, Any]], list[str]],
    fixture_name: str,
) -> None:
    candidate = fixture(fixture_name)
    candidate[field] = []
    assert_fails(validator(candidate), field)


def test_undeclared_property_fails() -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    candidate["undeclared"] = True
    assert_fails(validate_candidate(candidate), "undeclared")


@pytest.mark.parametrize("field", ["reviewed_by", "accepted_by", "converted_entry_id"])
def test_accepted_candidate_without_acceptance_evidence_fails(field: str) -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    candidate.update(
        lifecycle_status="accepted",
        reviewed_by="synthetic_reviewer",
        reviewed_at="2026-08-06T16:00:00Z",
        accepted_by="synthetic_accepter",
        accepted_at="2026-08-06T16:10:00Z",
        converted_entry_id="RM-0300",
    )
    candidate[field] = None
    assert_fails(validate_candidate(candidate), field)


def test_exception_only_without_known_exception_fails() -> None:
    candidate = fixture("reflex_memory_candidate_exception_only.json")
    candidate["known_exceptions"] = []
    assert_fails(validate_candidate(candidate), "known_exceptions")


def test_exception_generalized_into_future_permission_fails() -> None:
    candidate = fixture("reflex_memory_candidate_exception_only.json")
    candidate["proposed_lesson"] = "Future actions may proceed when the source is unavailable."
    assert_fails(validate_candidate(candidate), "future permission")


def test_disputed_without_contradictory_case_fails() -> None:
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    entry["epistemic_status"] = "disputed"
    entry["contradictory_cases"] = []
    assert_fails(validate_entry(entry), "contradictory_cases")


def test_contradicted_presented_as_universal_truth_fails() -> None:
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    entry["epistemic_status"] = "contradicted"
    entry["contradictory_cases"] = ["synthetic_counter_case"]
    entry["boundary_risk"] = "The lesson is universally established."
    assert_fails(validate_entry(entry), "universal")


def test_formal_adoption_without_acceptance_evidence_fails() -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    candidate["authority_treatment"] = "formally_adopted_by_local_authority"
    candidate["accepted_by"] = None
    candidate["accepted_at"] = None
    assert_fails(validate_candidate(candidate), "formal adoption")


def test_superseded_without_superseded_by_fails() -> None:
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    entry["epistemic_status"] = "superseded"
    entry["superseded_by"] = None
    assert_fails(validate_entry(entry), "superseded_by")


def test_authority_effect_not_none_fails() -> None:
    entry = fixture("reflex_memory_entry_governed_abstraction_v0_2.json")
    entry["authority_effect"] = "approve"
    assert_fails(validate_entry(entry), "authority_effect")


def test_precedent_effect_not_none_fails() -> None:
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    retrieval["precedent_effect"] = "binding"
    assert_fails(validate_retrieval(retrieval), "precedent_effect")


@pytest.mark.parametrize(
    "field",
    [
        "binding_precedent",
        "approve",
        "deny",
        "execute",
        "automatic_policy_update",
        "automatic_constraint_update",
        "automatic_learning",
    ],
)
def test_authority_or_automatic_fields_fail(field: str) -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    candidate[field] = True
    assert_fails(validate_candidate(candidate), field)


def test_retrieval_without_comparison_limits_fails() -> None:
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    retrieval["comparison_limits"] = []
    assert_fails(validate_retrieval(retrieval), "comparison_limits")


def test_retrieval_with_approval_recommendation_fails() -> None:
    retrieval = fixture("reflex_memory_retrieval_comparison_limits.json")
    retrieval["surfaced_because"] = ["recommend approval"]
    assert_fails(validate_retrieval(retrieval), "approval recommendation")


def test_candidate_misrepresented_as_active_memory_fails() -> None:
    candidate = fixture("reflex_memory_candidate_implicit_policy_conversion.json")
    candidate["active_reflex_memory_entry"] = True
    assert_fails(validate_candidate(candidate), "active_reflex_memory_entry")


def test_v0_2_runtime_activation_claim_fails() -> None:
    errors = validate_runtime_activation_claim("Reflex Memory v0.2 is active in production runtime.")
    assert_fails(errors, "runtime activation")


def test_missing_review_base_fails() -> None:
    _, errors = _changed_paths(review_base="refs/heads/definitely-missing-review-base")
    assert_fails(errors, "repository-boundary comparison failed")


def test_git_diff_command_failure_fails() -> None:
    def runner(args: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 2, stdout="", stderr="synthetic git failure")

    _, errors = _changed_paths(review_base="synthetic-base", runner=runner)
    assert_fails(errors, "returncode=2")
    assert_fails(errors, "synthetic git failure")


def boundary_runner(path: str) -> Callable[..., subprocess.CompletedProcess[str]]:
    def runner(args: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        if args[1] == "diff":
            return subprocess.CompletedProcess(args, 0, stdout=f"{path}\n", stderr="")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    return runner


def test_runtime_path_in_diff_fails() -> None:
    errors = _boundary_errors(
        review_base="synthetic-base",
        runner=boundary_runner("core/reflex_memory/new_runtime.py"),
    )
    assert_fails(errors, "runtime change detected")


def test_accepted_state_path_in_diff_fails() -> None:
    errors = _boundary_errors(
        review_base="synthetic-base",
        runner=boundary_runner("state/accepted-state/registry.json"),
    )
    assert_fails(errors, "accepted-state change detected")


def test_chronology_event_path_in_diff_fails() -> None:
    errors = _boundary_errors(
        review_base="synthetic-base",
        runner=boundary_runner("chronology/events/CHR-2026-08-06-999.json"),
    )
    assert_fails(errors, "chronology event change detected")


def test_empty_git_diff_with_identical_refs_is_permitted() -> None:
    paths, errors = _changed_paths(review_base="synthetic-base", runner=boundary_runner(""))
    assert paths == []
    assert errors == []


def test_ci_has_independent_reflex_abstraction_job() -> None:
    workflow = (ROOT / ".github/workflows/doctrine-lint.yml").read_text(encoding="utf-8")
    assert "  reflex_abstraction:\n" in workflow
    assert "fetch-depth: 0" in workflow
    assert "NOVA_REVIEW_BASE=${review_base}" in workflow
    assert "run: make verify-reflex-abstraction" in workflow


def test_ci_aggregate_gate_requires_reflex_abstraction() -> None:
    workflow = (ROOT / ".github/workflows/doctrine-lint.yml").read_text(encoding="utf-8")
    assert "      - reflex_abstraction\n" in workflow
    assert 'reflex_abstraction="${{ needs.reflex_abstraction.result }}"' in workflow
    assert '[ "${reflex_abstraction}" != "success" ]' in workflow


def test_repository_fixtures_are_not_rewritten_by_tests() -> None:
    paths = [FIXTURE_DIR / name for name in (
        "reflex_memory_candidate_implicit_policy_conversion.json",
        "reflex_memory_candidate_exception_only.json",
        "reflex_memory_candidate_governed_abstraction_accepted.json",
        "reflex_memory_entry_governed_abstraction_v0_2.json",
        "reflex_memory_entry_exception_only_v0_2.json",
        "reflex_memory_retrieval_comparison_limits.json",
    )]
    before = {path: path.read_bytes() for path in paths}
    for path in paths:
        json.loads(copy.deepcopy(path.read_text(encoding="utf-8")))
    after = {path: path.read_bytes() for path in paths}
    assert after == before
