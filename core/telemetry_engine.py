from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any, Deque, Dict, List, Optional


# Internal only. This module captures derivative decision-environment posture
# without exposing raw requests, actors, Reflex Memory internals, or causality.

ALLOW_STATUSES = {"ALLOW"}
CONSTRAIN_STATUSES = {"CONSTRAIN", "REDUCE", "DELAY", "RETRY_DELAYED"}
DENY_STATUSES = {"DENY", "VETO", "HALT", "RETRY_BLOCKED", "PRESSURE_ESCALATED"}

STATUS_WEIGHTS = {
    "ALLOW": 0.0,
    "CONSTRAIN": 0.55,
    "REDUCE": 0.58,
    "DELAY": 0.62,
    "RETRY_DELAYED": 0.66,
    "RETRY_BLOCKED": 0.82,
    "PRESSURE_ESCALATED": 0.9,
    "DENY": 0.88,
    "VETO": 0.95,
    "HALT": 1.0,
}

SYSTEM_STATE_WEIGHTS = {
    "NORMAL": 0.0,
    "CONSTRAINED_OPERATION": 0.45,
    "RECOVERY_REVIEW_REQUIRED": 0.52,
    "PRESSURE_ELEVATED": 0.7,
    "TELEMETRY_DEGRADED": 0.8,
    "HALT_RECOMMENDED": 0.9,
    "HALT_ACTIVE": 1.0,
}


@dataclass(frozen=True)
class InternalTelemetryRecord:
    timestamp: str
    decision_status: str
    system_state: str
    constraint_triggered: bool
    environment_epoch: Any
    decision_divergence_score: float
    admissibility_delta: float
    constraint_weight: float
    execution_posture: str
    constraint_category: Optional[str]
    environment_posture: str
    loop_pressure_score: float
    telemetry_integrity_state: str
    temporal_constraint_triggered: bool
    cross_source_disagreement: bool


def _round_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 3)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalized_status(value: Any) -> str:
    return str(value or "").strip().upper() or "UNKNOWN"


def _normalized_state(value: Any) -> str:
    return str(value or "").strip().upper() or "NORMAL"


def _constraint_category(payload: Dict[str, Any]) -> Optional[str]:
    trace = payload.get("constraint_trace")
    if isinstance(trace, dict) and trace.get("constraint_category"):
        return str(trace["constraint_category"])

    analysis = payload.get("constraint_analysis")
    if isinstance(analysis, dict) and analysis.get("constraint_category"):
        return str(analysis["constraint_category"])

    return None


def _environment_posture(system_state: str, status: str) -> str:
    if system_state in {"HALT_ACTIVE", "HALT_RECOMMENDED", "TELEMETRY_DEGRADED"}:
        return "DEFENSIVE"
    if system_state == "PRESSURE_ELEVATED" or status == "PRESSURE_ESCALATED":
        return "ESCALATING"
    if system_state == "RECOVERY_REVIEW_REQUIRED":
        return "RECOVERING"
    if system_state == "CONSTRAINED_OPERATION" or status in CONSTRAIN_STATUSES:
        return "CONSTRAINED"
    return "QUIET"


def _execution_posture(status: str, system_state: str) -> str:
    if status in ALLOW_STATUSES and system_state == "NORMAL":
        return "normal"
    if status in {"DELAY", "RETRY_DELAYED"}:
        return "paced"
    if status in CONSTRAIN_STATUSES:
        return "conditioned"
    if status in DENY_STATUSES:
        return "blocked"
    return "conditioned"


def build_internal_telemetry_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    status = _normalized_status(payload.get("decision_status"))
    system_state = _normalized_state(payload.get("system_state"))
    telemetry_state = str(payload.get("telemetry_integrity_state") or "not_evaluated")
    temporal_triggered = bool(payload.get("temporal_constraint_triggered"))
    cross_source_disagreement = bool(payload.get("cross_source_disagreement"))
    loop_pressure_score = _round_score(_coerce_float(payload.get("pressure_score"), 0.0))

    status_weight = STATUS_WEIGHTS.get(status, 0.5)
    system_weight = SYSTEM_STATE_WEIGHTS.get(system_state, 0.35)
    telemetry_weight = 0.2 if telemetry_state not in {"not_evaluated", "telemetry_clear", "None", ""} else 0.0
    temporal_weight = 0.15 if temporal_triggered else 0.0
    disagreement_weight = 0.15 if cross_source_disagreement else 0.0

    constraint_weight = _round_score(
        max(status_weight, system_weight, loop_pressure_score)
        + telemetry_weight
        + temporal_weight
        + disagreement_weight
    )
    decision_divergence_score = _round_score((status_weight * 0.65) + (system_weight * 0.25) + (loop_pressure_score * 0.1))
    admissibility_delta = _round_score(status_weight)
    constraint_triggered = (
        status not in ALLOW_STATUSES
        or system_state != "NORMAL"
        or temporal_triggered
        or telemetry_weight > 0.0
        or loop_pressure_score > 0.0
    )

    record = InternalTelemetryRecord(
        timestamp=str(payload.get("timestamp_utc") or ""),
        decision_status=status,
        system_state=system_state,
        constraint_triggered=constraint_triggered,
        environment_epoch=payload.get("epoch"),
        decision_divergence_score=decision_divergence_score,
        admissibility_delta=admissibility_delta,
        constraint_weight=constraint_weight,
        execution_posture=_execution_posture(status, system_state),
        constraint_category=_constraint_category(payload),
        environment_posture=_environment_posture(system_state, status),
        loop_pressure_score=loop_pressure_score,
        telemetry_integrity_state=telemetry_state,
        temporal_constraint_triggered=temporal_triggered,
        cross_source_disagreement=cross_source_disagreement,
    )
    return asdict(record)


class InternalTelemetryEngine:
    def __init__(self, max_records: int = 500) -> None:
        self._records: Deque[Dict[str, Any]] = deque(maxlen=max_records)
        self._lock = Lock()

    def capture_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = build_internal_telemetry_record(payload)
        with self._lock:
            self._records.append(record)
        return record

    def snapshot(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._lock:
            records = list(self._records)
        if limit is not None and limit >= 0:
            return records[-limit:]
        return records

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
