# Sharpe Nova OS — Category Definition

## The Shift

Capital workflows are becoming increasingly agent-prepared and machine-mediated.

Execution is getting faster. The harder problem is preserving the context, constraints,
uncertainty, and authority boundary around a consequential action before capital moves.

---

## The Problem

A transaction system can prove what executed and which credentials signed.

It may not preserve the exact decision context that local authority reviewed:

- which proposal version was under consideration;
- which sources were current;
- which evidence was missing, stale, conflicted, or unresolved;
- which institution-owned constraints applied;
- which prior accepted governance memory was relevant;
- where decision authority remained local.

As agents prepare actions faster, losing that distinction becomes more consequential.

---

## The Missing Layer

Sharpe Nova OS addresses the pre-execution gap between **prepared action** and
**local decision authority**.

It is not an execution kernel or authorization control plane.

It is a **pre-execution decision discipline layer** that conditions capital through
telemetry, Reflex Memory, and constraint logic before execution.

---

## Canonical Boundary

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

`Local authority` is a role in the architecture, not a requirement that a human
must always occupy that role. The institution may place a human, committee,
institution-owned policy process, or separately authorized machine process in
that position.

Nova does not decide who holds that authority and does not inherit it by being
required in the workflow.

---

## Exact-Action Binding

Nova review context is designed to remain bound to the exact proposal version
that was reviewed.

```text
prepared action version
        ↕
Nova review context / proof
        ↕
local authority process
        ↓
external execution
```

An institution may decide that a valid Nova review-context object is required
before its own authority process proceeds.

That requirement belongs to the institution.

```text
required input to authority
!= authority
```

Nova does not approve, deny, authorize, sign, settle, or execute the action.

---

## What Nova Preserves

Nova is designed to preserve and structure:

- proposal-version identity;
- source provenance and freshness;
- contradiction and missing-evidence visibility;
- institution-provided constraint context;
- chronology references;
- governed Reflex Memory references where authorized;
- review completeness and unresolved conditions;
- authority handoff and non-authority boundaries.

Reflex Memory is not merely a snapshot of what the world looked like.
It preserves accepted governance memory that may condition future review posture
without creating decision authority.

---

## What It Enables

- reproducible pre-execution review context;
- durable distinction between preparation, review, decision, signing, and execution;
- portable context that can survive changes in models, agents, wallets, or execution rails;
- institutional review continuity without transferring authority to Nova;
- machine-consumable context that can become a required precondition without becoming a control plane.

---

## Where It Fits

```text
[ Agent / Strategy / Local System ]
                ↓
      prepared financial action
                ↓
[ Sharpe Nova OS ]
 governed review context + proof
                ↓
[ Local Authority ]
     reviews and decides
                ↓
[ External Execution Systems ]
```

---

## What Nova Is Not

Nova is not:

- a trading system;
- a signal engine;
- a prediction layer;
- a portfolio optimizer;
- an execution engine;
- an approval or authorization authority;
- a wallet, custodian, settlement rail, or signing system;
- a policy-enforcement kernel that owns the institution's decision.

---

## Final Statement

Nova does not determine whether capital should move.

Nova structures verifiable decision context around the exact action under review
before local authority decides.

Authority remains local.

Execution remains external.
