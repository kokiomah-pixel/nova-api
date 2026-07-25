from __future__ import annotations

from typing import Any, Dict, Iterable, List

from core.public_surface_config import public_x402_operational
from core.telemetry_engine import ALLOW_STATUSES, CONSTRAIN_STATUSES, DENY_STATUSES


FEED_NAME_CONSTRAINT_PRESSURE = "Nova Constraint Pressure"
FEED_TYPE_ENVIRONMENTAL_CONDITIONING = "environmental_conditioning"
NON_ADMISSION_AUTHORITY = "non_admission_telemetry"
SOURCE_LAYER_DERIVED_STATE = "derived_environmental_state"


def _round_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 3)


def _average(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _status_bucket(status: Any) -> str:
    normalized = str(status or "").strip().upper()
    if normalized in ALLOW_STATUSES:
        return "allow"
    if normalized in CONSTRAIN_STATUSES:
        return "constrain"
    if normalized in DENY_STATUSES:
        return "deny"
    return "constrain"


def _rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 3)


def _constraint_pressure_label(score: float) -> str:
    if score >= 0.72:
        return "CONSTRAINED"
    if score >= 0.48:
        return "ELEVATED"
    if score >= 0.22:
        return "RISING"
    return "QUIET"


def _environment_posture_label(score: float, dominant_posture: str) -> str:
    if dominant_posture in {"DEFENSIVE", "ESCALATING"} and score >= 0.48:
        return "DEFENSIVE"
    if score >= 0.72:
        return "DEFENSIVE"
    if score >= 0.48:
        return "CONSTRAINED"
    if score >= 0.22:
        return "RECOVERING"
    return "QUIET"


def _stability_label(score: float) -> str:
    if score < 0.35:
        return "FRAGMENTED"
    if score < 0.55:
        return "UNSTABLE"
    if score < 0.78:
        return "RECOVERING"
    return "QUIET"


def _drift_label(score: float) -> str:
    if score >= 0.78:
        return "ESCALATING"
    if score >= 0.48:
        return "RISING"
    if score >= 0.22:
        return "RECOVERING"
    return "QUIET"


def _dominant_posture(records: List[Dict[str, Any]]) -> str:
    counts: Dict[str, int] = {}
    for record in records:
        posture = str(record.get("environment_posture") or "QUIET").upper()
        counts[posture] = counts.get(posture, 0) + 1
    if not counts:
        return "QUIET"
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _deny_cluster_score(records: List[Dict[str, Any]]) -> float:
    if not records:
        return 0.0

    window = records[-5:]
    longest = 0
    current = 0
    for record in window:
        if _status_bucket(record.get("decision_status")) == "deny":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return _round_score(longest / len(window))


def _transition_volatility(records: List[Dict[str, Any]]) -> float:
    if len(records) < 2:
        return 0.0
    buckets = [_status_bucket(record.get("decision_status")) for record in records]
    transitions = sum(1 for left, right in zip(buckets, buckets[1:]) if left != right)
    return _round_score(transitions / (len(records) - 1))


class EnvironmentalStateEngine:
    def derive_constraint_pressure(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        window = list(records)
        total = len(window)
        allow_count = sum(1 for record in window if _status_bucket(record.get("decision_status")) == "allow")
        constrain_count = sum(1 for record in window if _status_bucket(record.get("decision_status")) == "constrain")
        deny_count = sum(1 for record in window if _status_bucket(record.get("decision_status")) == "deny")

        allow_rate = _rate(allow_count, total)
        constrain_rate = _rate(constrain_count, total)
        deny_rate = _rate(deny_count, total)
        average_constraint_weight = _average([
            _coerce_float(record.get("constraint_weight"), 0.0)
            for record in window
        ])
        deny_cluster = _deny_cluster_score(window)

        pressure_score = _round_score(
            (constrain_rate * 0.36)
            + (deny_rate * 0.48)
            + (average_constraint_weight * 0.32)
            + (deny_cluster * 0.18)
        )
        dominant_posture = _dominant_posture(window)

        return {
            "constraint_pressure": _constraint_pressure_label(pressure_score),
            "pressure_score": pressure_score,
            "allow_rate": allow_rate,
            "constrain_rate": constrain_rate,
            "deny_rate": deny_rate,
            "environment_posture": _environment_posture_label(pressure_score, dominant_posture),
        }

    def derive_stability_state(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        window = list(records)
        if not window:
            return {
                "decision_stability": "QUIET",
                "stability_score": 1.0,
            }

        volatility = _transition_volatility(window)
        average_divergence = _average([
            _coerce_float(record.get("decision_divergence_score"), 0.0)
            for record in window
        ])
        coordination_instability = _average([
            max(
                _coerce_float(record.get("loop_pressure_score"), 0.0),
                1.0 if record.get("temporal_constraint_triggered") else 0.0,
                1.0 if record.get("cross_source_disagreement") else 0.0,
            )
            for record in window
        ])
        unique_postures = {
            str(record.get("environment_posture") or "QUIET").upper()
            for record in window
        }
        fragmentation = _round_score(max(len(unique_postures) - 1, 0) / 4)
        instability_score = _round_score(
            (volatility * 0.28)
            + (average_divergence * 0.28)
            + (coordination_instability * 0.3)
            + (fragmentation * 0.14)
        )
        stability_score = _round_score(1.0 - instability_score)

        return {
            "decision_stability": _stability_label(stability_score),
            "stability_score": stability_score,
        }

    def derive_drift_state(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        window = list(records)
        if not window:
            return {
                "agent_drift": "QUIET",
                "drift_score": 0.0,
            }

        total = len(window)
        inadmissible_rate = sum(
            1 for record in window
            if _status_bucket(record.get("decision_status")) != "allow"
        ) / total
        divergence = _average([
            _coerce_float(record.get("admissibility_delta"), 0.0)
            for record in window
        ])
        escalation_pressure = _average([
            1.0
            if str(record.get("system_state") or "").upper() in {
                "PRESSURE_ELEVATED",
                "TELEMETRY_DEGRADED",
                "HALT_RECOMMENDED",
                "HALT_ACTIVE",
            }
            else _coerce_float(record.get("loop_pressure_score"), 0.0)
            for record in window
        ])
        coordination_mismatch = _average([
            1.0
            if record.get("cross_source_disagreement") or record.get("temporal_constraint_triggered")
            else 0.0
            for record in window
        ])

        drift_score = _round_score(
            (inadmissible_rate * 0.32)
            + (divergence * 0.28)
            + (escalation_pressure * 0.28)
            + (coordination_mismatch * 0.12)
        )

        return {
            "agent_drift": _drift_label(drift_score),
            "drift_score": drift_score,
        }

    def derive_environmental_states(self, records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        window = list(records)
        return {
            "constraint_pressure": self.derive_constraint_pressure(window),
            "decision_stability": self.derive_stability_state(window),
            "agent_drift": self.derive_drift_state(window),
        }

    def build_constraint_pressure_feed(
        self,
        *,
        records: Iterable[Dict[str, Any]],
        timestamp_utc: str,
        environment_epoch: Any,
    ) -> Dict[str, Any]:
        pressure = self.derive_constraint_pressure(records)
        return {
            "feed_name": FEED_NAME_CONSTRAINT_PRESSURE,
            "feed_type": FEED_TYPE_ENVIRONMENTAL_CONDITIONING,
            "authority_layer": NON_ADMISSION_AUTHORITY,
            "runtime_role": "non_authority_environmental_conditioning",
            "constraint_pressure": pressure["constraint_pressure"],
            "pressure_score": pressure["pressure_score"],
            "allow_rate": pressure["allow_rate"],
            "constrain_rate": pressure["constrain_rate"],
            "deny_rate": pressure["deny_rate"],
            "environment_posture": pressure["environment_posture"],
            "feed_authority": NON_ADMISSION_AUTHORITY,
            "sovereign_admission_required": True,
            "source_layer": SOURCE_LAYER_DERIVED_STATE,
            "machine_consumable": True,
            "mcp_compatible": False,
            "x402_ready": public_x402_operational(),
            "agentic_market_ready": False,
            "semantic_version": "1.0",
            "timestamp_utc": timestamp_utc,
            "environment_epoch": environment_epoch,
            "non_substitution_rule": "telemetry_informs_posture_only",
        }
