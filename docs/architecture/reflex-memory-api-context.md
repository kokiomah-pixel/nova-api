# Reflex Memory API Context

## Status

Architecture note
Non-authority integration guidance
Not production claim

## Purpose

This note explains how Reflex Memory may appear in Nova API-emitted review context without making Nova an authority layer.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

## Integration Rule

Reflex Memory may inform API-emitted review context only as transparent context.

It must not invisibly alter authorization, execution, routing, settlement, signing, wallet behavior, agent control, compliance status, or audit status.

## Example Field

```yaml
reflex_memory_context:
  present: true
  version: reflex_memory_v0_1
  entries:
    - reflex_id: RM-0001
      source_chronology_event_ids:
        - CHR-2026-07-03-001
      trigger_pattern: source_state_conflict
      review_posture_effect: require_source_reconciliation_context
      authority_effect: none
      note: Prior source-state conflict should be visible in review context before local authority acts.
```

## Interpretation

The field means:

- prior accepted governance memory is relevant to review
- the reviewer should inspect the referenced chronology
- the context may require source reconciliation
- local authority remains responsible for the decision
- execution happens elsewhere

The field does not mean:

- Nova approved the action
- Nova denied the action
- Nova granted payment permission
- Nova blocked execution
- Nova routed a transaction
- Nova settled value
- Nova signed a transaction
- Nova performed compliance review
- Nova produced an audit report
- Nova replaced local authority

## Versioning

Every Reflex Memory API context field should include a version.

Example:

```yaml
version: reflex_memory_v0_1
```

Versioning is required so that future review can reconstruct which Reflex Memory semantics were active when context was emitted.

## Replay Requirement

A replay should be able to reconstruct:

- which Reflex Memory entries were present
- which chronology events they referenced
- what source-state classification applied
- what review posture effect was surfaced
- why the effect did not constitute authority

## v0.1 Fixture-Backed Integration

The initial `/v1/context` Reflex Memory integration is fixture-backed.

It exists to demonstrate how accepted Reflex Memory may appear in API-emitted review context.

It is not dynamic Reflex Memory storage.
It is not autonomous pattern detection.
It is not automatic memory mutation.
It is not a production persistence layer.

The v0.1 integration must preserve:

```yaml
authority_effect: none
```

The field exists so local authority can inspect relevant accepted governance memory before deciding.

It does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, perform audit reporting, manage wallets, supervise agents, or replace local authority.

## Final Rule

Reflex Memory may shape review context.

It must not shape execution authority.

Memory conditions review.
Authority remains local.
Execution happens elsewhere.
