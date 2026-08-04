#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

import yaml


ROOT = Path(__file__).resolve().parents[2]
YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
ALLOWED_CONTENT_AUTHORITIES = {
    "Architect",
    "Jarvis-Nova_CCO",
}
APPROVED_CONTENT_STATUSES = {"approved", "accepted"}


class ContentValidationError(ValueError):
    """Raised when a governed content artifact violates its contract."""


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def require_fields(record: dict[str, Any], fields: tuple[str, ...], context: str) -> None:
    missing = [field for field in fields if is_blank(record.get(field))]
    if missing:
        raise ContentValidationError(f"{context} missing required fields: {', '.join(missing)}")


def validate_content_approval(approval: Any, context: str) -> dict[str, Any]:
    if not isinstance(approval, dict) or not approval:
        raise ContentValidationError(f"{context} requires a structured approval")
    status = approval.get("status")
    if status not in APPROVED_CONTENT_STATUSES:
        raise ContentValidationError(f"{context} approval status must be approved or accepted")
    authority_role = approval.get("authority_role")
    if authority_role not in ALLOWED_CONTENT_AUTHORITIES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_AUTHORITIES))
        raise ContentValidationError(
            f"{context} has unauthorized authority_role {authority_role!r}; allowed roles: {allowed}"
        )
    require_fields(approval, ("approval_reference", "approved_at"), f"{context} approval")
    return approval


def load_yaml_documents(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        documents = [yaml.safe_load(text)]
    else:
        documents = [yaml.safe_load(block) for block in YAML_FENCE.findall(text)]
    return [document for document in documents if isinstance(document, dict)]


def find_mapping(path: Path, key: str) -> dict[str, Any]:
    for document in load_yaml_documents(path):
        value = document.get(key)
        if isinstance(value, dict):
            return value
    raise ContentValidationError(f"{path} does not contain a YAML mapping named {key}")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run_cli(
    validator: Callable[[Path], dict[str, Any]],
    default_path: Path,
) -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    try:
        result = validator(path)
    except (ContentValidationError, OSError, yaml.YAMLError) as error:
        print(json.dumps({"status": "failed", "path": display_path(path), "error": str(error)}, indent=2))
        raise SystemExit(1) from error
    print(json.dumps(result, indent=2, sort_keys=True))
