#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.content.validation_common import (
        ROOT,
        ContentValidationError,
        display_path,
        is_blank,
        require_fields,
        run_cli,
    )
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from validation_common import (  # type: ignore[no-redef]
        ROOT,
        ContentValidationError,
        display_path,
        is_blank,
        require_fields,
        run_cli,
    )


DEFAULT_PATH = ROOT / "docs/content/content-experiment-register.yaml"
ALLOWED_STATUSES = {"proposed", "approved", "active", "complete", "inconclusive", "promoted", "rejected"}
ALLOWED_PROMOTION = {"observation_only", "provisional_pattern", "candidate_rule", "canonical_rule"}
REQUIRED_WINDOWS = {"24_hours", "7_days", "30_days"}


def validate_experiment_register(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    experiments = payload.get("experiments") if isinstance(payload, dict) else None
    if not isinstance(experiments, list):
        raise ContentValidationError("experiment register requires an experiments list")
    seen: set[str] = set()
    active_count = 0
    approved_count = 0
    for experiment in experiments:
        if not isinstance(experiment, dict):
            raise ContentValidationError("each experiment must be a mapping")
        require_fields(
            experiment,
            (
                "experiment_id",
                "status",
                "hypothesis",
                "target_audience",
                "narrative_pillar",
                "variable_changed",
                "control_pattern",
                "test_pattern",
                "primary_metric",
                "audience_quality_metric",
                "narrative_accuracy_metric",
                "promotion_status",
            ),
            "experiment",
        )
        experiment_id = str(experiment["experiment_id"])
        if experiment_id in seen:
            raise ContentValidationError(f"duplicate experiment_id: {experiment_id}")
        seen.add(experiment_id)
        status = experiment["status"]
        if status not in ALLOWED_STATUSES:
            raise ContentValidationError(f"{experiment_id} has unsupported status: {status}")
        if status == "active":
            active_count += 1
        if status == "approved":
            approved_count += 1
            require_fields(
                experiment,
                ("activation_condition", "approved_by"),
                f"approved experiment {experiment_id}",
            )
        windows = set(experiment.get("measurement_windows") or [])
        if windows != REQUIRED_WINDOWS:
            raise ContentValidationError(f"{experiment_id} requires all standard measurement windows")
        promotion = experiment["promotion_status"]
        if promotion not in ALLOWED_PROMOTION:
            raise ContentValidationError(f"{experiment_id} has unsupported promotion status: {promotion}")
        if status in {"complete", "promoted"}:
            require_fields(
                experiment,
                ("posts_included", "result", "measurement_evidence", "evidence_strength", "interpretation"),
                f"completed experiment {experiment_id}",
            )
        if status == "promoted" or promotion == "canonical_rule":
            if is_blank(experiment.get("approved_by")):
                raise ContentValidationError(f"promoted experiment {experiment_id} requires approval")
    if active_count > 3:
        raise ContentValidationError("no more than three experiments may be active")
    return {
        "status": "passed",
        "path": display_path(path),
        "experiment_count": len(experiments),
        "active_experiment_count": active_count,
        "approved_experiment_count": approved_count,
    }


if __name__ == "__main__":
    run_cli(validate_experiment_register, DEFAULT_PATH)
