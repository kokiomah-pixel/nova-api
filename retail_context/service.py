from __future__ import annotations

import copy
import hmac
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from x402.http.constants import (
    PAYMENT_REQUIRED_HEADER,
    PAYMENT_RESPONSE_HEADER,
    PAYMENT_SIGNATURE_HEADER,
)
from x402.http.utils import (
    decode_payment_signature_header,
    encode_payment_response_header,
)
from x402.schemas import PaymentPayload, SettleResponse

from .control_store import (
    RetailProductionControlStore,
    SQLiteRetailProductionControlStore,
)
from .facilitator import RetailHTTPFacilitatorAdapter
from .production_controls import (
    evaluate_retail_pre_payment_admission,
    service_admission_allows_payment_challenge,
)
from .production_telemetry import hash_retail_subject
from .request_binding import (
    PreparedRetailRequest,
    load_server_source_registry,
    prepare_context_delta_request,
    prepare_state_ping_request,
)
from .runtime_config import PROOF_ACCESS_HEADER, RetailRuntimeConfig
from .runtime_delivery import (
    RetailDeliveryRecoveryError,
    claim_or_resume_retail_delivery,
    deliver_or_redeliver_retail_resource,
)
from .runtime_guard import SQLiteRetailRuntimeGuard
from .sources import validate_source_registry
from .x402_payment import (
    RetailX402Facilitator,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    payment_outcome_allows_resource_access,
    process_retail_x402_payment,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error(status_code: int, reason: str, *, headers: Mapping[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": reason, "authority_effect": "none"},
        headers=dict(headers or {}),
    )


def _admission_error_status(reason: str | None) -> int:
    if reason == "rate_limit_exceeded":
        return 429
    if reason in {"service_disabled", "control_store_unavailable"}:
        return 503
    return 400


def _ensure_runtime_admission(
    *,
    prepared: PreparedRetailRequest,
    store: RetailProductionControlStore,
    guard: SQLiteRetailRuntimeGuard,
    config: RetailRuntimeConfig,
    observed_at: str,
    payment_present: bool,
) -> str | None:
    subject_hash = hash_retail_subject(prepared.subject_key)
    existing = store.get_runtime_request(prepared.request_id)
    if existing is not None:
        if not store.is_healthy():
            return "control_store_unavailable"
        if store.get_service_mode() != "controlled_proof":
            return "service_disabled"
        if not (
            existing["request_digest"] == prepared.request_digest
            and existing["subject_hash"] == subject_hash
            and existing["resource_type"] == prepared.resource_type
            and existing["authority_effect"] == "none"
        ):
            return "request_reconciliation_failed"
        if existing["resource_uri"] != prepared.resource_uri:
            return (
                "source_binding_reconciliation_failed"
                if prepared.resource_type == "state_ping"
                else "request_reconciliation_failed"
            )
        try:
            if guard.get_request_guard(prepared.request_id) is None:
                guard.initialize_request(
                    request_id=prepared.request_id,
                    source_binding_digest=prepared.source_binding_digest,
                    observed_at=observed_at,
                    payment_already_present=payment_present,
                )
            retry = guard.consume_existing_attempt(
                request_id=prepared.request_id,
                source_binding_digest=prepared.source_binding_digest,
                payment_present=payment_present,
                observed_at=observed_at,
                window_seconds=config.production_controls.rate_limit_window_seconds,
                retry_limit=config.retry_max_requests,
            )
        except ValueError as exc:
            if str(exc) == "source_binding_reconciliation_failed":
                return "source_binding_reconciliation_failed"
            return "request_reconciliation_failed"
        except Exception:
            return "control_store_unavailable"
        return None if retry.permitted else "rate_limit_exceeded"

    admission = evaluate_retail_pre_payment_admission(
        subject_key=prepared.subject_key,
        resource_type=prepared.resource_type,
        request_id=prepared.request_id,
        store=store,
        config=config.production_controls,
        observed_at=observed_at,
    )
    if not service_admission_allows_payment_challenge(admission):
        return str(admission.get("failure_reason") or "service_admission_denied")
    recorded = store.record_runtime_request(
        {
            "request_id": prepared.request_id,
            "request_digest": prepared.request_digest,
            "subject_hash": subject_hash,
            "resource_type": prepared.resource_type,
            "resource_uri": prepared.resource_uri,
            "admitted_at": observed_at,
            "authority_effect": "none",
        }
    )
    if not recorded:
        return "request_reconciliation_failed"
    try:
        guard.initialize_request(
            request_id=prepared.request_id,
            source_binding_digest=prepared.source_binding_digest,
            observed_at=observed_at,
            payment_already_present=payment_present,
        )
    except ValueError:
        return "source_binding_reconciliation_failed"
    except Exception:
        return "control_store_unavailable"
    return None


def create_retail_app(
    *,
    config: RetailRuntimeConfig,
    store: RetailProductionControlStore,
    facilitator: RetailX402Facilitator,
    source_registry: Mapping[str, Any],
    clock: Callable[[], str] = _utc_now,
) -> FastAPI:
    """Create the isolated controlled-proof app without mounting Legacy routes."""

    store.initialize()
    guard = SQLiteRetailRuntimeGuard(store.db_path)
    guard.initialize()
    registry = copy.deepcopy(dict(source_registry))
    validate_source_registry(registry)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        close = getattr(facilitator, "close", None)
        if callable(close):
            close()

    app = FastAPI(
        title="Nova Retail Controlled Proof",
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    async def handle_paid_resource(
        request: Request,
        request_digest: str,
        resource_type: str,
    ) -> Response:
        supplied_token = request.headers.get(PROOF_ACCESS_HEADER)
        if not isinstance(supplied_token, str) or not hmac.compare_digest(
            supplied_token,
            config.controlled_proof_access_token,
        ):
            return _error(403, "controlled_proof_access_denied")

        raw_body = await request.body()
        if not raw_body or len(raw_body) > config.max_request_bytes:
            return _error(400, "invalid_request")
        try:
            envelope = json.loads(raw_body)
            if not isinstance(envelope, Mapping):
                raise ValueError("invalid_request")
            prepared = (
                prepare_state_ping_request(envelope, source_registry=registry)
                if resource_type == "state_ping"
                else prepare_context_delta_request(envelope)
            )
        except Exception:
            return _error(400, "invalid_request")
        if not hmac.compare_digest(request_digest, prepared.request_digest):
            return _error(400, "request_digest_mismatch")

        payment_header = request.headers.get(PAYMENT_SIGNATURE_HEADER)
        observed_at = clock()
        try:
            admission_failure = _ensure_runtime_admission(
                prepared=prepared,
                store=store,
                guard=guard,
                config=config,
                observed_at=observed_at,
                payment_present=bool(payment_header),
            )
        except Exception:
            admission_failure = "control_store_unavailable"
        if admission_failure is not None:
            return _error(
                _admission_error_status(admission_failure), admission_failure
            )

        requirement = build_retail_payment_requirement(
            resource_type=prepared.resource_type,
            resource_uri=prepared.resource_uri,
            settlement_wallet=config.settlement_wallet,
        )
        challenge = build_retail_payment_challenge(requirement)
        challenge_headers = {
            PAYMENT_REQUIRED_HEADER: challenge.payment_required_header
        }
        if not payment_header:
            return _error(402, "payment_required", headers=challenge_headers)
        try:
            payment_payload = decode_payment_signature_header(payment_header)
        except Exception:
            return _error(400, "invalid_payment_payload")
        if not isinstance(payment_payload, PaymentPayload):
            return _error(400, "unsupported_x402_version")

        payment_outcome = process_retail_x402_payment(
            requirement=requirement,
            payment_payload=payment_payload,
            facilitator=facilitator,
        )
        if not payment_outcome_allows_resource_access(payment_outcome):
            return _error(
                402,
                str(payment_outcome.get("failure_reason") or "payment_failed"),
                headers=challenge_headers,
            )
        try:
            delivery_capability = claim_or_resume_retail_delivery(
                payment_outcome=payment_outcome,
                prepared=prepared,
                store=store,
                observed_at=observed_at,
            )
            delivered = deliver_or_redeliver_retail_resource(
                capability=delivery_capability,
                prepared=prepared,
                store=store,
                observed_at=observed_at,
                max_response_bytes=config.max_response_bytes,
            )
        except RetailDeliveryRecoveryError as exc:
            status_code = 503 if exc.reason == "control_store_unavailable" else 409
            return _error(status_code, exc.reason)

        payment_response = SettleResponse(
            success=True,
            payer=payment_outcome["payer"],
            transaction=payment_outcome["transaction_reference"],
            network=payment_outcome["network"],
            amount=payment_outcome["amount_atomic"],
        )
        return Response(
            content=delivered.body,
            status_code=200,
            media_type="application/json",
            headers={
                PAYMENT_RESPONSE_HEADER: encode_payment_response_header(
                    payment_response
                ),
                "X-Nova-Retail-Delivery-Mode": delivered.delivery_mode,
                "X-Nova-Retail-Response-Digest": delivered.response_digest,
            },
        )

    @app.post(
        "/retail/v1/context/state-ping/{request_digest}",
        include_in_schema=False,
    )
    async def state_ping(request: Request, request_digest: str) -> Response:
        return await handle_paid_resource(request, request_digest, "state_ping")

    @app.post(
        "/retail/v1/context/context-delta/{request_digest}",
        include_in_schema=False,
    )
    async def context_delta(request: Request, request_digest: str) -> Response:
        return await handle_paid_resource(request, request_digest, "context_delta")

    return app


def create_retail_app_from_env() -> FastAPI:
    config = RetailRuntimeConfig.from_env()
    store = SQLiteRetailProductionControlStore(
        config.production_controls.control_db_path
    )
    source_registry = load_server_source_registry(config.source_registry_path)
    facilitator = RetailHTTPFacilitatorAdapter.from_runtime_config(config)
    return create_retail_app(
        config=config,
        store=store,
        facilitator=facilitator,
        source_registry=source_registry,
    )
