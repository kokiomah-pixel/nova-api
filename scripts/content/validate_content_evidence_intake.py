#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

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


DEFAULT_PATH = ROOT / "docs/content/templates/content-evidence-intake.yaml"
INTAKE_ID_PATTERN = re.compile(r"^INTAKE-\d{8}T\d{6}-[A-F0-9]{8}$")
PERMITTED_SOURCE_TYPES = {
    "LinkedIn_screenshot",
    "LinkedIn_export",
    "copied_analytics",
    "copied_post_text",
    "post_URL",
    "Architect_observation",
    "comment_screenshot",
    "profile_engagement_observation",
}
COUNT_METRICS = {
    "impressions",
    "reactions",
    "comments",
    "reposts",
    "saves",
    "profile_views",
    "new_followers",
    "link_clicks",
    "inbound_messages",
}
CONTROLLED_WINDOWS = {"24_hours", "7_days", "30_days"}
MEASUREMENT_WINDOWS = CONTROLLED_WINDOWS | {"ad_hoc", "historical_unknown_age"}
RELEVANCE_VALUES = {"high", "medium", "low", "unknown"}
UNDERSTANDING_VALUES = {
    "correct_Nova_understanding",
    "partial_understanding",
    "category_confusion",
    "no_evidence",
}
ALLOWED_AUDIENCE_FIELDS = {
    "date",
    "engagement_type",
    "person_or_company",
    "role",
    "company",
    "inferred_segment",
    "target_market_relevance",
    "relevance_basis",
    "content_understanding",
    "misunderstanding",
    "follow_up_occurred",
    "qualified_conversation",
    "evidence_status",
    "notes",
}


def validate_intake_mapping(intake: dict[str, Any]) -> dict[str, Any]:
    require_fields(
        intake,
        ("schema_version", "intake_id", "received_at", "supplied_by_role"),
        "content_evidence_intake",
    )
    if not INTAKE_ID_PATTERN.fullmatch(str(intake["intake_id"])):
        raise ContentValidationError("intake_id must use INTAKE-YYYYMMDDTHHMMSS-HASH8 format")
    if intake["supplied_by_role"] != "Architect":
        raise ContentValidationError("content evidence must be supplied by the Architect")

    identifier = intake.get("post_identifier")
    if not isinstance(identifier, dict) or not any(not is_blank(value) for value in identifier.values()):
        raise ContentValidationError("content evidence intake requires a post identifier")

    source = intake.get("source")
    if not isinstance(source, dict):
        raise ContentValidationError("content evidence intake requires source provenance")
    require_fields(source, ("source_type", "source_reference"), "content evidence source")
    if source["source_type"] not in PERMITTED_SOURCE_TYPES:
        raise ContentValidationError(f"unsupported content evidence source type: {source['source_type']}")

    observed = intake.get("observed_metrics")
    if not isinstance(observed, dict):
        raise ContentValidationError("observed_metrics must be a mapping")
    unknown_metrics = set(observed) - COUNT_METRICS
    if unknown_metrics:
        raise ContentValidationError(f"unsupported observed metrics: {', '.join(sorted(unknown_metrics))}")
    for metric, value in observed.items():
        if is_blank(value):
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            raise ContentValidationError(f"observed metric {metric} must be an integer count")
        if value < 0:
            raise ContentValidationError(f"observed metric {metric} cannot be negative")

    unavailable = intake.get("unavailable_metrics") or []
    if not isinstance(unavailable, list) or any(metric not in COUNT_METRICS for metric in unavailable):
        raise ContentValidationError("unavailable_metrics contains an unsupported metric")
    if len(unavailable) != len(set(unavailable)):
        raise ContentValidationError("unavailable_metrics cannot contain duplicates")
    overlap = {metric for metric, value in observed.items() if not is_blank(value)} & set(unavailable)
    if overlap:
        raise ContentValidationError(
            f"metrics cannot be both observed and unavailable: {', '.join(sorted(overlap))}"
        )

    measurement = intake.get("measurement")
    if not isinstance(measurement, dict):
        raise ContentValidationError("measurement must be a mapping")
    explicit = measurement.get("explicit_window")
    classified = measurement.get("classified_window")
    if not is_blank(explicit) and explicit not in MEASUREMENT_WINDOWS:
        raise ContentValidationError(f"unsupported explicit measurement window: {explicit}")
    if not is_blank(classified) and classified not in MEASUREMENT_WINDOWS:
        raise ContentValidationError(f"unsupported classified measurement window: {classified}")
    controlled = classified if classified in CONTROLLED_WINDOWS else explicit
    if controlled in CONTROLLED_WINDOWS and explicit not in CONTROLLED_WINDOWS:
        if is_blank(measurement.get("measured_at")) or is_blank(measurement.get("publication_timestamp")):
            raise ContentValidationError("controlled window classification requires explicit or timestamp evidence")

    audience = intake.get("audience_observations") or []
    if not isinstance(audience, list):
        raise ContentValidationError("audience_observations must be a list")
    for observation in audience:
        if not isinstance(observation, dict):
            raise ContentValidationError("each audience observation must be a mapping")
        extra = set(observation) - ALLOWED_AUDIENCE_FIELDS
        if extra:
            raise ContentValidationError(f"audience observation contains unsupported fields: {', '.join(sorted(extra))}")
        relevance = observation.get("target_market_relevance")
        understanding = observation.get("content_understanding")
        if not is_blank(relevance) and relevance not in RELEVANCE_VALUES:
            raise ContentValidationError(f"unsupported audience relevance: {relevance}")
        if not is_blank(understanding) and understanding not in UNDERSTANDING_VALUES:
            raise ContentValidationError(f"unsupported content understanding: {understanding}")

    authority = intake.get("authority")
    if not isinstance(authority, dict):
        raise ContentValidationError("authority must be a mapping")
    prohibited = [
        field
        for field in (
            "interpretation_authorized",
            "canonical_rule_change_authorized",
            "publication_authorized",
        )
        if authority.get(field) is not False
    ]
    if prohibited:
        raise ContentValidationError(f"ingestion cannot authorize: {', '.join(prohibited)}")

    evidence_action = intake.get("evidence_action") or {}
    record_action = evidence_action.get("record_action") or "observation"
    if record_action not in {"observation", "correction", "supersession"}:
        raise ContentValidationError(f"unsupported evidence record_action: {record_action}")
    if record_action in {"correction", "supersession"}:
        require_fields(
            evidence_action,
            ("supersedes_record_id", "correction_reason"),
            f"{record_action} evidence",
        )
    return intake


def validate_content_evidence_intake(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    intake = find_mapping(path, "content_evidence_intake")
    validate_intake_mapping(intake)
    return {
        "status": "passed",
        "path": display_path(path),
        "intake_id": intake["intake_id"],
        "source_type": intake["source"]["source_type"],
    }


if __name__ == "__main__":
    run_cli(validate_content_evidence_intake, DEFAULT_PATH)
