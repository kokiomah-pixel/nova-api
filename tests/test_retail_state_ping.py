from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

import retail_context.state_ping as state_ping_module
from retail_context.schema import validate_retail_context_object
from retail_context.state_ping import build_state_ping


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = REPO_ROOT / "fixtures" / "retail_context" / "state_ping" / "cases.json"
SOURCE_FIXTURE_DIR = REPO_ROOT / "fixtures" / "retail_context" / "sources"


def _merge(base: dict, overrides: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_case(name: str) -> dict:
    cases = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    case = copy.deepcopy(cases[name])
    observations = []
    for specification in case.pop("observations"):
        observation = json.loads(
            (SOURCE_FIXTURE_DIR / specification["fixture"]).read_text(
                encoding="utf-8"
            )
        )
        observations.append(_merge(observation, specification.get("overrides", {})))
    case["observations"] = observations
    return case


def build_case(name: str) -> dict:
    case = load_case(name)
    return build_state_ping(
        case["subject"],
        case["observations"],
        generated_at=case["generated_at"],
    )


def test_single_positive_observation_produces_valid_state_ping() -> None:
    result = build_case("single_verified_positive")
    assert result["resource_type"] == "state_ping"
    assert result["authority_effect"] == "none"
    validate_retail_context_object(result)


@pytest.mark.parametrize("case_name", ["unavailable_only", "unknown_only"])
def test_no_positive_observation_returns_insufficient_evidence(
    case_name: str,
) -> None:
    result = build_case(case_name)
    assert result["context_status"] == "insufficient_evidence"
    assert result["confidence"]["level"] == "indeterminate"
    assert result["freshness"] == {
        "observed_at": None,
        "source_age_seconds": None,
        "freshness_status": "unknown",
    }


def test_insufficient_evidence_fabricates_no_positive_material() -> None:
    result = build_case("unavailable_only")
    assert result["provenance"] == []
    assert result["evidence"] == []
    assert result["unresolved_evidence"]


def test_source_id_provenance_is_preserved() -> None:
    case = load_case("single_verified_positive")
    result = build_state_ping(
        case["subject"], case["observations"], generated_at=case["generated_at"]
    )
    source_id = case["observations"][0]["source_id"]
    assert result["provenance"][0]["source_id"] == source_id
    assert result["evidence"][0]["source_id"] == source_id


def test_unverified_input_is_not_upgraded() -> None:
    result = build_case("single_unverified")
    assert result["provenance"][0]["source_status"] == "present_unverified"
    assert result["context_status"] == "partially_resolved"
    assert result["confidence"]["level"] == "low"


def test_stale_contributing_observation_cannot_become_fresh() -> None:
    result = build_case("stale")
    assert result["freshness"]["freshness_status"] == "stale"
    assert result["context_status"] == "partially_resolved"
    assert any("stale" in item["description"] for item in result["limitations"])


def test_subject_mismatch_fails() -> None:
    case = load_case("subject_mismatch")
    with pytest.raises(ValueError, match="requested subject"):
        build_state_ping(
            case["subject"],
            case["observations"],
            generated_at=case["generated_at"],
        )


def test_raw_provider_payload_is_never_accepted() -> None:
    case = load_case("single_verified_positive")
    case["observations"][0]["raw_payload"] = {"unbounded": True}
    with pytest.raises(ValidationError):
        build_state_ping(
            case["subject"],
            case["observations"],
            generated_at=case["generated_at"],
        )


def test_deterministic_inputs_produce_byte_equivalent_output() -> None:
    case = load_case("multiple_positive")
    first = build_state_ping(
        case["subject"], case["observations"], generated_at=case["generated_at"]
    )
    second = build_state_ping(
        case["subject"],
        list(reversed(case["observations"])),
        generated_at=case["generated_at"],
    )
    canonical = lambda value: json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    assert canonical(first) == canonical(second)


def test_generated_at_is_explicit_and_preserved() -> None:
    case = load_case("single_verified_positive")
    result = build_state_ping(
        case["subject"], case["observations"], generated_at=case["generated_at"]
    )
    assert result["generated_at"] == case["generated_at"]


def test_matching_cross_source_claims_are_not_upgraded_to_corroborated() -> None:
    result = build_case("multiple_positive")
    assert result["context_status"] == "resolved"
    assert {item["evidence_status"] for item in result["evidence"]} == {"observed"}
    assert all(
        item["claim_reconciliation_status"] == "not_assessed"
        for item in result["provenance"]
    )


def test_contradictory_input_remains_first_class_and_not_resolved() -> None:
    result = build_case("contradictory")
    assert result["context_status"] == "unresolved"
    assert len(result["contradictions"]) == 1
    assert result["contradictions"][0]["status"] == "unresolved"
    assert result["contradictions"][0]["resolution_basis"] is None
    assert {item["evidence_status"] for item in result["evidence"]} == {
        "contradicted"
    }


def test_unresolved_evidence_is_preserved() -> None:
    result = build_case("single_unverified")
    assert any(
        item["claim_scope"] == "source verification"
        for item in result["unresolved_evidence"]
    )


@pytest.mark.parametrize(
    "field",
    [
        "institutional_tenant_id",
        "institutional_chronology_id",
        "institutional_reflex_memory_id",
        "institutional_credentials",
    ],
)
def test_institutional_fields_cannot_enter_output(field: str) -> None:
    case = load_case("single_verified_positive")
    case["observations"][0][field] = "prohibited"
    with pytest.raises(ValidationError):
        build_state_ping(
            case["subject"],
            case["observations"],
            generated_at=case["generated_at"],
        )


def test_no_action_or_directional_fields_are_present() -> None:
    result = build_case("single_verified_positive")
    serialized = json.dumps(result, sort_keys=True)
    for forbidden_field in (
        '"recommendation"',
        '"action"',
        '"buy"',
        '"sell"',
        '"position"',
    ):
        assert forbidden_field not in serialized


def test_returned_object_is_validated_before_return(monkeypatch) -> None:
    case = load_case("single_verified_positive")
    calls: list[dict] = []
    real_validator = state_ping_module.validate_retail_context_object

    def validating_spy(context: dict) -> None:
        calls.append(context)
        real_validator(context)

    monkeypatch.setattr(
        state_ping_module,
        "validate_retail_context_object",
        validating_spy,
    )
    result = build_state_ping(
        case["subject"], case["observations"], generated_at=case["generated_at"]
    )
    assert calls == [result]


def test_duplicate_observation_identity_fails_closed() -> None:
    case = load_case("single_verified_positive")
    with pytest.raises(ValueError, match="must be unique"):
        build_state_ping(
            case["subject"],
            case["observations"] * 2,
            generated_at=case["generated_at"],
        )


def test_empty_observation_input_fails_closed() -> None:
    with pytest.raises(ValueError, match="at least one"):
        build_state_ping(
            {"subject_id": "ethereum-mainnet", "subject_type": "network"},
            [],
            generated_at="2026-08-27T14:01:00Z",
        )
