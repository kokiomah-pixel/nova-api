from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from retail_context.sources import (
    FixtureRetailSourceAdapter,
    RetailSourceAdapter,
    is_source_usable,
    load_source_observation_schema,
    load_source_registry_schema,
    validate_source_observation,
    validate_source_registry,
)


FIXTURE_DIR = (
    Path(__file__).resolve().parents[1] / "fixtures" / "retail_context" / "sources"
)


def load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def source_entry(index: int = 0) -> dict:
    return copy.deepcopy(load_fixture("registry_fixture.json")["sources"][index])


def assert_invalid_registry(registry: dict) -> None:
    with pytest.raises(ValidationError):
        validate_source_registry(registry)


def assert_invalid_observation(observation: dict) -> None:
    with pytest.raises(ValidationError):
        validate_source_observation(observation)


def test_valid_authorized_public_source_registry_entry_passes_schema_but_fixture_is_not_usable() -> None:
    registry = load_fixture("registry_fixture.json")
    validate_source_registry(registry)
    assert registry["sources"][0]["source_namespace"] == "retail_fixture_sources"
    assert is_source_usable(registry["sources"][0]) is False


def test_authorized_public_source_in_public_namespace_is_configuration_eligible() -> None:
    source = source_entry()
    source["source_namespace"] = "retail_public_sources"
    assert is_source_usable(source) is True


def test_unauthorized_source_is_valid_but_not_usable() -> None:
    registry = load_fixture("registry_fixture.json")
    validate_source_registry(registry)
    assert registry["sources"][1]["authorization_state"] == "unauthorized"
    assert is_source_usable(registry["sources"][1]) is False


def test_valid_retail_licensed_source_is_configuration_eligible() -> None:
    source = source_entry()
    source.update(
        {
            "source_namespace": "retail_licensed_sources",
            "access_class": "retail_licensed",
            "licensing_state": "licensed",
            "credential_requirement": "retail_credential_required",
            "credential_namespace": "retail_context",
        }
    )
    assert is_source_usable(source) is True


def test_public_source_with_licensed_namespace_is_not_usable() -> None:
    source = source_entry()
    source["source_namespace"] = "retail_licensed_sources"
    assert is_source_usable(source) is False


def test_retail_licensed_source_with_public_namespace_is_not_usable() -> None:
    source = source_entry()
    source.update(
        {
            "source_namespace": "retail_public_sources",
            "access_class": "retail_licensed",
            "licensing_state": "licensed",
            "credential_requirement": "retail_credential_required",
            "credential_namespace": "retail_context",
        }
    )
    assert is_source_usable(source) is False


def test_institutional_access_class_is_rejected() -> None:
    registry = load_fixture("registry_fixture.json")
    registry["sources"][0]["access_class"] = "institutional"
    assert_invalid_registry(registry)


def test_institutional_credential_namespace_is_rejected() -> None:
    registry = load_fixture("registry_fixture.json")
    registry["sources"][0]["credential_namespace"] = "institutional_credentials"
    assert_invalid_registry(registry)


def test_institutional_source_namespace_is_rejected() -> None:
    registry = load_fixture("registry_fixture.json")
    registry["sources"][0]["source_namespace"] = "institutional_telemetry"
    assert_invalid_registry(registry)


def test_missing_licensing_state_fails() -> None:
    registry = load_fixture("registry_fixture.json")
    del registry["sources"][0]["licensing_state"]
    assert_invalid_registry(registry)


def test_missing_provenance_requirement_fails_closed() -> None:
    source = source_entry()
    del source["provenance_requirement"]
    assert is_source_usable(source) is False


def test_unsupported_authorization_state_fails() -> None:
    registry = load_fixture("registry_fixture.json")
    registry["sources"][0]["authorization_state"] = "implicitly_authorized"
    assert_invalid_registry(registry)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorization_state", "unauthorized"),
        ("licensing_state", "license_required"),
        ("configuration_state", "not_configured"),
        ("enabled", False),
    ],
)
def test_source_usability_fails_closed(field: str, value: object) -> None:
    source = source_entry()
    source["source_namespace"] = "retail_public_sources"
    source[field] = value
    assert is_source_usable(source) is False


def test_valid_normalized_positive_observation_passes() -> None:
    validate_source_observation(load_fixture("positive_observation.json"))


@pytest.mark.parametrize("field", ["source_id", "observed_at"])
def test_positive_observation_requires_identity_and_time(field: str) -> None:
    observation = load_fixture("positive_observation.json")
    del observation[field]
    assert_invalid_observation(observation)


def test_timestamp_derived_age_matches_observation_and_receipt_times() -> None:
    observation = load_fixture("positive_observation.json")
    assert observation["freshness_input"]["source_age_seconds"] == 5
    validate_source_observation(observation)


def test_mismatched_timestamp_derived_age_fails() -> None:
    observation = load_fixture("positive_observation.json")
    observation["freshness_input"]["source_age_seconds"] = 6
    assert_invalid_observation(observation)


def test_received_at_before_observed_at_fails() -> None:
    observation = load_fixture("positive_observation.json")
    observation["received_at"] = "2026-08-27T13:59:59Z"
    assert_invalid_observation(observation)


def test_unavailable_observation_may_omit_positive_claims() -> None:
    observation = load_fixture("unavailable_observation.json")
    assert observation["claims"] == []
    validate_source_observation(observation)


def test_no_observation_does_not_fabricate_timestamp_or_freshness() -> None:
    observation = load_fixture("unavailable_observation.json")
    assert observation["observed_at"] is None
    assert observation["freshness_input"] == {
        "source_age_seconds": None,
        "derivation_status": "not_available",
    }
    validate_source_observation(observation)


def test_unsupported_verification_state_fails() -> None:
    observation = load_fixture("positive_observation.json")
    observation["verification_status"] = "trusted"
    assert_invalid_observation(observation)


@pytest.mark.parametrize(
    "fixture_name", ["positive_observation.json", "registry_fixture.json"]
)
def test_authority_effect_other_than_none_fails(fixture_name: str) -> None:
    document = load_fixture(fixture_name)
    document["authority_effect"] = "approval"
    if fixture_name == "registry_fixture.json":
        assert_invalid_registry(document)
    else:
        assert_invalid_observation(document)


def test_arbitrary_raw_payload_field_is_rejected() -> None:
    observation = load_fixture("positive_observation.json")
    observation["raw_payload"] = {"provider": "unbounded"}
    assert_invalid_observation(observation)


@pytest.mark.parametrize(
    "field",
    [
        "institutional_tenant_id",
        "institutional_chronology_id",
        "institutional_reflex_memory_id",
        "institutional_credentials",
    ],
)
def test_institutional_state_fields_are_rejected(field: str) -> None:
    observation = load_fixture("positive_observation.json")
    observation[field] = "prohibited"
    assert_invalid_observation(observation)


def test_registry_presence_does_not_imply_runtime_availability() -> None:
    source = source_entry()
    source["source_namespace"] = "retail_public_sources"
    assert is_source_usable(source) is True
    assert "source_status" not in source
    assert "observed_at" not in source


def test_enabled_source_does_not_imply_verified_observation() -> None:
    source = source_entry(1)
    assert source["enabled"] is True
    assert "verification_status" not in source
    assert is_source_usable(source) is False


def test_unverified_observation_cannot_be_relabeled_verified() -> None:
    observation = load_fixture("unverified_observation.json")
    validate_source_observation(observation)
    observation["verification_status"] = "verified"
    assert_invalid_observation(observation)


def test_integrity_digest_must_match_normalized_claims() -> None:
    observation = load_fixture("positive_observation.json")
    observation["claims"][0]["claim_or_observation"] = "Changed content."
    assert_invalid_observation(observation)


def test_fixture_adapter_implements_provider_neutral_protocol() -> None:
    observation = load_fixture("positive_observation.json")
    adapter = FixtureRetailSourceAdapter(
        source_id=observation["source_id"],
        observation=observation,
    )
    assert isinstance(adapter, RetailSourceAdapter)
    result = adapter.observe(observation["subject"])
    assert result == observation
    assert result is not observation
    result["claims"][0]["claim_status"] = "unresolved"
    assert observation["claims"][0]["claim_status"] == "observed"


def test_fixture_adapter_rejects_a_different_subject() -> None:
    observation = load_fixture("positive_observation.json")
    adapter = FixtureRetailSourceAdapter(
        source_id=observation["source_id"],
        observation=observation,
    )
    with pytest.raises(ValueError, match="requested subject"):
        adapter.observe({"subject_id": "other", "subject_type": "network"})


@pytest.mark.parametrize(
    "load_schema",
    [load_source_registry_schema, load_source_observation_schema],
)
def test_schemas_validate_under_draft_2020_12(load_schema) -> None:
    Draft202012Validator.check_schema(load_schema())
