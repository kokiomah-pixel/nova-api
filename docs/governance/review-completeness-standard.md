# Review Completeness Standard

## Status

Governance standard
Architecture hardening artifact
Not execution logic
Not approval logic
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document defines the minimum conditions for an agent-prepared financial action to be considered review-ready inside Sharpe Nova OS.

Review-ready does not mean approved.

Review-ready does not mean authorized.

Review-ready does not mean executable.

Review-ready means local authority has sufficient governed context to begin review.

## Core Principle

Prepared action is not review readiness.

An agent can prepare an action package, but the package is not review-ready until the governed context around the action is structured.

Nova structures review context.

Local authority decides.

Execution happens elsewhere.

## Minimum Review-Ready Conditions

A prepared action is review-ready only when the review context includes, or explicitly flags the absence of, the following:

```yaml
minimum_review_ready_conditions:
  prepared_action_intent:
    required: true
    purpose: identify what action was prepared

  asset_or_instrument_context:
    required: true
    purpose: identify the asset, instrument, rail, venue, or workflow dependency involved

  source_context:
    required: true
    purpose: identify the sources used to prepare or review the action

  source_state:
    required: true
    purpose: classify whether sources are confirmed, incomplete, conflicting, stale, unavailable, or reconciled

  authority_path:
    required: true
    purpose: identify who must review or decide locally

  local_authority_boundary:
    required: true
    purpose: preserve that Nova does not decide

  constraint_pressure:
    required: true
    purpose: surface relevant limits, rules, thresholds, exceptions, or escalation pressure

  proof_metadata:
    required: true
    purpose: preserve reconstruction context for review

  chronology_relevance:
    required: if_available
    purpose: surface relevant accepted decision-state lineage

  reflex_memory_context:
    required: if_present
    purpose: surface accepted governance memory that may condition review posture

  exception_visibility:
    required: true
    purpose: make gaps, conflicts, missing proof, or unresolved context visible

  review_readiness_state:
    required: true
    purpose: distinguish review-ready from execution-ready

  execution_status:
    required: true
    allowed_value: not_executed
    purpose: preserve non-execution boundary
```

## Review-Ready Does Not Mean Complete Certainty

Review readiness does not require perfect information.

Review readiness requires visible classification of information quality.

A package can be review-ready with incomplete information only if the incompleteness is explicit.

Examples:

* source incomplete
* proof reference missing
* attribution input unavailable
* chronology unavailable
* source conflict unresolved
* escalation condition present

In these cases, Nova should surface the limitation as review context.

Nova should not resolve authority.

## Review Completeness States

Use these states:

```yaml
review_completeness_states:
  complete_for_review:
    meaning: required review-context fields are present and no unresolved gaps are hidden

  incomplete_but_visible:
    meaning: required fields contain gaps, but the gaps are explicitly surfaced for local authority

  blocked_for_review_context:
    meaning: required minimum review context is missing and the action should not be treated as review-ready

  not_applicable:
    meaning: field does not apply to this action type and the non-applicability is explicit
```

Do not use:

```yaml
unsafe_states:
  approved: forbidden
  denied: forbidden
  authorized: forbidden
  executable: forbidden
  cleared: forbidden
```

## Stop Conditions

A prepared action should not be treated as review-ready if:

* action intent is unclear
* local authority path is missing
* execution status is not `not_executed`
* proof metadata is absent and not flagged
* source context is absent and not flagged
* authority scope is ambiguous
* Nova output could be mistaken for approval, denial, authorization, routing, settlement, signing, or execution instruction

A stop condition does not mean Nova controls execution.

It means the prepared action is not review-ready as governed context.

Local authority remains responsible.

Execution happens elsewhere.

## Relationship to Reflex Memory

Reflex Memory may influence review posture by surfacing accepted governance memory.

Reflex Memory does not make a prepared action review-ready by itself.

Reflex Memory does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, control wallets, or replace local authority.

Memory conditions review.

Authority remains local.

Execution happens elsewhere.

## Relationship to Source State

Review completeness depends on source-state classification.

Missing, stale, conflicting, or incomplete sources do not automatically prevent review.

They must be visible.

Nova's role is to structure that visibility before local authority acts.

## Safe Language

Use:

```text
Review-ready means sufficient governed context exists for local authority to begin review.
```

Use:

```text
Incomplete context can be reviewable if the incompleteness is visible.
```

Use:

```text
Prepared action is not review readiness.
```

Use:

```text
Review readiness is not authority.
```

## Unsafe Language

Do not say Nova clears the action.

Do not say Nova controls whether the action proceeds.

Do not say Nova approves the action for execution.

Do not say Nova determines compliance readiness.

Do not say Nova certifies the action.

## Required Review Context Is Not Execution Control

An institution may require governed review context before local authority decides.

That does not make Nova an execution controller.

Nova does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, manage wallets, or replace local authority.

Safe compression:

```text
No governed review context, no local decision.
```

Unsafe compression:

```text
No Nova, no execution.
```

## Final Rule

Review completeness is about governed context.

It is not approval.

It is not execution.

It is not compliance determination.

It is not audit reporting.

Local authority decides.

Execution happens elsewhere.
