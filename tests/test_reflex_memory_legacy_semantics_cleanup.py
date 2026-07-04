from core.reflex_memory.registry import build_registry
from core.reflex_memory.schema import ReflexMemoryState
from core.reflex_memory.validation import validate_reflex_memory_state


def test_registry_uses_review_posture_not_decision_effects() -> None:
    registry = build_registry("Stress")
    assert registry

    entry = registry[0]
    assert hasattr(entry, "review_posture_effect")
    assert not hasattr(entry, "decision_effect")
    assert entry.review_posture_effect == "elevated_review_attention"
    assert "local authority" in entry.public_reason
    assert "block" not in entry.behavioral_effect.lower()
    assert "veto" not in entry.model_dump_json().lower()


def test_reflex_memory_state_preserves_authority_effect_none() -> None:
    state = ReflexMemoryState(
        persistence_state="retained",
        validation_status="validated",
        registered_entries=build_registry("Stress"),
        active_registry_id="stress_prior_stress_review_attention",
        triggered=True,
        review_context_applied=True,
        review_posture_before_reflex="baseline_review",
        review_posture_after_reflex="elevated_review_attention",
        authority_effect="none",
    )

    validated = validate_reflex_memory_state(state)
    assert validated.authority_effect == "none"
    assert validated.review_posture_after_reflex == "elevated_review_attention"
