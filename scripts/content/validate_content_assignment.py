#!/usr/bin/env python3
from __future__ import annotations

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


DEFAULT_PATH = ROOT / "docs/content/templates/post-brief-template.md"
REQUIRED_FIELDS = (
    "assignment_id",
    "publication_target_date",
    "intended_audience",
    "audience_stage",
    "narrative_pillar",
    "governed_distinction",
    "institutional_scenario",
    "content_objective",
    "desired_reader_understanding",
    "prohibited_misunderstanding",
    "content_pattern",
    "hook_direction",
    "CTA_direction",
    "media_format",
)


def validate_content_assignment(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    assignment = find_mapping(path, "content_assignment")
    require_fields(assignment, REQUIRED_FIELDS, "content_assignment")
    if isinstance(assignment["intended_audience"], list):
        if len(assignment["intended_audience"]) != 1:
            raise ContentValidationError("assignment must name exactly one intended audience")
    if isinstance(assignment["narrative_pillar"], list):
        if len(assignment["narrative_pillar"]) != 1:
            raise ContentValidationError("assignment must name exactly one narrative pillar")
    if not is_blank(assignment.get("experiment_id")):
        require_fields(
            assignment,
            ("variable_being_tested", "control_requirements"),
            "experimental content_assignment",
        )
    return {
        "status": "passed",
        "path": display_path(path),
        "assignment_id": assignment["assignment_id"],
        "experiment_id": assignment.get("experiment_id"),
    }


if __name__ == "__main__":
    run_cli(validate_content_assignment, DEFAULT_PATH)
