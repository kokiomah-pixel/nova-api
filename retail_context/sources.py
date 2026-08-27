from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .schema import _FORMAT_CHECKER


SCHEMA_VERSION = "0.1.0"
_SPEC_DIR = Path(__file__).resolve().parents[1] / "specs"
SOURCE_REGISTRY_SCHEMA_PATH = _SPEC_DIR / "retail_source_registry_v0_1.schema.json"
SOURCE_OBSERVATION_SCHEMA_PATH = (
    _SPEC_DIR / "retail_source_observation_v0_1.schema.json"
)


def _load_schema(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def load_source_registry_schema() -> dict[str, Any]:
    return _load_schema(SOURCE_REGISTRY_SCHEMA_PATH)


def load_source_observation_schema() -> dict[str, Any]:
    return _load_schema(SOURCE_OBSERVATION_SCHEMA_PATH)


def source_registry_validator() -> Draft202012Validator:
    return Draft202012Validator(
        load_source_registry_schema(),
        format_checker=_FORMAT_CHECKER,
    )


def source_observation_validator() -> Draft202012Validator:
    return Draft202012Validator(
        load_source_observation_schema(),
        format_checker=_FORMAT_CHECKER,
    )


def validate_source_registry(registry: Mapping[str, Any]) -> None:
    source_registry_validator().validate(registry)


def normalized_claims_digest(claims: object) -> str:
    """Return the bounded identity of normalized claims, not source trust proof."""

    encoded = json.dumps(
        claims,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_rfc3339(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_source_observation(observation: Mapping[str, Any]) -> None:
    source_observation_validator().validate(observation)

    freshness = observation["freshness_input"]
    if freshness["derivation_status"] == "derived_from_timestamps":
        observed_at = _parse_rfc3339(observation["observed_at"])
        received_at = _parse_rfc3339(observation["received_at"])
        if received_at < observed_at:
            raise ValidationError("received_at must not precede observed_at")
        expected_age = (received_at - observed_at).total_seconds()
        if freshness["source_age_seconds"] != expected_age:
            raise ValidationError(
                "freshness_input.source_age_seconds must equal received_at - observed_at"
            )

    integrity = observation["integrity"]
    if integrity["scope"] != "normalized_claims":
        return
    expected = normalized_claims_digest(observation["claims"])
    if integrity["digest"] != expected:
        raise ValidationError(
            "integrity.digest must identify the canonical normalized claims"
        )


def _source_entry_validator() -> Draft202012Validator:
    source_entry_schema = load_source_registry_schema()["$defs"]["sourceEntry"]
    return Draft202012Validator(source_entry_schema)


def is_source_usable(source: Mapping[str, Any]) -> bool:
    """Return configuration eligibility only; never infer runtime reachability."""

    try:
        _source_entry_validator().validate(source)
    except ValidationError:
        return False

    common_eligible = (
        source["enabled"] is True
        and source["authorization_state"] == "authorized"
        and source["configuration_state"] == "configured"
        and source["provenance_requirement"] == "required"
        and source["authority_effect"] == "none"
    )
    if not common_eligible:
        return False

    if source["source_namespace"] == "retail_fixture_sources":
        return False

    if source["access_class"] == "public":
        return (
            source["source_namespace"] == "retail_public_sources"
            and source["licensing_state"] == "public"
            and source["credential_requirement"] == "none"
            and source["credential_namespace"] == "none"
        )

    if source["access_class"] == "retail_licensed":
        return (
            source["source_namespace"] == "retail_licensed_sources"
            and source["licensing_state"] == "licensed"
            and source["credential_requirement"] == "retail_credential_required"
            and source["credential_namespace"] == "retail_context"
        )

    return False


@runtime_checkable
class RetailSourceAdapter(Protocol):
    source_id: str

    def observe(
        self,
        subject: Mapping[str, Any],
        as_of: str | None = None,
    ) -> dict[str, Any]:
        """Return one normalized observation without authority semantics."""


@dataclass(frozen=True)
class FixtureRetailSourceAdapter:
    """Deterministic adapter for contract tests; it performs no network calls."""

    source_id: str
    observation: Mapping[str, Any]

    def observe(
        self,
        subject: Mapping[str, Any],
        as_of: str | None = None,
    ) -> dict[str, Any]:
        result = copy.deepcopy(dict(self.observation))
        if result.get("source_id") != self.source_id:
            raise ValueError("fixture source_id does not match adapter source_id")
        if result.get("subject") != dict(subject):
            raise ValueError("fixture observation does not match requested subject")
        if as_of is not None and result.get("received_at") != as_of:
            raise ValueError("fixture adapter supports only its recorded as_of time")
        validate_source_observation(result)
        return result
