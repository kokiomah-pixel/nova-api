from __future__ import annotations

import copy
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest
from jsonschema.exceptions import ValidationError
from x402.schemas import PaymentPayload, SettleResponse, VerifyResponse

from retail_context.boundaries import (
    RetailIsolationViolation,
    assert_retail_module_allowed,
    validate_retail_package_imports,
)
from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.production_config import RetailProductionControlConfig
from retail_context.production_controls import (
    RetailProductionControlError,
    claim_settled_payment_for_delivery,
    delivery_outcome_allows_resource_delivery,
    evaluate_retail_control_readiness,
    evaluate_retail_pre_payment_admission,
    load_retail_production_control_schema,
    mark_retail_delivery_complete,
    mark_retail_delivery_failed,
    record_retail_operational_incident,
    service_admission_allows_payment_challenge,
    set_retail_service_mode,
    validate_retail_production_control_record,
)
from retail_context.production_telemetry import (
    RETAIL_OPERATIONAL_NAMESPACE,
    build_retail_telemetry_event,
)
from retail_context.x402_payment import (
    PAYMENT_NETWORK,
    RetailPaymentOutcome,
    build_retail_payment_challenge,
    build_retail_payment_requirement,
    process_retail_x402_payment,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OBSERVED_AT = "2026-08-27T12:00:00Z"
SETTLEMENT_WALLET = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"


class FakeFacilitator:
    def __init__(self, transaction: str) -> None:
        self.transaction = transaction

    def verify(self, payload, requirements):
        return VerifyResponse(is_valid=True, payer=PAYER)

    def settle(self, payload, requirements):
        return SettleResponse(
            success=True,
            payer=PAYER,
            transaction=self.transaction,
            network=PAYMENT_NETWORK,
            amount=requirements.amount,
        )


def config_at(
    path: Path,
    *,
    window: int = 60,
    state_ping_limit: int = 2,
    context_delta_limit: int = 1,
) -> RetailProductionControlConfig:
    return RetailProductionControlConfig(
        control_db_path=path,
        rate_limit_window_seconds=window,
        state_ping_max_requests=state_ping_limit,
        context_delta_max_requests=context_delta_limit,
    )


def controlled_store(tmp_path: Path) -> tuple[SQLiteRetailProductionControlStore, RetailProductionControlConfig]:
    path = tmp_path / "production_controls.sqlite3"
    store = SQLiteRetailProductionControlStore(path)
    store.initialize()
    set_retail_service_mode(
        store=store, mode="controlled_proof", changed_at=OBSERVED_AT
    )
    return store, config_at(path)


def payment_outcome(
    *,
    resource_type: str = "state_ping",
    transaction: str = "0xsettled",
) -> RetailPaymentOutcome:
    slug = resource_type.replace("_", "-")
    requirement = build_retail_payment_requirement(
        resource_type=resource_type,
        resource_uri=f"/retail/v1/context/{slug}",
        settlement_wallet=SETTLEMENT_WALLET,
    )
    challenge = build_retail_payment_challenge(requirement)
    payload = PaymentPayload(
        x402_version=2,
        payload={"signature": "raw-payment-signature-fixture"},
        accepted=challenge.payment_required.accepts[0],
        resource=challenge.payment_required.resource,
        extensions=challenge.payment_required.extensions,
    )
    return process_retail_x402_payment(
        requirement=requirement,
        payment_payload=payload,
        facilitator=FakeFacilitator(transaction),
    )


def admitted(
    store: SQLiteRetailProductionControlStore,
    config: RetailProductionControlConfig,
    *,
    subject: str = "opaque-retail-subject",
    resource_type: str = "state_ping",
    request_id: str = "request-1",
    observed_at: str = OBSERVED_AT,
):
    return evaluate_retail_pre_payment_admission(
        subject_key=subject,
        resource_type=resource_type,
        request_id=request_id,
        store=store,
        config=config,
        observed_at=observed_at,
    )


def claimed(
    store: SQLiteRetailProductionControlStore,
    *,
    outcome: RetailPaymentOutcome | None = None,
    request_id: str = "request-1",
    observed_at: str = OBSERVED_AT,
):
    return claim_settled_payment_for_delivery(
        payment_outcome=outcome or payment_outcome(),
        request_id=request_id,
        store=store,
        observed_at=observed_at,
    )


def test_disabled_service_is_denied_before_payment(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    store = SQLiteRetailProductionControlStore(path)
    store.initialize()
    outcome = admitted(store, config_at(path))
    assert outcome["service_admission_status"] == "denied"
    assert outcome["failure_reason"] == "service_disabled"
    assert not service_admission_allows_payment_challenge(outcome)


def test_supported_resource_under_limit_is_admitted(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    outcome = admitted(store, config)
    assert outcome["service_admission_status"] == "admitted"
    assert outcome["rate_limit_count"] == 1
    assert service_admission_allows_payment_challenge(outcome)


def test_unsupported_resource_is_denied_before_payment(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    outcome = admitted(store, config, resource_type="full_context")
    assert outcome["failure_reason"] == "unsupported_resource"
    assert not service_admission_allows_payment_challenge(outcome)


def test_plain_admission_dictionary_is_not_a_capability(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    outcome = admitted(store, config)
    assert not service_admission_allows_payment_challenge(dict(outcome))
    assert not service_admission_allows_payment_challenge(
        {"service_admission_status": "admitted"}
    )


def test_rate_limit_boundary_and_fixed_window_reset(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    first = admitted(store, config, request_id="request-1", observed_at="2026-08-27T12:00:00Z")
    second = admitted(store, config, request_id="request-2", observed_at="2026-08-27T12:00:59Z")
    denied = admitted(store, config, request_id="request-3", observed_at="2026-08-27T12:00:59Z")
    reset = admitted(store, config, request_id="request-4", observed_at="2026-08-27T12:01:00Z")
    assert [first["service_admission_status"], second["service_admission_status"]] == ["admitted", "admitted"]
    assert denied["failure_reason"] == "rate_limit_exceeded"
    assert reset["service_admission_status"] == "admitted"


def test_separate_subjects_do_not_share_admission_counters(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    first = admitted(store, config, subject="subject-a", resource_type="context_delta")
    second = admitted(store, config, subject="subject-b", resource_type="context_delta", request_id="request-2")
    assert first["service_admission_status"] == second["service_admission_status"] == "admitted"


def test_raw_subject_identifier_is_not_persisted(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    raw_subject = "private-subject@example.test"
    outcome = admitted(store, config, subject=raw_subject)
    assert raw_subject not in json.dumps(outcome)
    assert raw_subject.encode() not in config.control_db_path.read_bytes()
    assert len(outcome["subject_hash"]) == 64


def test_control_store_failure_denies_admission(tmp_path: Path) -> None:
    unavailable = tmp_path / "directory"
    unavailable.mkdir()
    store = SQLiteRetailProductionControlStore(unavailable)
    outcome = admitted(store, config_at(unavailable))
    assert outcome["failure_reason"] == "control_store_unavailable"


def test_plain_or_deserialized_rp6_receipt_cannot_be_claimed(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    actual = payment_outcome()
    for receipt in (dict(actual), json.loads(json.dumps(actual))):
        outcome = claim_settled_payment_for_delivery(
            payment_outcome=receipt,
            request_id="request-plain",
            store=store,
            observed_at=OBSERVED_AT,
        )
        assert outcome["failure_reason"] == "invalid_payment_outcome"
        assert not delivery_outcome_allows_resource_delivery(outcome)
    assert store.count_payment_claims() == 0


def test_actual_process_local_payment_outcome_can_be_claimed(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    outcome = claimed(store)
    assert outcome["delivery_eligibility_status"] == "eligible"
    assert outcome["delivery_status"] == "pending"
    assert delivery_outcome_allows_resource_delivery(outcome)
    assert store.count_payment_claims() == 1


def test_exact_duplicate_cannot_create_second_delivery_access(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    payment = payment_outcome()
    first = claimed(store, outcome=payment, request_id="request-1")
    second = claimed(store, outcome=payment, request_id="request-2", observed_at="2026-08-27T12:00:01Z")
    assert delivery_outcome_allows_resource_delivery(first)
    assert second["failure_reason"] == "payment_already_consumed"
    assert not delivery_outcome_allows_resource_delivery(second)
    assert store.count_payment_claims() == 1


def test_same_transaction_with_conflicting_resource_fails_closed(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    first = claimed(store, outcome=payment_outcome(transaction="0xsame"))
    conflicting = claimed(
        store,
        outcome=payment_outcome(resource_type="context_delta", transaction="0xsame"),
        request_id="request-2",
        observed_at="2026-08-27T12:00:01Z",
    )
    assert delivery_outcome_allows_resource_delivery(first)
    assert conflicting["failure_reason"] == "payment_replay_conflict"
    assert store.count_payment_claims() == 1


def test_receipt_id_uniqueness_is_enforced_by_store(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    outcome = claimed(store)
    persisted = store.get_payment_claim(outcome["claim_id"])
    assert persisted is not None
    conflicting = dict(persisted)
    conflicting["claim_id"] = "payment-claim-000000000000000000000000"
    conflicting["transaction_reference"] = "0xdifferent"
    decision = store.claim_payment(conflicting)
    assert not decision.claimed
    assert decision.failure_reason == "payment_replay_conflict"


def test_concurrent_duplicate_claim_has_exactly_one_winner(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    path = store.db_path
    payment = payment_outcome(transaction="0xconcurrent")

    def attempt(index: int):
        worker = SQLiteRetailProductionControlStore(path)
        return claimed(
            worker,
            outcome=payment,
            request_id=f"request-{index}",
            observed_at=f"2026-08-27T12:00:0{index}Z",
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, range(2)))
    assert sum(delivery_outcome_allows_resource_delivery(item) for item in results) == 1
    assert sum(item["failure_reason"] == "payment_already_consumed" for item in results) == 1
    assert store.count_payment_claims() == 1


def test_consumed_payment_and_reconciliation_survive_reopen(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    outcome = claimed(store)
    reopened = SQLiteRetailProductionControlStore(store.db_path)
    persisted = reopened.get_payment_claim(outcome["claim_id"])
    assert persisted is not None
    assert persisted["payment_receipt_id"] == outcome["payment_receipt_id"]
    assert persisted["payment_requirement_id"] == outcome["payment_requirement_id"]
    assert persisted["network"] == PAYMENT_NETWORK
    assert persisted["transaction_reference"] == "0xsettled"
    assert persisted["payer"] == PAYER
    assert persisted["resource_type"] == "state_ping"
    assert persisted["resource_uri"] == "/retail/v1/context/state-ping"
    assert persisted["amount_atomic"] == "2000"
    assert persisted["settlement_wallet"] == SETTLEMENT_WALLET
    assert persisted["delivery_status"] == "pending"


def test_raw_payment_material_and_credentials_are_never_persisted(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    claimed(store)
    database_bytes = store.db_path.read_bytes()
    for forbidden in (
        b"raw-payment-signature-fixture",
        b"PAYMENT-SIGNATURE",
        b"Authorization",
        b"Bearer ",
        b"CDP_API_KEY",
    ):
        assert forbidden not in database_bytes
    record = store.get_payment_claim("payment-claim-missing")
    assert record is None


def test_payment_settlement_and_delivery_status_remain_distinct(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    payment = payment_outcome()
    outcome = claimed(store, outcome=payment)
    assert payment["settlement_status"] == "settled"
    assert outcome["delivery_status"] == "pending"


def test_successful_delivery_marks_delivered_with_bounded_metrics(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    outcome = claimed(store)
    persisted = mark_retail_delivery_complete(
        delivery_outcome=outcome,
        store=store,
        observed_at="2026-08-27T12:00:01Z",
        response_digest="a" * 64,
        response_bytes=321,
        processing_duration_ms=17,
    )
    assert persisted["delivery_status"] == "delivered"
    assert persisted["delivered_at"] == "2026-08-27T12:00:01Z"
    assert persisted["response_digest"] == "a" * 64
    assert persisted["response_bytes"] == 321
    assert persisted["processing_duration_ms"] == 17


def test_failed_delivery_remains_consumed_and_creates_no_new_entitlement(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    payment = payment_outcome()
    outcome = claimed(store, outcome=payment)
    persisted = mark_retail_delivery_failed(
        delivery_outcome=outcome,
        store=store,
        observed_at="2026-08-27T12:00:01Z",
        failure_reason="resource_render_failed",
        processing_duration_ms=11,
    )
    assert persisted["delivery_status"] == "failed"
    assert store.count_payment_claims() == 1
    duplicate = claimed(store, outcome=payment, request_id="request-2")
    assert duplicate["failure_reason"] == "payment_already_consumed"
    assert store.count_payment_claims() == 1


def test_fabricated_delivery_capability_cannot_mark_success(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    actual = claimed(store)
    with pytest.raises(RetailProductionControlError, match="invalid_delivery_capability"):
        mark_retail_delivery_complete(
            delivery_outcome=dict(actual),
            store=store,
            observed_at="2026-08-27T12:00:01Z",
            response_digest="a" * 64,
            response_bytes=1,
            processing_duration_ms=1,
        )
    assert store.get_payment_claim(actual["claim_id"])["delivery_status"] == "pending"


def test_telemetry_is_retail_scoped_and_subject_is_hashed(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    admitted(store, config, subject="raw-private-subject")
    event = store.list_telemetry()[0]
    assert event["retail_namespace"] == RETAIL_OPERATIONAL_NAMESPACE
    assert event["authority_effect"] == "none"
    assert event["subject_hash"] != "raw-private-subject"
    assert len(event["subject_hash"]) == 64


def test_payment_telemetry_hashes_transaction_and_has_no_market_claims(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    claimed(store)
    event = next(item for item in store.list_telemetry() if item["event_type"] == "payment_claimed")
    assert event["transaction_reference_hash"] != "0xsettled"
    assert len(event["transaction_reference_hash"]) == 64
    rendered = json.dumps(event).lower()
    for forbidden in ("buyer_demand", "adoption", "pricing_power", "product_market_fit", "payer"):
        assert forbidden not in rendered


def test_delivery_telemetry_records_latency_and_result_size_not_body(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    outcome = claimed(store)
    mark_retail_delivery_complete(
        delivery_outcome=outcome,
        store=store,
        observed_at="2026-08-27T12:00:01Z",
        response_digest="b" * 64,
        response_bytes=1234,
        processing_duration_ms=29,
    )
    event = next(item for item in store.list_telemetry() if item["event_type"] == "delivery_completed")
    assert event["duration_ms"] == 29
    assert event["response_bytes"] == 1234
    assert "context_body" not in event
    assert "response_body" not in event


def test_telemetry_schema_rejects_context_body_or_credentials() -> None:
    event = build_retail_telemetry_event(
        occurred_at=OBSERVED_AT,
        event_type="latency_observed",
        request_id="request-1",
        duration_ms=5,
    )
    for field in ("context_body", "credentials", "authorization"):
        invalid = dict(event)
        invalid[field] = "secret"
        with pytest.raises(ValidationError):
            validate_retail_production_control_record(invalid, "telemetry_event")


def test_incident_evidence_persists_with_no_authority_or_mode_mutation(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    incident = record_retail_operational_incident(
        store=store,
        occurred_at=OBSERVED_AT,
        incident_type="control_store_unavailable",
        request_id="request-1",
        failure_reason="control_store_unavailable",
    )
    reopened = SQLiteRetailProductionControlStore(store.db_path)
    persisted = reopened.list_incidents()
    assert persisted[0]["incident_id"] == incident["incident_id"]
    assert persisted[0]["authority_effect"] == "none"
    assert reopened.get_service_mode() == "controlled_proof"


def test_incident_details_reject_unbounded_credential_material(tmp_path: Path) -> None:
    store, _ = controlled_store(tmp_path)
    with pytest.raises(ValueError, match="unbounded_retail_incident_details"):
        record_retail_operational_incident(
            store=store,
            occurred_at=OBSERVED_AT,
            incident_type="delivery_failure",
            failure_reason="delivery_failed",
            details={"authorization": "Bearer secret"},
        )
    assert store.list_incidents() == []


def test_readiness_is_not_ready_by_default(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    store = SQLiteRetailProductionControlStore(path)
    store.initialize()
    snapshot = evaluate_retail_control_readiness(
        store=store, config=config_at(path), observed_at=OBSERVED_AT
    )
    assert snapshot["readiness_status"] == "not_ready"
    assert not snapshot["checks"]["operating_mode_controlled_proof"]


def test_readiness_requires_all_controls_for_controlled_proof(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    first = evaluate_retail_control_readiness(store=store, config=config, observed_at=OBSERVED_AT)
    second = evaluate_retail_control_readiness(store=store, config=config, observed_at=OBSERVED_AT)
    assert first == second
    assert first["readiness_status"] == "ready_for_controlled_proof"
    assert all(first["checks"].values())
    assert first["failure_reasons"] == []
    assert first["authority_effect"] == "none"


def test_readiness_fails_closed_when_store_is_unavailable(tmp_path: Path) -> None:
    unavailable = tmp_path / "directory"
    unavailable.mkdir()
    snapshot = evaluate_retail_control_readiness(
        store=SQLiteRetailProductionControlStore(unavailable),
        config=config_at(unavailable),
        observed_at=OBSERVED_AT,
    )
    assert snapshot["readiness_status"] == "not_ready"
    assert "control_store_unavailable" in snapshot["failure_reasons"]


def test_readiness_fails_closed_for_invalid_config_object(tmp_path: Path) -> None:
    store = SQLiteRetailProductionControlStore(tmp_path / "controls.sqlite3")
    store.initialize()
    snapshot = evaluate_retail_control_readiness(
        store=store,
        config=object(),
        observed_at=OBSERVED_AT,
    )
    assert snapshot["readiness_status"] == "not_ready"
    assert "invalid_control_config" in snapshot["failure_reasons"]


def test_readiness_vocabulary_never_claims_production_operation(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    rendered = json.dumps(
        evaluate_retail_control_readiness(store=store, config=config, observed_at=OBSERVED_AT)
    )
    for forbidden in ("production_ready", "production_active", "public_live", "externally_verified"):
        assert forbidden not in rendered


@pytest.mark.parametrize(
    "resource",
    [
        {
            "resource_type": "state_ping",
            "context_status": "partially_resolved",
            "evidence": [{"evidence_id": "evidence-1"}],
            "confidence": {"level": "bounded"},
            "contradictions": [],
            "provenance": [{"source_id": "source-1"}],
            "freshness": {"status": "unknown"},
        },
        {
            "resource_type": "context_delta",
            "context_status": "changed",
            "evidence": [{"evidence_id": "evidence-2"}],
            "confidence": {"direction": "decreased"},
            "contradictions": [{"contradiction_id": "c-1"}],
            "provenance": [{"source_id": "source-2"}],
            "freshness": {"status": "stale"},
            "material_changes": [{"change_id": "change-1"}],
        },
    ],
)
def test_rp7_never_reads_or_mutates_context_content(tmp_path: Path, resource: dict[str, Any]) -> None:
    store, config = controlled_store(tmp_path)
    before = copy.deepcopy(resource)
    admitted(store, config, resource_type=resource["resource_type"])
    evaluate_retail_control_readiness(store=store, config=config, observed_at=OBSERVED_AT)
    assert resource == before


def test_no_generic_authorized_or_epistemic_fields_exist(tmp_path: Path) -> None:
    store, config = controlled_store(tmp_path)
    outputs = [
        admitted(store, config),
        claimed(store),
        evaluate_retail_control_readiness(store=store, config=config, observed_at=OBSERVED_AT),
    ]
    forbidden = {"authorized", "evidence_verified", "context_resolved", "action_approved", "execution_authorized"}
    for output in outputs:
        assert not (set(output) & forbidden)


@pytest.mark.parametrize(
    "module_name",
    ["core.telemetry_engine", "core.usage_meter", "core.cdp_auth", "app", "key_manager"],
)
def test_legacy_operational_imports_are_forbidden(module_name: str) -> None:
    with pytest.raises(RetailIsolationViolation):
        assert_retail_module_allowed(module_name)


def test_retail_isolation_validator_remains_clean() -> None:
    assert validate_retail_package_imports(REPO_ROOT / "retail_context") == []


def test_rp7_source_has_no_endpoint_network_live_or_marketplace_logic() -> None:
    sources = "\n".join(
        (REPO_ROOT / "retail_context" / name).read_text()
        for name in (
            "production_config.py",
            "control_store.py",
            "production_controls.py",
            "production_telemetry.py",
        )
    )
    for forbidden in (
        "FastAPI",
        "APIRouter",
        "import httpx",
        "import requests",
        "HTTPFacilitatorClient",
        "CDP_API_KEY",
        "Render",
        "Bazaar",
        "Marketplace",
    ):
        assert forbidden not in sources


def test_production_control_schema_is_strict_draft_2020_12() -> None:
    schema = load_retail_production_control_schema()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    for record_type in (
        "service_admission",
        "delivery_outcome",
        "telemetry_event",
        "incident",
        "readiness_snapshot",
    ):
        assert schema["$defs"][record_type]["additionalProperties"] is False
