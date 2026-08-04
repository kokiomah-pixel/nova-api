#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts.content.validation_common import (
        ROOT,
        ContentValidationError,
        display_path,
        find_mapping,
        is_blank,
        require_fields,
        run_cli,
    )
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from validation_common import (  # type: ignore[no-redef]
        ROOT,
        ContentValidationError,
        display_path,
        find_mapping,
        is_blank,
        require_fields,
        run_cli,
    )


DEFAULT_PATH = ROOT / "docs/content/templates/post-record-template.yaml"
ALLOWED_STATUSES = {"draft", "approved", "published", "archived"}
REQUIRED_WINDOWS = {"24_hours", "7_days", "30_days"}
PLACEHOLDER_COPY = {"[Exact published text]", "exact_published_text", "TODO", "TBD"}


def _markdown_published_copy(path: Path) -> str | None:
    if path.suffix.lower() != ".md":
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"^## Final published copy\s*\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else None


def validate_post_record(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    record = find_mapping(path, "post_record") if path.suffix.lower() != ".md" else None
    if record is None:
        post = find_mapping(path, "post")
        record = {"post": post}
        try:
            record["measurement_schedule"] = find_mapping(path, "measurement_schedule")
        except ContentValidationError:
            pass
    post = record.get("post")
    if not isinstance(post, dict):
        raise ContentValidationError("post_record.post must be a mapping")
    require_fields(
        post,
        (
            "post_id",
            "status",
            "intended_audience",
            "narrative_pillar",
            "governed_distinction",
        ),
        "post",
    )
    status = post["status"]
    if status not in ALLOWED_STATUSES:
        raise ContentValidationError(f"unsupported post status: {status}")

    schedule = record.get("measurement_schedule")
    if not isinstance(schedule, dict):
        raise ContentValidationError("post record requires a measurement_schedule")
    due = schedule.get("due")
    if not isinstance(due, list):
        raise ContentValidationError("measurement_schedule.due must be a list")
    windows = {entry.get("window") for entry in due if isinstance(entry, dict)}
    if windows != REQUIRED_WINDOWS:
        raise ContentValidationError("measurement schedule must contain 24_hours, 7_days, and 30_days")
    if status == "published":
        require_fields(post, ("publication_date", "post_url"), "published post")
        copy = record.get("final_published_copy") or _markdown_published_copy(path)
        if is_blank(copy) or str(copy).strip() in PLACEHOLDER_COPY:
            raise ContentValidationError("published post requires exact final published copy")
        for entry in due:
            if not isinstance(entry, dict) or is_blank(entry.get("date")):
                raise ContentValidationError("published post measurement windows require due dates")

    experiment_id = post.get("experiment_id")
    if post.get("experiment_applicable") is True and is_blank(experiment_id):
        raise ContentValidationError("experiment-applicable post requires experiment_id")
    return {
        "status": "passed",
        "path": display_path(path),
        "post_id": post["post_id"],
        "publication_status": status,
        "measurement_windows": sorted(windows),
    }


if __name__ == "__main__":
    run_cli(validate_post_record, DEFAULT_PATH)
