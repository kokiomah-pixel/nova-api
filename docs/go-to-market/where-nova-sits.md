# Where Nova Sits

## Status

Go-to-market integration-path framework  
Reviewer-facing placement document  
Non-authority documentation layer

## Purpose

This document explains where Sharpe Nova OS sits in an institutional workflow.

Nova is called after an action is prepared and before local authority decides.

Nova does not execute the action.

Nova does not approve, deny, authorize, block, route, settle, sign, process payments, manage wallets, perform treasury management, perform compliance review, perform audit reporting, optimize portfolios, or replace local authority.

Nova structures governed review context before local authority acts.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

All integration-path language must preserve this boundary.

---

## Placement in the Workflow

Nova sits between prepared action and local authority review.

```text
Agent / Local System
prepares intended action
        |
        v
Nova
structures governed review context
        |
        v
Local Authority
reviews and decides
        |
        v
Execution Systems Outside Nova
wallet / custodian / rail / settlement / TMS / venue
        |
        v
Nova Chronology
preserves accepted governance memory
```

Nova is upstream of execution systems.

Nova is downstream of action preparation.

Nova is not the execution layer.

---

## What Calls Nova

Nova may be called by a local system, workflow, operator process, or agent-prepared action pipeline seeking governed review context before local authority acts.

Examples:

* treasury workflow preparing a liquidity action
* agent-prepared stablecoin movement proposal
* custody-adjacent workflow preparing transfer context
* fund operations process preparing exposure adjustment context
* tokenized asset workflow preparing settlement review context
* local system assembling evidence before a decision queue

These are review-context examples.

They are not claims of production deployment.

---

## What Nova Returns

Nova returns governed review context.

A review-context packet may include:

```yaml
review_context_packet:
  prepared_action:
    purpose: identifies the action being prepared for review

  source_context:
    purpose: shows what sources are present, missing, stale, conflicted, or reconciled

  chronology_context:
    purpose: identifies relevant accepted decision-state lineage

  constraint_context:
    purpose: surfaces active constraint pressure or review-relevant conditions

  authority_scope:
    purpose: clarifies who decides and what Nova does not decide

  proof_metadata:
    purpose: supports reconstruction, replay, or inspection where applicable

  exception_visibility:
    purpose: surfaces items that require attention before local review
```

The packet is not an approval.

The packet is not an execution instruction.

The packet is not a payment message.

The packet is not a compliance determination.

The packet is governed review context.

---

## Who Reads It

The review-context packet may be read by:

* local authority
* treasury operations
* fund operations
* digital asset operations
* custody operations
* risk or governance teams
* authorized internal reviewers
* downstream systems controlled by the institution

The institution remains responsible for its decision process.

Nova does not replace local authority.

---

## What Decision It Supports

Nova supports the review of an agent-prepared or system-prepared capital action before local authority acts.

The relevant question is not:

```text
Should Nova approve this action?
```

The relevant question is:

```text
Does local authority have governed review context before deciding whether and how to proceed through systems outside Nova?
```

---

## What Happens Outside Nova

Execution happens outside Nova.

Examples of systems outside Nova:

* wallets
* custodians
* payment rails
* stablecoin settlement systems
* treasury management systems
* exchanges
* execution venues
* signing infrastructure
* compliance systems
* audit systems
* ERP systems
* internal approval tools

Nova may provide review context before these systems are used.

Nova does not operate them.

---

## First Adoption Path

The recommended first adoption path is staged.

### Stage 1 - Offline Review Packet

A sample or historical agent-prepared action is provided.

Nova structures a review-context packet.

No live integration.

No execution.

No authority transfer.

Purpose:

```text
Can the institution understand the value of structured pre-action context?
```

### Stage 2 - Shadow Pre-Action Review

Nova runs beside a real or simulated workflow.

The existing process remains unchanged.

Nova structures review context before local authority acts.

Execution still happens outside Nova.

Purpose:

```text
Does Nova improve reviewability, source clarity, chronology, exception visibility, and authority-scope recognition?
```

### Stage 3 - Required Review-Context Checkpoint

The institution may decide that certain workflows should not reach local authority without governed review context.

Use this phrasing:

```text
No governed review context, no local decision.
```

Do not use:

```text
No Nova, no execution.
```

Nova remains non-authority.

---

## What Nova Is Not

Nova is not:

* a payment rail
* a wallet
* a signing tool
* a custodian
* a settlement layer
* an exchange
* an execution venue
* a treasury management system
* a compliance product
* an audit system
* an approval engine
* an authorization layer
* an agent supervisor
* a trading system
* a signal engine
* a portfolio optimizer

Nova structures governed review context before local authority acts.

---

## Buyer Clarity

The buyer should understand Nova as:

```text
A pre-action review-context layer for programmable capital workflows.
```

The buyer should not understand Nova as:

```text
A system that approves, moves, controls, or executes capital.
```

---

## Final Compression

```text
Nova is called after an action is prepared and before local authority decides.

Agent prepares the action.
Nova structures the review context.
Local authority decides.
Execution happens elsewhere.
Chronology preserves the institution's governance memory.
```

---

## Related GTM Context

- [GTM Comprehension Test Protocol](gtm-comprehension-test-protocol.md)
