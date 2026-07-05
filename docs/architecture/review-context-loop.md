# Review-Context Loop

## Status

Architecture concept note
Doctrine candidate
Not product expansion
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document explains how Sharpe Nova OS can be understood as a bounded review-context loop for agent-prepared financial actions.

The goal is to make Nova's integration logic clearer without implying execution authority, agent supervision, approval authority, compliance review, audit reporting, wallet control, routing, settlement, or signing.

## Core Principle

Prepared action is not review readiness.

An agent may prepare an action, assemble inputs, and make a workflow appear ready for the next step.

That does not mean the action is governed, reviewable, or ready for local authority to decide.

Agent capability is not governance capacity.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## Why Loops Matter

Useful autonomy requires more than task completion.

Autonomous or semi-autonomous workflows need:

- clear scope
- explicit constraints
- source context
- feedback signals
- stop conditions
- verification checks
- review completeness
- human or local authority review

In financial workflows, the risk is not only that an agent prepares the wrong action.

The risk is that an action reaches local authority without sufficient governed review context.

## Nova Translation

In a developer workflow, a bounded loop may include:

```text
goal
rules
tools
feedback
tests
review
```

In a Nova-governed capital workflow, the equivalent is:

```text
authority scope
prepared action
source context
constraint pressure
chronology
proof metadata
review completeness
local authority decision
```

Nova does not run the financial workflow.

Nova structures the review context before local authority acts.

## Review-Context Loop

A bounded review-context loop can be described as:

```text
1. Institution defines authority and constraints.
2. Agent prepares financial action.
3. Nova receives or evaluates the prepared-action package.
4. Nova checks required review-context fields.
5. Nova surfaces source context, chronology, constraint pressure, and contradiction.
6. Nova emits governed review context.
7. Local authority decides.
8. Execution happens elsewhere.
9. Accepted governance record may enter chronology.
```

This loop makes the prepared action more reviewable.

It does not make Nova the authority.

## What Nova Adds

Nova helps convert:

```text
prepared action
```

into:

```text
review-ready context
```

by structuring:

- action intent
- source state
- authority scope
- constraint pressure
- chronology references
- Reflex Memory context
- proof metadata
- exception visibility
- local authority boundary

## Reflex Memory Role

Reflex Memory may inform the review-context loop by surfacing accepted governance memory.

It may condition future review posture.

It does not approve, deny, authorize, block, route, settle, sign, execute, supervise agents, perform compliance review, perform audit reporting, or replace local authority.

Memory conditions review.
Authority remains local.
Execution happens elsewhere.

## Failure Modes This Addresses

A review-context loop helps surface:

- unclear action intent
- unclear authority path
- unclear constraint boundary
- unclear escalation condition
- unclear review completeness
- unclear source state
- unclear memory acceptance rule
- prior governance stress not visible during review

## Unsafe Interpretations

Do not interpret this concept as:

- Nova runs agent loops.
- Nova completes financial workflows.
- Nova closes capital actions.
- Nova approves prepared actions.
- Nova blocks execution.
- Nova supervises agents.
- Nova controls wallets.
- Nova routes payments.
- Nova performs compliance review.
- Nova produces audit reports.

## Safe Interpretation

Use:

```text
Nova helps make agent-prepared financial actions review-ready before local authority decides.
```

Use:

```text
Prepared action is not review readiness.
```

Use:

```text
Agent capability is not governance capacity.
```

Use:

```text
Nova structures the bounded review context before capital movement is considered by local authority.
```

Always pair execution-adjacent language with:

```text
Local authority decides. Execution happens elsewhere.
```

## Relationship to Existing Architecture

This concept supports:

- `docs/architecture/pre-action-context-contract.md`
- `docs/go-to-market/where-nova-sits.md`
- `docs/go-to-market/first-use-case-agent-prepared-treasury-action.md`
- `docs/governance/reflex-memory-specification.md`
- `docs/validation/technical-evidence-map.md`

It does not replace those documents.

It gives readers a systems-level interpretation of why review context must be structured before action.

## Related Concept

For a broader context-flow explanation of what Nova receives, structures, emits, and preserves, see:

- `docs/architecture/governed-context-flow.md`

## Final Rule

Prepared action is not review readiness.

Nova structures review context.

Local authority decides.

Execution happens elsewhere.
