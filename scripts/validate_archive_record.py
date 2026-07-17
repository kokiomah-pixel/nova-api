#!/usr/bin/env python3
from __future__ import annotations

import json
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


class ArchiveRecordError(ValueError):
    pass


def validate_archive_record(path: Path = ARCHIVE_RECORD_PATH) -> dict[str, Any]:
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ArchiveRecordError("Archive record must be a YAML object")
    completion = record.get("completion", {})
    status = completion.get("status")
    if status not in ALLOWED_STATUSES:
        raise ArchiveRecordError(f"Unsupported archive completion status: {status}")
    if status == "completed_and_verified":
        if not completion.get("written_at") or not completion.get("receipt_or_reference"):
            raise ArchiveRecordError("completed_and_verified requires written_at and receipt_or_reference")
        if record.get("archive_standard", {}).get("local_preparation_establishes_completion") is False:
            if completion.get("verification") != "external_write_verified":
                raise ArchiveRecordError("completed_and_verified requires external write verification")
    if status != "completed_and_verified" and completion.get("verification") == "external_write_verified":
        raise ArchiveRecordError("External verification cannot be claimed before completion")
    included_text = json.dumps(record.get("included_references", []), sort_keys=True)
    for token in PROHIBITED_REFERENCE_TOKENS:
        if token in included_text:
            raise ArchiveRecordError(f"Archive record references prohibited material: {token}")
    return {
        "status": "passed",
        "archive_record_path": str(path.relative_to(ROOT)),
        "archive_completion_status": status,
        "archive_verified": status == "completed_and_verified",
    }


def main() -> None:
    print(json.dumps(validate_archive_record(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
