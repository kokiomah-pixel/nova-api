from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


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


def build_bounded_runtime_evidence() -> Dict[str, Any]:
    return {
        "data_mode": "unknown",
        "environment": "bounded_runtime",
        "observation_window": {"start": None, "end": None},
        "records": [],
        "limitations": [
            "Bounded runtime mode reports only evidence sources discoverable in the current environment.",
            "No live operating records are simulated by this generator.",
        ],
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


def discover_runtime_evidence_sources(repo_root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    candidates = [
        {
            "name": "proof_records",
            "path_or_interface": ".proof_registry.json",
            "data_mode": "unknown",
            "contains_sensitive_data": False,
            "retention_policy": "runtime_configured_file; not governed by this layer",
            "authoritative_for": ["proof_records_created", "proof_verification_inputs_if_present"],
            "not_authoritative_for": ["live_provenance", "chronology_acceptance", "external_execution"],
        },
        {
            "name": "reflex_governance_records",
            "path_or_interface": ".reflex_governance_records.jsonl",
            "data_mode": "unknown",
            "contains_sensitive_data": False,
            "retention_policy": "runtime_configured_file; not governed by this layer",
            "authoritative_for": ["classification_context_observations_if_present"],
            "not_authoritative_for": ["Reflex Memory acceptance", "production health"],
        },
        {
            "name": "application_code_contract",
            "path_or_interface": "app.py and core modules",
            "data_mode": "repository_validated",
            "contains_sensitive_data": False,
            "retention_policy": "git repository",
            "authoritative_for": ["designed_endpoints", "repository_validated_behavior"],
            "not_authoritative_for": ["observed_runtime_activity"],
        },
        {
            "name": "test_or_fixture_results",
            "path_or_interface": "tests/ and fixtures/",
            "data_mode": "offline_fixture",
            "contains_sensitive_data": False,
            "retention_policy": "git repository",
            "authoritative_for": ["contract_validation"],
            "not_authoritative_for": ["live operating evidence"],
        },
    ]
    available: List[Dict[str, Any]] = []
    missing: List[str] = []
    for source in candidates:
        source = dict(source)
        interface = str(source["path_or_interface"]).split(" and ")[0]
        available_now = (repo_root / interface).exists() if "." in interface or "/" in interface else False
        if source["name"] in {"application_code_contract", "test_or_fixture_results"}:
            available_now = True
        source["available_in_current_environment"] = available_now
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
        "status": evidence_value(_status_from_counts(len(requests), failures), "inferred" if requests else "unknown"),
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
        "status": evidence_value(_status_from_counts(len(records), unhealthy), "inferred" if records else "unknown"),
    }


def compute_context_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        "status": evidence_value(_status_from_counts(len(records), classification_failures + unexplained_changes + epoch_mismatches), "inferred" if records else "unknown"),
    }


def compute_proof_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    proof_records = [record for record in records if record.get("proof_created")]
    proof_failures = sum(1 for record in proof_records if record.get("proof_verification_failed"))
    replay_attempts = [record for record in records if record.get("replay_attempted")]
    replay_failures = sum(1 for record in replay_attempts if record.get("replay_failed"))
    signature_mismatches = sum(1 for record in records if record.get("canonical_signature_mismatch"))
    variance = sum(1 for record in records if record.get("unexplained_output_variance"))
    return {
        "proof_records_created": evidence_value(len(proof_records), "observed_runtime" if records else "unknown"),
        "proof_verification_passed": evidence_value(sum(1 for record in proof_records if record.get("proof_verification_passed")), "observed_runtime" if records else "unknown"),
        "proof_verification_failed": evidence_value(proof_failures, "observed_runtime" if records else "unknown"),
        "proof_verification_rate": rate_value(sum(1 for record in proof_records if record.get("proof_verification_passed")), len(proof_records)),
        "replay_attempts": evidence_value(len(replay_attempts), "observed_runtime" if records else "unknown"),
        "replay_passed": evidence_value(sum(1 for record in replay_attempts if record.get("replay_passed")), "observed_runtime" if records else "unknown"),
        "replay_failed": evidence_value(replay_failures, "observed_runtime" if records else "unknown"),
        "replay_rate": rate_value(sum(1 for record in replay_attempts if record.get("replay_passed")), len(replay_attempts)),
        "canonical_signature_mismatches": evidence_value(signature_mismatches, "observed_runtime" if records else "unknown"),
        "unexplained_output_variance": evidence_value(variance, "observed_runtime" if records else "unknown"),
        "status": evidence_value(_status_from_counts(len(proof_records) + len(replay_attempts), proof_failures + replay_failures + signature_mismatches + variance), "inferred" if records else "unknown"),
    }


def compute_chronology_health(records: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        "status": evidence_value(_status_from_counts(len(records), link_failures + interruptions + archive_deps), "inferred" if records else "unknown"),
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
        "status": evidence_value(_status_from_counts(len(records), failures), "inferred" if records else "unknown"),
    }


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
    anomalies = []
    for anomaly_type, record_ids in sorted(grouped.items()):
        severity = "watch"
        if anomaly_type in {"authority_effect_invalid", "execution_boundary_violation"}:
            severity = "critical"
        elif anomaly_type in {"chronology_link_failure", "canonical_signature_mismatch"}:
            severity = "material"
        first = min(str(record.get("observed_at") or "") for record in records if record["record_id"] in record_ids) or ""
        last = max(str(record.get("observed_at") or "") for record in records if record["record_id"] in record_ids) or ""
        anomalies.append(_build_anomaly(anomaly_type, record_ids, first, last, severity, explanations[anomaly_type]))
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
    runtime_sources, missing_sources = discover_runtime_evidence_sources(repo_root or Path.cwd())
    evidence_sources = list(evidence.get("evidence_sources") or []) + runtime_sources
    anomalies = apply_notification_rules(detect_anomalies(records), repeat_threshold=repeat_threshold)
    quiet_tracking = quiet_tracking_from_anomalies(anomalies)
    action_reasons = [
        f"{anomaly['anomaly_type']}:{anomaly['anomaly_id']}"
        for anomaly in anomalies
        if anomaly["Architect_notification"]
    ]
    data_mode = infer_data_mode(records, str(evidence.get("data_mode") or "unknown"))
    limitations = list(evidence.get("limitations") or [])
    if missing_sources:
        limitations.append("Some expected runtime evidence sources were unavailable in the current environment.")
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
    lines = [
        "# Architect Data Operations Brief",
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
    if action["required"]:
        lines.append("Architect action is required for this observation window.")
        for reason in action["reasons"]:
            lines.append(f"- {reason}")
    else:
        lines.append("No Architect action is required for this observation window.")
        lines.append("No decision-relevant anomaly was observed in the available evidence.")
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
    lines.extend(["", "## Material Changes", ""])
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
    parser.add_argument("--mode", choices=["offline_fixture", "bounded_runtime"], default="offline_fixture")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--snapshot-out", type=Path, default=Path("artifacts/operations/architect-data-operations-snapshot.json"))
    parser.add_argument("--brief-out", type=Path, default=Path("artifacts/operations/architect-data-operations-brief.md"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    if args.mode == "offline_fixture":
        if args.evidence is None:
            parser.error("--evidence is required in offline_fixture mode")
        evidence = load_bounded_evidence(args.evidence)
    else:
        evidence = build_bounded_runtime_evidence()
    snapshot = generate_canonical_snapshot(evidence, repo_root=args.repo_root)
    brief = render_architect_brief(snapshot)
    args.snapshot_out.parent.mkdir(parents=True, exist_ok=True)
    args.brief_out.parent.mkdir(parents=True, exist_ok=True)
    args.snapshot_out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.brief_out.write_text(brief, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
