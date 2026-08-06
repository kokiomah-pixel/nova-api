# Reflex Memory v0.1 Fixture

## Status

Reference fixture
Non-production
Non-authority
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This fixture demonstrates how Reflex Memory v0.1 can move from a reviewed chronology event into API-emitted review context without becoming authority.

It is intentionally deterministic and narrow.

It does not claim production readiness.

## Fixture Flow

```text
reviewed chronology event
-> Reflex Memory candidate
-> accepted Reflex Memory entry
-> API review-context field
-> local authority decision
-> execution elsewhere
```

## Included Files

```text
fixtures/reflex_memory/chronology_event_source_state_conflict.json
fixtures/reflex_memory/reflex_memory_candidate_source_state_conflict.json
fixtures/reflex_memory/reflex_memory_entry_source_state_conflict.json
fixtures/reflex_memory/api_review_context_with_reflex_memory.json
```

## Scenario

The fixture uses a source-state conflict scenario.

A connector-derived state may be stale or unverified relative to an Architect-confirmed current repo state.

The Reflex Memory entry does not decide anything.

It only causes the API review context to surface that prior source-state reconciliation context is relevant before local authority acts.

## Record to Chronology to Reflex Memory Lifecycle

Reflex Memory does not arise automatically from raw events.

Nova distinguishes between preserved records, reviewed chronology events, Reflex Memory candidates, and accepted Reflex Memory.

```yaml
record_to_memory_lifecycle:
  raw_record:
    meaning: captured or preserved information from a review or operating context
    may_be_preserved: true
    reviewed_and_classified: false
    may_condition_future_review: false
    authority_effect: none

  chronology_event:
    meaning: reviewed and classified decision-state lineage
    may_be_preserved: true
    reviewed_and_classified: true
    may_condition_future_review: false
    authority_effect: none

  reflex_memory_candidate:
    meaning: candidate governance memory derived from reviewed chronology
    may_be_preserved: true
    reviewed_and_classified: true
    may_condition_future_review: false
    requires_acceptance: true
    authority_effect: none

  accepted_reflex_memory:
    meaning: manually accepted governance memory that may condition future review posture
    may_be_preserved: true
    reviewed_and_classified: true
    may_condition_future_review: true
    requires_acceptance: completed
    authority_effect: none
```

The lifecycle protects Nova from automatic memory mutation.

A raw record does not become Reflex Memory.

A chronology event does not automatically condition future review.

A Reflex Memory candidate does not condition future review until accepted.

Accepted Reflex Memory may condition review posture only.

It does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, control wallets, or replace local authority.

Safe compression:

```text
Raw records do not become memory automatically.
```

```text
Memory conditions review.
Authority remains local.
Execution happens elsewhere.
```

## Temporal-State Context

Reflex Memory entries should not be interpreted as permanently current.

Current bounded v0.1 fixtures preserve:

- `accepted_at`
- `expiration_or_review_after`
- `source_state`
- `authority_effect: none`

These fields help reviewers understand when the entry was accepted, what source-state limitations existed, and when review should reconsider the entry.

Future Reflex Memory entries may add explicit temporal-state fields such as:

- `temporal_scope`
- `transition_reason`
- `relevance_condition`
- `staleness_handling`

These fields would qualify review relevance.

They would not create authority, production persistence, automatic expiration, autonomous memory mutation, market-regime detection, compliance review, audit reporting, or execution logic.

Replay reconstructs where Reflex Memory came from.

Replay does not prove current relevance by itself.

See:

- `docs/governance/reflex-memory-temporal-state-standard.md`

## Multi-Scenario Fixtures

Reflex Memory v0.1 now includes deterministic fixtures for multiple governance-stress scenarios:

- source-state conflict
- boundary-language drift
- proof-reference missing

These fixtures demonstrate scenario breadth.

They do not demonstrate production persistence, autonomous pattern detection, automatic memory mutation, market validation, buyer validation, adoption, or external integration.

Each accepted entry must preserve:

```yaml
authority_effect: none
```

## Schema Validation

Reflex Memory v0.1 fixtures are validated against machine-readable schemas under:

```text
schemas/reflex_memory/
```

This validation is fixture-backed.

It does not claim production persistence, dynamic storage, autonomous memory mutation, compliance review, audit reporting, or external integration.

## Governed Abstraction Extension

The v0.1 fixture continues to demonstrate the existing accepted-memory lifecycle.

Additional versioned fixtures demonstrate:

- an unaccepted implicit-policy-conversion candidate;
- an exception-only candidate;
- an accepted governed-abstraction v0.2 entry;
- a retrieval explanation with material comparison limits.

These fixtures are synthetic specification evidence.

They do not create accepted Reflex Memory, chronology, production state, or
runtime behavior.

Schemas:

- `schemas/reflex_memory/reflex_memory_candidate_v0_2.schema.json`
- `schemas/reflex_memory/reflex_memory_entry_v0_2.schema.json`
- `schemas/reflex_memory/reflex_memory_retrieval_explanation_v0_1.schema.json`

Fixtures:

- `fixtures/reflex_memory/reflex_memory_candidate_implicit_policy_conversion.json`
- `fixtures/reflex_memory/reflex_memory_candidate_exception_only.json`
- `fixtures/reflex_memory/reflex_memory_candidate_governed_abstraction_accepted.json`
- `fixtures/reflex_memory/reflex_memory_entry_governed_abstraction_v0_2.json`
- `fixtures/reflex_memory/reflex_memory_entry_exception_only_v0_2.json`
- `fixtures/reflex_memory/reflex_memory_retrieval_comparison_limits.json`

The accepted synthetic chains are:

```text
RMC-0201 → RM-0201
RMC-0002 → RM-0202 → RMR-0001
```

They demonstrate fixture referential integrity only. They are not active Reflex
Memory objects and create no chronology, production state, or runtime behavior.

## Replayability

Reflex Memory v0.1 includes a fixture-backed replay artifact that reconstructs API-emitted Reflex Memory context back to accepted Reflex Memory entries and source chronology IDs.

This replay artifact is for review-context inspection only.

It is not an audit report, compliance review, production lineage system, or authority mechanism.

## What This Demonstrates

The fixture demonstrates:

- Reflex Memory derives from reviewed chronology.
- Reflex Memory candidate state is distinct from accepted state.
- Acceptance is explicit.
- Reflex Memory references source chronology.
- Reflex Memory has `authority_effect: none`.
- API output remains review context.
- Local authority remains responsible.

## What This Does Not Demonstrate

The fixture does not demonstrate:

- production readiness
- institutional adoption
- market validation
- buyer validation
- live deployment
- autonomous learning
- automatic memory mutation
- approval
- denial
- authorization
- blocking
- routing
- settlement
- signing
- execution
- compliance review
- audit reporting
- wallet control
- agent supervision

## Safe Interpretation

Reflex Memory informs the review context emitted by the API.

Accepted governance memory may condition future review posture.

Memory conditions review.
Authority remains local.
Execution happens elsewhere.

## Endpoint Integration

The v0.1 fixture may be surfaced through `/v1/context` as `reflex_memory_context`.

This integration is bounded and fixture-backed.

It demonstrates review-context exposure only.

It does not demonstrate production persistence, live Reflex Memory mutation, autonomous learning, approval, denial, authorization, blocking, routing, settlement, signing, execution, compliance review, audit reporting, wallet control, or agent supervision.

## Final Rule

This fixture exists to make Reflex Memory inspectable.

It does not make Reflex Memory an authority layer.
