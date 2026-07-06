# Governed Context Flow

## Status

Architecture / integration-path artifact  
Doctrine-candidate support  
Not product expansion  
Not production claim  
Not adoption evidence  
Not market validation  
Not buyer validation

## Purpose

This document explains how Sharpe Nova OS structures governed context around agent-prepared financial actions before local authority decides.

The goal is to make the integration path legible:

```text
What context exists before Nova?
What does Nova require?
What does Nova structure?
What does Nova emit?
Who receives it?
What record may be preserved?
What can become Reflex Memory?
What does Nova never do?
```

## Core Principle

Prepared action is not review readiness.

Agent capability is not governance capacity.

Context availability is not context discipline.

A financial action may be prepared by an agent, but that does not mean the action is ready for local authority review.

Nova helps structure the governed context needed before local authority acts.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## Context Layers

Nova's context environment can be understood through three layers:

```text
Doctrine Context
Institution Context
Prepared-Action Context
```

These layers do not give Nova authority.

They define the governed review environment around a prepared action.

---

## 1. Doctrine Context

Doctrine Context includes durable boundaries that should not change unless explicitly governed.

Examples:

* Nova does not execute.
* Nova does not approve.
* Nova does not authorize.
* Nova does not replace local authority.
* Memory conditions review.
* Authority remains local.
* Execution happens elsewhere.
* Reflex Memory informs review posture only.
* Accepted governance memory may condition future review context.

Doctrine Context prevents Nova from drifting into execution, approval, compliance determination, audit reporting, wallet control, payment routing, settlement, signing, or agent supervision.

---

## 2. Institution Context

Institution Context belongs to the institution.

Examples:

* authority structure
* review thresholds
* escalation rules
* risk posture
* asset permissions
* jurisdictional posture
* workflow constraints
* governance chronology
* accepted Reflex Memory
* source-state requirements
* proof-reference expectations

Nova may structure this context for review.

Nova does not own the institution's authority.

Nova does not replace the institution's decision process.

---

## 3. Prepared-Action Context

Prepared-Action Context belongs to the current action package.

Examples:

* agent intent
* asset
* amount
* venue or destination
* rail dependency
* counterparty
* custodian dependency
* settlement path
* wallet or account reference
* source context
* proof metadata
* constraint pressure
* similar prior reviewed actions
* required authority path
* review readiness state

Nova may use this context to form governed review context.

Nova does not execute the prepared action.

---

## Governed Context Stack

Nova's capital-review context stack may include:

```yaml
nova_context_stack:
  chronology: prior accepted decision-state lineage
  doctrine: durable rules and boundaries
  precedents: prior examples of similar reviewed actions
  governance_records: structured records from prior review cycles
  previous_prepared_actions: actions proposed, paused, narrowed, escalated, or declined
  telemetry_and_constraints: current environmental and rule pressure
  review_state: where this action stands before local authority
```

This stack helps local authority review the prepared action with more complete governed context.

It does not make Nova the authority.

---

## Context Flow

A bounded Nova context flow can be described as:

```text
1. Agent prepares a financial action package.
2. Nova receives the prepared-action package and relevant context inputs.
3. Nova checks whether required review-context fields are present.
4. Nova retrieves or references relevant chronology.
5. Nova surfaces constraint pressure, source-state limitations, contradiction, and prior governance stress.
6. Nova emits governed review context.
7. Local authority reviews and decides.
8. Execution happens elsewhere.
9. Accepted records may enter chronology.
10. Accepted governance memory may later condition review posture as Reflex Memory.
```

This flow is pre-action and non-authority.

It does not approve, deny, authorize, route, settle, sign, or execute.

---

## What Nova Receives

Nova may receive:

* prepared-action package
* source context
* authority context
* constraint context
* chronology references
* proof metadata
* exception context
* Reflex Memory references
* review requirements

Receipt of context does not create authority.

---

## What Nova Structures

Nova structures:

* action intent
* source-state clarity
* authority scope
* constraint pressure
* chronology relevance
* proof-reference visibility
* exception visibility
* review readiness
* Reflex Memory review posture
* local authority boundary

Structuring context is not decision-making.

---

## What Nova Emits

Nova emits governed review context.

The output may include:

* prepared action summary
* source context
* authority context
* constraint context
* chronology references
* Reflex Memory context
* proof metadata
* exception visibility
* review readiness state
* non-authority statement

Nova's output is not:

* approval
* denial
* authorization
* execution instruction
* payment routing
* settlement instruction
* signing instruction
* wallet control
* compliance determination
* audit report
* agent supervision

---

## What May Be Preserved

After review, accepted records may enter chronology.

Chronology preserves decision-state lineage.

Chronology is not raw logging.

Chronology is not automatic memory.

Chronology is not execution history by itself.

Accepted chronology events may later produce Reflex Memory candidates.

Only accepted governance memory may condition future review posture.

---

## Reflex Memory Relationship

Reflex Memory is accepted governance memory derived from reviewed chronology events.

It may condition future review context by surfacing prior governance stress, source-state deterioration, boundary risk, proof-reference gaps, or recurring review-context patterns.

Reflex Memory does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, control wallets, or replace local authority.

Safe compression:

```text
Memory conditions review.
Authority remains local.
Execution happens elsewhere.
```

---

## Context Failure Modes

Nova exists because context failures can occur before capital moves.

Examples:

* prepared action lacks source context
* authority path is unclear
* constraint pressure is not visible
* proof references are incomplete
* prior governance stress is not surfaced
* stale context is reused
* review completeness is assumed but not established
* agent context is mistaken for governance context
* available information is not structured into review context

The deeper failure is not always the agent, rail, custodian, or workflow.

The failure may be the governed context environment around the action.

---

## Unsafe Interpretations

Do not interpret this document to mean:

* Nova is a generic AI context operating system.
* Nova is an enterprise knowledge system.
* Nova owns institutional memory.
* Nova controls financial workflows.
* Nova runs agent loops.
* Nova approves or denies actions.
* Nova has capital-movement authority.
* Nova performs compliance review.
* Nova produces audit reports.
* Nova controls wallets.
* Nova routes payments.
* Nova settles transactions.
* Nova signs transactions.
* Nova supervises agents.
* Nova replaces local authority.

---

## Safe Interpretation

Use:

```text
Nova structures governed context before local authority decides.
```

Use:

```text
Prepared action is not review readiness.
```

Use:

```text
Context availability is not context discipline.
```

Use:

```text
Agent context is not governance context.
```

Use:

```text
Memory conditions review.
Authority remains local.
Execution happens elsewhere.
```

## Relationship to Existing Architecture

This artifact supports:

* `docs/architecture/pre-action-context-contract.md`
* `docs/architecture/review-context-loop.md`
* `examples/agent_prepared_action/`
* `docs/governance/reflex-memory-specification.md`
* `docs/governance/reflex-memory-v0-1-fixture.md`
* `docs/validation/technical-evidence-map.md`

It does not replace those documents.

It explains how the context flows through them.

## Related Boundary Note

For the distinction between onchain transaction records, attribution layers, governed pre-action review context, and governance chronology, see:

* `docs/architecture/attribution-vs-governance-context.md`

## Related Integration Boundary

For future agent-framework adapter boundaries, see:

* `docs/architecture/agent-framework-adapter-contract.md`

## Related Strategy Boundary

For the commercial boundary around Nova's non-authority stance, see:

* `docs/strategy/non-authority-commercial-boundary.md`

## Related Governance Standards

For review-readiness conditions and source-state classification, see:

* `docs/governance/review-completeness-standard.md`
* `docs/governance/source-state-taxonomy.md`

## Final Rule

Agent-prepared action is not enough.

Governed context must be structured before local authority acts.

Nova structures review context.

Local authority decides.

Execution happens elsewhere.
