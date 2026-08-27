from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_PATH = (
    _REPOSITORY_ROOT
    / "specs"
    / "retail_controlled_production_proof_v0_1.schema.json"
)


def load_retail_controlled_proof_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def validate_retail_controlled_proof_evidence(
    evidence: Mapping[str, Any],
) -> None:
    Draft202012Validator(
        load_retail_controlled_proof_schema(),
        format_checker=FormatChecker(),
    ).validate(evidence)
