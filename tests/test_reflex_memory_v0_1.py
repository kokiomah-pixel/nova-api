import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "reflex_memory"


FORBIDDEN_AUTHORITY_EFFECTS = {
    "approve_action",
    "deny_action",
    "authorize_payment",
    "block_execution",
    "route_transaction",
    "settle_value",
    "sign_transaction",
    "manage_wallet",
    "supervise_agent",
    "perform_compliance_review",
    "perform_audit_reporting",
}


ALLOWED_REVIEW_POSTURE_EFFECTS = {
    "surface_prior_stress",
    "require_source_reconciliation_context",
    "flag_boundary_language_risk",
    "mark_context_as_source_limited",
    "preserve_manual_review_attention",
    "add_chronology_reference",
    "require_proof_reference",
    "highlight_recurring_context_pattern",
}


def load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def test_reflex_memory_candidate_is_not_accepted_memory() -> None:
    candidate = load_fixture("reflex_memory_candidate_source_state_conflict.json")

    assert candidate["status"] == "candidate"
    assert candidate["accepted_at"] is None
    assert candidate["accepted_by"] is None
    assert candidate["review_posture_effect"] in ALLOWED_REVIEW_POSTURE_EFFECTS
    assert "does not approve" in candidate["non_authority_statement"]


def test_accepted_reflex_memory_references_source_chronology() -> None:
    chronology = load_fixture("chronology_event_source_state_conflict.json")
    entry = load_fixture("reflex_memory_entry_source_state_conflict.json")

    assert entry["status"] == "accepted"
    assert chronology["chronology_event_id"] in entry["source_chronology_event_ids"]
    assert entry["accepted_at"] is not None
    assert entry["accepted_by"] is not None
    assert entry["review_posture_effect"] in ALLOWED_REVIEW_POSTURE_EFFECTS


def test_reflex_memory_has_no_authority_effect() -> None:
    entry = load_fixture("reflex_memory_entry_source_state_conflict.json")

    assert entry["authority_effect"] == "none"
    assert entry["review_posture_effect"] not in FORBIDDEN_AUTHORITY_EFFECTS
    assert "does not approve" in entry["non_authority_statement"]
    assert "execute" in entry["non_authority_statement"]


def test_api_context_exposes_reflex_memory_as_review_context_only() -> None:
    context = load_fixture("api_review_context_with_reflex_memory.json")

    assert context["prepared_action"]["execution_status"] == "not_executed"
    assert context["local_authority"]["decision_responsibility"] == "local_authority"
    assert context["local_authority"]["nova_authority"] == "none"

    reflex_context = context["reflex_memory_context"]
    assert reflex_context["present"] is True
    assert reflex_context["version"] == "reflex_memory_v0_1"

    entry = reflex_context["entries"][0]
    assert entry["authority_effect"] == "none"
    assert entry["review_posture_effect"] in ALLOWED_REVIEW_POSTURE_EFFECTS


def test_api_context_preserves_canonical_boundary() -> None:
    context = load_fixture("api_review_context_with_reflex_memory.json")

    assert context["canonical_boundary"] == [
        "Agent prepares action.",
        "Nova structures review context.",
        "Local authority decides.",
        "Nova does not execute.",
    ]


def test_fixture_forbidden_authority_terms_are_only_in_non_authority_statement() -> None:
    context = load_fixture("api_review_context_with_reflex_memory.json")

    statement = context["non_authority_statement"]
    assert "not approval" in statement
    assert "execution" in statement
    assert context["local_authority"]["nova_authority"] == "none"
