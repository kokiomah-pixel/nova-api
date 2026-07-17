# Architect Data Operations Protocol

## Status

Approved bounded implementation protocol
Architect operating-visibility artifact
Not a dashboard
Not production observability by itself
Not a governance authority
Not chronology repair
Not Reflex Memory mutation
Not market, buyer, partner, or adoption evidence

## Purpose

This protocol defines the first operating-state contract for the Sharpe Nova OS API.

It gives the Architect a bounded view of whether API data, proofs, provenance,
chronology, and authority boundaries are operating coherently over time.

The layer answers:

```text
Is the API functioning?
Is the data trustworthy?
Are proofs reproducible?
Is chronology intact?
Is the non-authority boundary preserved?
Does the Architect need to act?
```

The first artifact is a governed operating-state contract, not a dashboard. A
dashboard without this contract could make incomplete data look authoritative.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

The operating visibility layer reports evidence. It does not approve actions,
repair records, or modify accepted state.

It must not:

- authorize or deny actions;
- alter classification;
- mutate proofs;
- modify chronology;
- write Reflex Memory;
- infer buyer or institutional activity;
- expose sensitive internal policy weights;
- create a second source of truth.

## Operating Questions

The snapshot and brief must distinguish:

- designed behavior;
- observed runtime behavior;
- internally validated behavior;
- unknown behavior.

Never present design intent or test results as live operating evidence.

## Operating-State Layers

### Layer 1: Service Health

Question: Is the API available and processing requests as expected?

Fields:

```yaml
service_health:
  observation_window:
  endpoint_status:
    v1_context:
    v1_proof:
  requests_observed:
  successful_responses:
  validation_failures:
  internal_errors:
  latency:
    median_ms:
    p95_ms:
  status:
```

Allowed status values are `healthy`, `degraded`, `unavailable`, and `unknown`.

Service health is not proof health, chronology health, data health, or governance
health. A green API status does not establish that governance data is complete,
current, reproducible, or decision-ready.

### Layer 2: Intake and Source Health

Question: What data entered Nova, and what evidence identity did it carry?

Fields:

```yaml
intake_health:
  records_observed:
  source_classes:
    synthetic:
    production_like:
    live:
    inferred:
    unavailable:
    unknown:
  provenance:
    complete:
    incomplete:
    conflicting:
    missing:
  freshness:
    within_policy:
    stale:
    unknown:
  invalid_input_count:
  status:
```

No record may be reported as `live` without verified live provenance. When live
provenance cannot be established, the source class must be `unknown`.

### Layer 3: Context and Classification Health

Question: Did Nova form context consistently and explainably?

Fields:

```yaml
context_health:
  context_records_created:
  classification_paths_completed:
  classification_failures:
  expected_classification_changes:
  unexplained_classification_changes:
  constraint_contexts_created:
  governance_epoch_ids_observed:
  governance_epoch_mismatches:
  status:
```

A classification change is expected when input evidence or governance epoch
changes. A classification change without an explainable cause is drift.

### Layer 4: Proof and Replay Health

Question: Can derived context be verified and reproduced?

Fields:

```yaml
proof_health:
  proof_records_created:
  proof_verification_passed:
  proof_verification_failed:
  replay_attempts:
  replay_passed:
  replay_failed:
  canonical_signature_mismatches:
  unexplained_output_variance:
  status:
```

Do not report a percentage when the denominator is zero. Use:

```yaml
rate:
  value: null
  reason: no_observations
```

Unknown is better than false confidence.

### Layer 5: Chronology and Continuity Health

Question: Is the operating record preserved and reconstructable?

Fields:

```yaml
chronology_health:
  decision_ids_observed:
  records_with_complete_provenance:
  records_with_missing_provenance:
  chronology_links_verified:
  chronology_link_failures:
  governance_epoch_links_verified:
  continuity_interruptions:
  unresolved_archive_dependencies:
  status:
```

This layer observes chronology integrity. It must not write, repair, or accept
chronology automatically.

### Layer 6: Authority-Boundary Health

Question: Is Nova still operating as non-authority infrastructure?

Fields:

```yaml
boundary_health:
  records_with_authority_effect_none:
  missing_authority_effect:
  invalid_authority_effect:
  execution_attempts_by_Nova:
  authorization_or_approval_language_detected:
  local_authority_ownership_preserved:
  status:
```

Expected invariant:

```yaml
execution_attempts_by_Nova: 0
```

Any nonzero value is decision-relevant and must be escalated.

## Evidence-State Labels

Every field in the generated snapshot must carry or inherit an evidence state.

```yaml
evidence_states:
  observed_runtime:
    meaning: directly derived from bounded runtime records

  repository_validated:
    meaning: supported by tests or repository artifacts, not current runtime

  configured:
    meaning: derived from declared configuration

  inferred:
    meaning: computed from observed evidence using a documented rule

  unknown:
    meaning: insufficient evidence

  unavailable:
    meaning: evidence source was expected but inaccessible
```

The Architect-facing brief must not collapse these labels.

## Snapshot Contract

The snapshot is machine-readable JSON and validates against:

```text
specs/architect_data_operations_snapshot.schema.json
```

Top-level structure:

```yaml
architect_data_operations_snapshot:
  schema_version:
  generated_at:
  observation_window:
    start:
    end:
  environment:
  data_mode:
  evidence_sources: []
  service_health:
  intake_health:
  context_health:
  proof_health:
  chronology_health:
  boundary_health:
  anomalies: []
  quiet_tracking: []
  Architect_action:
    required:
    reasons: []
  limitations: []
  snapshot_identity:
    canonical_hash:
```

Allowed `data_mode` values:

- `synthetic`
- `offline_fixture`
- `production_like`
- `live`
- `mixed`
- `unknown`

A mixed snapshot must report counts by source class.

## Snapshot Identity

Every generated snapshot has deterministic identity.

The canonical representation excludes:

- generation timestamp from semantic comparison;
- volatile display formatting;
- non-deterministic field ordering.

Required fields:

```yaml
snapshot_identity:
  canonicalization_version:
  canonical_hash:
  input_record_count:
  source_window:
```

Equivalent source records and configuration should produce an equivalent semantic
hash.

## Evidence Sources

Candidate bounded sources:

```yaml
candidate_evidence_sources:
  - API_request_or_response_metadata
  - generated_context_records
  - proof_records
  - replay_results
  - classification_results
  - source_identity_metadata
  - governance_epoch_metadata
  - chronology_validation_results
  - application_logs
  - test_or_fixture_results
```

Each evidence source must document:

```yaml
evidence_source:
  name:
  path_or_interface:
  data_mode:
  contains_sensitive_data:
  retention_policy:
  available_in_current_environment:
  authoritative_for:
  not_authoritative_for:
```

Do not invent runtime data sources. When a source does not exist, report the gap.

Current bounded implementation source map:

```yaml
verified_evidence_source_map:
  proof_records:
    path_or_interface: .proof_registry.json
    current_status: optional_runtime_file
    authoritative_for:
      - proof_records_created_when_present
    not_authoritative_for:
      - live_provenance
      - external_execution

  reflex_governance_records:
    path_or_interface: .reflex_governance_records.jsonl
    current_status: optional_runtime_file
    authoritative_for:
      - classification_context_observations_when_present
    not_authoritative_for:
      - Reflex_Memory_acceptance
      - production_health

  application_code_contract:
    path_or_interface: app.py and core modules
    current_status: repository_available
    authoritative_for:
      - designed_endpoints
      - repository_validated_behavior
    not_authoritative_for:
      - observed_runtime_activity

  test_or_fixture_results:
    path_or_interface: tests/ and fixtures/
    current_status: repository_available
    authoritative_for:
      - contract_validation
    not_authoritative_for:
      - live_operating_evidence
```

## Anomaly Model

Allowed anomaly types:

```yaml
anomaly_types:
  - source_provenance_missing
  - source_class_conflict
  - stale_source
  - unexplained_classification_drift
  - governance_epoch_mismatch
  - proof_verification_failure
  - replay_failure
  - canonical_signature_mismatch
  - chronology_link_failure
  - authority_effect_invalid
  - execution_boundary_violation
  - evidence_source_unavailable
```

Anomaly structure:

```yaml
anomaly:
  anomaly_id:
  anomaly_type:
  first_observed:
  last_observed:
  occurrence_count:
  affected_record_ids: []
  severity:
  evidence_state:
  explanation:
  Architect_notification:
```

Severity values are `informational`, `watch`, `material`, and `critical`.

## Notification Rules

The Architect should not receive raw operational noise.

Immediate notification:

- `execution_boundary_violation`
- `authority_effect_invalid`
- live source without verified provenance
- critical chronology integrity failure

Notify when repeated:

- `unexplained_classification_drift`
- `proof_verification_failure`
- `replay_failure`
- `canonical_signature_mismatch`
- `chronology_link_failure`
- `source_provenance_missing`

Default repeat threshold:

```yaml
default_repeat_threshold:
  occurrences: 3
  independent_records_required: true
```

A single anomaly may still be escalated when severity is critical.

## Quiet Tracking

Track quietly:

- `isolated_validation_failure`
- `isolated_stale_fixture`
- `known_synthetic_source_gap`
- `expected_classification_change`
- `transient_endpoint_error`
- `evidence_source_temporarily_unavailable`

Quiet tracking becomes Architect-relevant when:

- the pattern repeats;
- severity increases;
- scope expands;
- a claim becomes inaccurate;
- a boundary becomes threatened.

## Reporting Cadence

The first implementation does not create a scheduler. Conservative fixture
defaults support ad hoc generation only.

Production cadence requires an Architect decision on:

- operating observation window;
- reporting cadence;
- runtime source retention;
- material-alert recipients.

## Retention and Privacy

The snapshot should contain metrics and identifiers needed for diagnosis, not
full sensitive payloads.

Do not include:

- API secrets;
- private keys;
- wallet credentials;
- personal data unless explicitly required and governed;
- complete financial-action payloads;
- hidden policy weights;
- raw model prompts;
- proprietary source content.

Use:

- bounded record identifiers;
- hashes;
- counts;
- classifications;
- anomaly references;
- redacted summaries.

## Initial Operating Modes

### Offline Fixture Mode

Purpose:

- validate snapshot contract;
- validate determinism;
- validate anomaly rules;
- validate brief rendering.

This mode uses approved fixtures and must be labeled clearly as non-live.

### Bounded Runtime Mode

Purpose:

- summarize available API operating evidence.

Only enable fields supported by actual runtime evidence. Unsupported fields must
remain `unknown` or `unavailable`. Do not simulate live data.

## Architect Brief

The Markdown brief must use:

```markdown
# Architect Data Operations Brief

## Observation Window

## What the Architect Should Know Now

## Service Health

## Data and Provenance Health

## Context and Classification Health

## Proof and Replay Health

## Chronology and Continuity Health

## Authority-Boundary Health

## Material Changes

## Quiet Tracking

## Architect Action

## Evidence Limitations
```

When no action is needed, use:

```text
No Architect action is required for this observation window.
```

Do not use "all systems normal" when evidence is incomplete. Use:

```text
No decision-relevant anomaly was observed in the available evidence.
```

## API, Data, Proof, Chronology, and Governance Health

API health means endpoints were reachable and produced responses.

Data health means records carried usable source identity, provenance, freshness,
and invalid-input visibility.

Proof health means proof material and replay outputs can be verified and
reproduced from available evidence.

Chronology health means records remain linked and reconstructable.

Governance health means the non-authority boundary remains visible and intact.

A green API status does not establish that governance data is complete, current,
reproducible, or decision-ready.

## Decisions Required After Initial Implementation

```yaml
Architect_decisions:
  - operating_observation_window
  - reporting_cadence
  - source_freshness_thresholds
  - anomaly_repeat_thresholds
  - severity_mapping
  - runtime_evidence_retention
  - permitted_record_identifiers
  - live_provenance_standard
  - production_log_source
  - chronology_validation_source
  - who_receives_material_alerts
```

Conservative defaults apply only to offline fixture validation. Production policy
must not be silently set by this layer.

## Final Operating Principle

```text
The Architect should not have to inspect raw data to know whether Nova is coherent.

But the summary must never claim more certainty than the underlying evidence supports.
```
