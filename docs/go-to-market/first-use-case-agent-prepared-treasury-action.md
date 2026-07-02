# First Use Case: Agent-Prepared Treasury Action

## Status

Go-to-market first-use-case framework  
Reviewer-facing scenario document  
Non-authority documentation layer

## Purpose

This document defines the first recommended go-to-market use case for Sharpe Nova OS:

```text
agent-prepared treasury action review
```

The use case is designed to make Nova's integration path concrete without making Nova a treasury system, payment rail, wallet, signing tool, approval engine, execution layer, compliance product, audit system, trading system, or portfolio optimizer.

---

## Core Scenario

An agent prepares a treasury-related capital action.

The action may involve:

* stablecoin movement context
* liquidity adjustment context
* venue or custody dependency
* collateral review context
* counterparty exposure context
* jurisdictional context
* settlement assumption context
* source-state uncertainty
* prior override or non-action history
* authority-scope requirements

Before local authority reviews the action, Nova structures the governed review context.

Local authority decides.

Execution happens outside Nova.

---

## Why This Use Case Comes First

This use case is concrete enough for the market to understand.

It sits near current market pressure around:

* agentic finance
* machine-prepared financial actions
* programmable capital
* stablecoins
* custody
* tokenized assets
* treasury workflows
* payment-adjacent systems
* institutional review obligations

But it remains upstream of execution.

Nova does not move funds.

Nova does not approve the action.

Nova does not route, settle, sign, or process payment.

Nova structures the review context before local authority acts.

---

## Problem

Agent-prepared capital actions can move faster than institutions can assemble governed review context.

A prepared action may arrive with:

* structured instruction
* supporting data
* agent-generated rationale
* source references
* proposed path
* expected outcome

But local authority still needs to know:

* what sources were used
* what sources were missing
* whether sources conflicted
* whether relevant chronology exists
* what constraints were active
* whether prior non-actions or overrides matter
* what authority boundary applies
* whether the review context can be reconstructed

The gap is not only action preparation.

The gap is review-context readiness.

---

## Nova's Role

Nova structures governed review context around the agent-prepared treasury action.

Nova may surface:

* source-context clarity
* chronology context
* constraint pressure
* proof metadata
* classification stability
* authority-scope recognition
* exception visibility
* relevant prior accepted decision-state lineage

Nova does not decide whether the treasury action should happen.

Nova does not execute the treasury action.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

This boundary is mandatory.

---

## First Test: Offline Review Packet

The first test should be offline.

Input:

```yaml
offline_input:
  prepared_action: sample_or_historical_agent_prepared_treasury_action
  source_context: attached_or_referenced_sources
  known_constraints: provided_if_available
  prior_records: provided_if_available
```

Nova output:

```yaml
offline_output:
  review_context_packet:
    prepared_action_summary:
    source_context:
    chronology_context:
    constraint_context:
    authority_scope:
    proof_metadata:
    exception_visibility:
    source_limitations:
```

Purpose:

```text
Can a reviewer understand the action better after seeing Nova-structured review context?
```

No live integration.

No execution.

No authority transfer.

No production claim.

---

## Second Test: Shadow Pre-Action Review

The second test may run beside an existing process.

Input:

```yaml
shadow_review_input:
  current_or_simulated_agent_prepared_action:
  local_review_process:
  available_sources:
  known_constraints:
```

Nova output:

```yaml
shadow_review_output:
  review_context_packet:
  source_limitations:
  authority_scope:
  chronology_candidate:
  exception_visibility:
```

Purpose:

```text
Does Nova improve reviewability before local authority acts without changing the existing execution process?
```

Execution remains outside Nova.

---

## Dependency Threshold

The first meaningful dependency threshold is not:

```text
No Nova, no execution.
```

The correct threshold is:

```text
No governed review context, no local decision.
```

This means the institution may decide that certain workflows should not reach local authority until a governed review-context packet exists.

Nova remains non-authority.

---

## Buyer Value

The buyer value is:

* better reviewability
* clearer source context
* preserved chronology
* visible source limitations
* authority-scope clarity
* exception visibility
* proof/replay support where applicable
* institution-owned governance memory
* reduced governance-context rot

This is not an investment performance claim.

This is not an automation claim.

This is not an approval claim.

This is not a compliance or audit claim.

---

## Early Buyer Profile

This use case may be relevant to teams operating near programmable capital workflows, including:

* treasury operations
* digital asset operations
* stablecoin treasury
* fund operations
* allocator operations
* custody operations
* tokenized asset operations
* governance or risk teams reviewing agent-prepared financial actions

The shared pain:

```text
Actions are being prepared faster than review context can be assembled.
```

---

## GTM Proof Questions

Use these questions to test whether the use case is legible.

### Comprehension

* Can the reviewer explain where Nova sits?
* Can the reviewer distinguish Nova from an approval system?
* Can the reviewer distinguish Nova from a payment rail, wallet, custodian, signing tool, or treasury system?
* Can the reviewer explain that execution happens outside Nova?

### Value

* Does the review-context packet make the prepared action easier to review?
* Does it surface missing, stale, conflicted, or reconciled sources?
* Does chronology improve understanding?
* Does authority-scope recognition reduce ambiguity?
* Does exception visibility improve the review process?

### Adoption Shape

* Would the team want this before certain actions reach local authority?
* Which workflows would require this type of packet?
* What system or process would call Nova?
* Who would read the packet?
* What would count as sufficient review context?

---

## Safe Public Language

Use:

```text
Nova is called after an action is prepared and before local authority decides.
```

Use:

```text
Nova structures governed review context around agent-prepared treasury actions before local authority acts.
```

Use:

```text
No governed review context, no local decision.
```

Use:

```text
Execution happens outside Nova.
```

---

## Unsafe Public Language

Do not say:

* Nova approves treasury actions
* Nova denies treasury actions
* Nova authorizes payments
* Nova blocks execution
* Nova routes transactions
* Nova settles stablecoins
* Nova signs transactions
* Nova manages wallets
* Nova supervises agents
* Nova performs treasury management
* Nova performs compliance review
* Nova performs audit reporting
* Nova replaces local authority
* No Nova, no execution

---

## Final Compression

```text
Agent-prepared treasury actions need governed review context before local authority acts.

Nova is called after the action is prepared and before the institution decides.

Execution happens elsewhere.

Chronology preserves the institution's governance memory.
```
