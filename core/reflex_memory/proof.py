from __future__ import annotations

from typing import Optional

from .schema import ReflexProof, ReflexRegistryEntry


def build_reflex_proof(
    *,
    entry: Optional[ReflexRegistryEntry],
    review_posture_before_reflex: str,
    review_posture_after_reflex: str,
) -> Optional[ReflexProof]:
    if entry is None:
        return None

    return ReflexProof(
        intervention_class="review_context_conditioning",
        failure_class=entry.failure_class,
        review_posture_before_reflex=review_posture_before_reflex,
        review_posture_after_reflex=review_posture_after_reflex,
        review_context_changed=review_posture_before_reflex != review_posture_after_reflex,
        authority_effect="none",
        triggered_registry_id=entry.registry_id,
        why_intervention_happened=entry.public_reason,
    )
