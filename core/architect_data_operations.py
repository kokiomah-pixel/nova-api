from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import yaml
from jsonschema import validate as validate_json_schema

from core.accepted_state_synchronization import synchronization_state


EVIDENCE_STATES = {
    "observed_runtime",
    "repository_validated",
    "configured",
    "inferred",
    "unknown",
    "unavailable",
}

DATA_MODES = {"synthetic", "offline_fixture", "production_like", "live", "mixed", "unknown"}
SOURCE_CLASSES = {"synthetic", "production_like", "live", "inferred", "unavailable", "unknown"}
STATUS_VALUES = {"healthy", "degraded", "unavailable", "unknown"}
AVAILABILITY_BASIS = {
    "verified_path",
    "runtime_discovery",
    "configured",
    "repository_contract",
    "unavailable",
    "unknown",
}
SOURCE_KINDS = {
    "runtime_record_source",
    "runtime_interface",
    "configured_source",
    "repository_contract",
    "fixture_source",
}
RUNTIME_OBSERVATION_STATUSES = {
    "no_sources_connected",
    "sources_discovered_no_records_ingested",
    "partial_records_ingested",
    "bounded_observation_complete",
    "unavailable",
    "unknown",
}
AUTHORITY_EFFECTS = {"none"}
ANOMALY_TYPES = {
    "source_provenance_missing",
    "source_class_conflict",
    "stale_source",
    "unexplained_classification_drift",
    "governance_epoch_mismatch",
    "proof_verification_failure",
    "replay_failure",
    "canonical_signature_mismatch",
    "chronology_link_failure",
    "authority_effect_invalid",
    "execution_boundary_violation",
    "evidence_source_unavailable",
    "unexpected_source_field",
}
SEVERITIES = {"informational", "watch", "material", "critical"}
IMMEDIATE_NOTIFICATION_TYPES = {
    "execution_boundary_violation",
    "authority_effect_invalid",
    "chronology_link_failure",
}
REPEATED_NOTIFICATION_TYPES = {
    "unexplained_classification_drift",
    "proof_verification_failure",
    "replay_failure",
    "canonical_signature_mismatch",
    "chronology_link_failure",
    "source_provenance_missing",
}
QUIET_TRACKING_TYPES = {
    "isolated_validation_failure",
    "isolated_stale_fixture",
    "known_synthetic_source_gap",
    "expected_classification_change",
    "transient_endpoint_error",
    "evidence_source_temporarily_unavailable",
}
SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "bearer",
    "private_key",
    "secret",
    "wallet_credentials",
    "raw_payload",
    "raw_prompt",
    "policy_weights",
}
SOURCE_DEPENDENCIES = [
    "production_API_request_metadata",
    "chronology_validation_results",
    "bounded_proof_record_ingestion",
    "bounded_reflex_governance_record_ingestion",
    "verified_live_provenance_source",
]
POLICY_DEPENDENCIES = [
    "operating_observation_window",
    "reporting_cadence",
    "source_freshness_thresholds",
    "anomaly_repeat_thresholds",
    "severity_mapping",
    "runtime_evidence_retention",
    "permitted_record_identifiers",
    "live_provenance_standard",
    "who_receives_material_alerts",
]
DEFAULT_POLICY_PATH = Path("config/architect_data_operations_policy.yaml")
POLICY_SCHEMA_PATH = Path("specs/architect_data_operations_policy.schema.json")
PROOF_REGISTRY_PERMITTED_FIELDS = {
    "proof_id",
    "decision_id",
    "created_at",
    "verified_at",
    "verification_status",
    "canonical_signature",
    "reproducibility_hash",
    "governance_epoch_id",
    "source_class",
    "provenance_status",
    "authority_effect",
}
PROHIBITED_RUNTIME_FIELDS = {
    "raw_payload",
    "action_payload",
    "private_key",
    "api_key",
    "API_key",
    "wallet_credentials",
    "account_number",
    "model_prompt",
    "hidden_policy_weights",
    "unrestricted_source_content",
}


def evidence_value(value: Any, evidence_state: str, reason: Optional[str] = None) -> Dict[str, Any]:
    if evidence_state not in EVIDENCE_STATES:
        raise ValueError(f"Unsupported evidence_state: {evidence_state}")
    item = {"value": value, "evidence_state": evidence_state}
    if reason:
        item["reason"] = reason
    return item


def rate_value(numerator: int, denominator: int) -> Dict[str, Any]:
    if denominator == 0:
        return {"value": None, "evidence_state": "unknown", "reason": "no_observations"}
    return {"value": round(numerator / denominator, 6), "evidence_state": "inferred"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(data: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_bounded_evidence(path: Path) -> Dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Architect data operations evidence must be a JSON object")
    payload.setdefault("records", [])
    payload.setdefault("evidence_sources", [])
    if not isinstance(payload["records"], list):
        raise ValueError("records must be a list")
    return payload


def load_runtime_evidence_policy(path: Path = DEFAULT_POLICY_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Runtime evidence policy is required before ingestion: {path}")
    with path.open("r", encoding="utf-8") as handle:
        policy = yaml.safe_load(handle)
    if not isinstance(policy, dict):
        raise ValueError("Runtime evidence policy must be a YAML object")
    validate_runtime_evidence_policy(policy)
    schema_path = POLICY_SCHEMA_PATH
    if schema_path.exists():
        schema = load_json(schema_path)
        validate_json_schema(instance=policy, schema=schema)
    return policy


def validate_runtime_evidence_policy(policy: Mapping[str, Any]) -> None:
    root = policy.get("runtime_evidence_policy")
    if not isinstance(root, Mapping):
        raise ValueError("runtime_evidence_policy is required")
    if str(root.get("policy_version")) != "1.0":
        raise ValueError("Only runtime evidence policy version 1.0 is supported")
    activation = root.get("activation")
    if not isinstance(activation, Mapping):
        raise ValueError("activation policy is required")
    required_false = {
        "recurring_scheduler_enabled",
        "external_alert_delivery_enabled",
        "runtime_mutation_allowed",
    }
    for key in required_false:
        if activation.get(key) is not False:
            raise ValueError(f"{key} must be false for policy version 1.0")
    if activation.get("read_only") is not True or activation.get("manual_execution_only") is not True:
        raise ValueError("Policy must require read-only manual execution")
    retention = root.get("retention_policy", {})
    raw_copy = retention.get("raw_source_payload_copy", {}) if isinstance(retention, Mapping) else {}
    if isinstance(raw_copy, Mapping) and raw_copy.get("allowed") is not False:
        raise ValueError("raw_source_payload_copy.allowed must be false")
    sources = root.get("approved_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("At least one approved source is required")
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("approved source entries must be objects")
        if not source.get("source_id"):
            raise ValueError("approved source requires source_id")
        if not source.get("permitted_fields"):
            raise ValueError(f"approved source {source.get('source_id')} requires permitted_fields")


def validate_source_authorization(policy: Mapping[str, Any], source_id: str) -> Dict[str, Any]:
    root = policy["runtime_evidence_policy"]
    for source in root.get("approved_sources", []):
        if source.get("source_id") == source_id:
            if source.get("ingestion_status") not in {
                "approved_for_bounded_metadata",
                "approved_when_structured_metadata_exists",
                "approved_when_deterministic_validator_output_exists",
            }:
                raise ValueError(f"Source {source_id} is not approved for ingestion")
            return dict(source)
    raise ValueError(f"Source is not approved by policy: {source_id}")


def apply_field_allowlist(
    record: Mapping[str, Any],
    permitted_fields: Iterable[str],
    prohibited_fields: Iterable[str],
    *,
    strict: bool = False,
) -> Tuple[Dict[str, Any], List[str], List[str]]:
    permitted = set(permitted_fields)
    prohibited = {field.lower() for field in prohibited_fields}
    clean: Dict[str, Any] = {}
    unexpected: List[str] = []
    rejected: List[str] = []
    for key, value in record.items():
        lowered = key.lower()
        if lowered in prohibited or any(token.lower() in lowered for token in PROHIBITED_RUNTIME_FIELDS):
            rejected.append(key)
            continue
        if key not in permitted:
            unexpected.append(key)
            continue
        clean[key] = value
    if strict and rejected:
        raise ValueError(f"Prohibited fields encountered: {', '.join(sorted(rejected))}")
    return clean, unexpected, rejected


def hash_permitted_identifier(value: Any, salt: Optional[str]) -> Dict[str, Any]:
    if not value or not salt:
        return evidence_value("redacted", "unavailable", "identifier_hash_policy_not_configured")
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
    return evidence_value(f"sha256:{digest}", "observed_runtime")


def apply_retention_metadata(policy: Mapping[str, Any]) -> Dict[str, Any]:
    retention = policy["runtime_evidence_policy"].get("retention_policy", {})
    return {
        "raw_source_payload_copy_allowed": False,
        "generated_snapshot_retention_days": retention.get("generated_snapshot", {}).get("retention_days"),
        "Architect_brief_retention_days": retention.get("Architect_brief", {}).get("retention_days"),
    }


def classify_live_provenance(record: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    standard = policy["runtime_evidence_policy"].get("live_provenance_standard", {})
    required = standard.get("required", [])
    if str(record.get("source_class")) in {"synthetic", "offline_fixture"}:
        return "synthetic"
    if all(record.get(condition) for condition in required):
        return "live"
    return "unknown"


def apply_severity_policy(anomaly_type: str, occurrence_count: int, independent_record_count: int) -> str:
    if anomaly_type in {"execution_boundary_violation", "authority_effect_invalid"}:
        return "critical"
    if occurrence_count >= 3 and independent_record_count >= 2:
        return "material"
    if occurrence_count > 0:
        return "watch"
    return "informational"


def parse_timestamp(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def rolling_window(generated_at: Optional[str], hours: int = 24) -> Dict[str, str]:
    end = parse_timestamp(generated_at) or datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(hours=hours)
    return {
        "start": start.isoformat().replace("+00:00", "Z"),
        "end": end.isoformat().replace("+00:00", "Z"),
        "timezone": "UTC",
    }


def event_in_window(timestamp: Optional[str], window: Mapping[str, str]) -> bool:
    event_time = parse_timestamp(timestamp)
    start = parse_timestamp(window.get("start"))
    end = parse_timestamp(window.get("end"))
    if event_time is None or start is None or end is None:
        return False
    return start <= event_time <= end


def build_bounded_runtime_evidence() -> Dict[str, Any]:
    return {
        "data_mode": "unknown",
        "environment": "bounded_runtime",
        "observation_window": {"start": None, "end": None},
        "records": [],
        "limitations": [
            "Bounded runtime mode reports only evidence sources discoverable in the current environment.",
            "No live operating records are simulated by this generator.",
            "Source existence does not establish service, proof, chronology, or governance health.",
            "Live operating health remains unknown.",
        ],
    }


def extract_proof_registry_metadata(raw_record: Mapping[str, Any], proof_id: str) -> Dict[str, Any]:
    proof = raw_record.get("proof") if isinstance(raw_record.get("proof"), Mapping) else {}
    validation = proof.get("validation") if isinstance(proof.get("validation"), Mapping) else {}
    verification_status = "passed" if validation.get("reproducibility_hash") or raw_record.get("reproducibility_hash") else "unknown"
    return {
        "proof_id": proof_id,
        "decision_id": raw_record.get("decision_id") or proof.get("decision_id"),
        "created_at": raw_record.get("created_at") or proof.get("created_at") or raw_record.get("timestamp_utc"),
        "verified_at": validation.get("verified_at"),
        "verification_status": raw_record.get("verification_status") or verification_status,
        "canonical_signature": raw_record.get("canonical_signature") or proof.get("canonical_signature"),
        "reproducibility_hash": raw_record.get("reproducibility_hash") or validation.get("reproducibility_hash"),
        "governance_epoch_id": raw_record.get("governance_epoch_id") or proof.get("governance_epoch_id"),
        "source_class": raw_record.get("source_class") or "unknown",
        "data_mode": raw_record.get("data_mode") or "offline_fixture",
        "live_provenance_verified": bool(raw_record.get("live_provenance_verified", False)),
        "provenance_status": raw_record.get("provenance_status") or "complete",
        "authority_effect": raw_record.get("authority_effect") or "none",
        "nova_execution_attempted": bool(raw_record.get("nova_execution_attempted", False)),
        "request_id": raw_record.get("request_id"),
        "chronology_record_id": raw_record.get("chronology_record_id"),
        "raw_external_identifier": raw_record.get("raw_external_identifier"),
        "unexpected_runtime_note": raw_record.get("unexpected_runtime_note"),
    }


def proof_metadata_to_observation(
    metadata: Mapping[str, Any],
    *,
    index: int,
    salt: Optional[str],
    policy: Mapping[str, Any],
    window: Mapping[str, str],
) -> Optional[Dict[str, Any]]:
    timestamp = metadata.get("created_at") or metadata.get("verified_at")
    if not event_in_window(str(timestamp) if timestamp else None, window):
        return None
    proof_identifier = hash_permitted_identifier(metadata.get("proof_id"), salt)
    decision_identifier = hash_permitted_identifier(metadata.get("decision_id"), salt)
    source_class = classify_live_provenance(metadata, policy)
    provenance_complete = bool(metadata.get("provenance_status") == "complete")
    verification_status = str(metadata.get("verification_status") or "unknown")
    return {
        "record_id": proof_identifier["value"] if proof_identifier["evidence_state"] == "observed_runtime" else f"proof_registry_record_{index}",
        "proof_id_hash": proof_identifier,
        "decision_id_hash": decision_identifier,
        "decision_id": decision_identifier["value"],
        "observed_at": timestamp,
        "source_class": source_class,
        "data_mode": str(metadata.get("data_mode") or "offline_fixture"),
        "live_provenance_verified": bool(metadata.get("live_provenance_verified", False)) and source_class == "live",
        "provenance_complete": provenance_complete,
        "provenance_missing": not provenance_complete,
        "freshness_state": "within_policy",
        "proof_created": True,
        "proof_verification_passed": verification_status == "passed",
        "proof_verification_failed": verification_status == "failed",
        "replay_attempted": False,
        "authority_effect": str(metadata.get("authority_effect") or "none"),
        "nova_execution_attempted": bool(metadata.get("nova_execution_attempted", False)),
        "governance_epoch_id": metadata.get("governance_epoch_id"),
    }


def build_proof_registry_pilot_evidence(
    *,
    policy_path: Path = DEFAULT_POLICY_PATH,
    repo_root: Path = Path.cwd(),
    generated_at: Optional[str] = None,
    identifier_salt: Optional[str] = None,
    proof_registry_path: Optional[Path] = None,
) -> Dict[str, Any]:
    policy = load_runtime_evidence_policy(policy_path)
    source_policy = validate_source_authorization(policy, "proof_registry")
    registry_path = proof_registry_path or (repo_root / str(source_policy.get("interface", ".proof_registry.json")))
    window = rolling_window(generated_at, hours=int(policy["runtime_evidence_policy"]["observation_window"]["duration_hours"]))
    if not registry_path.exists():
        return {
            "data_mode": "unknown",
            "environment": "local_or_controlled_private_environment",
            "observation_window": window,
            "records": [],
            "evidence_sources": [
                {
                    "name": "proof_registry",
                    "path_or_interface": str(registry_path),
                    "source_kind": "runtime_record_source",
                    "data_mode": "unknown",
                    "contains_sensitive_data": False,
                    "retention_policy": "source_file_unmodified",
                    "availability": _availability(
                        available=False,
                        basis="unavailable",
                        verified_at=generated_at,
                        records_ingested=False,
                        record_count=0,
                        reason="source_file_unavailable",
                    ),
                    "authoritative_for": source_policy["authority_scope"]["authoritative_for"],
                    "not_authoritative_for": source_policy["authority_scope"]["not_authoritative_for"],
                }
            ],
            "limitations": ["Proof registry source file was unavailable."],
            "policy_status": "loaded_and_validated",
            "retention_metadata": apply_retention_metadata(policy),
        }

    raw = load_json(registry_path)
    if not isinstance(raw, Mapping):
        raise ValueError("Proof registry must be a JSON object")
    permitted = source_policy.get("permitted_fields", [])
    prohibited = source_policy.get("prohibited_fields", [])
    records: List[Dict[str, Any]] = []
    unexpected_fields: List[str] = []
    rejected_fields: List[str] = []
    for index, (proof_id, raw_record) in enumerate(raw.items()):
        if not isinstance(raw_record, Mapping):
            continue
        metadata = extract_proof_registry_metadata(raw_record, str(proof_id))
        clean, unexpected, rejected = apply_field_allowlist(metadata, permitted, prohibited)
        unexpected_fields.extend(unexpected)
        rejected_fields.extend(rejected)
        observation = proof_metadata_to_observation(
            clean,
            index=index,
            salt=identifier_salt,
            policy=policy,
            window=window,
        )
        if observation:
            safe_unexpected = [
                field
                for field in unexpected
                if field
                not in {
                    "request_id",
                    "chronology_record_id",
                    "raw_external_identifier",
                    "data_mode",
                    "live_provenance_verified",
                    "nova_execution_attempted",
                }
            ]
            if safe_unexpected:
                observation["unexpected_source_fields"] = sorted(safe_unexpected)
            if rejected:
                observation["prohibited_source_fields"] = sorted(rejected)
            records.append(observation)
    limitations = [
        "Stage A reads proof-registry metadata only.",
        "No raw proof payloads, normalized requests, request bodies, prompts, wallet data, or policy weights are copied.",
    ]
    if not identifier_salt:
        limitations.append("Identifier salt was not configured; raw identifiers were redacted.")
    if unexpected_fields:
        limitations.append("Unexpected proof-registry fields were dropped by allowlist.")
    if rejected_fields:
        limitations.append("Prohibited proof-registry fields were rejected by field name.")
    return {
        "data_mode": "unknown",
        "environment": "local_or_controlled_private_environment",
        "observation_window": window,
        "records": records,
        "evidence_sources": [
            {
                "name": "proof_registry",
                "path_or_interface": str(registry_path),
                "source_kind": "runtime_record_source",
                "data_mode": "unknown",
                "contains_sensitive_data": False,
                "retention_policy": "source_file_unmodified",
                "availability": _availability(
                    available=True,
                    basis="verified_path",
                    verified_at=generated_at,
                    records_ingested=bool(records),
                    record_count=len(records),
                    reason="approved_stage_a_metadata_ingestion" if records else "no_in_window_records",
                ),
                "authoritative_for": source_policy["authority_scope"]["authoritative_for"],
                "not_authoritative_for": source_policy["authority_scope"]["not_authoritative_for"],
            }
        ],
        "limitations": limitations,
        "policy_status": "loaded_and_validated",
        "retention_metadata": apply_retention_metadata(policy),
    }


def redact_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    redacted: Dict[str, Any] = {}
    for key, value in record.items():
        lowered = key.lower()
        if lowered in SENSITIVE_KEYS or any(token in lowered for token in SENSITIVE_KEYS):
            continue
        if isinstance(value, dict):
            redacted[key] = redact_record(value)
        elif isinstance(value, list):
            redacted[key] = [
                redact_record(item) if isinstance(item, dict) else item
                for item in value
                if not isinstance(item, str) or len(item) <= 96
            ]
        elif isinstance(value, str) and len(value) > 160:
            redacted[key] = value[:64] + "...redacted"
        else:
            redacted[key] = value
    return redacted


def normalize_record(raw_record: Mapping[str, Any], index: int) -> Dict[str, Any]:
    record = redact_record(raw_record)
    record_id = str(record.get("record_id") or f"record-{index + 1}")
    source_class = str(record.get("source_class") or "unknown")
    if source_class not in SOURCE_CLASSES:
        source_class = "unknown"
    data_mode = str(record.get("data_mode") or "unknown")
    if data_mode not in DATA_MODES:
        data_mode = "unknown"
    normalized = dict(record)
    normalized.update(
        {
            "record_id": record_id,
            "source_class": source_class,
            "data_mode": data_mode,
            "live_provenance_verified": bool(record.get("live_provenance_verified", False)),
            "provenance_complete": bool(record.get("provenance_complete", False)),
            "provenance_conflicting": bool(record.get("provenance_conflicting", False)),
            "freshness_state": str(record.get("freshness_state") or "unknown"),
            "authority_effect": str(record.get("authority_effect") or ""),
            "nova_execution_attempted": bool(record.get("nova_execution_attempted", False)),
        }
    )
    if normalized["source_class"] == "live" and not normalized["live_provenance_verified"]:
        normalized["source_class"] = "unknown"
        normalized["source_class_reason"] = "live_source_requires_verified_provenance"
    return normalized


def normalize_records(records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_record(record, index) for index, record in enumerate(records)]


def _availability(
    *,
    available: bool,
    basis: str,
    verified_at: Optional[str],
    records_ingested: bool = False,
    record_count: int = 0,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    if basis not in AVAILABILITY_BASIS:
        raise ValueError(f"Unsupported availability basis: {basis}")
    result = {
        "available": available,
        "basis": basis,
        "verified_at": verified_at,
        "records_ingested": records_ingested,
        "record_count": record_count,
    }
    if reason:
        result["reason"] = reason
    return result


def _normalize_evidence_source(source: Mapping[str, Any]) -> Dict[str, Any]:
    normalized = dict(source)
    source_kind = str(normalized.get("source_kind") or "configured_source")
    if source_kind not in SOURCE_KINDS:
        source_kind = "configured_source"
    normalized["source_kind"] = source_kind
    if "availability" not in normalized:
        available = bool(normalized.pop("available_in_current_environment", False))
        normalized["availability"] = _availability(
            available=available,
            basis="configured" if available else "unknown",
            verified_at=None,
        )
    normalized.setdefault("contains_sensitive_data", False)
    normalized.setdefault("retention_policy", "not declared")
    normalized.setdefault("authoritative_for", [])
    normalized.setdefault("not_authoritative_for", ["operating_health"])
    return normalized


def discover_runtime_evidence_sources(
    repo_root: Path,
    *,
    verified_at: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    candidates = [
        {
            "name": "proof_registry",
            "path_or_interface": ".proof_registry.json",
            "source_kind": "runtime_record_source",
            "data_mode": "unknown",
            "contains_sensitive_data": False,
            "retention_policy": "runtime_configured_file; not governed by this layer",
            "authoritative_for": ["candidate_proof_record_surface"],
            "not_authoritative_for": ["live_provenance", "chronology_acceptance", "external_execution", "operating_health"],
        },
        {
            "name": "reflex_governance_records",
            "path_or_interface": ".reflex_governance_records.jsonl",
            "source_kind": "runtime_record_source",
            "data_mode": "unknown",
            "contains_sensitive_data": False,
            "retention_policy": "runtime_configured_file; not governed by this layer",
            "authoritative_for": ["candidate_classification_context_surface"],
            "not_authoritative_for": ["Reflex Memory acceptance", "production_health", "operating_health"],
        },
        {
            "name": "application_code_contract",
            "path_or_interface": "app.py and core modules",
            "source_kind": "repository_contract",
            "data_mode": "repository_validated",
            "contains_sensitive_data": False,
            "retention_policy": "git repository",
            "authoritative_for": ["designed_endpoints", "repository_validated_behavior"],
            "not_authoritative_for": ["observed_runtime_activity", "operating_health"],
        },
        {
            "name": "test_and_fixture_contract",
            "path_or_interface": "tests/ and fixtures/",
            "source_kind": "fixture_source",
            "data_mode": "offline_fixture",
            "contains_sensitive_data": False,
            "retention_policy": "git repository",
            "authoritative_for": ["contract_validation"],
            "not_authoritative_for": ["live_operating_evidence", "operating_health"],
        },
    ]
    available: List[Dict[str, Any]] = []
    missing: List[str] = []
    for source in candidates:
        source = dict(source)
        if source["name"] == "application_code_contract":
            available_now = (repo_root / "app.py").exists() and (repo_root / "core").exists()
            basis = "repository_contract" if available_now else "unavailable"
        elif source["name"] == "test_and_fixture_contract":
            available_now = (repo_root / "tests").exists() and (repo_root / "fixtures").exists()
            basis = "repository_contract" if available_now else "unavailable"
        else:
            available_now = (repo_root / str(source["path_or_interface"])).exists()
            basis = "verified_path" if available_now else "unavailable"
        source["availability"] = _availability(
            available=available_now,
            basis=basis,
            verified_at=verified_at if basis == "verified_path" else None,
            records_ingested=False,
            record_count=0,
            reason="ingestion_policy_not_yet_approved",
        )
        available.append(source)
        if not available_now:
            missing.append(source["name"])
    return available, missing


def _status_from_counts(total: int, failures: int) -> str:
    if total == 0:
        return "unknown"
    if failures == 0:
        return "healthy"
    if failures < total:
        return "degraded"
    return "unavailable"


def health_status(total: int, failures: int, observed: bool) -> Dict[str, Any]:
    if not observed:
        return evidence_value("unknown", "unknown", "no_runtime_records_ingested")
    return evidence_value(_status_from_counts(total, failures), "inferred")


def compute_service_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    requests = [record for record in records if record.get("request_observed")]
    failures = sum(1 for record in requests if record.get("validation_failed") or record.get("internal_error"))
    latencies = sorted(int(record.get("latency_ms", 0)) for record in requests if record.get("latency_ms") is not None)
    median = latencies[len(latencies) // 2] if latencies else None
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))] if latencies else None
    endpoints = {
        "v1_context": evidence_value(
            "observed" if any(record.get("endpoint") == "/v1/context" for record in requests) else "unknown",
            "observed_runtime" if requests else "unknown",
        ),
        "v1_proof": evidence_value(
            "observed" if any(str(record.get("endpoint", "")).startswith("/v1/proof") for record in requests) else "unknown",
            "observed_runtime" if requests else "unknown",
        ),
    }
    return {
        "endpoint_status": endpoints,
        "requests_observed": evidence_value(len(requests), "observed_runtime" if requests else "unknown"),
        "successful_responses": evidence_value(sum(1 for record in requests if record.get("response_success")), "observed_runtime" if requests else "unknown"),
        "validation_failures": evidence_value(sum(1 for record in requests if record.get("validation_failed")), "observed_runtime" if requests else "unknown"),
        "internal_errors": evidence_value(sum(1 for record in requests if record.get("internal_error")), "observed_runtime" if requests else "unknown"),
        "latency": {
            "median_ms": evidence_value(median, "observed_runtime" if latencies else "unknown", None if latencies else "no_observations"),
            "p95_ms": evidence_value(p95, "observed_runtime" if latencies else "unknown", None if latencies else "no_observations"),
        },
        "status": health_status(len(requests), failures, bool(requests)),
    }


def compute_intake_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    source_counts = Counter(record["source_class"] for record in records)
    provenance = Counter()
    freshness = Counter()
    invalid = 0
    for record in records:
        if record.get("invalid_input"):
            invalid += 1
        if record.get("provenance_conflicting"):
            provenance["conflicting"] += 1
        elif record.get("provenance_complete"):
            provenance["complete"] += 1
        elif record.get("provenance_missing"):
            provenance["missing"] += 1
        else:
            provenance["incomplete"] += 1
        freshness[str(record.get("freshness_state") or "unknown")] += 1
    unhealthy = provenance["conflicting"] + provenance["missing"] + invalid + freshness["stale"]
    return {
        "records_observed": evidence_value(len(records), "observed_runtime" if records else "unknown"),
        "source_classes": {name: evidence_value(source_counts[name], "observed_runtime" if records else "unknown") for name in SOURCE_CLASSES},
        "provenance": {name: evidence_value(provenance[name], "observed_runtime" if records else "unknown") for name in ("complete", "incomplete", "conflicting", "missing")},
        "freshness": {
            "within_policy": evidence_value(freshness["within_policy"], "observed_runtime" if records else "unknown"),
            "stale": evidence_value(freshness["stale"], "observed_runtime" if records else "unknown"),
            "unknown": evidence_value(freshness["unknown"], "observed_runtime" if records else "unknown"),
        },
        "invalid_input_count": evidence_value(invalid, "observed_runtime" if records else "unknown"),
        "status": health_status(len(records), unhealthy, bool(records)),
    }


def compute_context_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    context_observed = any(
        record.get("context_created")
        or record.get("classification_completed")
        or record.get("classification_failed")
        or record.get("classification_changed")
        or record.get("constraint_context_created")
        for record in records
    )
    context = [record for record in records if record.get("context_created")]
    classification_failures = sum(1 for record in records if record.get("classification_failed"))
    expected_changes = sum(1 for record in records if record.get("classification_changed") and record.get("classification_change_explained"))
    unexplained_changes = sum(1 for record in records if record.get("classification_changed") and not record.get("classification_change_explained"))
    epoch_mismatches = sum(1 for record in records if record.get("governance_epoch_mismatch"))
    return {
        "context_records_created": evidence_value(len(context), "observed_runtime" if records else "unknown"),
        "classification_paths_completed": evidence_value(sum(1 for record in records if record.get("classification_completed")), "observed_runtime" if records else "unknown"),
        "classification_failures": evidence_value(classification_failures, "observed_runtime" if records else "unknown"),
        "expected_classification_changes": evidence_value(expected_changes, "observed_runtime" if records else "unknown"),
        "unexplained_classification_changes": evidence_value(unexplained_changes, "observed_runtime" if records else "unknown"),
        "constraint_contexts_created": evidence_value(sum(1 for record in records if record.get("constraint_context_created")), "observed_runtime" if records else "unknown"),
        "governance_epoch_ids_observed": evidence_value(sorted({record.get("governance_epoch_id") for record in records if record.get("governance_epoch_id")}), "observed_runtime" if records else "unknown"),
        "governance_epoch_mismatches": evidence_value(epoch_mismatches, "observed_runtime" if records else "unknown"),
        "status": health_status(len(records), classification_failures + unexplained_changes + epoch_mismatches, context_observed),
    }


def compute_proof_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    proof_records = [record for record in records if record.get("proof_created")]
    proof_failures = sum(1 for record in proof_records if record.get("proof_verification_failed"))
    proof_passed = sum(1 for record in proof_records if record.get("proof_verification_passed"))
    proof_unknown = sum(1 for record in proof_records if not record.get("proof_verification_passed") and not record.get("proof_verification_failed"))
    replay_attempts = [record for record in records if record.get("replay_attempted")]
    replay_failures = sum(1 for record in replay_attempts if record.get("replay_failed"))
    signature_mismatches = sum(1 for record in records if record.get("canonical_signature_mismatch"))
    variance = sum(1 for record in records if record.get("unexplained_output_variance"))
    return {
        "records_observed": evidence_value(len(proof_records), "observed_runtime" if proof_records else "unknown"),
        "records_eligible": evidence_value(len(proof_records), "observed_runtime" if proof_records else "unknown"),
        "records_ingested": evidence_value(len(proof_records), "observed_runtime" if proof_records else "unknown"),
        "proof_records_created": evidence_value(len(proof_records), "observed_runtime" if records else "unknown"),
        "proof_verification_passed": evidence_value(proof_passed, "observed_runtime" if records else "unknown"),
        "proof_verification_failed": evidence_value(proof_failures, "observed_runtime" if records else "unknown"),
        "verification": {
            "passed": evidence_value(proof_passed, "observed_runtime" if proof_records else "unknown"),
            "failed": evidence_value(proof_failures, "observed_runtime" if proof_records else "unknown"),
            "unknown": evidence_value(proof_unknown, "observed_runtime" if proof_records else "unknown"),
        },
        "proof_verification_rate": rate_value(proof_passed, len(proof_records)),
        "replay_attempts": evidence_value(len(replay_attempts), "observed_runtime" if records else "unknown"),
        "replay_passed": evidence_value(sum(1 for record in replay_attempts if record.get("replay_passed")), "observed_runtime" if records else "unknown"),
        "replay_failed": evidence_value(replay_failures, "observed_runtime" if records else "unknown"),
        "replay_rate": rate_value(sum(1 for record in replay_attempts if record.get("replay_passed")), len(replay_attempts)),
        "canonical_signature_mismatches": evidence_value(signature_mismatches, "observed_runtime" if records else "unknown"),
        "unexplained_output_variance": evidence_value(variance, "observed_runtime" if records else "unknown"),
        "status": health_status(len(proof_records) + len(replay_attempts), proof_failures + replay_failures + signature_mismatches + variance, bool(records)),
        "scope": evidence_value("bounded_to_observed_record" if proof_records else "unknown", "observed_runtime" if proof_records else "unknown"),
        "production_health_claim_supported": False,
        "limitations": [
            "single_record_observation",
            "no_full_service_coverage",
            "no_chronology_validation",
            "no_external_identifier_continuity",
        ] if proof_records else [],
    }


def compute_chronology_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    chronology_observed = any(
        record.get("chronology_link_verified")
        or record.get("chronology_link_failed")
        or record.get("governance_epoch_link_verified")
        or record.get("continuity_interruption")
        or record.get("unresolved_archive_dependency")
        for record in records
    )
    decision_ids = sorted({record.get("decision_id") for record in records if record.get("decision_id")})
    complete = sum(1 for record in records if record.get("provenance_complete"))
    missing = sum(1 for record in records if record.get("provenance_missing") or not record.get("provenance_complete"))
    link_failures = sum(1 for record in records if record.get("chronology_link_failed"))
    interruptions = sum(1 for record in records if record.get("continuity_interruption"))
    archive_deps = sum(1 for record in records if record.get("unresolved_archive_dependency"))
    return {
        "decision_ids_observed": evidence_value(decision_ids, "observed_runtime" if records else "unknown"),
        "records_with_complete_provenance": evidence_value(complete, "observed_runtime" if records else "unknown"),
        "records_with_missing_provenance": evidence_value(missing, "observed_runtime" if records else "unknown"),
        "chronology_links_verified": evidence_value(sum(1 for record in records if record.get("chronology_link_verified")), "observed_runtime" if records else "unknown"),
        "chronology_link_failures": evidence_value(link_failures, "observed_runtime" if records else "unknown"),
        "governance_epoch_links_verified": evidence_value(sum(1 for record in records if record.get("governance_epoch_link_verified")), "observed_runtime" if records else "unknown"),
        "continuity_interruptions": evidence_value(interruptions, "observed_runtime" if records else "unknown"),
        "unresolved_archive_dependencies": evidence_value(archive_deps, "observed_runtime" if records else "unknown"),
        "status": health_status(len(records), link_failures + interruptions + archive_deps, chronology_observed),
    }


def compute_boundary_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    invalid = sum(1 for record in records if record.get("authority_effect") and record.get("authority_effect") not in AUTHORITY_EFFECTS)
    missing = sum(1 for record in records if not record.get("authority_effect"))
    attempts = sum(1 for record in records if record.get("nova_execution_attempted"))
    approval_language = sum(1 for record in records if record.get("authorization_or_approval_language_detected"))
    local_preserved = sum(1 for record in records if record.get("local_authority_ownership_preserved"))
    failures = invalid + attempts + approval_language
    return {
        "records_with_authority_effect_none": evidence_value(sum(1 for record in records if record.get("authority_effect") == "none"), "observed_runtime" if records else "unknown"),
        "missing_authority_effect": evidence_value(missing, "observed_runtime" if records else "unknown"),
        "invalid_authority_effect": evidence_value(invalid, "observed_runtime" if records else "unknown"),
        "execution_attempts_by_Nova": evidence_value(attempts, "observed_runtime" if records else "unknown"),
        "authorization_or_approval_language_detected": evidence_value(approval_language, "observed_runtime" if records else "unknown"),
        "local_authority_ownership_preserved": evidence_value(local_preserved, "observed_runtime" if records else "unknown"),
        "status": health_status(len(records), failures, bool(records)),
        "scope": evidence_value("bounded_observation_only" if records else "unknown", "observed_runtime" if records else "unknown"),
    }


def runtime_observation_from_sources(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    discovered = [
        source["name"]
        for source in sources
        if source.get("availability", {}).get("available")
    ]
    connected = [
        source["name"]
        for source in sources
        if source.get("availability", {}).get("records_ingested")
    ]
    records_ingested = sum(int(source.get("availability", {}).get("record_count", 0)) for source in sources)
    if records_ingested > 0 and connected:
        status = "bounded_observation_complete" if len(connected) == len(sources) else "partial_records_ingested"
    elif discovered:
        status = "sources_discovered_no_records_ingested"
    else:
        status = "no_sources_connected"
    limitations = []
    if records_ingested == 0:
        limitations = [
            "No bounded runtime records were ingested.",
            "Source existence does not establish service, proof, chronology, or governance health.",
            "Live operating health remains unknown.",
        ]
    return {
        "status": status,
        "evidence_state": "observed_runtime",
        "connected_sources": connected,
        "discovered_sources": discovered,
        "records_ingested": records_ingested,
        "limitations": limitations,
    }


def runtime_evidence_report(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    source_lookup = {source["name"]: source for source in sources}
    display_paths = {
        "proof_registry": ".proof_registry.json",
        "reflex_governance_records": ".reflex_governance_records.jsonl",
        "application_code_contract": "app.py_and_core_modules",
        "test_and_fixture_contract": "tests_and_fixtures",
    }
    return {
        "candidate_source_surfaces_discovered": [
            ".proof_registry.json",
            ".reflex_governance_records.jsonl",
            "app.py",
            "core_modules",
            "tests",
            "fixtures",
        ],
        "source_surfaces_verified": [
            {
                "name": source["name"],
                "path": display_paths.get(source["name"], source["path_or_interface"]),
                "available": source["availability"]["available"],
                "availability_basis": source["availability"]["basis"],
                "records_ingested": source["availability"]["records_ingested"],
                "record_count": source["availability"]["record_count"],
            }
            for source in sources
        ],
        "runtime_records_ingested": {
            "proof_registry": bool(source_lookup.get("proof_registry", {}).get("availability", {}).get("records_ingested")),
            "reflex_governance_records": bool(source_lookup.get("reflex_governance_records", {}).get("availability", {}).get("records_ingested")),
            "API_request_metadata": False,
            "chronology_validation_results": False,
        },
        "live_operating_health_established": False,
    }


def source_connection_report(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    connections = []
    for source in sources:
        availability = source.get("availability", {})
        connections.append(
            {
                "source_id": source["name"],
                "discovered": bool(availability.get("available")),
                "policy_authorized": source["name"] == "proof_registry",
                "connected": bool(availability.get("records_ingested")),
                "records_ingested": bool(availability.get("records_ingested")),
                "record_count": int(availability.get("record_count", 0)),
                "availability_basis": availability.get("basis", "unknown"),
                "last_observed_at": availability.get("verified_at"),
                "limitations": [availability["reason"]] if availability.get("reason") else [],
            }
        )
    return connections


def merge_evidence_sources(sources: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for source in sources:
        normalized = _normalize_evidence_source(source)
        name = normalized["name"]
        existing = merged.get(name)
        if existing is None:
            merged[name] = normalized
            continue
        if normalized["availability"].get("records_ingested") or not existing["availability"].get("records_ingested"):
            merged[name] = normalized
    return list(merged.values())


def source_dependencies_for(sources: List[Dict[str, Any]]) -> List[str]:
    dependencies = list(SOURCE_DEPENDENCIES)
    source_lookup = {source["name"]: source for source in sources}
    proof_source = source_lookup.get("proof_registry")
    if proof_source and proof_source["availability"].get("records_ingested"):
        dependencies = [item for item in dependencies if item != "bounded_proof_record_ingestion"]
    return dependencies


def policy_dependencies_for(evidence: Mapping[str, Any]) -> List[str]:
    if evidence.get("policy_status") == "loaded_and_validated":
        return []
    return list(POLICY_DEPENDENCIES)


def _anomaly_id(anomaly_type: str, affected_record_ids: List[str]) -> str:
    material = {"type": anomaly_type, "records": sorted(affected_record_ids)}
    return f"ado-{canonical_hash(material)[:12]}"


def _build_anomaly(
    anomaly_type: str,
    affected_record_ids: List[str],
    first_observed: str,
    last_observed: str,
    severity: str,
    explanation: str,
) -> Dict[str, Any]:
    if anomaly_type not in ANOMALY_TYPES:
        raise ValueError(f"Unsupported anomaly_type: {anomaly_type}")
    if severity not in SEVERITIES:
        raise ValueError(f"Unsupported severity: {severity}")
    return {
        "anomaly_id": _anomaly_id(anomaly_type, affected_record_ids),
        "anomaly_type": anomaly_type,
        "first_observed": first_observed,
        "last_observed": last_observed,
        "occurrence_count": len(affected_record_ids),
        "affected_record_ids": sorted(affected_record_ids),
        "severity": severity,
        "evidence_state": "observed_runtime",
        "explanation": explanation,
        "Architect_notification": False,
    }


def detect_anomalies(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[str]] = defaultdict(list)
    explanations = {
        "source_provenance_missing": "One or more records lacked complete provenance.",
        "source_class_conflict": "A record declared conflicting source identity.",
        "stale_source": "A record was outside the configured fixture freshness policy.",
        "unexplained_classification_drift": "Classification changed without an input or governance epoch explanation.",
        "governance_epoch_mismatch": "A record referenced an unexpected governance epoch.",
        "proof_verification_failure": "Proof verification failed for one or more records.",
        "replay_failure": "Replay failed for one or more records.",
        "canonical_signature_mismatch": "Canonical replay signature mismatch was observed.",
        "chronology_link_failure": "Chronology link validation failed.",
        "authority_effect_invalid": "A record carried an authority effect other than none.",
        "execution_boundary_violation": "A Nova execution attempt was observed.",
        "evidence_source_unavailable": "An expected evidence source was unavailable.",
        "unexpected_source_field": "A source record contained field names outside the policy allowlist; values were dropped.",
    }
    for record in records:
        record_id = record["record_id"]
        if record.get("provenance_missing") or not record.get("provenance_complete"):
            grouped["source_provenance_missing"].append(record_id)
        if record.get("provenance_conflicting"):
            grouped["source_class_conflict"].append(record_id)
        if record.get("freshness_state") == "stale":
            grouped["stale_source"].append(record_id)
        if record.get("classification_changed") and not record.get("classification_change_explained"):
            grouped["unexplained_classification_drift"].append(record_id)
        if record.get("governance_epoch_mismatch"):
            grouped["governance_epoch_mismatch"].append(record_id)
        if record.get("proof_verification_failed"):
            grouped["proof_verification_failure"].append(record_id)
        if record.get("replay_failed"):
            grouped["replay_failure"].append(record_id)
        if record.get("canonical_signature_mismatch"):
            grouped["canonical_signature_mismatch"].append(record_id)
        if record.get("chronology_link_failed"):
            grouped["chronology_link_failure"].append(record_id)
        if record.get("authority_effect") and record.get("authority_effect") not in AUTHORITY_EFFECTS:
            grouped["authority_effect_invalid"].append(record_id)
        if record.get("nova_execution_attempted"):
            grouped["execution_boundary_violation"].append(record_id)
        if record.get("unexpected_source_fields"):
            grouped["unexpected_source_field"].append(record_id)
    anomalies = []
    for anomaly_type, record_ids in sorted(grouped.items()):
        severity = "watch"
        if anomaly_type == "unexpected_source_field":
            severity = "informational"
        elif anomaly_type in {"authority_effect_invalid", "execution_boundary_violation"}:
            severity = "critical"
        elif anomaly_type in {"chronology_link_failure", "canonical_signature_mismatch"}:
            severity = "material"
        first = min(str(record.get("observed_at") or "") for record in records if record["record_id"] in record_ids) or ""
        last = max(str(record.get("observed_at") or "") for record in records if record["record_id"] in record_ids) or ""
        explanation = explanations[anomaly_type]
        if anomaly_type == "unexpected_source_field":
            field_names = sorted(
                {
                    field
                    for record in records
                    if record["record_id"] in record_ids
                    for field in record.get("unexpected_source_fields", [])
                }
            )
            if field_names:
                explanation = f"{explanation} Dropped field names: {', '.join(field_names)}."
        anomalies.append(_build_anomaly(anomaly_type, record_ids, first, last, severity, explanation))
    return anomalies


def apply_notification_rules(anomalies: List[Dict[str, Any]], repeat_threshold: int = 3) -> List[Dict[str, Any]]:
    updated = []
    for anomaly in anomalies:
        anomaly = dict(anomaly)
        anomaly_type = anomaly["anomaly_type"]
        notify = False
        if anomaly["severity"] == "critical" or anomaly_type in IMMEDIATE_NOTIFICATION_TYPES:
            notify = True
        elif anomaly_type in REPEATED_NOTIFICATION_TYPES and anomaly["occurrence_count"] >= repeat_threshold:
            notify = True
        anomaly["Architect_notification"] = notify
        updated.append(anomaly)
    return updated


def quiet_tracking_from_anomalies(anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    quiet = []
    for anomaly in anomalies:
        if anomaly["Architect_notification"]:
            continue
        quiet_type = "isolated_validation_failure"
        if anomaly["anomaly_type"] == "stale_source":
            quiet_type = "isolated_stale_fixture"
        elif anomaly["anomaly_type"] == "source_provenance_missing":
            quiet_type = "known_synthetic_source_gap"
        quiet.append(
            {
                "tracking_type": quiet_type,
                "source_anomaly_id": anomaly["anomaly_id"],
                "evidence_state": anomaly["evidence_state"],
                "explanation": anomaly["explanation"],
            }
        )
    return quiet


def infer_data_mode(records: List[Dict[str, Any]], configured_mode: str) -> str:
    if configured_mode in DATA_MODES and configured_mode != "unknown":
        return configured_mode
    modes = {record.get("data_mode", "unknown") for record in records}
    modes.discard("unknown")
    if not modes:
        return "unknown"
    if len(modes) == 1:
        return next(iter(modes))
    return "mixed"


def generate_canonical_snapshot(
    evidence: Mapping[str, Any],
    *,
    generated_at: Optional[str] = None,
    repo_root: Optional[Path] = None,
    repeat_threshold: int = 3,
) -> Dict[str, Any]:
    records = normalize_records(evidence.get("records", []))
    now = generated_at or utc_now()
    observation_window = evidence.get("observation_window") or {"start": None, "end": None}
    runtime_sources, missing_sources = discover_runtime_evidence_sources(repo_root or Path.cwd(), verified_at=now)
    evidence_sources = merge_evidence_sources(list(evidence.get("evidence_sources") or []) + runtime_sources)
    runtime_observation = runtime_observation_from_sources(evidence_sources)
    runtime_evidence = runtime_evidence_report(evidence_sources)
    source_connection = source_connection_report(evidence_sources)
    accepted_state_synchronization = synchronization_state(repo_root or Path.cwd())
    anomalies = apply_notification_rules(detect_anomalies(records), repeat_threshold=repeat_threshold)
    quiet_tracking = quiet_tracking_from_anomalies(anomalies)
    action_reasons = [
        f"{anomaly['anomaly_type']}:{anomaly['anomaly_id']}"
        for anomaly in anomalies
        if anomaly["Architect_notification"]
    ]
    data_mode = infer_data_mode(records, str(evidence.get("data_mode") or "unknown"))
    limitations = list(evidence.get("limitations") or [])
    for limitation in runtime_observation["limitations"]:
        if limitation not in limitations:
            limitations.append(limitation)
    if missing_sources:
        limitations.append("Some candidate source surfaces were unavailable in the current environment.")
        for source_name in missing_sources:
            anomalies.append(
                {
                    "anomaly_id": _anomaly_id("evidence_source_unavailable", [source_name]),
                    "anomaly_type": "evidence_source_unavailable",
                    "first_observed": now,
                    "last_observed": now,
                    "occurrence_count": 1,
                    "affected_record_ids": [source_name],
                    "severity": "informational",
                    "evidence_state": "unavailable",
                    "explanation": f"Expected evidence source is unavailable: {source_name}.",
                    "Architect_notification": False,
                }
            )
    snapshot: Dict[str, Any] = {
        "architect_data_operations_snapshot": {
            "schema_version": "1.0.0",
            "generated_at": now,
            "observation_window": observation_window,
            "environment": evidence.get("environment", "unknown"),
            "data_mode": data_mode,
            "runtime_observation": runtime_observation,
            "runtime_evidence": runtime_evidence,
            "source_connection": source_connection,
            "accepted_state_synchronization": accepted_state_synchronization,
            "live_operating_health_established": False,
            "policy_status": evidence.get("policy_status", "not_loaded"),
            "retention_metadata": evidence.get("retention_metadata", {}),
            "evidence_sources": evidence_sources,
            "service_health": compute_service_health(records),
            "intake_health": compute_intake_health(records),
            "context_health": compute_context_health(records),
            "proof_health": compute_proof_health(records),
            "chronology_health": compute_chronology_health(records),
            "boundary_health": compute_boundary_health(records),
            "anomalies": anomalies,
            "quiet_tracking": quiet_tracking,
            "Architect_action": {
                "required": bool(action_reasons),
                "reasons": action_reasons,
            },
            "source_dependencies": {
                "missing_or_unconnected": source_dependencies_for(evidence_sources),
            },
            "policy_dependencies": {
                "unresolved": policy_dependencies_for(evidence),
            },
            "candidate_source_surfaces_missing": missing_sources,
            "required_operating_sources_unconnected": [
                "production_API_request_metadata",
                "chronology_validation_results",
                "live_provenance_source",
            ],
            "limitations": limitations,
            "snapshot_identity": {},
        }
    }
    semantic = json.loads(canonical_json(snapshot["architect_data_operations_snapshot"]))
    semantic.pop("generated_at", None)
    semantic["snapshot_identity"] = {}
    snapshot["architect_data_operations_snapshot"]["snapshot_identity"] = {
        "canonicalization_version": "architect_data_operations_canonical_v1",
        "canonical_hash": canonical_hash(semantic),
        "input_record_count": len(records),
        "source_window": observation_window,
    }
    return snapshot


def _value(item: Mapping[str, Any]) -> Any:
    return item.get("value")


def render_architect_brief(snapshot: Mapping[str, Any]) -> str:
    root = snapshot["architect_data_operations_snapshot"]
    action = root["Architect_action"]
    sync = root.get("accepted_state_synchronization", {})
    action_state = sync.get("action_state", {})
    runtime_observation = root["runtime_observation"]
    input_record_count = int(root["snapshot_identity"].get("input_record_count", 0))
    lines = [
        "# Architect Data Operations Brief",
        "",
        "## Policy Status",
        "",
        f"- Status: {root.get('policy_status', 'not_loaded')}",
        "- Activation mode: bounded_read_only_pilot" if root.get("policy_status") == "loaded_and_validated" else "- Activation mode: not_active",
        "",
        "## Observation Window",
        "",
        f"- Start: {root['observation_window'].get('start') or 'unknown'}",
        f"- End: {root['observation_window'].get('end') or 'unknown'}",
        f"- Data mode: {root['data_mode']}",
        f"- Snapshot hash: {root['snapshot_identity'].get('canonical_hash')}",
        "",
        "## What the Architect Should Know Now",
        "",
    ]
    if input_record_count == 0:
        lines.append("The operating visibility contract is active.")
        if runtime_observation["discovered_sources"]:
            lines.append("Potential evidence surfaces were discovered.")
        lines.append("Runtime evidence surfaces were discovered, but no bounded operating records were ingested for this observation.")
        lines.append("Service, intake, context, proof, chronology, and authority-boundary health therefore remain unknown.")
        lines.append(
            "No decision-relevant anomaly was observed in the available evidence. This statement does not establish that the operating environment is healthy."
        )
    else:
        proof_records = root["proof_health"].get("records_ingested", {}).get("value", 0)
        if proof_records:
            lines.append(f"{proof_records} bounded proof record was ingested for the declared observation window.")
            lines.append("The record passed the policy allowlist and preserved authority_effect: none.")
            lines.append(
                "Identifier continuity could not be established because an external hashing salt was not configured. Raw identifiers were not emitted."
            )
            lines.append(
                "This observation supports only the bounded proof result reported here. It does not establish full API, chronology, or production health."
            )
            lines.append("No Stage B, C, or D source was activated.")
    if action["required"]:
        lines.append("Architect action is required for this observation window.")
        for reason in action["reasons"]:
            lines.append(f"- {reason}")
    else:
        lines.append("No Architect action is required for this observation window.")
        if input_record_count > 0:
            lines.append("No decision-relevant anomaly was observed in the available evidence.")
    lines.extend(["", "## Runtime Observation Status", ""])
    status_label = runtime_observation["status"].replace("_", " ")
    if runtime_observation["status"] == "sources_discovered_no_records_ingested":
        lines.append("Observation status: Sources discovered; no records ingested.")
    else:
        lines.append(f"Observation status: {status_label}.")
    lines.append(f"- Evidence state: {runtime_observation['evidence_state']}")
    lines.append(f"- Records ingested: {runtime_observation['records_ingested']}")
    lines.extend(["", "## Runtime Sources Connected", ""])
    if runtime_observation["connected_sources"]:
        for source in runtime_observation["connected_sources"]:
            lines.append(f"- {source}")
    else:
        lines.append("[]")
    lines.extend(["", "## Records Ingested", "", f"- Total records ingested: {runtime_observation['records_ingested']}"])
    lines.extend(["", "## Connected and Discovered Sources", ""])
    if runtime_observation["connected_sources"]:
        lines.append("Connected sources:")
        for source in runtime_observation["connected_sources"]:
            lines.append(f"- {source}")
    else:
        lines.append("Connected sources: []")
    if runtime_observation["discovered_sources"]:
        lines.append("Discovered sources:")
        for source in runtime_observation["discovered_sources"]:
            lines.append(f"- {source}")
    else:
        lines.append("Discovered sources: []")
    sections = [
        ("Service Health", "service_health", "status"),
        ("Data and Provenance Health", "intake_health", "status"),
        ("Context and Classification Health", "context_health", "status"),
        ("Proof and Replay Health", "proof_health", "status"),
        ("Chronology and Continuity Health", "chronology_health", "status"),
        ("Authority-Boundary Health", "boundary_health", "status"),
    ]
    for title, key, status_key in sections:
        status = root[key][status_key]
        lines.extend(["", f"## {title}", "", f"- Status: {_value(status)} ({status['evidence_state']})"])
        if key == "proof_health" and root[key].get("scope"):
            lines.append(f"- Scope: {_value(root[key]['scope'])}")
            lines.append(
                f"- Production health claim supported: {str(root[key].get('production_health_claim_supported', False)).lower()}"
            )
    lines.extend(["", "## Material Anomalies", ""])
    material = [anomaly for anomaly in root["anomalies"] if anomaly.get("Architect_notification")]
    if material:
        for anomaly in material:
            lines.append(f"- {anomaly['anomaly_type']} ({anomaly['severity']}): {anomaly['explanation']}")
    else:
        lines.append("No material change was observed in the available evidence.")
    lines.extend(["", "## Quiet Tracking", ""])
    if root["quiet_tracking"]:
        for item in root["quiet_tracking"]:
            lines.append(f"- {item['tracking_type']}: {item['explanation']}")
    else:
        lines.append("No quiet tracking items were created for this observation window.")
    lines.extend(["", "## Architect Action", "", f"Architect_action:", f"  required: {str(action['required']).lower()}", "  reasons:"])
    if action["reasons"]:
        for reason in action["reasons"]:
            lines.append(f"    - {reason}")
    else:
        lines.append("    []")
    lines.extend(
        [
            "",
            "## Operating Action State",
            "",
            "Operating_action_state:",
            f"  system_maintenance_action_required: {str(action_state.get('system_maintenance_action_required', False)).lower()}",
            f"  Architect_decision_required: {str(action_state.get('Architect_decision_required', False)).lower()}",
            f"  external_dependency_action_required: {str(action_state.get('external_dependency_action_required', False)).lower()}",
            "  assigned_to:",
        ]
    )
    assigned_to = action_state.get("assigned_to") or []
    if assigned_to:
        for actor in assigned_to:
            lines.append(f"    - {actor}")
    else:
        lines.append("    []")
    lines.extend(
        [
            f"  action_type: {action_state.get('action_type', 'none')}",
            f"  blocking_state: {action_state.get('blocking_state', 'non_blocking')}",
            f"  rationale: {action_state.get('rationale', '')}",
            "",
            "## Accepted-State Synchronization",
            "",
            f"- Operating state: {sync.get('operating_state', 'source_incomplete')}",
            f"- Current repo movement reviewed: {str(sync.get('repository', {}).get('current_repo_movement_reviewed', False)).lower()}",
            f"- Current repo movement accepted: {str(sync.get('repository', {}).get('current_repo_movement_accepted', False)).lower()}",
            f"- Accepted remote head: {sync.get('repository', {}).get('accepted_remote_head') or 'unknown'}",
            f"- Registry path: {sync.get('accepted_state_registry', {}).get('path') or 'unknown'}",
            f"- Registry updated: {str(sync.get('accepted_state_registry', {}).get('updated', False)).lower()}",
            f"- Registry schema valid: {str(sync.get('accepted_state_registry', {}).get('schema_valid', False)).lower()}",
            f"- Accepted entry ID: {sync.get('accepted_state_registry', {}).get('accepted_entry_id') or 'unknown'}",
            f"- Chronology event status: {sync.get('chronology', {}).get('canonical_event_status') or 'unknown'}",
            f"- Chronology event ID: {sync.get('chronology', {}).get('event_id') or 'unknown'}",
            f"- Durable archive status: {sync.get('durable_archive', {}).get('status') or 'unknown'}",
            f"- Archive reference: {sync.get('durable_archive', {}).get('archive_reference') or 'pending_external_write'}",
        ]
    )
    lines.extend(["", "## Source Dependencies", ""])
    for dependency in root["source_dependencies"]["missing_or_unconnected"]:
        lines.append(f"- {dependency}")
    lines.extend(["", "## Policy Dependencies", ""])
    if root["policy_dependencies"]["unresolved"]:
        for dependency in root["policy_dependencies"]["unresolved"]:
            lines.append(f"- {dependency}")
    else:
        lines.append("[]")
    lines.extend(["", "## Evidence Limitations", ""])
    if root["limitations"]:
        for limitation in root["limitations"]:
            lines.append(f"- {limitation}")
    else:
        lines.append("No additional limitations were declared beyond field-level evidence states.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Architect data operations snapshot and brief.")
    parser.add_argument("--mode", choices=["offline_fixture", "bounded_runtime", "pilot_proof_registry"], default="offline_fixture")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--identifier-salt")
    parser.add_argument("--generated-at")
    parser.add_argument("--proof-registry-path", type=Path)
    parser.add_argument("--snapshot-out", type=Path, default=Path("artifacts/operations/architect-data-operations-snapshot.json"))
    parser.add_argument("--brief-out", type=Path, default=Path("artifacts/operations/architect-data-operations-brief.md"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    if args.mode == "offline_fixture":
        if args.evidence is None:
            parser.error("--evidence is required in offline_fixture mode")
        evidence = load_bounded_evidence(args.evidence)
    elif args.mode == "bounded_runtime":
        evidence = build_bounded_runtime_evidence()
    else:
        evidence = build_proof_registry_pilot_evidence(
            policy_path=args.policy,
            repo_root=args.repo_root,
            identifier_salt=args.identifier_salt,
            generated_at=args.generated_at,
            proof_registry_path=args.proof_registry_path,
        )
    snapshot = generate_canonical_snapshot(evidence, generated_at=args.generated_at, repo_root=args.repo_root)
    brief = render_architect_brief(snapshot)
    args.snapshot_out.parent.mkdir(parents=True, exist_ok=True)
    args.brief_out.parent.mkdir(parents=True, exist_ok=True)
    args.snapshot_out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.brief_out.write_text(brief, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
