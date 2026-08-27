from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Mapping

from .control_store import RetailProductionControlStore
from .production_controls import (
    claim_settled_payment_for_delivery,
    delivery_outcome_allows_resource_delivery,
    record_retail_operational_incident,
)
from .request_binding import PreparedRetailRequest, canonical_json_bytes
from .x402_payment import (
    RetailPaymentOutcome,
    payment_outcome_allows_resource_access,
)


_RUNTIME_DELIVERY_CAPABILITY = object()
_RECONCILIATION_FIELDS = (
    "payment_receipt_id",
    "payment_requirement_id",
    "network",
    "transaction_reference",
    "payer",
    "resource_type",
    "resource_uri",
    "amount_atomic",
    "settlement_wallet",
)


class RetailDeliveryRecoveryError(ValueError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class RetailRuntimeDeliveryCapability:
    """Non-serialized permission derived from fresh RP6 and durable RP7 state."""

    __slots__ = (
        "claim_id",
        "delivery_status",
        "payment_receipt_id",
        "request_id",
        "resource_uri",
        "_capability",
    )

    def __init__(
        self,
        *,
        claim_id: str,
        delivery_status: str,
        payment_receipt_id: str,
        request_id: str,
        resource_uri: str,
        _capability: object | None = None,
    ) -> None:
        self.claim_id = claim_id
        self.delivery_status = delivery_status
        self.payment_receipt_id = payment_receipt_id
        self.request_id = request_id
        self.resource_uri = resource_uri
        self._capability = _capability


@dataclass(frozen=True)
class DeliveredRetailResource:
    body: bytes
    response_digest: str
    response_bytes: int
    delivery_mode: str


def _claim_matches_outcome(
    claim: Mapping[str, Any],
    payment_outcome: Mapping[str, Any],
    prepared: PreparedRetailRequest,
) -> bool:
    return (
        claim["request_id"] == prepared.request_id
        and claim["resource_uri"] == prepared.resource_uri
        and all(claim[field] == payment_outcome[field] for field in _RECONCILIATION_FIELDS)
    )


def claim_or_resume_retail_delivery(
    *,
    payment_outcome: RetailPaymentOutcome | Mapping[str, Any],
    prepared: PreparedRetailRequest,
    store: RetailProductionControlStore,
    observed_at: str,
) -> RetailRuntimeDeliveryCapability:
    if not payment_outcome_allows_resource_access(payment_outcome):
        raise RetailDeliveryRecoveryError("invalid_payment_outcome")
    if payment_outcome["resource_type"] != prepared.resource_type:
        raise RetailDeliveryRecoveryError("payment_replay_conflict")
    if payment_outcome["resource_uri"] != prepared.resource_uri:
        raise RetailDeliveryRecoveryError("payment_replay_conflict")

    try:
        initial = claim_settled_payment_for_delivery(
            payment_outcome=payment_outcome,
            request_id=prepared.request_id,
            store=store,
            observed_at=observed_at,
        )
    except Exception as exc:
        raise RetailDeliveryRecoveryError("control_store_unavailable") from exc
    if delivery_outcome_allows_resource_delivery(initial):
        return RetailRuntimeDeliveryCapability(
            claim_id=initial["claim_id"],
            delivery_status="pending",
            payment_receipt_id=initial["payment_receipt_id"],
            request_id=prepared.request_id,
            resource_uri=prepared.resource_uri,
            _capability=_RUNTIME_DELIVERY_CAPABILITY,
        )

    reason = initial.get("failure_reason")
    if reason != "payment_already_consumed":
        raise RetailDeliveryRecoveryError(str(reason or "invalid_payment_outcome"))
    try:
        existing = store.get_payment_claim_by_settlement(
            network=payment_outcome["network"],
            transaction_reference=payment_outcome["transaction_reference"],
        )
    except Exception as exc:
        raise RetailDeliveryRecoveryError("control_store_unavailable") from exc
    if existing is None or not _claim_matches_outcome(
        existing, payment_outcome, prepared
    ):
        raise RetailDeliveryRecoveryError("payment_replay_conflict")
    if existing["delivery_status"] == "failed":
        raise RetailDeliveryRecoveryError("delivery_reconciliation_required")
    if existing["delivery_status"] not in {"pending", "delivered"}:
        raise RetailDeliveryRecoveryError("invalid_delivery_state")
    return RetailRuntimeDeliveryCapability(
        claim_id=existing["claim_id"],
        delivery_status=existing["delivery_status"],
        payment_receipt_id=existing["payment_receipt_id"],
        request_id=prepared.request_id,
        resource_uri=prepared.resource_uri,
        _capability=_RUNTIME_DELIVERY_CAPABILITY,
    )


def _capability_is_valid(
    capability: object,
    prepared: PreparedRetailRequest,
) -> bool:
    return (
        isinstance(capability, RetailRuntimeDeliveryCapability)
        and capability._capability is _RUNTIME_DELIVERY_CAPABILITY
        and capability.request_id == prepared.request_id
        and capability.resource_uri == prepared.resource_uri
    )


def deliver_or_redeliver_retail_resource(
    *,
    capability: RetailRuntimeDeliveryCapability,
    prepared: PreparedRetailRequest,
    store: RetailProductionControlStore,
    observed_at: str,
    max_response_bytes: int,
) -> DeliveredRetailResource:
    if not _capability_is_valid(capability, prepared):
        raise RetailDeliveryRecoveryError("invalid_delivery_capability")
    started = time.perf_counter()
    try:
        body = canonical_json_bytes(prepared.build_resource())
    except Exception as exc:
        processing_duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        try:
            claim = store.get_payment_claim(capability.claim_id)
        except Exception as store_exc:
            raise RetailDeliveryRecoveryError("control_store_unavailable") from store_exc
        if claim is not None and claim["delivery_status"] == "pending":
            try:
                store.mark_delivery(
                    claim_id=capability.claim_id,
                    status="failed",
                    occurred_at=observed_at,
                    processing_duration_ms=processing_duration_ms,
                    failure_reason="resource_render_failed",
                )
            except Exception as store_exc:
                raise RetailDeliveryRecoveryError(
                    "control_store_unavailable"
                ) from store_exc
        raise RetailDeliveryRecoveryError("resource_render_failed") from exc
    if len(body) > max_response_bytes:
        processing_duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        try:
            claim = store.get_payment_claim(capability.claim_id)
        except Exception as store_exc:
            raise RetailDeliveryRecoveryError("control_store_unavailable") from store_exc
        if claim is not None and claim["delivery_status"] == "pending":
            try:
                store.mark_delivery(
                    claim_id=capability.claim_id,
                    status="failed",
                    occurred_at=observed_at,
                    processing_duration_ms=processing_duration_ms,
                    failure_reason="response_size_exceeded",
                )
            except Exception as store_exc:
                raise RetailDeliveryRecoveryError(
                    "control_store_unavailable"
                ) from store_exc
        raise RetailDeliveryRecoveryError("response_size_exceeded")

    response_digest = hashlib.sha256(body).hexdigest()
    processing_duration_ms = max(0, int((time.perf_counter() - started) * 1000))
    try:
        claim = store.get_payment_claim(capability.claim_id)
    except Exception as exc:
        raise RetailDeliveryRecoveryError("control_store_unavailable") from exc
    if claim is None or not (
        claim["request_id"] == prepared.request_id
        and claim["resource_uri"] == prepared.resource_uri
        and claim["payment_receipt_id"] == capability.payment_receipt_id
    ):
        raise RetailDeliveryRecoveryError("payment_replay_conflict")
    if claim["delivery_status"] == "failed":
        raise RetailDeliveryRecoveryError("delivery_reconciliation_required")
    if claim["delivery_status"] == "delivered":
        if (
            claim["response_digest"] != response_digest
            or claim["response_bytes"] != len(body)
        ):
            try:
                record_retail_operational_incident(
                    store=store,
                    occurred_at=observed_at,
                    incident_type="delivery_failure",
                    request_id=prepared.request_id,
                    resource_type=prepared.resource_type,
                    payment_receipt_id=capability.payment_receipt_id,
                    failure_reason="response_digest_mismatch",
                )
            except Exception as exc:
                raise RetailDeliveryRecoveryError(
                    "control_store_unavailable"
                ) from exc
            raise RetailDeliveryRecoveryError("response_digest_mismatch")
        return DeliveredRetailResource(
            body=body,
            response_digest=response_digest,
            response_bytes=len(body),
            delivery_mode="idempotent_redelivery",
        )
    if claim["delivery_status"] != "pending":
        raise RetailDeliveryRecoveryError("invalid_delivery_state")
    try:
        store.mark_delivery(
            claim_id=capability.claim_id,
            status="delivered",
            occurred_at=observed_at,
            response_digest=response_digest,
            response_bytes=len(body),
            processing_duration_ms=processing_duration_ms,
        )
    except ValueError:
        try:
            raced = store.get_payment_claim(capability.claim_id)
        except Exception as exc:
            raise RetailDeliveryRecoveryError("control_store_unavailable") from exc
        if raced is None or raced["delivery_status"] != "delivered":
            raise RetailDeliveryRecoveryError("invalid_delivery_state")
        if (
            raced["response_digest"] != response_digest
            or raced["response_bytes"] != len(body)
        ):
            raise RetailDeliveryRecoveryError("response_digest_mismatch")
        return DeliveredRetailResource(
            body=body,
            response_digest=response_digest,
            response_bytes=len(body),
            delivery_mode="idempotent_redelivery",
        )
    except Exception as exc:
        raise RetailDeliveryRecoveryError("control_store_unavailable") from exc
    return DeliveredRetailResource(
        body=body,
        response_digest=response_digest,
        response_bytes=len(body),
        delivery_mode="initial_delivery",
    )
