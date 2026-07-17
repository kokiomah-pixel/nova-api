# Architect Runtime Evidence Policy

## Status

Approved bounded implementation policy
Read-only Architect Data Operations pilot
Not automated surveillance
Not production-health certification
Not authority to approve, block, repair, execute, or accept state

## Purpose

This policy authorizes the Architect Data Operations visibility layer to move
from source-surface discovery to bounded, read-only metadata ingestion.

The approval is narrow. It allows Nova to observe only the metadata required to
describe operating coherence during a controlled pilot. It does not authorize
raw financial-action payload collection, prompt collection, wallet or account
surveillance, automatic chronology repair, Reflex Memory mutation, external
alert delivery, or public production-health claims.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

The operating-visibility layer:

```text
observes
normalizes bounded metadata
evaluates evidence health
generates an Architect brief
```

It does not:

```text
approve
block
repair
execute
accept
```

## Activation Mode

```yaml
activation_mode:
  environment: local_or_controlled_private_environment
  access: read_only
  operation: manual
  scheduling: disabled
  runtime_mutation: prohibited
  external_delivery: prohibited
  pilot_status: approved
```

The pilot duration is seven days. The observation window is a rolling 24 hours
in UTC. Generation is once daily and manual. No scheduler is approved.

## Approved Sources

### Stage A: Proof Registry

Stage A is the only active source in the initial implementation.

```yaml
source_id: proof_registry
interface: .proof_registry.json
source_kind: runtime_record_source
ingestion_status: approved_for_bounded_metadata
```

The proof registry is authoritative only for bounded proof identity,
proof-record presence, proof creation timestamp when recorded, proof verification
result when recorded, and canonical signature or reproducibility references when
recorded.

It is not authoritative for live source provenance, chronology acceptance,
external execution, institutional review outcome, commercial usage, or
production health.

Permitted fields:

```yaml
permitted_fields:
  - proof_id
  - decision_id
  - created_at
  - verified_at
  - verification_status
  - canonical_signature
  - reproducibility_hash
  - governance_epoch_id
  - source_class
  - provenance_status
  - authority_effect
```

Prohibited fields include raw payloads, action payloads, private keys, API keys,
wallet credentials, account numbers, model prompts, hidden policy weights, and
unrestricted source content.

### Later Stages

Reflex governance records, API request metadata, and chronology validation
results are policy-approved only when their specific structured metadata
interfaces are available and reviewed. They are not activated by Stage A.

## Observation Window

```yaml
observation_window:
  type: rolling
  duration_hours: 24
  timezone: UTC
```

Records are current only when their event timestamp falls inside the declared
window, or when they directly validate or reference an in-window record.

Missing or invalid timestamps are classified as `freshness_state: unknown`.
They must not be silently placed inside the current window.

Historical records may support replay comparison, classification-drift
comparison, or chronology-link validation. They must not be counted as current
operating volume.

## Identifier Policy

Only bounded identifiers may enter generated snapshots or briefs.

Permitted identifiers are salted hashes of request, decision, proof, or
chronology record identifiers, plus governance epoch and validator run IDs.

The salt must be supplied outside the repository. If no stable external salt is
available, identifiers must be redacted with:

```yaml
identifier_state:
  value: redacted
  evidence_state: unavailable
  reason: identifier_hash_policy_not_configured
```

The implementation must not fall back to raw identifiers.

## Live Provenance Standard

A record may be classified as `live` only when every required provenance
condition is present:

```yaml
required:
  - source_origin_identified
  - environment_identified
  - collection_timestamp_present
  - immutable_or_stable_source_reference_present
  - integrity_hash_or_equivalent_present
  - authoritative_scope_declared
  - record_not_fixture_or_test_generated
  - policy_permitted_fields_only
```

A production-shaped record is not automatically live. A runtime-file record is
not automatically live. A developer-environment record is not automatically
production-like.

## Retention

The visibility layer must minimize copied data.

```yaml
retention_policy:
  raw_source_payload_copy:
    allowed: false

  ingestion:
    mode: in_memory_or_ephemeral
    temporary_files_allowed: false

  generated_snapshot:
    retention_days: 30
    storage_scope: private_local_or_governed_internal
    contains_raw_payloads: false

  Architect_brief:
    retention_days: 90
    storage_scope: private_internal
```

Existing source files retain their own governed lifecycle. This policy does not
alter proof registry, Reflex record, API infrastructure, or chronology-system
retention behavior.

Generated operating snapshots and briefs remain uncommitted by default.

## Privacy and Redaction

Before any source record enters a snapshot:

```text
load
field allowlist
sensitive-key rejection
identifier hashing
length and type validation
normalization
```

Allowlist behavior is mandatory. A denylist alone is insufficient.

Unknown fields are dropped. Field names may be reported as informational
metadata; field values must not be copied.

## Severity and Notification

The pilot repeat threshold is:

```yaml
repeat_threshold:
  occurrence_count: 3
  independent_record_count: 2
  window_hours: 24
```

Automatic alert delivery is disabled. Critical anomalies are surfaced in the
next manually generated brief. This does not authorize email, SMS, Slack,
webhook, paging, or other external delivery.

## Architect Action Logic

Architect action is required for critical anomalies, material anomalies that
require a policy or architecture decision, source gaps that invalidate a current
operating claim, sensitive data exposure, or authority-boundary failure.

Architect action is not required for no records ingested, isolated noncritical
anomalies, expected classification changes, or known offline-fixture limitations.

No action required does not mean healthy.

## Operating Health Claim Rules

Allowed:

```text
Bounded runtime records were ingested for the declared observation window.
No decision-relevant anomaly was observed in the available evidence.
Proof verification passed for the records observed in this bounded window.
Chronology validation was unavailable; chronology health remains unknown.
```

Not allowed:

```text
All systems normal.
The Nova API is fully healthy.
Production is operating correctly.
All data is trustworthy.
No governance risk exists.
```

Every operating statement must state the evidence boundary that supports it.

## Stage Sequence

```text
policy enforcement
proof-registry read-only pilot
first Architect brief
review
Reflex-record activation
API metadata
chronology validation
```

Do not connect all sources simultaneously.

## Final Rule

The Architect authorizes bounded evidence visibility. Nova reads only what is
necessary to describe operating coherence. Observation does not create authority.
Availability does not establish health. Evidence does not become live merely
because it exists.
