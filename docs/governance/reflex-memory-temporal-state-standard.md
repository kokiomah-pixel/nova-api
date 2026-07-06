# Reflex Memory Temporal-State Standard

## Status

Governance standard
Architecture hardening artifact
Not regime engine
Not production state management
Not automatic expiration
Not autonomous memory mutation
Not market-regime detection
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document defines how Reflex Memory should carry temporal-state context so accepted governance memory is not mistaken for permanently current review posture.

Replay shows where Reflex Memory came from.

Temporal-state discipline shows whether the memory remains review-relevant.

This standard protects Sharpe Nova OS from stale-memory interpretation, epoch confusion, and replay-overclaiming.

## Core Principle

Reflex Memory may condition future review posture only when its temporal relevance is visible.

Old governance stress should not appear current without qualification.

Replay reconstructs context.

Replay does not prove current relevance by itself.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## What Temporal-State Context Means

Temporal-state context describes:

- when a Reflex Memory entry was accepted
- what review environment it came from
- when it should be reviewed again
- what conditions make it relevant
- what conditions may make it stale
- what transition or stress caused it to exist
- how it should appear in future review context

Temporal-state context does not create authority.

It does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, control wallets, or replace local authority.

## Required Temporal-State Fields

Future Reflex Memory entries should preserve or derive these fields:

```yaml
reflex_memory_temporal_state_fields:
  accepted_at:
    required: true
    purpose: records when the Reflex Memory entry was accepted

  expiration_or_review_after:
    required: true
    purpose: defines when governance review should reconsider the entry

  temporal_scope:
    required: recommended
    purpose: describes the time, condition, or review environment in which the memory remains relevant

  transition_reason:
    required: recommended
    purpose: explains why this memory became accepted or why review posture changed

  relevance_condition:
    required: recommended
    purpose: describes when this memory should be surfaced again

  staleness_handling:
    required: recommended
    purpose: defines whether to surface, suppress, mark stale, or require review when context changes

  source_state:
    required: true
    purpose: preserves the quality and limitations of the source context

  authority_effect:
    required: true
    required_value: none
    purpose: preserves non-authority boundary
```

Current bounded v0.1 fixtures already preserve:

* `accepted_at`
* `expiration_or_review_after`
* `source_state`
* `authority_effect: none`

This standard clarifies the semantic role of those fields and identifies recommended future fields.

## Temporal-State Classes

Use these classes when describing Reflex Memory relevance:

```yaml
temporal_state_classes:
  current_for_review:
    meaning: entry remains review-relevant under current review conditions
    review_effect: may appear as normal Reflex Memory context

  review_after_due:
    meaning: entry has reached or passed its review-after date
    review_effect: should be surfaced with review-needed context

  conditionally_relevant:
    meaning: entry is relevant only if the current prepared action matches stated relevance conditions
    review_effect: should be surfaced with condition context

  potentially_stale:
    meaning: entry may no longer reflect current review environment
    review_effect: should be marked stale or routed for governance review context

  superseded:
    meaning: later accepted governance memory or reviewed chronology has replaced the entry
    review_effect: should not be treated as current without explicit explanation

  historical_only:
    meaning: entry remains part of chronology but should not condition current review posture
    review_effect: may support replay or lineage, not active review posture
```

These classes do not approve, deny, authorize, or block anything.

They qualify review context.

## Epoch and Regime Language

Nova should use epoch or regime language carefully.

Safe use:

```text
A reviewed transition may explain why prior governance memory should be reconsidered.
```

Safe use:

```text
Temporal-state context can qualify whether Reflex Memory remains relevant across review periods.
```

Unsafe use:

```text
Nova detects market regimes.
```

Unsafe use:

```text
Nova automatically transitions epochs.
```

Unsafe use:

```text
Nova expires memory autonomously.
```

Unsafe use:

```text
Nova manages market states.
```

Unsafe use:

```text
Nova decides when memory applies.
```

## Replay Boundary

Replay reconstructs:

* context entry
* accepted Reflex Memory entry
* source chronology IDs
* evidence references
* authority effect
* fixture-backed lineage

Replay does not prove:

* current relevance
* production lineage
* audit readiness
* compliance status
* authority
* execution readiness
* live integration status

A replay artifact should always preserve the distinction:

```text
traceability is not current relevance
```

## Staleness Discipline

Reflex Memory should not be treated as permanently active.

A Reflex Memory entry should be reconsidered when:

* `expiration_or_review_after` is reached
* source state has changed materially
* authority structure has changed
* relevant constraints have changed
* a later chronology event supersedes the original stress pattern
* the memory is being surfaced in a different action type or review environment
* replay shows lineage but not current applicability

Staleness handling should be visible in review context.

Nova should not silently treat stale memory as current.

## Relationship to Source-State Taxonomy

Temporal-state context depends on source-state classification.

Source state describes the condition of the context.

Temporal state describes whether the accepted memory remains review-relevant.

Both are review-context qualifiers.

Neither creates authority.

## Relationship to Review Completeness

A prepared action should not be treated as review-ready if Reflex Memory is surfaced without temporal-state visibility when temporal relevance is material.

Review completeness requires that Reflex Memory context be either:

* current for review
* conditionally relevant
* flagged for review-after
* marked potentially stale
* marked historical only
* explicitly not applicable

## Relationship to Record Lifecycle

Raw records do not become memory automatically.

Chronology events do not automatically condition future review.

Reflex Memory candidates do not condition future review until accepted.

Accepted Reflex Memory may condition review posture only if its temporal-state context remains visible.

## Safe Language

Use:

```text
Reflex Memory should carry temporal-state context so old governance stress is surfaced with its review relevance intact.
```

Use:

```text
Replay reconstructs context; it does not prove current relevance by itself.
```

Use:

```text
Temporal state qualifies review posture. It does not create authority.
```

Use:

```text
Old governance stress should not appear current without qualification.
```

## Unsafe Language

Do not say:

```text
Nova detects market regimes.
```

Do not say:

```text
Nova automatically transitions epochs.
```

Do not say:

```text
Nova expires Reflex Memory autonomously.
```

Do not say:

```text
Nova decides when memory applies.
```

Do not say:

```text
Replay proves current risk.
```

Do not say:

```text
Replay is an audit trail.
```

Do not say:

```text
Temporal state authorizes review outcomes.
```

## Final Rule

Replay shows lineage.

Temporal-state discipline qualifies relevance.

Memory conditions review.

Authority remains local.

Execution happens elsewhere.
