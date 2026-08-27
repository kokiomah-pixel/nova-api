from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Protocol


SERVICE_MODES = frozenset({"disabled", "controlled_proof"})
DELIVERY_STATUSES = frozenset({"pending", "delivered", "failed"})
REQUIRED_TABLES = frozenset(
    {
        "retail_control_schema",
        "retail_service_state",
        "retail_rate_limits",
        "retail_payment_consumption",
        "retail_operational_telemetry",
        "retail_operational_incidents",
    }
)


@dataclass(frozen=True)
class RateLimitDecision:
    permitted: bool
    request_count: int
    limit: int
    window_started_at_epoch: int


@dataclass(frozen=True)
class PaymentClaimDecision:
    claimed: bool
    failure_reason: str | None
    record: Mapping[str, Any] | None


class RetailProductionControlStore(Protocol):
    db_path: Path

    def initialize(self) -> None: ...
    def is_healthy(self) -> bool: ...
    def get_service_mode(self) -> str: ...
    def set_service_mode(self, mode: str, *, changed_at: str) -> None: ...
    def consume_rate_limit(
        self,
        *,
        subject_hash: str,
        resource_type: str,
        window_started_at_epoch: int,
        limit: int,
        observed_at: str,
    ) -> RateLimitDecision: ...
    def claim_payment(self, record: Mapping[str, Any]) -> PaymentClaimDecision: ...
    def mark_delivery(
        self,
        *,
        claim_id: str,
        status: str,
        occurred_at: str,
        response_digest: str | None = None,
        response_bytes: int | None = None,
        processing_duration_ms: int | None = None,
        failure_reason: str | None = None,
    ) -> Mapping[str, Any]: ...
    def record_telemetry(self, event: Mapping[str, Any]) -> None: ...
    def record_incident(self, incident: Mapping[str, Any]) -> None: ...
    def health_snapshot(self) -> Mapping[str, bool]: ...


class SQLiteRetailProductionControlStore:
    """Transactional, durable single-node retail production-control store."""

    def __init__(self, db_path: str | Path, *, timeout_seconds: float = 5.0) -> None:
        self.db_path = Path(db_path).expanduser()
        self.timeout_seconds = timeout_seconds

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            str(self.db_path),
            timeout=self.timeout_seconds,
            isolation_level=None,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS retail_control_schema (
                    schema_version TEXT PRIMARY KEY,
                    initialized_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS retail_service_state (
                    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
                    operating_mode TEXT NOT NULL
                        CHECK (operating_mode IN ('disabled', 'controlled_proof')),
                    changed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS retail_rate_limits (
                    subject_hash TEXT NOT NULL,
                    resource_type TEXT NOT NULL
                        CHECK (resource_type IN ('state_ping', 'context_delta')),
                    window_started_at_epoch INTEGER NOT NULL,
                    request_count INTEGER NOT NULL CHECK (request_count > 0),
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (subject_hash, resource_type, window_started_at_epoch)
                );

                CREATE TABLE IF NOT EXISTS retail_payment_consumption (
                    claim_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    payment_receipt_id TEXT NOT NULL UNIQUE,
                    payment_requirement_id TEXT NOT NULL,
                    network TEXT NOT NULL,
                    transaction_reference TEXT NOT NULL,
                    payer TEXT,
                    resource_type TEXT NOT NULL
                        CHECK (resource_type IN ('state_ping', 'context_delta')),
                    resource_uri TEXT NOT NULL,
                    amount_atomic TEXT NOT NULL,
                    settlement_wallet TEXT NOT NULL,
                    claimed_at TEXT NOT NULL,
                    delivery_status TEXT NOT NULL
                        CHECK (delivery_status IN ('pending', 'delivered', 'failed')),
                    delivered_at TEXT,
                    failed_at TEXT,
                    response_digest TEXT,
                    response_bytes INTEGER CHECK (response_bytes IS NULL OR response_bytes >= 0),
                    processing_duration_ms INTEGER
                        CHECK (processing_duration_ms IS NULL OR processing_duration_ms >= 0),
                    delivery_failure_reason TEXT,
                    authority_effect TEXT NOT NULL CHECK (authority_effect = 'none'),
                    UNIQUE (network, transaction_reference)
                );

                CREATE TABLE IF NOT EXISTS retail_operational_telemetry (
                    event_id TEXT PRIMARY KEY,
                    occurred_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    resource_type TEXT,
                    subject_hash TEXT,
                    payment_receipt_id TEXT,
                    payment_requirement_id TEXT,
                    transaction_reference_hash TEXT,
                    duration_ms INTEGER CHECK (duration_ms IS NULL OR duration_ms >= 0),
                    response_bytes INTEGER CHECK (response_bytes IS NULL OR response_bytes >= 0),
                    failure_reason TEXT,
                    retail_namespace TEXT NOT NULL CHECK (retail_namespace = 'retail_production_controls'),
                    authority_effect TEXT NOT NULL CHECK (authority_effect = 'none')
                );

                CREATE TABLE IF NOT EXISTS retail_operational_incidents (
                    incident_id TEXT PRIMARY KEY,
                    occurred_at TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    request_id TEXT,
                    resource_type TEXT,
                    payment_receipt_id TEXT,
                    failure_reason TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    retail_namespace TEXT NOT NULL CHECK (retail_namespace = 'retail_production_controls'),
                    authority_effect TEXT NOT NULL CHECK (authority_effect = 'none')
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO retail_control_schema "
                "(schema_version, initialized_at) VALUES ('0.1.0', 'schema-initialization')"
            )
            connection.execute(
                "INSERT OR IGNORE INTO retail_service_state "
                "(singleton_id, operating_mode, changed_at) "
                "VALUES (1, 'disabled', 'schema-initialization')"
            )

    def get_service_mode(self) -> str:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT operating_mode FROM retail_service_state WHERE singleton_id = 1"
            ).fetchone()
        if row is None:
            raise RuntimeError("control_store_unavailable")
        return str(row["operating_mode"])

    def set_service_mode(self, mode: str, *, changed_at: str) -> None:
        if mode not in SERVICE_MODES:
            raise ValueError("unsupported_service_mode")
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE retail_service_state SET operating_mode = ?, changed_at = ? "
                "WHERE singleton_id = 1",
                (mode, changed_at),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise RuntimeError("control_store_unavailable")
            connection.commit()

    def consume_rate_limit(
        self,
        *,
        subject_hash: str,
        resource_type: str,
        window_started_at_epoch: int,
        limit: int,
        observed_at: str,
    ) -> RateLimitDecision:
        if resource_type not in {"state_ping", "context_delta"} or limit <= 0:
            raise ValueError("invalid_rate_limit")
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT request_count FROM retail_rate_limits "
                "WHERE subject_hash = ? AND resource_type = ? "
                "AND window_started_at_epoch = ?",
                (subject_hash, resource_type, window_started_at_epoch),
            ).fetchone()
            current_count = 0 if row is None else int(row["request_count"])
            if current_count >= limit:
                connection.commit()
                return RateLimitDecision(
                    permitted=False,
                    request_count=current_count,
                    limit=limit,
                    window_started_at_epoch=window_started_at_epoch,
                )
            new_count = current_count + 1
            connection.execute(
                "INSERT INTO retail_rate_limits "
                "(subject_hash, resource_type, window_started_at_epoch, request_count, updated_at) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(subject_hash, resource_type, window_started_at_epoch) "
                "DO UPDATE SET request_count = excluded.request_count, "
                "updated_at = excluded.updated_at",
                (
                    subject_hash,
                    resource_type,
                    window_started_at_epoch,
                    new_count,
                    observed_at,
                ),
            )
            connection.commit()
        return RateLimitDecision(
            permitted=True,
            request_count=new_count,
            limit=limit,
            window_started_at_epoch=window_started_at_epoch,
        )

    @staticmethod
    def _payment_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return None if row is None else dict(row)

    def claim_payment(self, record: Mapping[str, Any]) -> PaymentClaimDecision:
        columns = (
            "claim_id",
            "request_id",
            "payment_receipt_id",
            "payment_requirement_id",
            "network",
            "transaction_reference",
            "payer",
            "resource_type",
            "resource_uri",
            "amount_atomic",
            "settlement_wallet",
            "claimed_at",
            "delivery_status",
            "authority_effect",
        )
        values = tuple(record[column] for column in columns)
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    f"INSERT INTO retail_payment_consumption ({', '.join(columns)}) "
                    f"VALUES ({', '.join('?' for _ in columns)})",
                    values,
                )
            except sqlite3.IntegrityError:
                transaction_row = connection.execute(
                    "SELECT * FROM retail_payment_consumption "
                    "WHERE network = ? AND transaction_reference = ?",
                    (record["network"], record["transaction_reference"]),
                ).fetchone()
                receipt_row = connection.execute(
                    "SELECT * FROM retail_payment_consumption WHERE payment_receipt_id = ?",
                    (record["payment_receipt_id"],),
                ).fetchone()
                connection.rollback()
                existing = transaction_row or receipt_row
                if transaction_row is not None and all(
                    transaction_row[field] == record[field]
                    for field in (
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
                ):
                    return PaymentClaimDecision(
                        claimed=False,
                        failure_reason="payment_already_consumed",
                        record=self._payment_row(existing),
                    )
                return PaymentClaimDecision(
                    claimed=False,
                    failure_reason="payment_replay_conflict",
                    record=self._payment_row(existing),
                )
            connection.commit()
            row = connection.execute(
                "SELECT * FROM retail_payment_consumption WHERE claim_id = ?",
                (record["claim_id"],),
            ).fetchone()
        return PaymentClaimDecision(
            claimed=True,
            failure_reason=None,
            record=self._payment_row(row),
        )

    def get_payment_claim(self, claim_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM retail_payment_consumption WHERE claim_id = ?",
                (claim_id,),
            ).fetchone()
        return self._payment_row(row)

    def mark_delivery(
        self,
        *,
        claim_id: str,
        status: str,
        occurred_at: str,
        response_digest: str | None = None,
        response_bytes: int | None = None,
        processing_duration_ms: int | None = None,
        failure_reason: str | None = None,
    ) -> Mapping[str, Any]:
        if status not in {"delivered", "failed"}:
            raise ValueError("invalid_delivery_status")
        delivered_at = occurred_at if status == "delivered" else None
        failed_at = occurred_at if status == "failed" else None
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE retail_payment_consumption SET delivery_status = ?, "
                "delivered_at = ?, failed_at = ?, response_digest = ?, "
                "response_bytes = ?, processing_duration_ms = ?, "
                "delivery_failure_reason = ? "
                "WHERE claim_id = ? AND delivery_status = 'pending'",
                (
                    status,
                    delivered_at,
                    failed_at,
                    response_digest,
                    response_bytes,
                    processing_duration_ms,
                    failure_reason,
                    claim_id,
                ),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise ValueError("invalid_delivery_state")
            connection.commit()
            row = connection.execute(
                "SELECT * FROM retail_payment_consumption WHERE claim_id = ?",
                (claim_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("control_store_unavailable")
        return dict(row)

    def record_telemetry(self, event: Mapping[str, Any]) -> None:
        columns = (
            "event_id",
            "occurred_at",
            "event_type",
            "request_id",
            "resource_type",
            "subject_hash",
            "payment_receipt_id",
            "payment_requirement_id",
            "transaction_reference_hash",
            "duration_ms",
            "response_bytes",
            "failure_reason",
            "retail_namespace",
            "authority_effect",
        )
        with self._connection() as connection:
            connection.execute(
                f"INSERT OR IGNORE INTO retail_operational_telemetry "
                f"({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
                tuple(event[column] for column in columns),
            )

    def record_incident(self, incident: Mapping[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO retail_operational_incidents "
                "(incident_id, occurred_at, incident_type, request_id, resource_type, "
                "payment_receipt_id, failure_reason, details_json, retail_namespace, "
                "authority_effect) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    incident["incident_id"],
                    incident["occurred_at"],
                    incident["incident_type"],
                    incident["request_id"],
                    incident["resource_type"],
                    incident["payment_receipt_id"],
                    incident["failure_reason"],
                    json.dumps(
                        incident["details"], separators=(",", ":"), sort_keys=True
                    ),
                    incident["retail_namespace"],
                    incident["authority_effect"],
                ),
            )

    def list_telemetry(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM retail_operational_telemetry ORDER BY occurred_at, event_id"
            ).fetchall()
        return [dict(row) for row in rows]

    def list_incidents(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM retail_operational_incidents ORDER BY occurred_at, incident_id"
            ).fetchall()
        return [dict(row) for row in rows]

    def count_payment_claims(self) -> int:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM retail_payment_consumption"
            ).fetchone()
        return int(row["count"])

    def health_snapshot(self) -> Mapping[str, bool]:
        try:
            with self._connection() as connection:
                connection.execute("BEGIN IMMEDIATE")
                tables = {
                    str(row["name"])
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                }
                connection.rollback()
            schema_initialized = REQUIRED_TABLES.issubset(tables)
            return {
                "control_store_open": True,
                "schema_initialized": schema_initialized,
                "payment_persistence_available": "retail_payment_consumption" in tables,
                "telemetry_persistence_available": "retail_operational_telemetry" in tables,
            }
        except (OSError, sqlite3.Error):
            return {
                "control_store_open": False,
                "schema_initialized": False,
                "payment_persistence_available": False,
                "telemetry_persistence_available": False,
            }

    def is_healthy(self) -> bool:
        return all(self.health_snapshot().values())
