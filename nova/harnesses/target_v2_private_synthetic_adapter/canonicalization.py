"""Independent canonicalization for the private synthetic adapter.

This implementation does not import the Gate 3 reference-semantics module.
Gate 3 may be used by tests as an oracle, never as this adapter's code path.
No production digest or signature algorithm is selected here.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Callable, Iterable


SAFE_IJSON_INTEGER = 9_007_199_254_740_991
_TIMESTAMP_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?P<fraction>\.\d+)?(?P<offset>Z|[+-]\d{2}:\d{2})$"
)
_DECIMAL_RE = re.compile(
    r"^(?P<sign>-?)(?P<integer>0|[1-9]\d*)(?:\.(?P<fraction>\d+))?"
    r"(?:[eE](?P<exponent_sign>[+-]?)(?P<exponent>\d+))?$"
)


class CanonicalizationError(ValueError):
    """Input cannot be represented by the design-v2.1 profile."""


def _utf16_key(value: str) -> bytes:
    try:
        return value.encode("utf-16-be")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("invalid Unicode or lone surrogate") from exc


def _string(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("invalid Unicode or lone surrogate") from exc
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def canonicalize_jcs(value: Any) -> bytes:
    """Serialize the constrained JCS structural profile.

    Exact financial values must already be typed objects.  Binary floating
    point is rejected instead of being rounded or truncated.
    """

    def serialize(item: Any) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if isinstance(item, str):
            return _string(item)
        if isinstance(item, int):
            if abs(item) > SAFE_IJSON_INTEGER:
                raise CanonicalizationError("integer exceeds exact I-JSON range")
            return str(item)
        if isinstance(item, float):
            raise CanonicalizationError("binary floating-point values are prohibited")
        if isinstance(item, list):
            return "[" + ",".join(serialize(element) for element in item) + "]"
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise CanonicalizationError("object keys must be strings")
            keys = sorted(item, key=_utf16_key)
            return "{" + ",".join(f"{_string(key)}:{serialize(item[key])}" for key in keys) + "}"
        raise CanonicalizationError(f"unsupported canonical type: {type(item).__name__}")

    return serialize(value).encode("utf-8")


def normalize_exact_decimal(
    value: str,
    *,
    max_precision: int,
    max_scale: int,
    max_abs_exponent: int,
    max_input_characters: int,
    fixed_scale: int | None = None,
) -> dict[str, Any]:
    """Normalize exact base-10 input without rounding."""

    if max_precision <= 0 or min(max_scale, max_abs_exponent) < 0:
        raise CanonicalizationError("invalid decimal bounds")
    if max_input_characters <= 0 or len(value) > max_input_characters:
        raise CanonicalizationError("decimal input exceeds its bounded size")
    if fixed_scale is not None and not 0 <= fixed_scale <= max_scale:
        raise CanonicalizationError("fixed scale exceeds max_scale")
    match = _DECIMAL_RE.fullmatch(value)
    if match is None:
        raise CanonicalizationError("invalid exact decimal syntax")

    exponent_text = (match.group("exponent") or "0").lstrip("0") or "0"
    bound_text = str(max_abs_exponent)
    if len(exponent_text) > len(bound_text) or (
        len(exponent_text) == len(bound_text) and exponent_text > bound_text
    ):
        raise CanonicalizationError("absolute exponent exceeds its early bound")
    exponent = int(exponent_text)
    if match.group("exponent_sign") == "-":
        exponent = -exponent

    fraction = match.group("fraction") or ""
    digits = (match.group("integer") + fraction).lstrip("0") or "0"
    scale = len(fraction) - exponent
    if digits == "0":
        digits = "0"
        output_scale = fixed_scale or 0
        expansion = 0
    elif fixed_scale is None:
        while digits.endswith("0"):
            digits = digits[:-1]
            scale -= 1
        output_scale = max(scale, 0)
        expansion = max(-scale, 0)
    else:
        shift = fixed_scale - scale
        if shift < 0:
            removable = -shift
            if len(digits) < removable or not digits.endswith("0" * removable):
                raise CanonicalizationError("rounding would be required")
            digits = digits[:-removable] or "0"
            expansion = 0
        else:
            expansion = shift
        output_scale = fixed_scale

    if output_scale > max_scale:
        raise CanonicalizationError("canonical scale exceeds max_scale")
    precision = 1 if digits == "0" else len(digits) + expansion
    if precision > max_precision:
        raise CanonicalizationError("canonical precision exceeds max_precision")
    if expansion:
        digits += "0" * expansion
    coefficient = "0" if digits == "0" else ("-" if match.group("sign") else "") + digits
    return {"numeric_type": "decimal", "coefficient": coefficient, "scale": output_scale}


def normalize_monetary_amount(
    value: str,
    *,
    asset_id: str,
    scale: int,
    max_precision: int,
    max_scale: int,
    max_abs_exponent: int,
    max_input_characters: int,
) -> dict[str, Any]:
    if not asset_id:
        raise CanonicalizationError("monetary asset/unit must be explicit")
    normalized = normalize_exact_decimal(
        value,
        max_precision=max_precision,
        max_scale=max_scale,
        max_abs_exponent=max_abs_exponent,
        max_input_characters=max_input_characters,
        fixed_scale=scale,
    )
    return {
        "numeric_type": "monetary_amount",
        "asset_id": asset_id,
        "coefficient": normalized["coefficient"],
        "scale": normalized["scale"],
    }


def normalize_timestamp(value: str) -> str:
    match = _TIMESTAMP_RE.fullmatch(value)
    if match is None or match.group("offset") == "-00:00":
        raise CanonicalizationError("timestamp requires an explicit known RFC3339 offset")
    fraction = (match.group("fraction") or "")[1:]
    if len(fraction) > 6:
        raise CanonicalizationError("sub-microsecond precision is prohibited")
    fraction = fraction.ljust(6, "0")
    source = f"{match.group('date')}T{match.group('time')}.{fraction}{match.group('offset')}"
    try:
        parsed = datetime.fromisoformat(source.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CanonicalizationError("invalid RFC3339 calendar value") from exc
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def normalize_declared_set(
    items: Iterable[Any],
    *,
    tuple_fields: tuple[str, ...] | None = None,
    scalar: bool = False,
    item_normalizer: Callable[[Any], Any] | None = None,
) -> list[Any]:
    """Normalize a declared set and reject ambiguous primary identities.

    Whole-item canonical bytes are used only to detect identity equality.  They
    never order different items sharing a primary tuple.
    """

    normalizer = item_normalizer or (lambda item: item)
    by_key: dict[tuple[Any, ...], tuple[bytes, Any]] = {}
    for raw in items:
        item = normalizer(raw)
        if scalar:
            if isinstance(item, (dict, list)):
                raise CanonicalizationError("scalar set received a structured item")
            key = (item,)
        else:
            if not isinstance(item, dict) or not tuple_fields:
                raise CanonicalizationError("reference set requires a declared primary tuple")
            missing = [field for field in tuple_fields if field not in item]
            if missing:
                raise CanonicalizationError(f"reference missing tuple fields: {missing}")
            key = tuple(item[field] for field in tuple_fields)
        encoded = canonicalize_jcs(item)
        prior = by_key.get(key)
        if prior is not None and prior[0] != encoded:
            raise CanonicalizationError("different normalized items share a primary tuple")
        by_key[key] = (encoded, item)
    return [by_key[key][1] for key in sorted(by_key, key=lambda parts: tuple(_utf16_key(str(part)) for part in parts))]


def fixture_checksum_v0(material: bytes) -> str:
    """A deliberately non-cryptographic checksum for synthetic fixtures only."""

    accumulator = 0
    for index, byte in enumerate(material, start=1):
        accumulator = (accumulator + index * byte) % 4_294_967_291
    return f"{len(material)}-{accumulator:08x}"
