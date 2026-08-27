from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from typing import Any, Mapping, Sequence

from .schema import validate_retail_context_object
from .sources import validate_source_observation


POSITIVE_SOURCE_STATUSES = frozenset({"observed", "stale"})
EXCLUDED_SOURCE_STATUSES = frozenset({"unavailable", "rejected", "unknown"})


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _stable_id(prefix: str, *parts: object) -> str:
    digest = hashlib.sha256(_canonical_json(parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def _rp2_provenance_status(verification_status: str) -> str:
    if verification_status == "verified":
        return "verified"
    if verification_status == "verification_failed":
        return "verification_failed"
    return "present_unverified"


def _gap_status(source_status: str) -> str:
    if source_status == "unavailable":
        return "unavailable"
    return "unresolved"


def build_state_ping(
    subject: Mapping[str, Any],
    observations: Sequence[Mapping[str, Any]],
    *,
    generated_at: str,
) -> dict[str, Any]:
    """Build deterministic, authority-neutral current context from RP3 evidence."""

    if not observations:
        raise ValueError("State Ping requires at least one normalized observation")

    requested_subject = copy.deepcopy(dict(subject))
    normalized_observations: list[dict[str, Any]] = []
    seen_observation_ids: set[str] = set()

    for observation in observations:
        normalized = copy.deepcopy(dict(observation))
        validate_source_observation(normalized)
        if normalized["subject"] != requested_subject:
            raise ValueError("all observations must match the requested subject")
        observation_id = normalized["observation_id"]
        if observation_id in seen_observation_ids:
            raise ValueError("observation_id values must be unique")
        seen_observation_ids.add(observation_id)
        normalized_observations.append(normalized)

    normalized_observations.sort(
        key=lambda item: (item["source_id"], item["observation_id"])
    )
    positive = [
        item
        for item in normalized_observations
        if item["source_status"] in POSITIVE_SOURCE_STATUSES
    ]
    excluded = [
        item
        for item in normalized_observations
        if item["source_status"] in EXCLUDED_SOURCE_STATUSES
    ]

    evidence: list[dict[str, Any]] = []
    claim_metadata: list[dict[str, str]] = []
    limitations_by_id: dict[str, dict[str, Any]] = {}
    gaps_by_id: dict[str, dict[str, Any]] = {}

    def add_limitation(
        key: object,
        description: str,
        impact: str,
    ) -> None:
        limitation_id = _stable_id("limit", key)
        limitations_by_id[limitation_id] = {
            "limitation_id": limitation_id,
            "description": description,
            "impact": impact,
        }

    def add_gap(
        key: object,
        status: str,
        claim_scope: str,
        reason: str,
        source_ids: Sequence[str] = (),
    ) -> None:
        issue_id = _stable_id("gap", key)
        gap: dict[str, Any] = {
            "issue_id": issue_id,
            "status": status,
            "claim_scope": claim_scope,
            "reason": reason,
        }
        if source_ids:
            gap["related_source_ids"] = sorted(set(source_ids))
        gaps_by_id[issue_id] = gap

    for observation in normalized_observations:
        for limitation in observation["limitations"]:
            add_limitation(
                (
                    observation["source_id"],
                    observation["observation_id"],
                    limitation["limitation_id"],
                ),
                limitation["description"],
                limitation["impact"],
            )
            if limitation["impact"] in {"material", "indeterminate"}:
                add_gap(
                    (
                        "input-limitation",
                        observation["observation_id"],
                        limitation["limitation_id"],
                    ),
                    "unresolved",
                    "source limitation",
                    limitation["description"],
                    [observation["source_id"]],
                )

    for observation in excluded:
        source_status = observation["source_status"]
        description = (
            f"Source {observation['source_id']} was excluded from positive evidence "
            f"because its status is {source_status}."
        )
        add_limitation(
            ("excluded-source", observation["observation_id"]),
            description,
            "material",
        )
        add_gap(
            ("excluded-source", observation["observation_id"]),
            _gap_status(source_status),
            "current subject context",
            description,
            [observation["source_id"]],
        )

    for observation in positive:
        source_id = observation["source_id"]
        observation_id = observation["observation_id"]
        for claim in sorted(
            observation["claims"],
            key=lambda item: (item["claim_id"], item["claim_or_observation"]),
        ):
            evidence_id = _stable_id(
                "evidence",
                observation_id,
                source_id,
                claim["claim_id"],
                claim["claim_or_observation"],
            )
            evidence_status = (
                "observed" if claim["claim_status"] == "observed" else "unresolved"
            )
            evidence.append(
                {
                    "evidence_id": evidence_id,
                    "source_id": source_id,
                    "claim_or_observation": claim["claim_or_observation"],
                    "evidence_status": evidence_status,
                }
            )
            claim_metadata.append(
                {
                    "claim_id": claim["claim_id"],
                    "claim_status": claim["claim_status"],
                    "statement": claim["claim_or_observation"],
                    "evidence_id": evidence_id,
                    "source_id": source_id,
                    "observation_id": observation_id,
                }
            )
            if claim["claim_status"] != "observed":
                add_gap(
                    ("claim-status", observation_id, claim["claim_id"]),
                    "unresolved",
                    claim["claim_id"],
                    f"The normalized claim status is {claim['claim_status']}.",
                    [source_id],
                )

        if observation["source_status"] == "stale":
            description = (
                f"Contributing source {source_id} explicitly reports stale status."
            )
            add_limitation(
                ("stale-source", observation_id),
                description,
                "material",
            )
            add_gap(
                ("stale-source", observation_id),
                "unresolved",
                "current source observation",
                description,
                [source_id],
            )

        if observation["verification_status"] != "verified":
            verification_status = observation["verification_status"]
            description = (
                f"Contributing source {source_id} retains verification status "
                f"{verification_status}."
            )
            add_limitation(
                ("verification", observation_id, verification_status),
                description,
                "material",
            )
            add_gap(
                ("verification", observation_id, verification_status),
                "unresolved",
                "source verification",
                description,
                [source_id],
            )

    claims_by_scope: dict[str, list[dict[str, str]]] = defaultdict(list)
    for metadata in claim_metadata:
        claims_by_scope[metadata["claim_id"]].append(metadata)

    contradictions: list[dict[str, Any]] = []
    contradicted_evidence_ids: set[str] = set()
    for claim_id in sorted(claims_by_scope):
        scoped_claims = claims_by_scope[claim_id]
        statements = {item["statement"] for item in scoped_claims}
        source_ids = {item["source_id"] for item in scoped_claims}
        if len(statements) < 2 or len(source_ids) < 2:
            continue
        evidence_ids = sorted({item["evidence_id"] for item in scoped_claims})
        contradicted_evidence_ids.update(evidence_ids)
        contradiction_id = _stable_id(
            "contradiction", claim_id, evidence_ids, sorted(statements)
        )
        contradictions.append(
            {
                "contradiction_id": contradiction_id,
                "evidence_ids": evidence_ids,
                "summary": (
                    f"Multiple sources emitted incompatible normalized values for "
                    f"claim scope {claim_id}."
                ),
                "status": "unresolved",
                "resolution_basis": None,
            }
        )
        add_gap(
            ("contradiction", contradiction_id),
            "unresolved",
            claim_id,
            "The cross-source contradiction remains unresolved.",
            sorted(source_ids),
        )

    for item in evidence:
        if item["evidence_id"] in contradicted_evidence_ids:
            item["evidence_status"] = "contradicted"
    evidence.sort(key=lambda item: item["evidence_id"])

    provenance: list[dict[str, Any]] = []
    for observation in positive:
        observation_claims = [
            item
            for item in claim_metadata
            if item["observation_id"] == observation["observation_id"]
        ]
        if any(
            item["evidence_id"] in contradicted_evidence_ids
            for item in observation_claims
        ):
            reconciliation_status = "contradicted"
        elif any(item["claim_status"] != "observed" for item in observation_claims):
            reconciliation_status = "unresolved"
        else:
            reconciliation_status = "not_assessed"
        provenance.append(
            {
                "source_id": observation["source_id"],
                "source_type": observation["provenance"]["retrieval_mode"],
                "observed_at": observation["observed_at"],
                "source_status": _rp2_provenance_status(
                    observation["verification_status"]
                ),
                "claim_reconciliation_status": reconciliation_status,
                "contribution_scope": sorted(
                    {item["claim_id"] for item in observation_claims}
                ),
            }
        )
    provenance.sort(key=lambda item: item["source_id"])

    if not positive:
        add_gap(
            "no-positive-observation",
            "missing",
            "current subject context",
            "No usable positive retail source observation was available.",
        )
        context_status = "insufficient_evidence"
        freshness = {
            "observed_at": None,
            "source_age_seconds": None,
            "freshness_status": "unknown",
        }
        confidence = {
            "level": "indeterminate",
            "basis": "No positive normalized source observation was available.",
        }
    else:
        oldest = max(
            positive,
            key=lambda item: (
                item["freshness_input"]["source_age_seconds"],
                item["source_id"],
                item["observation_id"],
            ),
        )
        freshness = {
            "observed_at": oldest["observed_at"],
            "source_age_seconds": oldest["freshness_input"]["source_age_seconds"],
            "freshness_status": (
                "stale"
                if any(item["source_status"] == "stale" for item in positive)
                else "unknown"
            ),
        }
        has_material_gap = bool(gaps_by_id)
        if contradictions:
            context_status = "unresolved"
            confidence = {
                "level": "low",
                "basis": "Positive normalized evidence contains an unresolved cross-source contradiction.",
            }
        elif has_material_gap:
            context_status = "partially_resolved"
            all_verified_non_stale = all(
                item["verification_status"] == "verified"
                and item["source_status"] == "observed"
                for item in positive
            )
            confidence = {
                "level": "medium" if all_verified_non_stale else "low",
                "basis": "Some current context is supported, but material evidence gaps or limitations remain.",
            }
        else:
            context_status = "resolved"
            confidence = {
                "level": "medium",
                "basis": "Contributing evidence is verified and has no material unresolved gap or contradiction.",
            }

    resource_material = {
        "subject": requested_subject,
        "observations": normalized_observations,
        "generated_at": generated_at,
    }
    result = {
        "resource_id": _stable_id("state-ping", resource_material),
        "resource_type": "state_ping",
        "subject": requested_subject,
        "schema_version": "0.1.0",
        "generated_at": generated_at,
        "context_status": context_status,
        "freshness": freshness,
        "confidence": confidence,
        "provenance": provenance,
        "evidence": evidence,
        "contradictions": contradictions,
        "unresolved_evidence": [
            gaps_by_id[key] for key in sorted(gaps_by_id)
        ],
        "limitations": [
            limitations_by_id[key] for key in sorted(limitations_by_id)
        ],
        "authority_effect": "none",
    }
    validate_retail_context_object(result)
    return result
