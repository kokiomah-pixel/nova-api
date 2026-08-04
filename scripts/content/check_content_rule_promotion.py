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
        run_cli,
    )
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from validation_common import (  # type: ignore[no-redef]
        ROOT,
        ContentValidationError,
        display_path,
        find_mapping,
        is_blank,
        run_cli,
    )


DEFAULT_PATH = ROOT / "docs/content/templates/content-os-change-proposal.md"
ALLOWED_PROMOTIONS = {"observation_only", "provisional_pattern", "candidate_rule", "canonical_rule"}
APPROVED_STATUSES = {"approved", "accepted"}


def check_content_rule_promotion(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    proposal = find_mapping(path, "content_OS_change_proposal")
    requested = proposal.get("requested_promotion_status")
    if is_blank(requested):
        raise ContentValidationError("change proposal requires requested_promotion_status")
    if requested not in ALLOWED_PROMOTIONS:
        raise ContentValidationError(f"unsupported promotion status: {requested}")
    posts = set(proposal.get("supporting_posts") or [])
    pillars = set(proposal.get("supporting_pillars") or [])
    months = set(proposal.get("supporting_months") or [])
    windows = set(proposal.get("supporting_measurement_windows") or [])
    if requested == "provisional_pattern" and (len(posts) < 3 or not windows):
        raise ContentValidationError("provisional pattern requires three comparable posts and window evidence")
    if requested in {"candidate_rule", "canonical_rule"}:
        if len(posts) < 3 or not windows or (len(pillars) < 2 and len(months) < 2):
            raise ContentValidationError("candidate rule requires repeated evidence across pillars or two months")
    if requested == "canonical_rule":
        if proposal.get("approval_status") not in APPROVED_STATUSES or is_blank(proposal.get("approved_by")):
            raise ContentValidationError("canonical rule requires explicit Architect or CCO approval")
    return {
        "status": "passed",
        "path": display_path(path),
        "requested_promotion_status": requested,
        "supporting_post_count": len(posts),
    }


if __name__ == "__main__":
    run_cli(check_content_rule_promotion, DEFAULT_PATH)
