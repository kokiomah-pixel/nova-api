# Agent-Prepared Action Example

## Status

Bounded example
Not external integration
Not production claim
Not adoption evidence
Not buyer validation
Not market validation

## Purpose

This example shows how an agent-prepared financial action package can be consumed by Sharpe Nova OS as review context.

It demonstrates where Nova sits:

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.
```

## What This Example Shows

The example demonstrates:

- an agent prepares a financial action package
- the package includes action intent, source context, authority context, and review requirements
- Nova can consume the package as input to review-context formation
- Reflex Memory context can appear as review context with `authority_effect: none`
- local authority remains responsible for any decision
- execution happens outside Nova

## What This Example Does Not Show

This example does not show:

- external production integration
- live agent framework integration
- wallet control
- payment routing
- settlement
- signing
- trade execution
- approval
- denial
- authorization
- compliance review
- audit reporting
- agent supervision
- market validation
- buyer validation
- institutional adoption

## Example Package

See:

```text
examples/agent_prepared_action/agent_prepared_treasury_action.json
```

## Safe Interpretation

Use:

```text
Prepared action is not review readiness.
```

Use:

```text
Nova helps make agent-prepared financial actions review-ready before local authority decides.
```

Use:

```text
Local authority decides. Execution happens elsewhere.
```

## Final Rule

This example is a boundary-safe integration illustration.

It does not make Nova an execution layer or agent supervisor.
