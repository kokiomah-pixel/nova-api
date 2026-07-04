from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


SchemaVersion = Literal["1.0"]
PersistenceState = Literal["ephemeral", "retained"]
ValidationStatus = Literal["observed", "validated"]


class ReflexRegistryEntry(BaseModel):
    registry_id: str
    origin: str
    failure_class: str
    activation_condition: str
    behavioral_effect: str
    persistence_state: PersistenceState
    validation_status: ValidationStatus
    review_posture_effect: Optional[
        Literal[
            "baseline_review",
            "constrained_review",
            "elevated_review_attention",
        ]
    ] = None
    review_context_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    public_reason: str


class ReflexProof(BaseModel):
    schema_version: SchemaVersion = "1.0"
    intervention_class: str
    failure_class: str
    review_posture_before_reflex: str
    review_posture_after_reflex: str
    review_context_changed: bool
    authority_effect: Literal["none"] = "none"
    triggered_registry_id: Optional[str] = None
    why_intervention_happened: str


class ReflexMemoryState(BaseModel):
    schema_version: SchemaVersion = "1.0"
    enabled: bool = True
    mode: str = "retained_discipline"
    persistence_state: PersistenceState
    validation_status: ValidationStatus
    registered_entries: list[ReflexRegistryEntry]
    active_registry_id: Optional[str] = None
    triggered: bool = False
    review_context_applied: bool = False
    review_posture_before_reflex: str
    review_posture_after_reflex: str
    authority_effect: Literal["none"] = "none"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    proof: Optional[ReflexProof] = None
