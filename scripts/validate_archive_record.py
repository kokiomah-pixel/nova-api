#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RECORD_PATH = ROOT / "archive/governance/architect-data-operations-stage-a-acceptance-2026-07-17.yaml"
ALLOWED_STATUSES = {
    "completed_and_verified",
    "written_receipt_pending",
    "pending_external_write",
    "destination_unavailable",
    "standard_unresolved",
}
PROHIBITED_REFERENCE_TOKENS = {
    "raw_payload",
    "raw_external_identifier",
    "request_body",
    "response_body",
    "local_secret_salt",
}
VERIFIED_COMPLETION_MARKERS = {
    "external_write_verified",
    "merge_commit_resolved_in_main",
}
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ArchiveRecordError(ValueError):
    pass


def _reference_value(record: dict[str, Any], reference_type: str) -> str:
    for reference in record.get("included_references", []):
        if reference.get("reference_type") == reference_type:
            return str(reference.get("value", ""))
    raise ArchiveRecordError(f"Missing archive reference: {reference_type}")


def expected_archive_package_hash(record: dict[str, Any]) -> str:
    """Hash the immutable archive package references, excluding completion receipt state."""
    integrity = record.get("integrity", {})
    parts = [
        str(record.get("archive_record_id", "")),
        str(integrity.get("accepted_state_hash", "")),
        str(integrity.get("chronology_event_hash", "")),
        _reference_value(record, "PR_4_merge_commit"),
        _reference_value(record, "PR_5_merge_commit"),
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def validate_archive_record(path: Path = ARCHIVE_RECORD_PATH) -> dict[str, Any]:
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ArchiveRecordError("Archive record must be a YAML object")
    completion = record.get("completion", {})
    status = completion.get("status")
    if status not in ALLOWED_STATUSES:
        raise ArchiveRecordError(f"Unsupported archive completion status: {status}")
    verification = completion.get("verification")
    if status == "completed_and_verified":
        if not completion.get("written_at") or not completion.get("receipt_or_reference"):
            raise ArchiveRecordError("completed_and_verified requires written_at and receipt_or_reference")
        if record.get("archive_standard", {}).get("local_preparation_establishes_completion") is False:
            if verification not in VERIFIED_COMPLETION_MARKERS:
                raise ArchiveRecordError("completed_and_verified requires external write verification")
        if verification == "merge_commit_resolved_in_main" and not FULL_SHA_PATTERN.fullmatch(
            str(completion.get("receipt_or_reference"))
        ):
            raise ArchiveRecordError("merge_commit_resolved_in_main requires a full Git commit receipt")
    if status != "completed_and_verified" and (
        completion.get("written_at")
        or completion.get("receipt_or_reference")
        or verification in VERIFIED_COMPLETION_MARKERS
    ):
        raise ArchiveRecordError("External verification cannot be claimed before completion")
    integrity = record.get("integrity", {})
    expected_hash = expected_archive_package_hash(record)
    if integrity.get("archive_package_hash") != expected_hash:
        raise ArchiveRecordError("Archive package hash does not match immutable package references")
    included_text = json.dumps(record.get("included_references", []), sort_keys=True)
    for token in PROHIBITED_REFERENCE_TOKENS:
        if token in included_text:
            raise ArchiveRecordError(f"Archive record references prohibited material: {token}")
    try:
        display_path = str(path.relative_to(ROOT))
    except ValueError:
        display_path = str(path)
    return {
        "status": "passed",
        "archive_record_path": display_path,
        "archive_completion_status": status,
        "archive_verified": status == "completed_and_verified",
        "archive_package_hash_valid": True,
    }


def main() -> None:
    print(json.dumps(validate_archive_record(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
