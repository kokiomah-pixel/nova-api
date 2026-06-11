from __future__ import annotations

import json
from typing import Any, Dict


UNCLASSIFIED_GOVERNANCE_EVENT = "unclassified_governance_event"

_SYNTHETIC_MARKERS = ("synthetic", "memory-user")
_AUDIT_MARKERS = ("audit-", "audit_")
_INTERNAL_MARKERS = ("internal", "manual-admin", "feed-metering-user")
_EXTERNAL_MARKERS = ("external", "partner", "customer", "client")
_PRODUCTION_LIKE_MARKERS = ("production", "prod-", "prod_")


def _normalized_text(value: Any, *, uppercase: bool = False) -> Any:
    if value is None:
        return None
    normalized = " ".join(str(value).strip().split())
    if not normalized:
        return None
    return normalized.upper() if uppercase else normalized.lower()


def normalized_canonical_request(intent_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "asset": _normalized_text(intent_dict.get("asset"), uppercase=True),
        "intent": _normalized_text(intent_dict.get("intent")),
        "requested_action": _normalized_text(intent_dict.get("requested_action")),
    }


def compute_canonical_signature(intent_dict: Dict[str, Any]) -> str:
    """Return Nova's stable canonical signature for governance record grouping."""
    return json.dumps(
        normalized_canonical_request(intent_dict),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def infer_record_source_type(account_id: Any) -> str:
    normalized = str(account_id or "").strip().lower()
    if not normalized:
        return "unknown"
    if any(marker in normalized for marker in _SYNTHETIC_MARKERS):
        return "synthetic"
    if any(marker in normalized for marker in _AUDIT_MARKERS):
        return "audit"
    if any(marker in normalized for marker in _INTERNAL_MARKERS):
        return "internal"
    if any(marker in normalized for marker in _PRODUCTION_LIKE_MARKERS):
        return "production_like"
    if any(marker in normalized for marker in _EXTERNAL_MARKERS):
        return "external"
    return "unknown"
