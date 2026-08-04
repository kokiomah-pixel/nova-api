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
        validate_content_approval,
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
        validate_content_approval,
    )


DEFAULT_PATH = ROOT / "docs/content/monthly/2026-08-content-performance-review.md"
ENGAGEMENT_ONLY_BASES = {"engagement_only", "impressions_only", "likes_only", "follower_growth_only"}


def validate_monthly_review(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    review = find_mapping(path, "monthly_review_validation")
    require_fields(review, ("month", "demand_claim_basis"), "monthly_review_validation")
    if review["demand_claim_basis"] in ENGAGEMENT_ONLY_BASES:
        raise ContentValidationError("demand claims may not be based only on engagement")
    comparisons = review.get("measurement_window_comparisons") or []
    if not isinstance(comparisons, list):
        raise ContentValidationError("measurement_window_comparisons must be a list")
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            raise ContentValidationError("measurement-window comparison must be a mapping")
        windows = set(comparison.get("windows") or [])
        if len(windows) > 1 and is_blank(comparison.get("inconsistency_disclosed")):
            raise ContentValidationError("unlike measurement windows require explicit disclosure")
    canonical_changes = review.get("canonical_rule_changes") or []
    if not isinstance(canonical_changes, list):
        raise ContentValidationError("canonical_rule_changes must be a list")
    for change in canonical_changes:
        if not isinstance(change, dict):
            raise ContentValidationError("canonical rule change must be a mapping")
        validate_content_approval(change.get("approval"), "canonical rule change")
        require_fields(change, ("supporting_posts", "supporting_measurement_windows"), "canonical rule change")
    findings = review.get("findings") or []
    if not isinstance(findings, list):
        raise ContentValidationError("findings must be a list")
    for finding in findings:
        if not isinstance(finding, dict):
            raise ContentValidationError("monthly finding must be a mapping")
        require_fields(
            finding,
            ("finding_id", "observed", "inferred", "recommended_test", "evidence_strength"),
            "monthly finding",
        )
        if not is_blank(finding.get("accepted_rule")):
            if is_blank(finding.get("supporting_posts")) or is_blank(finding.get("supporting_measurement_windows")):
                raise ContentValidationError("accepted rule requires supporting post and window evidence")
            validate_content_approval(finding.get("approval"), "accepted monthly rule")
    return {
        "status": "passed",
        "path": display_path(path),
        "month": review["month"],
        "finding_count": len(findings),
        "canonical_rule_change_count": len(canonical_changes),
    }


if __name__ == "__main__":
    run_cli(validate_monthly_review, DEFAULT_PATH)
