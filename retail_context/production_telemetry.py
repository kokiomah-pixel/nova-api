from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping


RETAIL_OPERATIONAL_NAMESPACE = "retail_production_controls"
AUTHORITY_EFFECT = "none"
TELEMETRY_EVENT_TYPES = frozenset(
    {
        "pre_payment_admitted",
        "pre_payment_denied",
        "rate_limit_denied",
        "payment_claimed",
        "payment_replay_denied",
        "delivery_completed",
        "delivery_failed",
        "service_disabled",
        "control_store_failure",
        "latency_observed",
    }
)
INCIDENT_TYPES = frozenset(
    {
        "payment_replay_conflict",
        "control_store_unavailable",
        "delivery_failure",
        "rate_limit_pressure",
        "service_kill_switch_active",
    }
)
INCIDENT_DETAIL_KEYS = frozenset({"request_count", "limit", "conflict_scope"})
_FAILURE_REASON_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def stable_operational_id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256(_canonical_json(parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def hash_retail_subject(subject_key: object) -> str:
    if not isinstance(subject_key, str) or not subject_key.strip():
        raise ValueError("invalid_retail_subject")
    material = f"nova-retail-subject-v0.1\x00{subject_key}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def hash_transaction_reference(transaction_reference: str | None) -> str | None:
    if not transaction_reference:
        return None
    material = f"nova-retail-transaction-v0.1\x00{transaction_reference}".encode(
        "utf-8"
    )
    return hashlib.sha256(material).hexdigest()


def build_retail_telemetry_event(
    *,
    occurred_at: str,
    event_type: str,
    request_id: str,
    resource_type: str | None = None,
    subject_hash: str | None = None,
    payment_receipt_id: str | None = None,
    payment_requirement_id: str | None = None,
    transaction_reference: str | None = None,
    duration_ms: int | None = None,
    response_bytes: int | None = None,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    if event_type not in TELEMETRY_EVENT_TYPES:
        raise ValueError("unsupported_retail_telemetry_event")
    if failure_reason is not None and not _FAILURE_REASON_PATTERN.fullmatch(
        failure_reason
    ):
        raise ValueError("invalid_operational_failure_reason")
    if duration_ms is not None and duration_ms < 0:
        raise ValueError("invalid_operational_metric")
    if response_bytes is not None and response_bytes < 0:
        raise ValueError("invalid_operational_metric")
    event = {
        "schema_version": "0.1.0",
        "record_type": "telemetry_event",
        "event_id": stable_operational_id(
            "retail-event",
            occurred_at,
            event_type,
            request_id,
            resource_type,
            payment_receipt_id,
            failure_reason,
        ),
        "occurred_at": occurred_at,
        "event_type": event_type,
        "request_id": request_id,
        "resource_type": resource_type,
        "subject_hash": subject_hash,
        "payment_receipt_id": payment_receipt_id,
        "payment_requirement_id": payment_requirement_id,
        "transaction_reference_hash": hash_transaction_reference(
            transaction_reference
        ),
        "duration_ms": duration_ms,
        "response_bytes": response_bytes,
        "failure_reason": failure_reason,
        "retail_namespace": RETAIL_OPERATIONAL_NAMESPACE,
        "authority_effect": AUTHORITY_EFFECT,
    }
    return event


def build_retail_incident(
    *,
    occurred_at: str,
    incident_type: str,
    request_id: str | None = None,
    resource_type: str | None = None,
    payment_receipt_id: str | None = None,
    failure_reason: str,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if incident_type not in INCIDENT_TYPES:
        raise ValueError("unsupported_retail_incident")
    bounded_details = dict(details or {})
    if not _FAILURE_REASON_PATTERN.fullmatch(failure_reason):
        raise ValueError("invalid_operational_failure_reason")
    if not set(bounded_details).issubset(INCIDENT_DETAIL_KEYS):
        raise ValueError("unbounded_retail_incident_details")
    if any(
        not isinstance(value, (str, int, bool)) or isinstance(value, float)
        for value in bounded_details.values()
    ):
        raise ValueError("unbounded_retail_incident_details")
    incident = {
        "schema_version": "0.1.0",
        "record_type": "incident",
        "incident_id": stable_operational_id(
            "retail-incident",
            occurred_at,
            incident_type,
            request_id,
            resource_type,
            payment_receipt_id,
            failure_reason,
            bounded_details,
        ),
        "occurred_at": occurred_at,
        "incident_type": incident_type,
        "request_id": request_id,
        "resource_type": resource_type,
        "payment_receipt_id": payment_receipt_id,
        "failure_reason": failure_reason,
        "details": bounded_details,
        "retail_namespace": RETAIL_OPERATIONAL_NAMESPACE,
        "authority_effect": AUTHORITY_EFFECT,
    }
    return incident
