#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.content.validate_content_evidence_intake import (
        CONTROLLED_WINDOWS,
        COUNT_METRICS,
        MEASUREMENT_WINDOWS,
        validate_intake_mapping,
    )
    from scripts.content.validate_experiment_register import validate_experiment_register
    from scripts.content.validate_post_record import validate_post_record
    from scripts.content.validation_common import ContentValidationError, is_blank, load_yaml_documents
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from validate_content_evidence_intake import (  # type: ignore[no-redef]
        CONTROLLED_WINDOWS,
        COUNT_METRICS,
        MEASUREMENT_WINDOWS,
        validate_intake_mapping,
    )
    from validate_experiment_register import validate_experiment_register  # type: ignore[no-redef]
    from validate_post_record import validate_post_record  # type: ignore[no-redef]
    from validation_common import (  # type: ignore[no-redef]
        ContentValidationError,
        is_blank,
        load_yaml_documents,
    )


PERFORMANCE_HEADER = [
    "evidence_record_id",
    "source_intake_id",
    "source_fingerprint",
    "record_action",
    "supersedes_record_id",
    "post_id",
    "post_date",
    "post_url",
    "measurement_window",
    "measurement_date",
    "topic",
    "narrative_pillar",
    "intended_audience",
    "audience_stage",
    "hook_type",
    "post_pattern",
    "post_length",
    "media_format",
    "cta_type",
    "impressions",
    "reactions",
    "comments",
    "reposts",
    "saves",
    "profile_views",
    "new_followers",
    "link_clicks",
    "inbound_messages",
    "target_role_engagements",
    "target_company_engagements",
    "qualified_operator_comments",
    "qualified_inbound_conversations",
    "misunderstanding_signals",
    "strongest_line",
    "weakest_section",
    "evidence_status",
    "notes",
]
AUDIENCE_HEADER = [
    "engagement_id",
    "source_intake_id",
    "source_fingerprint",
    "post_id",
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
]
RECORD_ACTIONS = {"observation", "correction", "supersession"}
SUCCESS_STATUSES = {"persisted_to_evidence_branch", "correction_appended"}
POST_ID_PATTERN = re.compile(r"^POST-\d{4}-\d{2}-\d{2}-[A-F0-9]{8}$")
EVIDENCE_BRANCH_PATTERN = re.compile(r"^ops/content-evidence-\d{4}-\d{2}$")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _parse_datetime(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    else:
        raw = str(value).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError as error:
            raise ContentValidationError(f"{field} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _date_part(value: Any, field: str) -> date:
    return _parse_datetime(value, field).date()


def _hash8(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8].upper()


def classify_measurement_window(
    measurement: dict[str, Any],
    *,
    tolerance_24_hours: float = 6,
    tolerance_7_days: float = 24,
    tolerance_30_days: float = 72,
) -> tuple[str, float | None]:
    explicit = measurement.get("explicit_window")
    if explicit in MEASUREMENT_WINDOWS:
        return str(explicit), measurement.get("calculated_age_hours")
    classified = measurement.get("classified_window")
    if classified in {"ad_hoc", "historical_unknown_age"}:
        return str(classified), measurement.get("calculated_age_hours")
    measured_at = measurement.get("measured_at")
    published_at = measurement.get("publication_timestamp")
    if is_blank(measured_at) or is_blank(published_at):
        return "historical_unknown_age", None
    age_hours = (_parse_datetime(measured_at, "measurement.measured_at") - _parse_datetime(
        published_at, "measurement.publication_timestamp"
    )).total_seconds() / 3600
    if age_hours < 0:
        raise ContentValidationError("measurement time cannot precede publication time")
    if abs(age_hours - 24) <= tolerance_24_hours:
        return "24_hours", round(age_hours, 3)
    if abs(age_hours - 168) <= tolerance_7_days:
        return "7_days", round(age_hours, 3)
    if abs(age_hours - 720) <= tolerance_30_days:
        return "30_days", round(age_hours, 3)
    return "ad_hoc", round(age_hours, 3)


def _read_csv(path: Path, expected_header: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_header:
            raise ContentValidationError(f"{path.name} header does not match the governed schema")
        return list(reader)


def _render_csv(header: list[str], rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=header, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _text(row.get(field)) for field in header})
    return buffer.getvalue()


def validate_performance_ledger(path: Path, valid_intake_ids: set[str] | None = None) -> dict[str, Any]:
    rows = _read_csv(path, PERFORMANCE_HEADER)
    record_ids: set[str] = set()
    for row in rows:
        record_id = row["evidence_record_id"]
        if not record_id or record_id in record_ids:
            raise ContentValidationError("performance ledger evidence_record_id values must be unique")
        if not row["source_intake_id"] or not row["source_fingerprint"]:
            raise ContentValidationError(f"{record_id} requires source intake provenance")
        if valid_intake_ids is not None and row["source_intake_id"] not in valid_intake_ids:
            raise ContentValidationError(f"{record_id} references an unknown source intake")
        if row["record_action"] not in RECORD_ACTIONS:
            raise ContentValidationError(f"{record_id} has unsupported record_action")
        if row["measurement_window"] not in MEASUREMENT_WINDOWS:
            raise ContentValidationError(f"{record_id} has unsupported measurement_window")
        if row["record_action"] in {"correction", "supersession"}:
            supersedes = row["supersedes_record_id"]
            if not supersedes or supersedes not in record_ids:
                raise ContentValidationError(f"{record_id} correction must reference an earlier record")
        for metric in COUNT_METRICS:
            value = row[metric]
            if value in {"", "unavailable"}:
                continue
            try:
                number = int(value)
            except ValueError as error:
                raise ContentValidationError(f"{record_id} metric {metric} must be unavailable or an integer") from error
            if number < 0 or str(number) != value:
                raise ContentValidationError(f"{record_id} metric {metric} must be a nonnegative integer")
        record_ids.add(record_id)
    return {"status": "passed", "row_count": len(rows)}


def validate_audience_ledger(path: Path, valid_intake_ids: set[str] | None = None) -> dict[str, Any]:
    rows = _read_csv(path, AUDIENCE_HEADER)
    engagement_ids: set[str] = set()
    for row in rows:
        engagement_id = row["engagement_id"]
        if not engagement_id or engagement_id in engagement_ids:
            raise ContentValidationError("audience ledger engagement_id values must be unique")
        if not row["source_intake_id"] or not row["source_fingerprint"]:
            raise ContentValidationError(f"{engagement_id} requires source intake provenance")
        if valid_intake_ids is not None and row["source_intake_id"] not in valid_intake_ids:
            raise ContentValidationError(f"{engagement_id} references an unknown source intake")
        engagement_ids.add(engagement_id)
    return {"status": "passed", "row_count": len(rows)}


def validate_receipt_mapping(receipt: dict[str, Any]) -> dict[str, Any]:
    required = ("schema_version", "intake_id", "processed_at", "status", "repository", "files", "validators")
    missing = [field for field in required if is_blank(receipt.get(field))]
    if missing:
        raise ContentValidationError(f"content evidence receipt missing: {', '.join(missing)}")
    if receipt["status"] in SUCCESS_STATUSES:
        repository = receipt["repository"]
        files = receipt["files"]
        if is_blank(repository.get("branch")) or is_blank(repository.get("commit")):
            raise ContentValidationError("persisted receipt requires branch and durable transaction reference")
        if not files.get("created") and not files.get("updated"):
            raise ContentValidationError("persisted receipt requires at least one repository write")
        failures = [name for name, status in receipt["validators"].items() if status != "passed"]
        if failures:
            raise ContentValidationError(f"persisted receipt has failed validators: {', '.join(failures)}")
    return receipt


def _current_branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _published_copy(path: Path) -> str:
    match = re.search(
        r"^## Final published copy\s*\n(.*?)(?=^## |\Z)",
        path.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _load_post(path: Path) -> dict[str, Any]:
    documents = load_yaml_documents(path)
    for document in documents:
        post = document.get("post")
        if isinstance(post, dict):
            return {"post": post, "copy": _published_copy(path), "path": path}
    raise ContentValidationError(f"post record has no post metadata: {path}")


def _content_evidence_state(path: Path) -> dict[str, Any]:
    for document in load_yaml_documents(path):
        state = document.get("content_evidence_state")
        if isinstance(state, dict):
            return state
    return {
        "performance_references": [],
        "completed_measurement_windows": [],
        "remaining_measurement_windows": ["24_hours", "7_days", "30_days"],
        "qualitative_observations": [],
    }


def _replace_evidence_state(text: str, state: dict[str, Any]) -> str:
    block = "## Content evidence state\n\n```yaml\n" + yaml.safe_dump(
        {"content_evidence_state": state}, sort_keys=False
    ).rstrip() + "\n```"
    pattern = re.compile(r"^## Content evidence state\s*\n```yaml\n.*?```", re.MULTILINE | re.DOTALL)
    if pattern.search(text):
        return pattern.sub(block, text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def _render_new_post(post: dict[str, Any], copy: str, evidence_state: dict[str, Any]) -> str:
    publication_date = _date_part(post["publication_date"], "post publication date")
    due = [
        {"window": "24_hours", "date": (publication_date + timedelta(days=1)).isoformat()},
        {"window": "7_days", "date": (publication_date + timedelta(days=7)).isoformat()},
        {"window": "30_days", "date": (publication_date + timedelta(days=30)).isoformat()},
    ]
    sections = [
        "# Post Record",
        "",
        "## Metadata",
        "",
        "```yaml",
        yaml.safe_dump({"post": post}, sort_keys=False).rstrip(),
        "```",
        "",
        "## Final published copy",
        "",
        copy,
        "",
        "## Intended reader understanding",
        "",
        _text(post.get("intended_reader_understanding")),
        "",
        "## Prohibited misunderstanding",
        "",
        _text(post.get("prohibited_misunderstanding")),
        "",
        "## Measurement schedule",
        "",
        "```yaml",
        yaml.safe_dump({"measurement_schedule": {"post_id": post["post_id"], "due": due}}, sort_keys=False).rstrip(),
        "```",
        "",
        "## Performance references",
        "",
        "## Qualitative observations",
        "",
        "## Content-production notes",
        "",
        "## Content evidence state",
        "",
        "```yaml",
        yaml.safe_dump({"content_evidence_state": evidence_state}, sort_keys=False).rstrip(),
        "```",
        "",
    ]
    return "\n".join(sections)


class ContentEvidenceStore:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.content_root = self.repo_root / "docs/content"
        self.performance_path = self.content_root / "performance/content-performance-ledger.csv"
        self.audience_path = self.content_root / "performance/audience-engagement-ledger.csv"
        self.current_state_path = self.content_root / "content-current-state.yaml"
        self.experiment_path = self.content_root / "content-experiment-register.yaml"

    def _relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.repo_root))

    def _post_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in sorted((self.content_root / "posts").glob("*/*/*.md")):
            records.append(_load_post(path))
        return records

    def _resolve_post(self, intake: dict[str, Any], allow_create: bool) -> dict[str, Any]:
        identifier = intake["post_identifier"]
        records = self._post_records()

        post_id = identifier.get("post_id")
        if not is_blank(post_id):
            matches = [record for record in records if record["post"].get("post_id") == post_id]
            if len(matches) == 1:
                return {"status": "resolved_existing", "confidence": "exact", **matches[0]}

        post_url = identifier.get("post_url")
        if not is_blank(post_url):
            matches = [record for record in records if record["post"].get("post_url") == post_url]
            if len(matches) == 1:
                return {"status": "resolved_existing", "confidence": "exact", **matches[0]}
            if len(matches) > 1:
                return {"status": "needs_resolution", "confidence": "insufficient", "post_id": None}

        publication_date = _text(identifier.get("publication_date"))
        context = intake.get("post_creation_context") or {}
        exact_copy = context.get("exact_published_copy")
        if publication_date and not is_blank(exact_copy):
            matches = [
                record
                for record in records
                if _text(record["post"].get("publication_date")) == publication_date and record["copy"] == exact_copy
            ]
            if len(matches) == 1:
                return {"status": "resolved_existing", "confidence": "high", **matches[0]}
            if len(matches) > 1:
                return {"status": "needs_resolution", "confidence": "insufficient", "post_id": None}

        title = identifier.get("title_or_working_name")
        if publication_date and not is_blank(title):
            matches = [
                record
                for record in records
                if _text(record["post"].get("publication_date")) == publication_date
                and record["post"].get("title_or_working_name") == title
            ]
            if len(matches) == 1:
                return {"status": "resolved_existing", "confidence": "high", **matches[0]}
            if len(matches) > 1:
                return {"status": "needs_resolution", "confidence": "insufficient", "post_id": None}

        if allow_create:
            required = ("exact_published_copy", "intended_audience", "narrative_pillar", "governed_distinction")
            missing = [field for field in required if is_blank(context.get(field))]
            publication_value = identifier.get("publication_date") or intake["measurement"].get("publication_timestamp")
            if is_blank(publication_value):
                missing.append("publication_date_or_timestamp")
            if is_blank(post_url):
                missing.append("post_url")
            if missing:
                return {
                    "status": "rejected",
                    "confidence": "insufficient",
                    "post_id": None,
                    "reason": f"new post record missing: {', '.join(missing)}",
                }
            publication_day = _date_part(publication_value, "post publication date").isoformat()
            generated_id = post_id or f"POST-{publication_day}-{_hash8(str(post_url or exact_copy))}"
            if not POST_ID_PATTERN.fullmatch(str(generated_id)):
                raise ContentValidationError("new post_id must use POST-YYYY-MM-DD-HASH8 format")
            post = {
                "post_id": generated_id,
                "title_or_working_name": identifier.get("title_or_working_name"),
                "publication_date": publication_day,
                "post_url": post_url,
                "intended_audience": context.get("intended_audience"),
                "audience_stage": context.get("audience_stage"),
                "narrative_pillar": context.get("narrative_pillar"),
                "governed_distinction": context.get("governed_distinction"),
                "hook_type": context.get("hook_type"),
                "content_pattern": context.get("content_pattern"),
                "experiment_id": context.get("experiment_id"),
                "status": "published",
            }
            path = self.content_root / f"posts/{publication_day[:4]}/{publication_day[5:7]}/{generated_id}.md"
            return {
                "status": "create_new_record",
                "confidence": "exact",
                "post_id": generated_id,
                "post": post,
                "copy": exact_copy,
                "path": path,
            }
        return {"status": "needs_resolution", "confidence": "insufficient", "post_id": None}

    def _source_fingerprint(self, intake: dict[str, Any]) -> str:
        source = intake["source"]
        if not is_blank(source.get("source_fingerprint")):
            return str(source["source_fingerprint"])
        return hashlib.sha256(
            f"{source['source_type']}|{source['source_reference']}".encode("utf-8")
        ).hexdigest()

    def _intake_paths(self, intake: dict[str, Any]) -> tuple[Path, Path]:
        received = _parse_datetime(intake["received_at"], "received_at")
        intake_path = self.content_root / f"intake/{received:%Y/%m}/{intake['intake_id']}.yaml"
        receipt_path = self.content_root / f"receipts/{received:%Y/%m}/{intake['intake_id']}.yaml"
        return intake_path, receipt_path

    def _material_audience_rows(
        self,
        intake: dict[str, Any],
        post_id: str,
        fingerprint: str,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for observation in intake.get("audience_observations") or []:
            if is_blank(observation.get("engagement_type")) or is_blank(observation.get("relevance_basis")):
                continue
            if all(is_blank(observation.get(field)) for field in ("person_or_company", "role", "company")):
                continue
            observation_date = _text(observation.get("date") or intake["measurement"].get("measured_at"))[:10]
            identity = json.dumps(observation, sort_keys=True, default=str)
            row = {field: "" for field in AUDIENCE_HEADER}
            row.update(observation)
            row.update(
                {
                    "engagement_id": f"ENGAGE-{post_id}-{observation_date}-{_hash8(identity)}",
                    "source_intake_id": intake["intake_id"],
                    "source_fingerprint": fingerprint,
                    "post_id": post_id,
                    "date": observation_date,
                    "evidence_status": observation.get("evidence_status") or "observed",
                }
            )
            rows.append(row)
        return rows

    def _receipt(
        self,
        intake: dict[str, Any],
        *,
        post_id: str | None,
        window: str,
        status: str,
        branch: str | None,
        transaction_reference: str | None,
        created: list[str],
        updated: list[str],
        performance_rows: int,
        audience_rows: int,
        validators: dict[str, str],
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "intake_id": intake["intake_id"],
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "post_id": post_id,
            "measurement_window": window,
            "status": status,
            "repository": {
                "repository": self.repo_root.name,
                "branch": branch,
                "commit": transaction_reference,
                "pull_request": None,
                "main_merge_verified": False,
            },
            "repository_state": {
                "persisted_to_monthly_branch": status in SUCCESS_STATUSES,
                "merged_to_main": False,
            },
            "files": {"created": created, "updated": updated},
            "rows": {
                "performance_rows_added": performance_rows,
                "audience_rows_added": audience_rows,
            },
            "validators": validators,
            "unresolved_fields": (intake.get("extraction") or {}).get("unresolved_fields") or [],
            "unavailable_metrics": intake.get("unavailable_metrics") or [],
            "effects": {
                "interpretation_created": False,
                "canonical_rule_changed": False,
                "accepted_state_changed": False,
                "chronology_event_created": False,
                "Reflex_Memory_object_created": False,
            },
        }

    def ingest(
        self,
        intake: dict[str, Any],
        *,
        apply: bool = False,
        allow_create_post: bool = False,
        expected_branch: str | None = None,
        current_branch: str | None = None,
        receipt_out: Path | None = None,
        fail_after_writes: int | None = None,
    ) -> dict[str, Any]:
        intake = deepcopy(intake)
        validate_intake_mapping(intake)
        fingerprint = self._source_fingerprint(intake)
        intake["source"]["source_fingerprint"] = fingerprint
        window, age_hours = classify_measurement_window(intake["measurement"])
        intake["measurement"]["classified_window"] = window
        intake["measurement"]["calculated_age_hours"] = age_hours
        allow_create = allow_create_post or bool((intake.get("post_creation_context") or {}).get("allow_create_post"))
        resolution = self._resolve_post(intake, allow_create)
        post_id = resolution.get("post_id") or (resolution.get("post") or {}).get("post_id")
        blockers: list[str] = []
        if resolution["status"] in {"needs_resolution", "rejected"}:
            blockers.append(resolution.get("reason") or "post identity requires Architect resolution")

        performance_rows = _read_csv(self.performance_path, PERFORMANCE_HEADER)
        audience_rows = _read_csv(self.audience_path, AUDIENCE_HEADER)
        matching_window = [
            row for row in performance_rows if row["post_id"] == post_id and row["measurement_window"] == window
        ]
        exact_duplicate = next(
            (row for row in matching_window if row["source_fingerprint"] == fingerprint),
            None,
        )
        action = (intake.get("evidence_action") or {}).get("record_action") or "observation"
        supersedes = (intake.get("evidence_action") or {}).get("supersedes_record_id")
        if action not in RECORD_ACTIONS:
            raise ContentValidationError(f"unsupported evidence record_action: {action}")

        observed = intake.get("observed_metrics") or {}
        proposed_metric_values = {
            metric: _text(observed.get(metric)) if not is_blank(observed.get(metric)) else (
                "unavailable" if metric in set(intake.get("unavailable_metrics") or []) else ""
            )
            for metric in COUNT_METRICS
        }
        if matching_window and not exact_duplicate:
            values_match = any(
                all(row[metric] == proposed_metric_values[metric] for metric in COUNT_METRICS)
                for row in matching_window
            )
            if not values_match:
                referenced = next((row for row in matching_window if row["evidence_record_id"] == supersedes), None)
                if action not in {"correction", "supersession"} or referenced is None:
                    blockers.append("conflicting same-window values require correction metadata")

        experiment_payload = yaml.safe_load(self.experiment_path.read_text(encoding="utf-8"))
        experiment_id = (resolution.get("post") or {}).get("experiment_id")
        experiment = next(
            (item for item in experiment_payload.get("experiments", []) if item.get("experiment_id") == experiment_id),
            None,
        )
        if experiment_id and (experiment is None or experiment.get("status") != "active"):
            blockers.append(f"experiment {experiment_id} is not active")

        planned: list[dict[str, str]] = []
        intake_path, default_receipt_path = self._intake_paths(intake)
        receipt_path = receipt_out.resolve() if receipt_out else default_receipt_path
        try:
            receipt_path.relative_to(self.repo_root)
        except ValueError as error:
            raise ContentValidationError("receipt path must remain inside the repository") from error
        if not blockers and not exact_duplicate:
            targets = [intake_path, resolution.get("path"), self.performance_path, self.current_state_path, receipt_path]
            if self._material_audience_rows(intake, str(post_id), fingerprint):
                targets.append(self.audience_path)
            if experiment_id and window in CONTROLLED_WINDOWS:
                targets.append(self.experiment_path)
            for target in targets:
                if not isinstance(target, Path):
                    continue
                planned.append({"path": self._relative(target), "action": "update" if target.exists() else "create"})

        preview = {
            "intake_id": intake["intake_id"],
            "post_resolution": {
                "status": resolution["status"],
                "confidence": resolution.get("confidence"),
                "post_id": post_id,
            },
            "measurement": {
                "classified_window": window,
                "measured_at": _text(intake["measurement"].get("measured_at")),
                "calculated_age_hours": age_hours,
                "controlled_experiment_eligible": window in CONTROLLED_WINDOWS,
            },
            "observed_metrics": observed,
            "unavailable_metrics": intake.get("unavailable_metrics") or [],
            "uncertain_fields": (intake.get("extraction") or {}).get("uncertain_fields") or [],
            "audience_observations": {"count": len(self._material_audience_rows(intake, str(post_id), fingerprint))},
            "planned_writes": planned,
            "interpretation_created": False,
            "canonical_rule_effect": "none",
            "chronology_effect": "none",
            "Reflex_Memory_effect": "none",
            "persistence_ready": not blockers and exact_duplicate is None,
            "blockers": blockers,
            "writes_performed": False,
        }
        validators = {
            "intake": "passed",
            "post_record": "not_run",
            "performance_ledger": "not_run",
            "audience_ledger": "not_run",
            "experiment_register": "not_run",
            "current_state": "not_run",
        }
        if blockers:
            status = "needs_post_resolution" if resolution["status"] == "needs_resolution" else "conflict_requires_review"
            receipt = self._receipt(
                intake,
                post_id=post_id,
                window=window,
                status=status,
                branch=None,
                transaction_reference=None,
                created=[],
                updated=[],
                performance_rows=0,
                audience_rows=0,
                validators=validators,
            )
            return {"ingestion_preview": preview, "content_evidence_receipt": receipt}
        if exact_duplicate or intake_path.exists():
            receipt = self._receipt(
                intake,
                post_id=str(post_id),
                window=window,
                status="duplicate_noop",
                branch=None,
                transaction_reference=None,
                created=[],
                updated=[],
                performance_rows=0,
                audience_rows=0,
                validators=validators,
            )
            return {"ingestion_preview": preview, "content_evidence_receipt": receipt}
        if not apply:
            receipt = self._receipt(
                intake,
                post_id=str(post_id),
                window=window,
                status="prepared_not_persisted",
                branch=None,
                transaction_reference=None,
                created=[],
                updated=[],
                performance_rows=0,
                audience_rows=0,
                validators=validators,
            )
            return {"ingestion_preview": preview, "content_evidence_receipt": receipt}

        branch = current_branch or _current_branch(self.repo_root)
        if expected_branch:
            branch_allowed = branch == expected_branch
        else:
            branch_allowed = bool(EVIDENCE_BRANCH_PATTERN.fullmatch(branch))
        if not branch_allowed:
            raise ContentValidationError(f"apply requires an approved evidence branch; current branch is {branch!r}")

        record_id = f"EVID-{post_id}-{window}-{_hash8(fingerprint)}"
        performance_row = {field: "" for field in PERFORMANCE_HEADER}
        post = resolution["post"]
        copy = resolution.get("copy") or ""
        measurement_date = _text(intake["measurement"].get("measured_at"))[:10]
        qualitative = intake.get("qualitative_observations") or {}
        performance_row.update(
            {
                "evidence_record_id": record_id,
                "source_intake_id": intake["intake_id"],
                "source_fingerprint": fingerprint,
                "record_action": action,
                "supersedes_record_id": supersedes,
                "post_id": post_id,
                "post_date": post.get("publication_date"),
                "post_url": post.get("post_url"),
                "measurement_window": window,
                "measurement_date": measurement_date,
                "topic": post.get("title_or_working_name"),
                "narrative_pillar": post.get("narrative_pillar"),
                "intended_audience": post.get("intended_audience"),
                "audience_stage": post.get("audience_stage"),
                "hook_type": post.get("hook_type"),
                "post_pattern": post.get("content_pattern"),
                "post_length": len(copy.split()),
                "media_format": "text",
                "misunderstanding_signals": " | ".join(qualitative.get("misunderstanding_signals") or []),
                "strongest_line": qualitative.get("strongest_line"),
                "weakest_section": qualitative.get("weakest_section"),
                "evidence_status": "observed",
                "notes": " | ".join(qualitative.get("notes") or []),
            }
        )
        performance_row.update(proposed_metric_values)
        new_performance_rows = performance_rows + [performance_row]
        material_audience = self._material_audience_rows(intake, str(post_id), fingerprint)
        new_audience_rows = audience_rows + material_audience

        evidence_state = _content_evidence_state(resolution["path"]) if resolution["status"] == "resolved_existing" else {
            "performance_references": [],
            "completed_measurement_windows": [],
            "remaining_measurement_windows": ["24_hours", "7_days", "30_days"],
            "qualitative_observations": [],
        }
        for field in ("performance_references", "completed_measurement_windows", "qualitative_observations"):
            evidence_state.setdefault(field, [])
        if record_id not in evidence_state["performance_references"]:
            evidence_state["performance_references"].append(record_id)
        if window in CONTROLLED_WINDOWS and window not in evidence_state["completed_measurement_windows"]:
            evidence_state["completed_measurement_windows"].append(window)
        evidence_state["remaining_measurement_windows"] = [
            item for item in ("24_hours", "7_days", "30_days") if item not in evidence_state["completed_measurement_windows"]
        ]
        if any(not is_blank(value) for value in qualitative.values()):
            evidence_state["qualitative_observations"].append(
                {"evidence_record_id": record_id, **qualitative}
            )
        if resolution["status"] == "resolved_existing":
            post_content = _replace_evidence_state(resolution["path"].read_text(encoding="utf-8"), evidence_state)
        else:
            post_content = _render_new_post(post, copy, evidence_state)

        state_payload = yaml.safe_load(self.current_state_path.read_text(encoding="utf-8"))
        current_state = state_payload["content_current_state"]
        current_state.setdefault("published_posts", [])
        if post_id not in current_state["published_posts"]:
            current_state["published_posts"].append(post_id)
        current_state.setdefault("metrics_due", [])
        current_state["metrics_due"] = [
            item
            for item in current_state["metrics_due"]
            if not isinstance(item, dict) or item.get("post_id") != post_id
        ]
        publication_day = _date_part(post["publication_date"], "post publication date")
        window_offsets = {"24_hours": 1, "7_days": 7, "30_days": 30}
        current_state["metrics_due"].extend(
            {
                "post_id": post_id,
                "window": pending_window,
                "due_date": (publication_day + timedelta(days=window_offsets[pending_window])).isoformat(),
            }
            for pending_window in evidence_state["remaining_measurement_windows"]
        )
        current_state.setdefault("pending_evidence_resolution", [])
        current_state["last_content_evidence_ingestion"] = intake["intake_id"]
        ingestion_state = current_state.setdefault("content_evidence_ingestion", {})
        ingestion_state.update(
            {
                "last_intake_id": intake["intake_id"],
                "last_ingested_at": datetime.now(timezone.utc).isoformat(),
                "pending_intakes": [],
                "unresolved_intakes": ingestion_state.get("unresolved_intakes") or [],
                "evidence_branch": branch,
                "evidence_pull_request": ingestion_state.get("evidence_pull_request"),
            }
        )
        state_content = yaml.safe_dump(state_payload, sort_keys=False)

        experiment_changed = False
        if experiment and window in CONTROLLED_WINDOWS:
            if post_id not in experiment["posts_included"]:
                experiment["posts_included"].append(post_id)
            evidence_ref = {
                "evidence_record_id": record_id,
                "post_id": post_id,
                "measurement_window": window,
            }
            if evidence_ref not in experiment["measurement_evidence"]:
                experiment["measurement_evidence"].append(evidence_ref)
            experiment_changed = True

        normalized_intake_content = yaml.safe_dump({"content_evidence_intake": intake}, sort_keys=False)
        changes: dict[Path, str] = {
            intake_path: normalized_intake_content,
            resolution["path"]: post_content,
            self.performance_path: _render_csv(PERFORMANCE_HEADER, new_performance_rows),
            self.current_state_path: state_content,
        }
        if material_audience:
            changes[self.audience_path] = _render_csv(AUDIENCE_HEADER, new_audience_rows)
        if experiment_changed:
            changes[self.experiment_path] = yaml.safe_dump(experiment_payload, sort_keys=False)

        created = sorted(self._relative(path) for path in changes if not path.exists())
        updated = sorted(self._relative(path) for path in changes if path.exists())
        receipt_relative = self._relative(receipt_path)
        (created if not receipt_path.exists() else updated).append(receipt_relative)
        transaction_material = "\n".join(
            f"{self._relative(path)}\n{content}" for path, content in sorted(changes.items(), key=lambda item: str(item[0]))
        )
        transaction_reference = f"transaction:{hashlib.sha256(transaction_material.encode('utf-8')).hexdigest()}"
        validators = {name: "passed" for name in validators}
        status = "correction_appended" if action in {"correction", "supersession"} else "persisted_to_evidence_branch"
        receipt = self._receipt(
            intake,
            post_id=str(post_id),
            window=window,
            status=status,
            branch=branch,
            transaction_reference=transaction_reference,
            created=sorted(created),
            updated=sorted(updated),
            performance_rows=1,
            audience_rows=len(material_audience),
            validators=validators,
        )
        changes[receipt_path] = yaml.safe_dump({"content_evidence_receipt": receipt}, sort_keys=False)
        try:
            self._apply_transaction(
                changes,
                intake_id=intake["intake_id"],
                post_path=resolution["path"],
                receipt=receipt,
                fail_after_writes=fail_after_writes,
            )
        except Exception as error:
            rollback_receipt = self._receipt(
                intake,
                post_id=str(post_id),
                window=window,
                status="rolled_back",
                branch=branch,
                transaction_reference=None,
                created=[],
                updated=[],
                performance_rows=0,
                audience_rows=0,
                validators={**validators, "transaction": "failed"},
            )
            rollback_receipt["transaction_result"] = {
                "repository_changed": False,
                "error": str(error),
                "failed_validator": "transaction_or_affected_artifact",
            }
            preview["blockers"].append(str(error))
            preview["persistence_ready"] = False
            return {"ingestion_preview": preview, "content_evidence_receipt": rollback_receipt}
        preview["writes_performed"] = True
        return {"ingestion_preview": preview, "content_evidence_receipt": receipt}

    def _apply_transaction(
        self,
        changes: dict[Path, str],
        *,
        intake_id: str,
        post_path: Path,
        receipt: dict[str, Any],
        fail_after_writes: int | None,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="content-evidence-") as temp_dir_name:
            temp_root = Path(temp_dir_name)
            staged: dict[Path, Path] = {}
            for target, content in changes.items():
                relative = target.resolve().relative_to(self.repo_root)
                temp_path = temp_root / relative
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path.write_text(content, encoding="utf-8")
                staged[target] = temp_path

            intake_temp = next(path for target, path in staged.items() if target.name == f"{intake_id}.yaml" and "intake" in target.parts)
            from scripts.content.validate_content_evidence_intake import validate_content_evidence_intake

            validate_content_evidence_intake(intake_temp)
            validate_post_record(staged[post_path])
            validate_performance_ledger(staged[self.performance_path], {intake_id} | {
                row["source_intake_id"] for row in _read_csv(self.performance_path, PERFORMANCE_HEADER)
            })
            validate_audience_ledger(staged.get(self.audience_path, self.audience_path), {intake_id} | {
                row["source_intake_id"] for row in _read_csv(self.audience_path, AUDIENCE_HEADER)
            })
            validate_experiment_register(staged.get(self.experiment_path, self.experiment_path))
            state_path = staged[self.current_state_path]
            state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            if not isinstance(state, dict) or not isinstance(state.get("content_current_state"), dict):
                raise ContentValidationError("content current state failed validation")
            validate_receipt_mapping(receipt)

            originals = {target: target.read_bytes() if target.exists() else None for target in changes}
            written = 0
            try:
                for target, temp_path in staged.items():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(temp_path, target)
                    written += 1
                    if fail_after_writes is not None and written >= fail_after_writes:
                        raise OSError("simulated transactional write failure")
            except Exception:
                for target, original in originals.items():
                    if original is None:
                        if target.exists():
                            target.unlink()
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
                            handle.write(original)
                            restore_path = Path(handle.name)
                        os.replace(restore_path, target)
                raise
