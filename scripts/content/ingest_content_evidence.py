#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

try:
    from scripts.content.content_evidence_store import ContentEvidenceStore
    from scripts.content.validation_common import ROOT, ContentValidationError, find_mapping
except ModuleNotFoundError:  # Direct execution from scripts/content.
    from content_evidence_store import ContentEvidenceStore  # type: ignore[no-redef]
    from validation_common import ROOT, ContentValidationError, find_mapping  # type: ignore[no-redef]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview or apply governed content evidence ingestion.")
    parser.add_argument("intake", type=Path, help="Normalized content-evidence intake YAML")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview only; this is the default")
    mode.add_argument("--apply", action="store_true", help="Apply the validated transaction")
    mode.add_argument(
        "--publish",
        action="store_true",
        help="Commit and push the validated transaction to the monthly evidence branch",
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--receipt-out", type=Path)
    parser.add_argument("--allow-create-post", action="store_true")
    parser.add_argument("--expected-branch")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    receipt_out = args.receipt_out
    if receipt_out and not receipt_out.is_absolute():
        receipt_out = repo_root / receipt_out
    try:
        intake = find_mapping(args.intake, "content_evidence_intake")
        store = ContentEvidenceStore(repo_root)
        if args.publish:
            if not args.expected_branch:
                raise ContentValidationError("--publish requires --expected-branch")
            result = store.publish(
                intake,
                expected_branch=args.expected_branch,
                allow_create_post=args.allow_create_post,
                receipt_out=receipt_out,
            )
        else:
            result = store.ingest(
                intake,
                apply=args.apply,
                allow_create_post=args.allow_create_post,
                expected_branch=args.expected_branch,
                receipt_out=receipt_out,
            )
    except (ContentValidationError, OSError, ValueError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, indent=2))
        raise SystemExit(1) from error
    print(yaml.safe_dump(result, sort_keys=False).rstrip())
    status = result["content_evidence_receipt"]["status"]
    if status in {"needs_post_resolution", "conflict_requires_review", "rolled_back"}:
        raise SystemExit(2)
    if args.publish and status not in {
        "persisted_to_evidence_branch",
        "correction_persisted_to_evidence_branch",
        "duplicate_noop",
    }:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
