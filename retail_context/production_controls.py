from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .control_store import RetailProductionControlStore
from .production_config import RetailProductionControlConfig
from .production_telemetry import (
    build_retail_incident,
    build_retail_telemetry_event,
    hash_retail_subject,
    stable_operational_id,
)
from .x402_payment import (
    RetailPaymentOutcome,
    payment_outcome_allows_resource_access,
)


AUTHORITY_EFFECT = "none"
SUPPORTED_RESOURCE_TYPES = frozenset({"state_ping", "context_delta"})
SCHEMA_VERSION = "0.1.0"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "retail_production_control_v0_1.schema.json"
)
_ADMISSION_CAPABILITY = object()
_DELIVERY_CAPABILITY = object()
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class RetailProductionControlError(ValueError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class RetailServiceAdmissionOutcome(dict[str, Any]):
    """Process-local ability to proceed toward a payment challenge."""

    __slots__ = ("_admission_capability",)

    def __init__(
        self,
        record: Mapping[str, Any],
        *,
        _admission_capability: object | None = None,
    ) -> None:
        super().__init__(record)
        self._admission_capability = _admission_capability

    def to_record(self) -> dict[str, Any]:
        return dict(self)


class RetailResourceDeliveryOutcome(dict[str, Any]):
    """Process-local delivery eligibility, separate from its audit record."""

    __slots__ = ("_delivery_capability",)

    def __init__(
        self,
        record: Mapping[str, Any],
        *,
        _delivery_capability: object | None = None,
    ) -> None:
        super().__init__(record)
        self._delivery_capability = _delivery_capability

    def to_record(self) -> dict[str, Any]:
        return dict(self)


def load_retail_production_control_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def retail_production_control_validator(record_type: str) -> Draft202012Validator:
    schema = load_retail_production_control_schema()
    if record_type not in schema["$defs"]:
        raise ValueError(f"unknown retail production-control record: {record_type}")
    return Draft202012Validator(
        {"$ref": f"#/$defs/{record_type}", "$defs": schema["$defs"]}
    )


def validate_retail_production_control_record(
    record: Mapping[str, Any], record_type: str
) -> None:
    retail_production_control_validator(record_type).validate(record)


def _timestamp_epoch(value: str) -> int:
    if not isinstance(value, str):
        raise RetailProductionControlError("invalid_observed_at")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RetailProductionControlError("invalid_observed_at") from exc
    if parsed.tzinfo is None:
        raise RetailProductionControlError("invalid_observed_at")
    return int(parsed.timestamp())


def _validate_request_id(request_id: object) -> str:
    if not isinstance(request_id, str) or not request_id.strip():
        raise RetailProductionControlError("invalid_request_id")
    return request_id.strip()


def _record_telemetry(
    store: RetailProductionControlStore,
    event: Mapping[str, Any],
) -> None:
    validate_retail_production_control_record(event, "telemetry_event")
    store.record_telemetry(event)


def record_retail_operational_incident(
    *,
    store: RetailProductionControlStore,
    occurred_at: str,
    incident_type: str,
    failure_reason: str,
    request_id: str | None = None,
    resource_type: str | None = None,
    payment_receipt_id: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _timestamp_epoch(occurred_at)
    incident = build_retail_incident(
        occurred_at=occurred_at,
        incident_type=incident_type,
        request_id=request_id,
        resource_type=resource_type,
        payment_receipt_id=payment_receipt_id,
        failure_reason=failure_reason,
        details=details,
    )
    validate_retail_production_control_record(incident, "incident")
    store.record_incident(incident)
    return incident


def set_retail_service_mode(
    *,
    store: RetailProductionControlStore,
    mode: str,
    changed_at: str,
) -> None:
    _timestamp_epoch(changed_at)
    if mode not in {"disabled", "controlled_proof"}:
        raise RetailProductionControlError("unsupported_service_mode")
    store.set_service_mode(mode, changed_at=changed_at)


def _admission_record(
    *,
    request_id: str,
    resource_type: str,
    subject_hash: str,
    observed_at: str,
    status: str,
    failure_reason: str | None,
    rate_limit_count: int | None,
    rate_limit_max_requests: int | None,
    rate_limit_window_started_at_epoch: int | None,
) -> dict[str, Any]:
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "service_admission",
        "service_admission_id": stable_operational_id(
            "service-admission",
            request_id,
            resource_type,
            subject_hash,
            observed_at,
            status,
            failure_reason,
        ),
        "request_id": request_id,
        "resource_type": resource_type,
        "subject_hash": subject_hash,
        "observed_at": observed_at,
        "service_admission_status": status,
        "failure_reason": failure_reason,
        "rate_limit_count": rate_limit_count,
        "rate_limit_max_requests": rate_limit_max_requests,
        "rate_limit_window_started_at_epoch": rate_limit_window_started_at_epoch,
        "authority_effect": AUTHORITY_EFFECT,
    }
    validate_retail_production_control_record(record, "service_admission")
    return record


def evaluate_retail_pre_payment_admission(
    *,
    subject_key: str,
    resource_type: str,
    request_id: str,
    store: RetailProductionControlStore,
    config: RetailProductionControlConfig,
    observed_at: str,
) -> RetailServiceAdmissionOutcome:
    """Fail closed before payment when the service cannot safely admit a request."""

    request_id = _validate_request_id(request_id)
    observed_epoch = _timestamp_epoch(observed_at)
    subject_hash = hash_retail_subject(subject_key)
    if not isinstance(config, RetailProductionControlConfig):
        return RetailServiceAdmissionOutcome(
            _admission_record(
                request_id=request_id,
                resource_type=resource_type,
                subject_hash=subject_hash,
                observed_at=observed_at,
                status="denied",
                failure_reason="invalid_control_config",
                rate_limit_count=None,
                rate_limit_max_requests=None,
                rate_limit_window_started_at_epoch=None,
            )
        )

    try:
        if not store.is_healthy():
            raise RuntimeError("control_store_unavailable")
        mode = store.get_service_mode()
        if mode != "controlled_proof":
            record = _admission_record(
                request_id=request_id,
                resource_type=resource_type,
                subject_hash=subject_hash,
                observed_at=observed_at,
                status="denied",
                failure_reason="service_disabled",
                rate_limit_count=None,
                rate_limit_max_requests=None,
                rate_limit_window_started_at_epoch=None,
            )
            _record_telemetry(
                store,
                build_retail_telemetry_event(
                    occurred_at=observed_at,
                    event_type="service_disabled",
                    request_id=request_id,
                    resource_type=resource_type,
                    subject_hash=subject_hash,
                    failure_reason="service_disabled",
                ),
            )
            record_retail_operational_incident(
                store=store,
                occurred_at=observed_at,
                incident_type="service_kill_switch_active",
                request_id=request_id,
                resource_type=resource_type,
                failure_reason="service_disabled",
            )
            return RetailServiceAdmissionOutcome(record)

        limit = config.max_requests_for(resource_type)
        if resource_type not in SUPPORTED_RESOURCE_TYPES or limit is None:
            record = _admission_record(
                request_id=request_id,
                resource_type=resource_type,
                subject_hash=subject_hash,
                observed_at=observed_at,
                status="denied",
                failure_reason="unsupported_resource",
                rate_limit_count=None,
                rate_limit_max_requests=None,
                rate_limit_window_started_at_epoch=None,
            )
            _record_telemetry(
                store,
                build_retail_telemetry_event(
                    occurred_at=observed_at,
                    event_type="pre_payment_denied",
                    request_id=request_id,
                    resource_type=None,
                    subject_hash=subject_hash,
                    failure_reason="unsupported_resource",
                ),
            )
            return RetailServiceAdmissionOutcome(record)

        window_start = (
            observed_epoch // config.rate_limit_window_seconds
        ) * config.rate_limit_window_seconds
        decision = store.consume_rate_limit(
            subject_hash=subject_hash,
            resource_type=resource_type,
            window_started_at_epoch=window_start,
            limit=limit,
            observed_at=observed_at,
        )
        if not decision.permitted:
            record = _admission_record(
                request_id=request_id,
                resource_type=resource_type,
                subject_hash=subject_hash,
                observed_at=observed_at,
                status="denied",
                failure_reason="rate_limit_exceeded",
                rate_limit_count=decision.request_count,
                rate_limit_max_requests=limit,
                rate_limit_window_started_at_epoch=window_start,
            )
            _record_telemetry(
                store,
                build_retail_telemetry_event(
                    occurred_at=observed_at,
                    event_type="rate_limit_denied",
                    request_id=request_id,
                    resource_type=resource_type,
                    subject_hash=subject_hash,
                    failure_reason="rate_limit_exceeded",
                ),
            )
            record_retail_operational_incident(
                store=store,
                occurred_at=observed_at,
                incident_type="rate_limit_pressure",
                request_id=request_id,
                resource_type=resource_type,
                failure_reason="rate_limit_exceeded",
                details={"request_count": decision.request_count, "limit": limit},
            )
            return RetailServiceAdmissionOutcome(record)

        record = _admission_record(
            request_id=request_id,
            resource_type=resource_type,
            subject_hash=subject_hash,
            observed_at=observed_at,
            status="admitted",
            failure_reason=None,
            rate_limit_count=decision.request_count,
            rate_limit_max_requests=limit,
            rate_limit_window_started_at_epoch=window_start,
        )
        _record_telemetry(
            store,
            build_retail_telemetry_event(
                occurred_at=observed_at,
                event_type="pre_payment_admitted",
                request_id=request_id,
                resource_type=resource_type,
                subject_hash=subject_hash,
            ),
        )
        return RetailServiceAdmissionOutcome(
            record, _admission_capability=_ADMISSION_CAPABILITY
        )
    except Exception:
        record = _admission_record(
            request_id=request_id,
            resource_type=resource_type,
            subject_hash=subject_hash,
            observed_at=observed_at,
            status="denied",
            failure_reason="control_store_unavailable",
            rate_limit_count=None,
            rate_limit_max_requests=None,
            rate_limit_window_started_at_epoch=None,
        )
        return RetailServiceAdmissionOutcome(record)


def service_admission_allows_payment_challenge(
    outcome: Mapping[str, Any],
) -> bool:
    if not isinstance(outcome, RetailServiceAdmissionOutcome):
        return False
    if outcome._admission_capability is not _ADMISSION_CAPABILITY:
        return False
    try:
        validate_retail_production_control_record(outcome, "service_admission")
    except Exception:
        return False
    expected_id = stable_operational_id(
        "service-admission",
        outcome["request_id"],
        outcome["resource_type"],
        outcome["subject_hash"],
        outcome["observed_at"],
        outcome["service_admission_status"],
        outcome["failure_reason"],
    )
    return (
        outcome["service_admission_status"] == "admitted"
        and outcome["failure_reason"] is None
        and outcome["authority_effect"] == AUTHORITY_EFFECT
        and outcome["service_admission_id"] == expected_id
    )


def _delivery_record(
    *,
    request_id: str,
    payment_receipt_id: str | None,
    payment_requirement_id: str | None,
    resource_type: str | None,
    resource_uri: str | None,
    claim_id: str | None,
    claimed_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "delivery_outcome",
        "delivery_outcome_id": stable_operational_id(
            "delivery-outcome",
            request_id,
            payment_receipt_id,
            claim_id,
            claimed_at,
            status,
            failure_reason,
        ),
        "claim_id": claim_id,
        "request_id": request_id,
        "payment_receipt_id": payment_receipt_id,
        "payment_requirement_id": payment_requirement_id,
        "resource_type": resource_type,
        "resource_uri": resource_uri,
        "delivery_eligibility_status": "eligible" if status == "pending" else "denied",
        "delivery_status": status,
        "claimed_at": claimed_at,
        "failure_reason": failure_reason,
        "authority_effect": AUTHORITY_EFFECT,
    }
    validate_retail_production_control_record(record, "delivery_outcome")
    return record


def claim_settled_payment_for_delivery(
    *,
    payment_outcome: RetailPaymentOutcome | Mapping[str, Any],
    request_id: str,
    store: RetailProductionControlStore,
    observed_at: str,
) -> RetailResourceDeliveryOutcome:
    request_id = _validate_request_id(request_id)
    _timestamp_epoch(observed_at)
    if not payment_outcome_allows_resource_access(payment_outcome):
        return RetailResourceDeliveryOutcome(
            _delivery_record(
                request_id=request_id,
                payment_receipt_id=payment_outcome.get("payment_receipt_id"),
                payment_requirement_id=payment_outcome.get("payment_requirement_id"),
                resource_type=payment_outcome.get("resource_type"),
                resource_uri=payment_outcome.get("resource_uri"),
                claim_id=None,
                claimed_at=observed_at,
                status="denied",
                failure_reason="invalid_payment_outcome",
            )
        )

    try:
        if not store.is_healthy():
            raise RuntimeError("control_store_unavailable")
        if store.get_service_mode() != "controlled_proof":
            return RetailResourceDeliveryOutcome(
                _delivery_record(
                    request_id=request_id,
                    payment_receipt_id=payment_outcome["payment_receipt_id"],
                    payment_requirement_id=payment_outcome["payment_requirement_id"],
                    resource_type=payment_outcome["resource_type"],
                    resource_uri=payment_outcome["resource_uri"],
                    claim_id=None,
                    claimed_at=observed_at,
                    status="denied",
                    failure_reason="service_disabled",
                )
            )

        claim_id = stable_operational_id(
            "payment-claim",
            payment_outcome["payment_receipt_id"],
            payment_outcome["network"],
            payment_outcome["transaction_reference"],
        )
        claim_record = {
            "claim_id": claim_id,
            "request_id": request_id,
            "payment_receipt_id": payment_outcome["payment_receipt_id"],
            "payment_requirement_id": payment_outcome["payment_requirement_id"],
            "network": payment_outcome["network"],
            "transaction_reference": payment_outcome["transaction_reference"],
            "payer": payment_outcome["payer"],
            "resource_type": payment_outcome["resource_type"],
            "resource_uri": payment_outcome["resource_uri"],
            "amount_atomic": payment_outcome["amount_atomic"],
            "settlement_wallet": payment_outcome["settlement_wallet"],
            "claimed_at": observed_at,
            "delivery_status": "pending",
            "authority_effect": AUTHORITY_EFFECT,
        }
        decision = store.claim_payment(claim_record)
        if not decision.claimed:
            _record_telemetry(
                store,
                build_retail_telemetry_event(
                    occurred_at=observed_at,
                    event_type="payment_replay_denied",
                    request_id=request_id,
                    resource_type=payment_outcome["resource_type"],
                    payment_receipt_id=payment_outcome["payment_receipt_id"],
                    payment_requirement_id=payment_outcome["payment_requirement_id"],
                    transaction_reference=payment_outcome["transaction_reference"],
                    failure_reason=decision.failure_reason,
                ),
            )
            if decision.failure_reason == "payment_replay_conflict":
                record_retail_operational_incident(
                    store=store,
                    occurred_at=observed_at,
                    incident_type="payment_replay_conflict",
                    request_id=request_id,
                    resource_type=payment_outcome["resource_type"],
                    payment_receipt_id=payment_outcome["payment_receipt_id"],
                    failure_reason="payment_replay_conflict",
                    details={"conflict_scope": "settlement_reconciliation"},
                )
            return RetailResourceDeliveryOutcome(
                _delivery_record(
                    request_id=request_id,
                    payment_receipt_id=payment_outcome["payment_receipt_id"],
                    payment_requirement_id=payment_outcome["payment_requirement_id"],
                    resource_type=payment_outcome["resource_type"],
                    resource_uri=payment_outcome["resource_uri"],
                    claim_id=None,
                    claimed_at=observed_at,
                    status="denied",
                    failure_reason=decision.failure_reason,
                )
            )

        _record_telemetry(
            store,
            build_retail_telemetry_event(
                occurred_at=observed_at,
                event_type="payment_claimed",
                request_id=request_id,
                resource_type=payment_outcome["resource_type"],
                payment_receipt_id=payment_outcome["payment_receipt_id"],
                payment_requirement_id=payment_outcome["payment_requirement_id"],
                transaction_reference=payment_outcome["transaction_reference"],
            ),
        )
        record = _delivery_record(
            request_id=request_id,
            payment_receipt_id=payment_outcome["payment_receipt_id"],
            payment_requirement_id=payment_outcome["payment_requirement_id"],
            resource_type=payment_outcome["resource_type"],
            resource_uri=payment_outcome["resource_uri"],
            claim_id=claim_id,
            claimed_at=observed_at,
            status="pending",
            failure_reason=None,
        )
        return RetailResourceDeliveryOutcome(
            record, _delivery_capability=_DELIVERY_CAPABILITY
        )
    except Exception:
        return RetailResourceDeliveryOutcome(
            _delivery_record(
                request_id=request_id,
                payment_receipt_id=payment_outcome["payment_receipt_id"],
                payment_requirement_id=payment_outcome["payment_requirement_id"],
                resource_type=payment_outcome["resource_type"],
                resource_uri=payment_outcome["resource_uri"],
                claim_id=None,
                claimed_at=observed_at,
                status="denied",
                failure_reason="control_store_unavailable",
            )
        )


def delivery_outcome_allows_resource_delivery(
    outcome: Mapping[str, Any],
) -> bool:
    if not isinstance(outcome, RetailResourceDeliveryOutcome):
        return False
    if outcome._delivery_capability is not _DELIVERY_CAPABILITY:
        return False
    try:
        validate_retail_production_control_record(outcome, "delivery_outcome")
    except Exception:
        return False
    expected_id = stable_operational_id(
        "delivery-outcome",
        outcome["request_id"],
        outcome["payment_receipt_id"],
        outcome["claim_id"],
        outcome["claimed_at"],
        outcome["delivery_status"],
        outcome["failure_reason"],
    )
    return (
        outcome["delivery_eligibility_status"] == "eligible"
        and outcome["delivery_status"] == "pending"
        and outcome["failure_reason"] is None
        and outcome["authority_effect"] == AUTHORITY_EFFECT
        and outcome["delivery_outcome_id"] == expected_id
    )


def mark_retail_delivery_complete(
    *,
    delivery_outcome: RetailResourceDeliveryOutcome | Mapping[str, Any],
    store: RetailProductionControlStore,
    observed_at: str,
    response_digest: str,
    response_bytes: int,
    processing_duration_ms: int,
) -> dict[str, Any]:
    _timestamp_epoch(observed_at)
    if not delivery_outcome_allows_resource_delivery(delivery_outcome):
        raise RetailProductionControlError("invalid_delivery_capability")
    if not _SHA256_PATTERN.fullmatch(response_digest):
        raise RetailProductionControlError("invalid_response_digest")
    if response_bytes < 0 or processing_duration_ms < 0:
        raise RetailProductionControlError("invalid_delivery_metrics")
    record = dict(
        store.mark_delivery(
            claim_id=delivery_outcome["claim_id"],
            status="delivered",
            occurred_at=observed_at,
            response_digest=response_digest,
            response_bytes=response_bytes,
            processing_duration_ms=processing_duration_ms,
        )
    )
    _record_telemetry(
        store,
        build_retail_telemetry_event(
            occurred_at=observed_at,
            event_type="delivery_completed",
            request_id=delivery_outcome["request_id"],
            resource_type=delivery_outcome["resource_type"],
            payment_receipt_id=delivery_outcome["payment_receipt_id"],
            payment_requirement_id=delivery_outcome["payment_requirement_id"],
            duration_ms=processing_duration_ms,
            response_bytes=response_bytes,
        ),
    )
    return record


def mark_retail_delivery_failed(
    *,
    delivery_outcome: RetailResourceDeliveryOutcome | Mapping[str, Any],
    store: RetailProductionControlStore,
    observed_at: str,
    failure_reason: str,
    processing_duration_ms: int | None = None,
) -> dict[str, Any]:
    _timestamp_epoch(observed_at)
    if not delivery_outcome_allows_resource_delivery(delivery_outcome):
        raise RetailProductionControlError("invalid_delivery_capability")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", failure_reason) or (
        processing_duration_ms is not None and processing_duration_ms < 0
    ):
        raise RetailProductionControlError("invalid_delivery_failure")
    record = dict(
        store.mark_delivery(
            claim_id=delivery_outcome["claim_id"],
            status="failed",
            occurred_at=observed_at,
            processing_duration_ms=processing_duration_ms,
            failure_reason=failure_reason,
        )
    )
    _record_telemetry(
        store,
        build_retail_telemetry_event(
            occurred_at=observed_at,
            event_type="delivery_failed",
            request_id=delivery_outcome["request_id"],
            resource_type=delivery_outcome["resource_type"],
            payment_receipt_id=delivery_outcome["payment_receipt_id"],
            payment_requirement_id=delivery_outcome["payment_requirement_id"],
            duration_ms=processing_duration_ms,
            failure_reason=failure_reason,
        ),
    )
    record_retail_operational_incident(
        store=store,
        occurred_at=observed_at,
        incident_type="delivery_failure",
        request_id=delivery_outcome["request_id"],
        resource_type=delivery_outcome["resource_type"],
        payment_receipt_id=delivery_outcome["payment_receipt_id"],
        failure_reason=failure_reason,
    )
    return record


def evaluate_retail_control_readiness(
    *,
    store: RetailProductionControlStore,
    config: RetailProductionControlConfig | object,
    observed_at: str,
) -> dict[str, Any]:
    _timestamp_epoch(observed_at)
    checks = {
        "control_store_open": False,
        "schema_initialized": False,
        "operating_mode_controlled_proof": False,
        "rate_limit_configuration_valid": isinstance(
            config, RetailProductionControlConfig
        ),
        "payment_persistence_available": False,
        "telemetry_persistence_available": False,
    }
    failure_reasons: list[str] = []
    if isinstance(config, RetailProductionControlConfig):
        try:
            health = store.health_snapshot()
            checks.update(
                {
                    "control_store_open": bool(health["control_store_open"]),
                    "schema_initialized": bool(health["schema_initialized"]),
                    "payment_persistence_available": bool(
                        health["payment_persistence_available"]
                    ),
                    "telemetry_persistence_available": bool(
                        health["telemetry_persistence_available"]
                    ),
                    "operating_mode_controlled_proof": store.get_service_mode()
                    == "controlled_proof",
                }
            )
            if Path(store.db_path) != config.control_db_path:
                checks["control_store_open"] = False
                failure_reasons.append("control_store_config_mismatch")
        except Exception:
            failure_reasons.append("control_store_unavailable")
    else:
        failure_reasons.append("invalid_control_config")
    for check_name, passed in checks.items():
        if not passed and check_name not in {
            "control_store_open",
            "rate_limit_configuration_valid",
        }:
            failure_reasons.append(check_name)
    if not checks["control_store_open"] and "control_store_unavailable" not in failure_reasons:
        failure_reasons.append("control_store_unavailable")
    if not checks["rate_limit_configuration_valid"] and "invalid_control_config" not in failure_reasons:
        failure_reasons.append("invalid_control_config")
    failure_reasons = sorted(set(failure_reasons))
    readiness_status = (
        "ready_for_controlled_proof" if all(checks.values()) else "not_ready"
    )
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "readiness_snapshot",
        "readiness_snapshot_id": stable_operational_id(
            "readiness", observed_at, checks, readiness_status
        ),
        "observed_at": observed_at,
        "readiness_status": readiness_status,
        "checks": checks,
        "failure_reasons": failure_reasons,
        "authority_effect": AUTHORITY_EFFECT,
    }
    validate_retail_production_control_record(snapshot, "readiness_snapshot")
    return snapshot
