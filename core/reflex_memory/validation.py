from __future__ import annotations

from .schema import ReflexMemoryState


ALLOWED_REVIEW_POSTURES = {
    "baseline_review",
    "constrained_review",
    "elevated_review_attention",
}


def validate_reflex_memory_state(state: ReflexMemoryState) -> ReflexMemoryState:
    if state.proof and not state.triggered:
        raise ValueError("Reflex proof cannot exist without a triggered review-context state.")
    if state.review_context_applied and not state.triggered:
        raise ValueError("Reflex review context cannot be applied when no registry entry triggered.")
    if state.review_posture_after_reflex not in ALLOWED_REVIEW_POSTURES:
        raise ValueError("Unexpected review_posture_after_reflex value.")
    if state.authority_effect != "none":
        raise ValueError("Reflex Memory authority_effect must remain none.")
    if state.proof and state.proof.authority_effect != "none":
        raise ValueError("Reflex Memory proof authority_effect must remain none.")
    return state
