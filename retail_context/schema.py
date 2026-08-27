from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_VERSION = "0.1.0"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "retail_context_object_v0_1.schema.json"
)
_RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_FORMAT_CHECKER = FormatChecker()


@_FORMAT_CHECKER.checks("date-time", raises=(TypeError, ValueError))
def _is_rfc3339_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return True
    if not _RFC3339_PATTERN.fullmatch(value):
        return False
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.tzinfo is not None


def load_retail_context_schema() -> dict[str, Any]:
    """Load the canonical retail context object schema."""

    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def retail_context_validator() -> Draft202012Validator:
    """Build a Draft 2020-12 validator with timestamp format enforcement."""

    return Draft202012Validator(
        load_retail_context_schema(),
        format_checker=_FORMAT_CHECKER,
    )


def validate_retail_context_object(context: Mapping[str, Any]) -> None:
    """Validate one authority-neutral retail context object."""

    retail_context_validator().validate(context)
