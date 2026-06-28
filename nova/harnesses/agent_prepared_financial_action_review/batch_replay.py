from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .governance_record import build_governance_record
from .reviewer import review_agent_prepared_action
from .schema import AgentPreparedFinancialAction


BATCH_ID = "agent-prepared-financial-action-batch-replay-v0.2"
FORMAL_HARNESS_NAME = "Agent-Prepared Financial Action Review Harness"


def iter_json_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.iterdir() if path.suffix == ".json")


def classify_error(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return "invalid_json"
    if isinstance(exc, (TypeError, ValueError)):
        return "schema_error"
    return "input_error"


def run_batch_replay(input_files: Iterable[Path]) -> dict[str, Any]:
    files = [Path(path) for path in input_files]
    results: list[dict[str, Any]] = []
    input_errors: list[dict[str, Any]] = []
    review_status_counts: Counter[str] = Counter()
    reason_code_counts: Counter[str] = Counter()

    for input_file in files:
        try:
            data = json.loads(input_file.read_text(encoding="utf-8"))
            action = AgentPreparedFinancialAction.from_dict(data)
            review = review_agent_prepared_action(action)
            governance_record = build_governance_record(action, review)

            review_status_counts[review.review_status] += 1
            reason_code_counts.update(review.reason_codes)

            results.append(
                {
                    "input_file": str(input_file),
                    "action_id": action.action_id,
                    "review": review.to_dict(),
                    "governance_record": governance_record,
                }
            )
        except Exception as exc:  # noqa: BLE001 - batch replay should keep going.
            input_errors.append(
                {
                    "input_file": str(input_file),
                    "error_type": classify_error(exc),
                    "message": str(exc),
                }
            )

    return {
        "batch_id": BATCH_ID,
        "harness_version": "v0.2",
        "formal_harness_name": FORMAL_HARNESS_NAME,
        "classification": {
            "offline_replay": True,
            "continuous_operation": False,
            "live_integration": False,
            "execution_capability": False,
            "market_validation": False,
            "production_readiness": False,
            "buyer_validation": False,
        },
        "summary": {
            "total_files_seen": len(files),
            "valid_records": len(results),
            "input_errors": len(input_errors),
            "review_status_counts": dict(review_status_counts),
            "reason_code_counts": dict(reason_code_counts),
        },
        "results": results,
        "input_errors": input_errors,
    }


def run_batch_replay_for_directory(input_dir: Path) -> dict[str, Any]:
    return run_batch_replay(iter_json_files(input_dir))

