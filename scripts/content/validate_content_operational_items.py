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


DEFAULT_PATH = ROOT / "docs/content/content-operational-items.yaml"
ALLOWED_STATUSES = {
    "observed",
    "review_required",
    "due",
    "assigned",
    "in_progress",
    "evidence_submitted",
    "verified_complete",
    "closed",
    "blocked",
    "superseded",
}
COMPLETION_STATUSES = {"verified_complete", "closed"}


def validate_content_operational_items(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = payload.get("operational_items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ContentValidationError("operational items file requires an operational_items list")
    seen: set[str] = set()
    completed = 0
    for item in items:
        if not isinstance(item, dict):
            raise ContentValidationError("each operational item must be a mapping")
        require_fields(
            item,
            (
                "item_id",
                "title",
                "affected_layer",
                "owner",
                "urgency",
                "status",
                "created_at",
                "target_date",
                "completion_condition",
            ),
            "operational item",
        )
        item_id = str(item["item_id"])
        if item_id in seen:
            raise ContentValidationError(f"duplicate item_id: {item_id}")
        seen.add(item_id)
        status = item["status"]
        if status not in ALLOWED_STATUSES:
            raise ContentValidationError(f"{item_id} has unsupported status: {status}")
        if status in COMPLETION_STATUSES:
            completed += 1
            evidence = item.get("completion_evidence")
            if not isinstance(evidence, dict):
                raise ContentValidationError(f"completed item {item_id} requires completion_evidence")
            require_fields(evidence, ("artifact_path", "verified_at", "verified_by"), f"completed item {item_id}")
            has_measurement = not is_blank(evidence.get("measurement_records"))
            has_review = not is_blank(evidence.get("review_record"))
            if not has_measurement and not has_review:
                raise ContentValidationError(f"completed item {item_id} requires measurement or review evidence")
    return {
        "status": "passed",
        "path": display_path(path),
        "item_count": len(items),
        "completed_item_count": completed,
    }


if __name__ == "__main__":
    run_cli(validate_content_operational_items, DEFAULT_PATH)
