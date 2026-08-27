from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.production_config import (
    CONTEXT_DELTA_MAX_REQUESTS_ENV,
    CONTROL_DB_ENV,
    RATE_LIMIT_WINDOW_ENV,
    STATE_PING_MAX_REQUESTS_ENV,
    RetailProductionControlConfig,
    RetailProductionControlConfigError,
)
from retail_context.production_controls import set_retail_service_mode


OBSERVED_AT = "2026-08-27T12:00:00Z"


def store_at(tmp_path: Path) -> SQLiteRetailProductionControlStore:
    store = SQLiteRetailProductionControlStore(tmp_path / "production_controls.sqlite3")
    store.initialize()
    return store


def test_default_service_state_is_disabled(tmp_path: Path) -> None:
    assert store_at(tmp_path).get_service_mode() == "disabled"


@pytest.mark.parametrize("mode", ["public", "live", "production_active"])
def test_public_or_live_service_modes_are_rejected(tmp_path: Path, mode: str) -> None:
    store = store_at(tmp_path)
    with pytest.raises(ValueError, match="unsupported_service_mode"):
        set_retail_service_mode(store=store, mode=mode, changed_at=OBSERVED_AT)
    assert store.get_service_mode() == "disabled"


def test_controlled_proof_can_be_explicitly_enabled(tmp_path: Path) -> None:
    store = store_at(tmp_path)
    set_retail_service_mode(
        store=store, mode="controlled_proof", changed_at=OBSERVED_AT
    )
    assert store.get_service_mode() == "controlled_proof"


def test_service_state_survives_store_reopen(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    first = SQLiteRetailProductionControlStore(path)
    first.initialize()
    set_retail_service_mode(
        store=first, mode="controlled_proof", changed_at=OBSERVED_AT
    )
    reopened = SQLiteRetailProductionControlStore(path)
    reopened.initialize()
    assert reopened.get_service_mode() == "controlled_proof"
    set_retail_service_mode(
        store=reopened, mode="disabled", changed_at="2026-08-27T12:01:00Z"
    )
    assert SQLiteRetailProductionControlStore(path).get_service_mode() == "disabled"


@pytest.mark.parametrize(
    "values",
    [
        (0, 1, 1),
        (-1, 1, 1),
        (60, 0, 1),
        (60, 1, 0),
        (True, 1, 1),
    ],
)
def test_invalid_direct_control_config_fails_closed(
    tmp_path: Path, values: tuple[object, object, object]
) -> None:
    with pytest.raises(RetailProductionControlConfigError):
        RetailProductionControlConfig(tmp_path / "controls.sqlite3", *values)  # type: ignore[arg-type]


def test_missing_required_env_control_config_fails_closed() -> None:
    with pytest.raises(RetailProductionControlConfigError):
        RetailProductionControlConfig.from_env({})


def test_control_config_uses_only_retail_owned_env(tmp_path: Path) -> None:
    path = tmp_path / "configured.sqlite3"
    config = RetailProductionControlConfig.from_env(
        {
            CONTROL_DB_ENV: str(path),
            RATE_LIMIT_WINDOW_ENV: "60",
            STATE_PING_MAX_REQUESTS_ENV: "3",
            CONTEXT_DELTA_MAX_REQUESTS_ENV: "2",
            "NOVA_RATE_LIMIT_WINDOW_SECONDS": "1",
            "X402_RATE_LIMIT_WINDOW_SECONDS": "1",
            "CDP_API_KEY_ID": "not-used",
            "STRIPE_API_KEY": "not-used",
        }
    )
    assert config.control_db_path == path
    assert config.rate_limit_window_seconds == 60
    assert config.state_ping_max_requests == 3
    assert config.context_delta_max_requests == 2


def test_default_control_path_is_inside_retail_state_namespace(tmp_path: Path) -> None:
    config = RetailProductionControlConfig.from_env(
        {
            "NOVA_RETAIL_STATE_DIR": str(tmp_path / "retail"),
            RATE_LIMIT_WINDOW_ENV: "60",
            STATE_PING_MAX_REQUESTS_ENV: "3",
            CONTEXT_DELTA_MAX_REQUESTS_ENV: "2",
        }
    )
    assert config.control_db_path == tmp_path / "retail" / "production_controls.sqlite3"


def test_rate_limit_exact_boundary_is_deterministic(tmp_path: Path) -> None:
    store = store_at(tmp_path)
    decisions = [
        store.consume_rate_limit(
            subject_hash="a" * 64,
            resource_type="state_ping",
            window_started_at_epoch=100,
            limit=2,
            observed_at=OBSERVED_AT,
        )
        for _ in range(3)
    ]
    assert [item.permitted for item in decisions] == [True, True, False]
    assert [item.request_count for item in decisions] == [1, 2, 2]


def test_rate_limit_state_persists_across_reopen(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    first = SQLiteRetailProductionControlStore(path)
    first.initialize()
    first.consume_rate_limit(
        subject_hash="a" * 64,
        resource_type="state_ping",
        window_started_at_epoch=100,
        limit=1,
        observed_at=OBSERVED_AT,
    )
    reopened = SQLiteRetailProductionControlStore(path)
    decision = reopened.consume_rate_limit(
        subject_hash="a" * 64,
        resource_type="state_ping",
        window_started_at_epoch=100,
        limit=1,
        observed_at=OBSERVED_AT,
    )
    assert not decision.permitted
    assert decision.request_count == 1


def test_separate_subjects_and_resources_have_separate_counters(tmp_path: Path) -> None:
    store = store_at(tmp_path)
    for subject_hash, resource_type in (
        ("a" * 64, "state_ping"),
        ("b" * 64, "state_ping"),
        ("a" * 64, "context_delta"),
    ):
        decision = store.consume_rate_limit(
            subject_hash=subject_hash,
            resource_type=resource_type,
            window_started_at_epoch=100,
            limit=1,
            observed_at=OBSERVED_AT,
        )
        assert decision.permitted
        assert decision.request_count == 1


def test_different_fixed_window_resets_counter(tmp_path: Path) -> None:
    store = store_at(tmp_path)
    first = store.consume_rate_limit(
        subject_hash="a" * 64,
        resource_type="state_ping",
        window_started_at_epoch=100,
        limit=1,
        observed_at=OBSERVED_AT,
    )
    second = store.consume_rate_limit(
        subject_hash="a" * 64,
        resource_type="state_ping",
        window_started_at_epoch=160,
        limit=1,
        observed_at="2026-08-27T12:01:00Z",
    )
    assert first.permitted and second.permitted
    assert first.request_count == second.request_count == 1


def test_concurrent_rate_limit_boundary_has_exact_winners(tmp_path: Path) -> None:
    path = tmp_path / "controls.sqlite3"
    store = SQLiteRetailProductionControlStore(path)
    store.initialize()

    def attempt(index: int) -> bool:
        worker = SQLiteRetailProductionControlStore(path)
        return worker.consume_rate_limit(
            subject_hash="a" * 64,
            resource_type="state_ping",
            window_started_at_epoch=100,
            limit=3,
            observed_at=f"2026-08-27T12:00:0{index}Z",
        ).permitted

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(attempt, range(8)))
    assert results.count(True) == 3
    assert results.count(False) == 5


def test_store_health_is_false_before_schema_initialization(tmp_path: Path) -> None:
    store = SQLiteRetailProductionControlStore(tmp_path / "not-initialized.sqlite3")
    snapshot = store.health_snapshot()
    assert snapshot["control_store_open"] is True
    assert snapshot["schema_initialized"] is False
    assert not store.is_healthy()


def test_store_health_fails_closed_for_unopenable_database(tmp_path: Path) -> None:
    directory_path = tmp_path / "directory-not-database"
    directory_path.mkdir()
    store = SQLiteRetailProductionControlStore(directory_path)
    assert not store.is_healthy()
