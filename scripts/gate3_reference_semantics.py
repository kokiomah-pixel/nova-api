#!/usr/bin/env python3
"""Executable Gate 3 reference semantics for design validation only.

This module is not target-v2 runtime code and selects no production hash or
signature algorithm.  It exercises the proposed projection, canonicalization,
ordering, numeric, temporal, migration, and proof-state rules.
"""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


SAFE_IJSON_INTEGER = 9_007_199_254_740_991
CANONICAL_TIMESTAMP_PRECISION = 6
_TIMESTAMP_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?P<fraction>\.\d+)?(?P<offset>Z|[+-]\d{2}:\d{2})$"
)
_EXACT_DECIMAL_RE = re.compile(
    r"^(?P<sign>-?)(?P<integer>0|[1-9]\d*)(?:\.(?P<fraction>\d+))?"
    r"(?:[eE](?P<exponent_sign>[+-]?)(?P<exponent>\d+))?$"
)


class ReferenceSemanticsError(ValueError):
    """Raised when data cannot satisfy the proposed reference profile."""


def parse_json_no_duplicates(text: str) -> Any:
    """Parse JSON while rejecting duplicate object member names."""

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ReferenceSemanticsError(f"duplicate object member: {key}")
            result[key] = value
        return result

    def reject_implicit_decimal(_: str) -> Any:
        raise ReferenceSemanticsError("implicit JSON decimal is prohibited; use typed normalization")

    return json.loads(text, object_pairs_hook=reject_duplicates, parse_float=reject_implicit_decimal)


def _utf16_sort_key(value: str) -> bytes:
    try:
        return value.encode("utf-16-be")
    except UnicodeEncodeError as exc:
        raise ReferenceSemanticsError("lone Unicode surrogate is prohibited") from exc


def _serialize_string(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ReferenceSemanticsError("invalid Unicode string") from exc
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def canonicalize_jcs_profile(value: Any) -> bytes:
    """Serialize the constrained Nova JCS application profile to UTF-8 bytes.

    RFC 8785 array order and Unicode code points are preserved.  Binary floats
    and Decimal objects are rejected: exact decimals must first be converted to
    the typed coefficient/scale representation defined by G3-R11.
    """

    def serialize(item: Any) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if isinstance(item, str):
            return _serialize_string(item)
        if isinstance(item, int):
            if abs(item) > SAFE_IJSON_INTEGER:
                raise ReferenceSemanticsError("integer exceeds exact I-JSON range; use typed exact integer")
            return str(item)
        if isinstance(item, float):
            raise ReferenceSemanticsError("binary/implicit decimal numbers are prohibited; use typed normalization")
        if isinstance(item, list):
            return "[" + ",".join(serialize(element) for element in item) + "]"
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise ReferenceSemanticsError("JSON object keys must be strings")
            ordered = sorted(item, key=_utf16_sort_key)
            return "{" + ",".join(f"{_serialize_string(key)}:{serialize(item[key])}" for key in ordered) + "}"
        raise ReferenceSemanticsError(f"unsupported canonical type: {type(item).__name__}")

    return serialize(value).encode("utf-8")


def normalize_exact_integer(value: str | int, *, max_digits: int) -> dict[str, Any]:
    """Return the one exact integer representation; exponent syntax is invalid."""

    text = str(value)
    if not re.fullmatch(r"-?(0|[1-9]\d*)", text):
        raise ReferenceSemanticsError("integer must use base-10 digits without exponent or leading zeros")
    integer = int(text)
    digits = len(str(abs(integer)))
    if digits > max_digits:
        raise ReferenceSemanticsError("integer precision exceeds the declared profile")
    return {"numeric_type": "integer", "value": "0" if integer == 0 else str(integer)}


def normalize_exact_decimal(
    value: str,
    *,
    max_precision: int,
    max_scale: int,
    max_abs_exponent: int,
    fixed_scale: int | None = None,
) -> dict[str, Any]:
    """Normalize an exact decimal to a signed coefficient and nonnegative scale.

    Exponent input is accepted at the normalization boundary but never appears
    in canonical material.  No rounding is performed.  Generic trailing zeros
    are insignificant; fixed-scale fields retain exactly their declared scale.
    """

    if min(max_precision, max_scale, max_abs_exponent) < 0 or max_precision == 0:
        raise ReferenceSemanticsError("decimal limits must be explicit nonnegative bounds with positive precision")
    if fixed_scale is not None and (fixed_scale < 0 or fixed_scale > max_scale):
        raise ReferenceSemanticsError("fixed scale exceeds the declared maximum scale")

    match = _EXACT_DECIMAL_RE.fullmatch(value)
    if not match:
        raise ReferenceSemanticsError("invalid exact decimal syntax")
    exponent_digits = (match.group("exponent") or "0").lstrip("0") or "0"
    exponent_limit = str(max_abs_exponent)
    if len(exponent_digits) > len(exponent_limit) or (
        len(exponent_digits) == len(exponent_limit) and exponent_digits > exponent_limit
    ):
        raise ReferenceSemanticsError("decimal exponent exceeds the declared absolute bound")
    exponent = int(exponent_digits)
    if match.group("exponent_sign") == "-":
        exponent = -exponent

    fraction = match.group("fraction") or ""
    coefficient_digits = (match.group("integer") + fraction).lstrip("0") or "0"
    scale = len(fraction) - exponent
    if max(scale, 0) > max_scale:
        raise ReferenceSemanticsError("decimal scale exceeds the declared maximum before expansion")

    if coefficient_digits == "0":
        expansion = 0
        canonical_scale = fixed_scale if fixed_scale is not None else 0
    elif fixed_scale is None:
        while coefficient_digits != "0" and coefficient_digits.endswith("0"):
            coefficient_digits = coefficient_digits[:-1]
            scale -= 1
        expansion = max(-scale, 0)
        canonical_scale = max(scale, 0)
    else:
        shift = fixed_scale - scale
        if shift < 0:
            removable = -shift
            if len(coefficient_digits) < removable or not coefficient_digits.endswith("0" * removable):
                raise ReferenceSemanticsError("value exceeds fixed scale; rounding is prohibited")
            coefficient_digits = coefficient_digits[:-removable] or "0"
            expansion = 0
        else:
            expansion = shift
        canonical_scale = fixed_scale

    if canonical_scale > max_scale:
        raise ReferenceSemanticsError("decimal scale exceeds the declared maximum before expansion")
    precision = 1 if coefficient_digits == "0" else len(coefficient_digits) + expansion
    if precision > max_precision:
        raise ReferenceSemanticsError("decimal precision exceeds the declared profile")
    if expansion:
        coefficient_digits += "0" * expansion
    coefficient = "0" if coefficient_digits == "0" else ("-" if match.group("sign") else "") + coefficient_digits
    return {
        "numeric_type": "decimal",
        "coefficient": coefficient,
        "scale": canonical_scale,
    }


def normalize_monetary_amount(
    value: str,
    *,
    asset_id: str,
    scale: int,
    max_precision: int,
    max_scale: int,
    max_abs_exponent: int,
) -> dict[str, Any]:
    """Normalize money without float conversion, rounding, or implicit units."""

    decimal_value = normalize_exact_decimal(
        value,
        max_precision=max_precision,
        max_scale=max_scale,
        max_abs_exponent=max_abs_exponent,
        fixed_scale=scale,
    )
    return {
        "numeric_type": "monetary_amount",
        "asset_id": asset_id,
        "coefficient": decimal_value["coefficient"],
        "scale": decimal_value["scale"],
    }


def normalize_timestamp(value: str, *, precision: int = CANONICAL_TIMESTAMP_PRECISION) -> str:
    """Normalize RFC 3339 input to UTC with one fixed fractional precision."""

    match = _TIMESTAMP_RE.fullmatch(value)
    if not match:
        raise ReferenceSemanticsError("timestamp must be RFC 3339 with an explicit offset")
    if match.group("offset") == "-00:00":
        raise ReferenceSemanticsError("RFC 3339 -00:00 unknown offset is rejected, not normalized to UTC")
    fraction = match.group("fraction")
    input_precision = len(fraction) - 1 if fraction else 0
    if input_precision > precision:
        raise ReferenceSemanticsError("timestamp exceeds canonical precision; rounding is prohibited")
    iso_value = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError as exc:
        raise ReferenceSemanticsError("invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise ReferenceSemanticsError("timestamp offset is required")
    utc = parsed.astimezone(timezone.utc)
    fraction_text = f"{utc.microsecond:06d}"[:precision]
    suffix = f".{fraction_text}" if precision else ""
    return utc.strftime("%Y-%m-%dT%H:%M:%S") + suffix + "Z"


def normalize_reference_array(
    values: Iterable[Any],
    *,
    identity_key: str | None = None,
) -> list[Any]:
    """Canonical-sort set-like references, dedupe exact copies, reject collisions."""

    unique: dict[bytes, Any] = {}
    identities: dict[Any, bytes] = {}
    for value in values:
        encoded = canonicalize_jcs_profile(value)
        if identity_key and isinstance(value, dict):
            identity = value.get(identity_key)
            if identity is None:
                raise ReferenceSemanticsError(f"reference lacks identity key: {identity_key}")
            previous = identities.get(identity)
            if previous is not None and previous != encoded:
                raise ReferenceSemanticsError(f"conflicting duplicate reference identity: {identity}")
            identities[identity] = encoded
        unique.setdefault(encoded, copy.deepcopy(value))
    return [unique[key] for key in sorted(unique)]


def normalize_semantic_array(
    values: Iterable[Any],
    *,
    semantics: str,
    identity_key: str | None = None,
) -> list[Any]:
    """Apply one explicitly declared array semantic class."""

    materialized = [copy.deepcopy(value) for value in values]
    if semantics == "ordered_sequence":
        return materialized
    if semantics == "set":
        return normalize_reference_array(materialized, identity_key=identity_key)
    if semantics == "multiset":
        return sorted(materialized, key=canonicalize_jcs_profile)
    raise ReferenceSemanticsError(f"undeclared array semantics: {semantics}")


def derive_record_source_type(source_segments: Iterable[str]) -> str:
    """Derive the proposed aggregate without environment ranking or promotion."""

    permitted = {"synthetic", "production_like", "live"}
    represented = set(source_segments)
    if not represented or not represented <= permitted:
        raise ReferenceSemanticsError("source segments must use one or more declared evidence environments")
    return next(iter(represented)) if len(represented) == 1 else "mixed"


def evaluate_review_completeness(
    *,
    profile_available: bool,
    required_field_inventory_available: bool,
    unresolved_material_conflicts: Iterable[Any],
    missing_or_unavailable_required_context: Iterable[Any],
    explicit_unresolved_required_context: Iterable[Any],
    profile_allows_explicit_unresolved: bool,
    all_required_dimensions_represented: bool,
) -> str:
    """Apply the proposed contract-level completeness meanings and precedence."""

    if not profile_available or not required_field_inventory_available:
        return "unavailable"
    if any(True for _ in unresolved_material_conflicts):
        return "conflicted"
    disallowed_unresolved = (
        any(True for _ in explicit_unresolved_required_context)
        and not profile_allows_explicit_unresolved
    )
    if (
        any(True for _ in missing_or_unavailable_required_context)
        or disallowed_unresolved
        or not all_required_dimensions_represented
    ):
        return "partial"
    return "complete"


FingerprintFunction = Callable[[bytes], str]


def resolve_prepared_action_identity(
    *,
    prepared_action: dict[str, Any],
    action_id: str | None,
    external_proposal_version_id: str | None,
    fingerprint_algorithm: str | None = None,
    fingerprint_function: FingerprintFunction | None = None,
) -> dict[str, Any]:
    """Resolve proposed request/response identities without inventing lineage.

    The fallback receives only canonical prepared-action material. It is a
    proposal fingerprint, never a stable action identifier, and the injected
    fixture function does not select a production digest algorithm.
    """

    lineage = (
        {"value": action_id, "source": "external_institution_or_orchestrator", "lineage": "available"}
        if action_id
        else {"value": None, "source": "unavailable", "lineage": "unavailable"}
    )
    if external_proposal_version_id:
        proposal = {
            "value": external_proposal_version_id,
            "source": "external_institution_or_orchestrator",
        }
    else:
        if not fingerprint_algorithm or fingerprint_function is None:
            raise ReferenceSemanticsError("proposal version needs an external identifier or algorithm-qualified Nova fingerprint")
        material = canonicalize_jcs_profile({"prepared_action": copy.deepcopy(prepared_action)})
        proposal = {
            "value": fingerprint_function(material),
            "source": "Nova_derived_proposal_fingerprint",
            "algorithm": fingerprint_algorithm,
            "material_scope": "canonical_prepared_action_material_only",
        }
    return {
        "action_id": lineage,
        "proposal_version_id": proposal,
        "same_action_inference_permitted": action_id is not None,
    }


def _get_path(value: dict[str, Any], parts: list[str]) -> tuple[bool, Any]:
    current: Any = value
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _set_path(value: dict[str, Any], parts: list[str], field_value: Any) -> None:
    current = value
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = field_value


def _normalize_field_value(path: str, value: Any, profile: dict[str, Any]) -> Any:
    if value is None and path not in set(profile.get("nullable_semantic_paths", [])):
        raise ReferenceSemanticsError(f"null is not declared for semantic field: {path}")
    timestamp_paths = set(profile.get("timestamp_paths", []))
    if path in timestamp_paths and isinstance(value, str):
        value = normalize_timestamp(value, precision=profile["timestamp"]["fractional_second_digits"])
    if isinstance(value, list):
        rule = profile.get("array_rules", {}).get(path)
        if not rule:
            raise ReferenceSemanticsError(f"semantic array lacks an explicit rule: {path}")
        value = normalize_semantic_array(
            value,
            semantics=rule.get("semantics", ""),
            identity_key=rule.get("identity_key"),
        )
    return value


def project_semantic_material(response: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Project only field rules declared for semantic-hash inclusion."""

    projected: dict[str, Any] = {}
    profile = spec["canonical_numeric_and_interoperability_profile"]
    for path, rule in spec["field_rules"].items():
        template = spec["rule_templates"][rule["template"]]
        included = rule.get("semantic_hash_inclusion", template["semantic_hash_inclusion"])
        if not included:
            continue
        parts = path.split(".")
        if parts[0] != "review_context_response":
            raise ReferenceSemanticsError(f"unexpected field-rule root: {path}")
        found, field_value = _get_path(response, parts[1:])
        if not found:
            raise ReferenceSemanticsError(f"required semantic field absent: {path}")
        _set_path(projected, parts[1:], _normalize_field_value(path, copy.deepcopy(field_value), profile))
    return {
        "canonicalization_version": spec["semantic_context_integrity_proposal"]["canonicalization_version"],
        "derivation_version": spec["semantic_context_integrity_proposal"]["derivation_version"],
        "review_context_response": projected,
    }


def canonical_semantic_bytes(response: dict[str, Any], spec: dict[str, Any]) -> bytes:
    """Project and canonicalize semantic material using declared rules."""

    return canonicalize_jcs_profile(project_semantic_material(response, spec))


DigestFunction = Callable[[bytes], str]


def build_digest_evidence(
    canonical_bytes: bytes,
    digesters: dict[str, DigestFunction],
) -> list[dict[str, str]]:
    """Build fixture-only algorithm-qualified evidence over the same bytes."""

    return [
        {"algorithm": algorithm, "digest": digesters[algorithm](canonical_bytes)}
        for algorithm in sorted(digesters)
    ]


def verify_semantic_identity_continuity(
    canonical_materials: list[bytes],
    evidence: list[dict[str, str]],
    digesters: dict[str, DigestFunction],
) -> dict[str, Any]:
    """Verify successor digests bind one identical semantic byte sequence."""

    if not canonical_materials:
        return {"continuous": False, "reason": "canonical_material_unavailable"}
    canonical_bytes = canonical_materials[0]
    if any(material != canonical_bytes for material in canonical_materials[1:]):
        return {"continuous": False, "reason": "canonical_semantic_bytes_changed"}
    for record in evidence:
        algorithm = record.get("algorithm")
        if algorithm not in digesters:
            return {"continuous": False, "reason": "digest_algorithm_unverifiable"}
        if digesters[algorithm](canonical_bytes) != record.get("digest"):
            return {"continuous": False, "reason": "digest_verification_failed"}
    return {
        "continuous": True,
        "canonical_semantic_bytes_identical": True,
        "historical_digest_evidence_preserved": True,
        "digest_values_are_semantic_identity": False,
        "digest_values": [record["digest"] for record in evidence],
    }


def evaluate_proof_verification(
    *,
    suite_status: str,
    signature_valid: bool | None,
    presented_profile_version: int,
    required_profile_version: int,
    context_state: str,
    source_state: str,
    review_completeness: str,
) -> dict[str, Any]:
    """Evaluate proof state without mutating semantic context dimensions."""

    reasons: list[str] = []
    downgrade_detected = presented_profile_version < required_profile_version
    if downgrade_detected:
        state = "unverifiable"
        reasons.append("cryptographic_profile_downgrade")
    elif suite_status == "unknown":
        state = "unverifiable"
        reasons.append("unknown_signature_suite")
    elif signature_valid is False:
        state = "invalid"
        reasons.append("signature_invalid")
    elif signature_valid is None:
        state = "unresolved"
        reasons.append("signature_not_evaluated")
    elif suite_status == "deprecated":
        state = "verified_with_deprecated_suite"
        reasons.append("suite_deprecated")
    else:
        state = "verified"
    return {
        "proof_verification_state": state,
        "reasons": reasons,
        "downgrade_detected": downgrade_detected,
        "downgrade_behavior": "fail_closed",
        "context_state": context_state,
        "source_state": source_state,
        "review_completeness": review_completeness,
    }


def reference_self_check(spec: dict[str, Any], fixtures: dict[str, Any]) -> list[str]:
    """Run small executable vectors used by the design validator."""

    errors: list[str] = []
    try:
        if canonicalize_jcs_profile({"z": 1, "a": 2}) != canonicalize_jcs_profile({"a": 2, "z": 1}):
            errors.append("object key order is not invariant")
        if canonicalize_jcs_profile("é") == canonicalize_jcs_profile("e\u0301"):
            errors.append("JCS Unicode preservation was replaced by normalization")
        decimal_vector = fixtures["reference_vectors"]["decimal"]
        if normalize_exact_decimal(
            decimal_vector["input"],
            max_precision=decimal_vector["max_precision"],
            max_scale=decimal_vector["max_scale"],
            max_abs_exponent=decimal_vector["max_abs_exponent"],
        ) != decimal_vector["expected"]:
            errors.append("exact decimal vector failed")
        timestamp_vector = fixtures["reference_vectors"]["timestamp"]
        if normalize_timestamp(timestamp_vector["input"]) != timestamp_vector["expected"]:
            errors.append("timestamp vector failed")
        money_vector = fixtures["reference_vectors"]["monetary_amount"]
        if normalize_monetary_amount(
            money_vector["input"],
            asset_id=money_vector["asset_id"],
            scale=money_vector["scale"],
            max_precision=money_vector["max_precision"],
            max_scale=money_vector["max_scale"],
            max_abs_exponent=money_vector["max_abs_exponent"],
        ) != money_vector["expected"]:
            errors.append("monetary amount vector failed")
        excessive_exponent = fixtures["reference_vectors"]["decimal_excessive_exponent"]
        try:
            normalize_exact_decimal(
                excessive_exponent["input"],
                max_precision=excessive_exponent["max_precision"],
                max_scale=excessive_exponent["max_scale"],
                max_abs_exponent=excessive_exponent["max_abs_exponent"],
            )
            errors.append("excessive decimal exponent was not rejected")
        except ReferenceSemanticsError:
            pass
        try:
            normalize_timestamp(fixtures["reference_vectors"]["timestamp_unknown_offset"]["input"])
            errors.append("RFC3339 unknown offset was normalized instead of rejected")
        except ReferenceSemanticsError:
            pass
        reference_vector = fixtures["reference_vectors"]["references"]
        if normalize_reference_array(reference_vector["input"], identity_key="source_id") != reference_vector["expected"]:
            errors.append("reference ordering/deduplication vector failed")
        if canonicalize_jcs_profile({"value": None}) == canonicalize_jcs_profile({}):
            errors.append("null and absent canonicalized identically")
        if derive_record_source_type(["production_like", "live"]) != "mixed":
            errors.append("mixed evidence environments did not produce mixed")
        if evaluate_review_completeness(
            profile_available=True,
            required_field_inventory_available=True,
            unresolved_material_conflicts=["material-conflict"],
            missing_or_unavailable_required_context=["missing"],
            explicit_unresolved_required_context=[],
            profile_allows_explicit_unresolved=False,
            all_required_dimensions_represented=False,
        ) != "conflicted":
            errors.append("review completeness precedence failed")
        identity_vectors = fixtures["reference_vectors"]["prepared_action_versions"]
        fixture_fingerprint = lambda value: f"fixture:{len(value)}:{sum(value)}"
        identity_v1 = resolve_prepared_action_identity(
            prepared_action=identity_vectors["v1"],
            action_id=None,
            external_proposal_version_id=None,
            fingerprint_algorithm="fixture-only",
            fingerprint_function=fixture_fingerprint,
        )
        identity_v2 = resolve_prepared_action_identity(
            prepared_action=identity_vectors["v2"],
            action_id=None,
            external_proposal_version_id=None,
            fingerprint_algorithm="fixture-only",
            fingerprint_function=fixture_fingerprint,
        )
        if identity_v1["same_action_inference_permitted"] or identity_v2["same_action_inference_permitted"]:
            errors.append("missing action_id permitted cross-revision lineage inference")
        if identity_v1["proposal_version_id"]["value"] == identity_v2["proposal_version_id"]["value"]:
            errors.append("prepared-action revisions did not produce distinct proposal fingerprints")
        response = fixtures["reference_response"]
        before = canonical_semantic_bytes(response, spec)
        changed = copy.deepcopy(response)
        changed["context_id"] = "generated-context-changed"
        changed["created_at"] = "2028-08-24T12:00:00Z"
        changed["reproducibility"]["signature"] = "fixture-signature-changed"
        if canonical_semantic_bytes(changed, spec) != before:
            errors.append("generated/proof metadata changed semantic bytes")
        reordered = copy.deepcopy(response)
        reordered["source_state"]["sources"] = list(reversed(reordered["source_state"]["sources"]))
        reordered["source_state"]["sources"].append(copy.deepcopy(reordered["source_state"]["sources"][0]))
        if canonical_semantic_bytes(reordered, spec) != before:
            errors.append("declared reference set order/duplicates changed semantic bytes")
        profile = spec["canonical_numeric_and_interoperability_profile"]
        for path, rule in profile["array_rules"].items():
            if rule["semantics"] != "set":
                continue
            identity_key = rule.get("identity_key")
            values = (
                [{identity_key: "b", "value": 2}, {identity_key: "a", "value": 1}]
                if identity_key
                else ["b", "a"]
            )
            normalized = normalize_semantic_array(values, semantics="set", identity_key=identity_key)
            reordered_values = list(reversed(values)) + [copy.deepcopy(values[0])]
            if normalize_semantic_array(reordered_values, semantics="set", identity_key=identity_key) != normalized:
                errors.append(f"set order/duplicate invariance failed: {path}")
        digesters = {
            "fixture-digest-a": lambda value: f"a:{sum(value) % 1_000_003}",
            "fixture-digest-b": lambda value: f"b:{len(value)}:{sum(reversed(value)) % 1_000_033}",
        }
        evidence = build_digest_evidence(before, digesters)
        continuity = verify_semantic_identity_continuity([before, before], evidence, digesters)
        if not continuity.get("continuous") or continuity.get("digest_values_are_semantic_identity") is not False:
            errors.append("digest-migration continuity vector failed")
        proof = evaluate_proof_verification(
            suite_status="permitted",
            signature_valid=True,
            presented_profile_version=1,
            required_profile_version=2,
            context_state="current",
            source_state="complete",
            review_completeness="partial",
        )
        if proof["proof_verification_state"] != "unverifiable" or proof["context_state"] != "current" or not proof["downgrade_detected"]:
            errors.append("downgrade/proof-state separation vector failed")
    except (KeyError, TypeError, ReferenceSemanticsError) as exc:
        errors.append(str(exc))
    return errors


__all__ = [
    "ReferenceSemanticsError",
    "build_digest_evidence",
    "canonical_semantic_bytes",
    "canonicalize_jcs_profile",
    "derive_record_source_type",
    "evaluate_proof_verification",
    "evaluate_review_completeness",
    "normalize_exact_decimal",
    "normalize_exact_integer",
    "normalize_monetary_amount",
    "normalize_reference_array",
    "normalize_semantic_array",
    "normalize_timestamp",
    "parse_json_no_duplicates",
    "project_semantic_material",
    "reference_self_check",
    "resolve_prepared_action_identity",
    "verify_semantic_identity_continuity",
]
