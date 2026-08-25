"""Gate 4 private synthetic adapter for the target-v2 design contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from .canonicalization import (
    CanonicalizationError,
    canonicalize_jcs,
    normalize_declared_set,
    normalize_monetary_amount,
    normalize_timestamp,
)


SCHEMA_VERSION = "design-v2.1"
DERIVATION_VERSION = "gate4-private-synthetic-adapter-v0.1"
CANONICALIZATION_VERSION = "nova-jcs-exact-financial-json-design-v0.1"
SOURCE_TUPLE = (
    "source_id",
    "source_version_or_digest",
    "observed_at",
    "received_at",
    "record_source_type",
)
CONSTRAINT_TUPLE = ("constraint_id_or_digest", "source_id")
CHRONOLOGY_TUPLE = ("reference_type", "reference_id", "version_or_digest")
PERMITTED_ENVIRONMENTS = {"synthetic", "production_like", "live"}


class SyntheticAdapterError(ValueError):
    """Synthetic input violates a declared target-v2 field rule."""


@dataclass(frozen=True)
class AdapterResult:
    response: dict[str, Any]
    normalized_prepared_action_material: dict[str, Any]
    canonical_semantic_material: bytes
    proof_envelope_inputs: dict[str, Any]


class TargetV2SyntheticAdapter:
    """Pure in-memory transformation of explicit synthetic fixture inputs."""

    def __init__(
        self,
        *,
        fingerprint_algorithm_qualification: str,
        fingerprint_function: Callable[[bytes], str],
    ) -> None:
        if not fingerprint_algorithm_qualification.startswith("fixture-only-"):
            raise SyntheticAdapterError("fingerprint algorithm must be explicitly fixture-only")
        self._fingerprint_algorithm_qualification = fingerprint_algorithm_qualification
        self._fingerprint_function = fingerprint_function

    def adapt(self, request: dict[str, Any]) -> AdapterResult:
        """Construct one deterministic response without external side effects."""

        try:
            prepared = self._normalize_prepared_action(request["prepared_action"])
            created_at = normalize_timestamp(request["synthetic_record_created_at"])
            sources = self._normalize_sources(request["evidence"].get("sources", []))
            profile = self._normalize_profile(request["review_profile"])
            constraints = self._normalize_constraints(
                request["institution_context"].get("relevant_constraints", [])
            )
            prior = self._normalize_chronology(
                request["institution_context"].get("prior_review_references", [])
            )
            memory = self._normalize_chronology(
                request["institution_context"].get("accepted_memory_references", [])
            )
        except (KeyError, TypeError, CanonicalizationError) as exc:
            raise SyntheticAdapterError(str(exc)) from exc

        conflicts = self._normalize_conflicts(
            request["evidence"].get("unresolved_source_conflicts", [])
        )
        environments = {source["record_source_type"] for source in sources}
        record_source_value = next(iter(environments)) if len(environments) == 1 else "mixed"
        source_state = self._source_state(sources, conflicts)
        context_state, temporal_reasons = self._context_state(
            sources=sources,
            created_at=created_at,
            max_age_seconds=profile.get("source_max_age_seconds"),
            superseded_by=request["prepared_action"].get("superseded_by_reference"),
        )
        missing = self._missing_required_context(request, profile)
        completeness = self._completeness(profile, conflicts, missing)
        identity = self._proposal_identity(prepared, request["prepared_action"])

        intended_window = prepared["intended_time_window"]
        observed_values = [source["observed_at"] for source in sources if source["observed_at"] is not None]
        received_values = [source["received_at"] for source in sources if source["received_at"] is not None]
        response: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "context_id": f"synthetic-context:{request['request_id']}",
            "request_id": request["request_id"],
            "created_at": created_at,
            "prepared_action_reference": {
                "reference_id": request["prepared_action"].get("reference_id", identity["value"]),
                "proposal_version_identity": identity,
                "reference_type": "opaque_external_reference",
                "payload_embedded": False,
            },
            "review_profile_reference": {
                key: profile[key] for key in ("profile_id", "profile_version", "profile_owner", "profile_hash")
            },
            "record_source_type": {"value": record_source_value, "source_segmentation": deepcopy(sources)},
            "context_state": {"value": context_state, "reasons": temporal_reasons},
            "source_state": {
                "value": source_state,
                "sources": deepcopy(sources),
                "unresolved_source_conflicts": deepcopy(conflicts),
            },
            "constraint_context": {
                "observed_constraints": deepcopy(constraints),
                "constraint_sources": [],
                "unresolved_constraint_questions": [],
            },
            "temporal_context": {
                "source_observed_at": min(observed_values) if observed_values else {"state": "unavailable"},
                "source_received_at": max(received_values) if received_values else {"state": "unavailable"},
                "review_context_created_at": created_at,
                "intended_action_window": deepcopy(intended_window),
                "temporal_conflicts": [],
                "pending_state": [] if context_state in {"current", "stale", "superseded"} else [{"condition_id": "missing_source_time"}],
            },
            "contradiction_context": {
                "source_conflicts": deepcopy(conflicts),
                "constraint_conflicts": [],
                "temporal_conflicts": [],
                "chronology_conflicts": [],
                "unresolved_questions": [],
            },
            "review_completeness": {
                "value": completeness,
                "missing_context": missing,
                "unresolved_conditions": [],
            },
            "chronology_context": {
                "prior_review_references": prior,
                "accepted_memory_references": memory,
                "relevant_changes_since_prior_review": [],
            },
            "authority_handoff": {
                "decision_owner": "local_institutional_authority",
                "execution_owner": "external_system",
                "Nova_authority_effect": "none",
            },
            "reproducibility": {
                "schema_version": SCHEMA_VERSION,
                "source_versions": normalize_declared_set(
                    [source["source_version_or_digest"] for source in sources], scalar=True
                ),
                "classification_version": DERIVATION_VERSION,
                "review_profile_id": profile["profile_id"],
                "review_profile_version": profile["profile_version"],
                "review_profile_hash": profile["profile_hash"],
                "record_source_type": record_source_value,
                "source_segmentation": deepcopy(sources),
                "context_hash": {"state": "not_constructed", "reason": "production_algorithm_not_selected"},
                "signature": {"state": "not_constructed", "reason": "production_signature_not_selected"},
            },
            "boundary": {
                "approval_effect": "none",
                "authorization_effect": "none",
                "execution_effect": "none",
            },
        }
        action_id = request["prepared_action"].get("action_id")
        if action_id is not None:
            response["prepared_action_reference"]["action_id"] = action_id

        semantic_projection = self._semantic_projection(response)
        semantic_bytes = canonicalize_jcs(semantic_projection)
        proof_inputs = {
            "semantic_context_material": semantic_bytes,
            "canonicalization_version": CANONICALIZATION_VERSION,
            "derivation_version": DERIVATION_VERSION,
            "schema_version": SCHEMA_VERSION,
            "record_identity": response["context_id"],
            "record_created_at": created_at,
            "digest_algorithm_selection": "not_selected",
            "signature_algorithm_selection": "not_selected",
            "authority_effect": "none",
            "execution_effect": "none",
        }
        return AdapterResult(response, prepared, semantic_bytes, proof_inputs)

    def _normalize_prepared_action(self, raw: dict[str, Any]) -> dict[str, Any]:
        amount = raw["amount_or_scope"]
        window = raw["intended_time_window"]
        normalized_window: dict[str, Any] = {}
        for boundary in ("start", "end"):
            value = window.get(boundary)
            if not isinstance(value, str):
                raise SyntheticAdapterError(f"intended_time_window.{boundary} is required")
            normalized_window[boundary] = normalize_timestamp(value)
        return {
            "action_type": raw["action_type"],
            "asset_or_resource": raw["asset_or_resource"],
            "amount_or_scope": normalize_monetary_amount(
                amount["value"],
                asset_id=amount["asset_id"],
                scale=amount["scale"],
                max_precision=amount["max_precision"],
                max_scale=amount["max_scale"],
                max_abs_exponent=amount["max_abs_exponent"],
                max_input_characters=amount["max_input_characters"],
            ),
            "destination_or_venue": raw["destination_or_venue"],
            "intended_time_window": normalized_window,
        }

    def _normalize_sources(self, raw_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not raw_sources:
            raise SyntheticAdapterError("a source environment cannot be inferred from an empty source set")
        normalized: list[dict[str, Any]] = []
        for raw in raw_sources:
            environment = raw["record_source_type"]
            if environment not in PERMITTED_ENVIRONMENTS:
                raise SyntheticAdapterError(f"invalid evidence environment: {environment}")
            item = {
                "source_id": raw["source_id"],
                "source_version_or_digest": raw["source_version_or_digest"],
                "observed_at": normalize_timestamp(raw["observed_at"]) if raw.get("observed_at") else None,
                "received_at": normalize_timestamp(raw["received_at"]) if raw.get("received_at") else None,
                "record_source_type": environment,
            }
            normalized.append(item)
        return normalize_declared_set(normalized, tuple_fields=SOURCE_TUPLE)

    @staticmethod
    def _normalize_constraints(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        allowed = set(CONSTRAINT_TUPLE)
        for item in raw_items:
            if set(item) != allowed:
                raise SyntheticAdapterError("constraint references must use only the approved opaque identity")
        return normalize_declared_set(raw_items, tuple_fields=CONSTRAINT_TUPLE)

    @staticmethod
    def _normalize_conflicts(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for item in raw_items:
            if set(item) != {"conflict_id", "variants"}:
                raise SyntheticAdapterError("source conflicts must use the bounded synthetic conflict shape")
            normalized.append(
                {
                    "conflict_id": item["conflict_id"],
                    "variants": normalize_declared_set(item["variants"], scalar=True),
                }
            )
        return normalize_declared_set(normalized, tuple_fields=("conflict_id",))

    def _normalize_chronology(self, raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        allowed = set(CHRONOLOGY_TUPLE)
        for item in raw_items:
            if set(item) != allowed:
                raise SyntheticAdapterError("chronology and accepted-memory references must remain opaque identities")
        return normalize_declared_set(raw_items, tuple_fields=CHRONOLOGY_TUPLE)

    @staticmethod
    def _normalize_profile(raw: dict[str, Any]) -> dict[str, Any]:
        for key in ("profile_id", "profile_version", "profile_owner", "profile_hash"):
            if key not in raw:
                raise SyntheticAdapterError(f"review profile missing {key}")
        return deepcopy(raw)

    def _proposal_identity(self, prepared: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
        external = raw.get("proposal_version_id")
        if external is not None:
            return {
                "value": external,
                "source_type": "external_institution_or_orchestrator",
                "establishes_action_lineage": False,
            }
        material = canonicalize_jcs(prepared)
        return {
            "value": self._fingerprint_function(material),
            "source_type": "Nova_derived_proposal_fingerprint",
            "algorithm_qualification": self._fingerprint_algorithm_qualification,
            "material_scope": "canonical_prepared_action_material_only",
            "establishes_action_lineage": False,
        }

    @staticmethod
    def _source_state(sources: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> str:
        if not sources:
            return "unavailable"
        if conflicts:
            return "conflicted"
        if any(source["observed_at"] is None or source["received_at"] is None for source in sources):
            return "partial"
        return "complete"

    @staticmethod
    def _context_state(
        *,
        sources: list[dict[str, Any]],
        created_at: str,
        max_age_seconds: int | None,
        superseded_by: Any,
    ) -> tuple[str, list[str]]:
        if superseded_by is not None:
            return "superseded", ["explicit_superseding_reference"]
        if not sources or any(source["observed_at"] is None for source in sources):
            return "uncertain", ["missing_source_observed_at"]
        if max_age_seconds is None:
            return "uncertain", ["profile_source_age_threshold_unavailable"]
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        observed = [datetime.fromisoformat(source["observed_at"].replace("Z", "+00:00")) for source in sources]
        if any((created - value).total_seconds() > max_age_seconds for value in observed):
            return "stale", ["profile_source_age_threshold_exceeded"]
        return "current", []

    @staticmethod
    def _missing_required_context(request: dict[str, Any], profile: dict[str, Any]) -> list[str]:
        if profile.get("required_field_inventory_available") is False:
            return []
        missing: list[str] = []
        for path in profile.get("required_context_fields", []):
            cursor: Any = request
            absent = False
            for part in path.split("."):
                if not isinstance(cursor, dict) or part not in cursor or cursor[part] is None:
                    absent = True
                    break
                cursor = cursor[part]
            if absent or cursor == []:
                missing.append(path)
        return normalize_declared_set(missing, scalar=True)

    @staticmethod
    def _completeness(
        profile: dict[str, Any], conflicts: list[dict[str, Any]], missing: list[str]
    ) -> str:
        if profile.get("required_field_inventory_available") is False:
            return "unavailable"
        if conflicts:
            return "conflicted"
        if missing:
            return "partial"
        return "complete"

    @staticmethod
    def _semantic_projection(response: dict[str, Any]) -> dict[str, Any]:
        projection = deepcopy(response)
        for key in ("context_id", "request_id", "created_at"):
            projection.pop(key, None)
        projection["temporal_context"].pop("review_context_created_at", None)
        projection["reproducibility"].pop("context_hash", None)
        projection["reproducibility"].pop("signature", None)
        return {
            "schema_identity": SCHEMA_VERSION,
            "derivation_identity": DERIVATION_VERSION,
            "canonicalization_identity": CANONICALIZATION_VERSION,
            "review_context_response": projection,
        }
