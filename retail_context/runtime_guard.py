from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class RetryDecision:
    permitted: bool
    retry_count: int
    retry_limit: int
    continuation_exempt: bool


class SQLiteRetailRuntimeGuard:
    """RP8-only durable guard for source binding and bounded same-request retries."""

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
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        return connection

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS retail_runtime_guards (
                    request_id TEXT PRIMARY KEY,
                    source_binding_digest TEXT NOT NULL,
                    payment_continuation_used INTEGER NOT NULL DEFAULT 0
                        CHECK (payment_continuation_used IN (0, 1)),
                    retry_window_started_at_epoch INTEGER,
                    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
                    updated_at TEXT NOT NULL,
                    authority_effect TEXT NOT NULL CHECK (authority_effect = 'none')
                )
                """
            )
        finally:
            connection.close()

    @staticmethod
    def _window_epoch(observed_at: str, window_seconds: int) -> int:
        parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        epoch = int(parsed.timestamp())
        return epoch - (epoch % window_seconds)

    def initialize_request(
        self,
        *,
        request_id: str,
        source_binding_digest: str,
        observed_at: str,
        payment_already_present: bool,
    ) -> None:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM retail_runtime_guards WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO retail_runtime_guards "
                    "(request_id, source_binding_digest, payment_continuation_used, "
                    "retry_window_started_at_epoch, retry_count, updated_at, authority_effect) "
                    "VALUES (?, ?, ?, NULL, 0, ?, 'none')",
                    (
                        request_id,
                        source_binding_digest,
                        1 if payment_already_present else 0,
                        observed_at,
                    ),
                )
                connection.commit()
                return
            if (
                row["source_binding_digest"] != source_binding_digest
                or row["authority_effect"] != "none"
            ):
                connection.rollback()
                raise ValueError("source_binding_reconciliation_failed")
            if payment_already_present and not row["payment_continuation_used"]:
                connection.execute(
                    "UPDATE retail_runtime_guards SET payment_continuation_used = 1, "
                    "updated_at = ? WHERE request_id = ?",
                    (observed_at, request_id),
                )
            connection.commit()
        finally:
            connection.close()

    def consume_existing_attempt(
        self,
        *,
        request_id: str,
        source_binding_digest: str,
        payment_present: bool,
        observed_at: str,
        window_seconds: int,
        retry_limit: int,
    ) -> RetryDecision:
        if window_seconds <= 0 or retry_limit <= 0:
            raise ValueError("invalid_retry_limit")
        window_epoch = self._window_epoch(observed_at, window_seconds)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM retail_runtime_guards WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if row is None:
                connection.rollback()
                raise RuntimeError("runtime_guard_unavailable")
            if (
                row["source_binding_digest"] != source_binding_digest
                or row["authority_effect"] != "none"
            ):
                connection.rollback()
                raise ValueError("source_binding_reconciliation_failed")

            if payment_present and not bool(row["payment_continuation_used"]):
                connection.execute(
                    "UPDATE retail_runtime_guards SET payment_continuation_used = 1, "
                    "updated_at = ? WHERE request_id = ?",
                    (observed_at, request_id),
                )
                connection.commit()
                return RetryDecision(
                    permitted=True,
                    retry_count=int(row["retry_count"]),
                    retry_limit=retry_limit,
                    continuation_exempt=True,
                )

            current_count = (
                int(row["retry_count"])
                if row["retry_window_started_at_epoch"] == window_epoch
                else 0
            )
            if current_count >= retry_limit:
                connection.commit()
                return RetryDecision(
                    permitted=False,
                    retry_count=current_count,
                    retry_limit=retry_limit,
                    continuation_exempt=False,
                )
            new_count = current_count + 1
            connection.execute(
                "UPDATE retail_runtime_guards SET retry_window_started_at_epoch = ?, "
                "retry_count = ?, updated_at = ? WHERE request_id = ?",
                (window_epoch, new_count, observed_at, request_id),
            )
            connection.commit()
            return RetryDecision(
                permitted=True,
                retry_count=new_count,
                retry_limit=retry_limit,
                continuation_exempt=False,
            )
        finally:
            connection.close()

    def get_request_guard(self, request_id: str) -> dict[str, object] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM retail_runtime_guards WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        finally:
            connection.close()
        return None if row is None else dict(row)
