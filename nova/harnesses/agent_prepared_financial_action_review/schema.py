from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


AuthorityProximity = Literal["low", "medium", "high"]
ConfirmationStatus = Literal["complete", "incomplete", "unknown"]
SettlementContext = Literal["normal", "degraded", "unknown"]
ReviewStatus = Literal["normal_review", "constrained_review", "escalation_review"]


_AUTHORITY_PROXIMITIES = {"low", "medium", "high"}
_CONFIRMATION_STATUSES = {"complete", "incomplete", "unknown"}
_SETTLEMENT_CONTEXTS = {"normal", "degraded", "unknown"}


@dataclass(frozen=True)
class AgentPreparedFinancialAction:
    action_id: str
    agent_id: str
    action_type: str
    materiality: str
    route_confirmed: bool
    confirmation_status: ConfirmationStatus
    retry_count: int
    same_route_retry: bool
    liquidity_source_age_minutes: int
    expected_source_freshness_minutes: int
    settlement_context: SettlementContext
    source_conflict: bool
    source_conflict_description: str | None
    venue_condition_summary: str | None
    authority_proximity: AuthorityProximity
    local_authority_context: str

    def __post_init__(self) -> None:
        if self.authority_proximity not in _AUTHORITY_PROXIMITIES:
            raise ValueError(f"Invalid authority_proximity: {self.authority_proximity}")
        if self.confirmation_status not in _CONFIRMATION_STATUSES:
            raise ValueError(f"Invalid confirmation_status: {self.confirmation_status}")
        if self.settlement_context not in _SETTLEMENT_CONTEXTS:
            raise ValueError(f"Invalid settlement_context: {self.settlement_context}")
        if self.retry_count < 0:
            raise ValueError("retry_count must be greater than or equal to 0")
        if self.liquidity_source_age_minutes < 0:
            raise ValueError(
                "liquidity_source_age_minutes must be greater than or equal to 0"
            )
        if self.expected_source_freshness_minutes < 0:
            raise ValueError(
                "expected_source_freshness_minutes must be greater than or equal to 0"
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentPreparedFinancialAction":
        return cls(**data)


@dataclass(frozen=True)
class ReviewOutput:
    action_id: str
    review_status: ReviewStatus
    reason_codes: list[str]
    nova_surface_summary: list[str]
    boundary_log: dict[str, bool]
    local_authority_required: bool
    governance_record_candidate: bool
    reflex_memory_candidate: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "review_status": self.review_status,
            "reason_codes": self.reason_codes,
            "nova_surface_summary": self.nova_surface_summary,
            "boundary_log": self.boundary_log,
            "local_authority_required": self.local_authority_required,
            "governance_record_candidate": self.governance_record_candidate,
            "reflex_memory_candidate": self.reflex_memory_candidate,
        }

