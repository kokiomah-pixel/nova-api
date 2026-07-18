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
  runtime_observation:
    status:
    evidence_state:
    connected_sources: []
    discovered_sources: []
    records_ingested:
    limitations: []
  runtime_evidence:
    candidate_source_surfaces_discovered: []
    source_surfaces_verified: []
    runtime_records_ingested: {}
    live_operating_health_established:
  live_operating_health_established:
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
  source_dependencies:
    missing_or_unconnected: []
  policy_dependencies:
    unresolved: []
  candidate_source_surfaces_missing: []
  required_operating_sources_unconnected: []
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

Allowed runtime observation status values:

```yaml
runtime_observation_status:
  - no_sources_connected
  - sources_discovered_no_records_ingested
  - partial_records_ingested
  - bounded_observation_complete
  - unavailable
  - unknown
```

When no records are ingested and no critical configuration defect exists:

```yaml
Architect_action:
  required: false
  reasons: []
```

This means no Architect action is required for the observation window. It does
not mean system health has been established.

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

Evidence-source discovery establishes that a potential source surface exists. It
does not establish that records were ingested, that the source is authoritative
for operating health, or that any health state has been observed.

Repository contracts, tests, and fixtures may validate implementation behavior.
They are not live operating evidence.

A bounded runtime report with zero ingested records is an evidence-gap report,
not a health report.

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
  source_kind:
  data_mode:
  contains_sensitive_data:
  retention_policy:
  availability:
    available:
    basis:
    verified_at:
    records_ingested:
    record_count:
  authoritative_for:
  not_authoritative_for:
```

Do not invent runtime data sources. When a source does not exist, report the gap.
Do not mark a `repository_contract` source as runtime-observed.

Allowed source kinds:

```yaml
source_kind:
  - runtime_record_source
  - runtime_interface
  - configured_source
  - repository_contract
  - fixture_source
```

Allowed availability basis values:

```yaml
availability_basis:
  - verified_path
  - runtime_discovery
  - configured
  - repository_contract
  - unavailable
  - unknown
```

Availability basis definitions:

```yaml
availability_basis_definitions:
  verified_path:
    meaning: path existence was directly checked in the current environment

  runtime_discovery:
    meaning: source was discovered through a bounded runtime interface

  configured:
    meaning: source was declared through configuration but not independently verified

  repository_contract:
    meaning: source represents code, tests, fixtures, or documentation rather than runtime observations

  unavailable:
    meaning: expected source could not be accessed

  unknown:
    meaning: availability could not be determined
```

Current bounded implementation source map:

```yaml
verified_evidence_source_map:
  proof_registry:
    path_or_interface: .proof_registry.json
    source_kind: runtime_record_source
    current_status: candidate_runtime_surface_only
    records_ingested: false
    authoritative_for:
      - candidate_proof_record_surface
    not_authoritative_for:
      - live_provenance
      - external_execution
      - operating_health

  reflex_governance_records:
    path_or_interface: .reflex_governance_records.jsonl
    source_kind: runtime_record_source
    current_status: candidate_runtime_surface_only
    records_ingested: false
    authoritative_for:
      - candidate_classification_context_surface
    not_authoritative_for:
      - Reflex_Memory_acceptance
      - production_health
      - operating_health

  application_code_contract:
    path_or_interface: app.py and core modules
    source_kind: repository_contract
    current_status: repository_available
    records_ingested: false
    authoritative_for:
      - designed_endpoints
      - repository_validated_behavior
    not_authoritative_for:
      - observed_runtime_activity
      - operating_health

  test_and_fixture_contract:
    path_or_interface: tests/ and fixtures/
    source_kind: fixture_source
    current_status: repository_available
    records_ingested: false
    authoritative_for:
      - contract_validation
    not_authoritative_for:
      - live_operating_evidence
      - operating_health
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

## Runtime Observation Status

## Connected and Discovered Sources

## Service Health

## Data and Provenance Health

## Context and Classification Health

## Proof and Replay Health

## Chronology and Continuity Health

## Authority-Boundary Health

## Material Changes

## Quiet Tracking

## Architect Action

## Source Dependencies

## Policy Dependencies

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

When no records are ingested, the brief must state:

```text
Runtime evidence surfaces were discovered, but no bounded operating records were ingested for this observation.

Service, intake, context, proof, chronology, and authority-boundary health therefore remain unknown.

No decision-relevant anomaly was observed in the available evidence. This statement does not establish that the operating environment is healthy.
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

## Accepted-State Synchronization

Repository movement must not be promoted into accepted shared state solely
because it is merged. Promotion requires explicit evidence of Architect or CCO
review, an accepted claim boundary, and successful accepted-state registry
validation.

Once explicit review and accepted claim boundaries exist, the Daily Coherence
Agent must classify the remaining work as state synchronization rather than
continuing to report the repository movement as unreviewed.

Acceptance of a bounded implementation does not promote excluded claims such as
live operation, production health, external comprehension, buyer adoption, or
operator dependency.

The action-state model must distinguish system maintenance from Architect
decision requirements:

```yaml
action_state:
  system_maintenance_action_required:
  Architect_decision_required:
  external_dependency_action_required:
  assigned_to: []
  action_type:
  blocking_state:
  rationale:
```

Allowed action types are `none`, `registry_synchronization`,
`chronology_write`, `archive_write`, `repo_review`, `source_acquisition`,
`Architect_policy_decision`, `contradiction_resolution`, and
`external_validation`.

Allowed blocking states are `non_blocking`, `blocks_state_acceptance`,
`blocks_Architect_decision`, `blocks_external_claim`, and
`blocks_production_claim`.

Actor assignment rules:

```yaml
registry_delta_reviewed_but_not_written:
  system_maintenance_action_required: true
  Architect_decision_required: false
  assigned_to:
    - accepted_state_registry_writer

canonical_event_required_but_not_written:
  system_maintenance_action_required: true
  Architect_decision_required: false
  assigned_to:
    - Chronology_Agent

durable_archive_pending:
  system_maintenance_action_required: true
  Architect_decision_required: false
  external_dependency_action_required: true_or_false_based_on_destination
  assigned_to:
    - archive_writer_or_Architect_when_credentials_required

policy_boundary_unresolved:
  system_maintenance_action_required: false
  Architect_decision_required: true
  assigned_to:
    - Architect
    - Jarvis_Nova_CCO

source_unavailable_but_no_decision_blocked:
  Architect_decision_required: false
  blocking_state: non_blocking
```

A canonical chronology event is required when reviewed repository movement
changes the accepted governance infrastructure, evidence policy, authority
boundary, or stage activation state. The Daily Coherence Agent may recommend or
stage a chronology event but must not write one unless the chronology writer is
explicitly authorized.

Durable archive status must distinguish local preparation from verified
external completion. `pending_external_archive` remains active until the
authoritative archive destination confirms the write or provides a verifiable
archive reference.

Accepted-state registry ingestion must use the merged repository registry on
`main` as the canonical source unless a governing standard explicitly
designates another authoritative store. A local mirror may improve availability,
but it is non-authoritative and must not create, amend, or reconcile accepted
state independently.

When a repository registry and a local mirror both exist, the Daily Coherence
Agent must prefer the valid canonical repository registry, record the canonical
commit, and classify mirror lag as system maintenance rather than an Architect
decision. If the canonical source is unavailable and only a stale mirror exists,
the mirror may be used only for bounded historical context; it must not be
presented as current accepted state.

Mirror refresh requires schema validation before replacement, atomic write
behavior, mirror metadata containing the canonical repository, canonical commit,
synchronization time, content hash, schema version, and sync status, and
preservation of the last valid mirror when validation fails. Local and remote
entries must not be merged heuristically.

Accepted-state delta reporting must use a bounded observation checkpoint. A
registry entry is newly accepted only when it is present in the canonical
registry and has not already been acknowledged by the Daily Coherence Agent
checkpoint. The checkpoint is an observation cursor, not an accepted-state
registry, and must not contain independent governance claims. Refreshing a
local mirror must not create a chronology event or a new accepted-state entry.

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
