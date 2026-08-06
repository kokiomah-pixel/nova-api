# Reflex Memory vs Agent Memory

## Status

Architecture boundary note
Category hardening artifact
Not runtime adapter
Not production memory system
Not shared-substrate validation
Not audit product
Not authority management
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document clarifies how Sharpe Nova OS Reflex Memory differs from agent self-reflection, episodic memory, vector memory, and simple event sourcing.

Reflex Memory should not be interpreted as agent memory.

Reflex Memory is accepted governance memory derived from reviewed chronology events.

It may condition future review posture.

It does not decide.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## Core Distinction

Reflex Memory is not an agent remembering what it learned.

Reflex Memory is an institution preserving what it has accepted as governance memory before future review.

Safe compression:

```text
Reflex Memory is governed institutional memory, not agent memory.
```

## What Reflex Memory Is

Reflex Memory is:

* accepted governance memory
* derived from reviewed chronology events
* source-linked
* evidence-referenced
* bounded by non-authority invariants
* exposed only as review context
* able to condition future review posture
* replayable back to accepted entries and source chronology IDs in bounded v0.1 fixtures

Reflex Memory helps surface prior governance stress, source-state deterioration, boundary risk, proof-reference gaps, or recurring review-context patterns.

## What Reflex Memory Is Not

Reflex Memory is not:

* agent self-reflection
* general episodic memory
* vector recall
* autonomous learning
* model memory
* prompt memory
* execution memory
* audit reporting
* compliance determination
* authority management
* payment permission
* wallet control
* trading signal
* portfolio recommendation
* production memory store

Reflex Memory does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, manage wallets, or replace local authority.

## Difference from Reflexion-Style Self-Reflection

Reflexion-style memory is usually agent-centered.

It helps an agent improve future task behavior by reflecting on prior attempts.

Nova Reflex Memory is institution-centered.

It helps preserve accepted governance memory so future review posture can be conditioned before local authority decides.

```yaml
reflexion_style_memory:
  subject: agent
  purpose: improve_agent_behavior
  source: task_attempts_or_self_reflection
  mutation: often_model_or_loop_generated
  output: improved_next_agent_action
  authority_boundary: not_the_primary_object

nova_reflex_memory:
  subject: institutional_review_context
  purpose: condition_future_review_posture
  source: reviewed_chronology_events_only
  mutation: manual_acceptance_required
  output: governed_review_context
  authority_boundary: core_invariant
```

Safe distinction:

```text
Reflexion helps an agent learn from itself.
Reflex Memory helps an institution preserve accepted governance memory before future review.
```

## Difference from Episodic Agent Memory

Episodic memory usually preserves prior runs, conversations, tool calls, task outcomes, or agent experiences.

Nova Reflex Memory does not preserve everything that happened.

It preserves only accepted governance memory derived from reviewed chronology events.

```yaml
episodic_agent_memory:
  remembers: prior_events_or_agent_experience
  selection_boundary: operational_or_task_based
  purpose: recall_context_for_future_tasks

nova_reflex_memory:
  remembers: accepted_governance_stress
  selection_boundary: reviewed_chronology_then_explicit_acceptance
  purpose: condition_review_posture_before_local_authority_decides
```

Safe distinction:

```text
Episodic memory recalls prior experience.
Reflex Memory preserves accepted governance memory.
```

## Difference from Knowledge-Centric Agent Memory

Knowledge-centric agent memory may transform interaction history into reusable
facts, procedures, or task guidance to improve later agent performance.

Sharpe Nova OS does not treat extracted knowledge as institutionally valid by
default.

```yaml
knowledge_centric_agent_memory:
  objective: improve_future_agent_performance
  abstraction: may_be_automatic
  retrieval: task_relevance
  institutional_acceptance: not_required_by_default

nova_governed_abstraction:
  objective: preserve_reviewable_institutional_learning
  abstraction: candidate_only_until_reviewed
  retrieval: governance_relevance_with_comparison_limits
  institutional_acceptance: explicit
  policy_effect: none_by_default
  authority_effect: none
```

Safe distinction:

```text
Agent memory extracts what may help the machine.

Nova governs whether an institutional lesson may condition review,
while preserving its origin, limits, exceptions, and authority status.
```

## Difference from Vector Memory

Vector memory retrieves semantically similar context.

Nova Reflex Memory is not similarity search.

It is structured governance memory with explicit source chronology, evidence references, source-state classification, review-posture effect, expiration or review-after, and authority effect set to none.

```yaml
vector_memory:
  retrieval_basis: semantic_similarity
  source_boundary: depends_on_index
  governance_acceptance: not_required_by_default
  authority_boundary: external_to_memory

nova_reflex_memory:
  retrieval_basis: accepted_governance_relevance
  source_boundary: source_chronology_event_ids
  governance_acceptance: required
  authority_boundary: embedded_in_entry
```

Safe distinction:

```text
Vector memory retrieves similar context.
Reflex Memory surfaces accepted governance memory.
```

## Difference from Event Sourcing

Event sourcing records events so system state can be reconstructed.

Nova Reflex Memory uses lineage and replay, but it is not merely event sourcing.

A raw event does not become Reflex Memory.

A chronology event must be reviewed.

A Reflex Memory candidate must be derived.

A candidate must be explicitly accepted.

Only accepted Reflex Memory may condition future review posture.

```text
raw event
-> reviewed chronology event
-> Reflex Memory candidate
-> accepted Reflex Memory
-> future review posture conditioning
```

Safe distinction:

```text
Event sourcing reconstructs system history.
Reflex Memory reconstructs governance-memory lineage and preserves review-boundary context.
```

## Data Model Summary

A bounded v0.1 Reflex Memory entry preserves:

```yaml
reflex_memory_entry_v0_1:
  reflex_id: required
  version: reflex_memory_v0_1
  status: accepted
  source_chronology_event_ids: required
  created_at: required
  reviewed_at: required
  accepted_at: required
  accepted_by: required
  source_state:
    classification: required
    limitations: required
  trigger_pattern: required
  stress_type: required
  boundary_risk: required
  review_posture_effect: required
  evidence_refs: required
  expiration_or_review_after: required
  authority_effect: none
  non_authority_statement: required
```

The important feature is not only that the object can be replayed.

The important feature is that it remains source-linked, accepted, bounded, and non-authority.

## Shared Substrate Boundary

Reflex Memory may become useful across agent frameworks because it is not model-native memory.

It is schema-backed governance memory.

However, cross-framework substrate validation is not currently claimed.

Current status:

```yaml
shared_substrate_status:
  conceptual_compatibility: plausible
  schema_backed_unit: present
  fixture_backed_replay: present
  framework_adapter_tests: not_implemented
  production_memory_store: not_implemented
  cross_framework_validation: not_claimed
```

Safe language:

```text
Reflex Memory is architecturally compatible with a model-independent governance-memory layer.
```

Do not say:

```text
Reflex Memory is already a validated shared cognition substrate across agent frameworks.
```

## Correct Language

Use:

```text
lineage reconstruction
```

Use:

```text
review-context conditioning
```

Use:

```text
authority-boundary preservation
```

Use:

```text
governed institutional memory
```

Use:

```text
accepted governance memory
```

## Unsafe Language

Do not say:

```text
authority management
```

Do not say:

```text
audit product
```

Do not say:

```text
audit-ready memory layer
```

Do not say:

```text
agent brain
```

Do not say:

```text
shared cognition substrate already validated
```

Do not say:

```text
Nova memory controls future action
```

Do not say:

```text
Reflex Memory lets Nova decide
```

## Final Rule

Reflex Memory is not agent memory.

It is governed institutional memory that may condition future review posture.

Authority remains local.

Execution happens elsewhere.
