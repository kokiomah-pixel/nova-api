# Model Independence and Context Continuity Standard

## Status

Internal operating resilience standard
Model-provider independence discipline
Not model equivalence claim
Not production failover certification
Not autonomous continuity

## Purpose

Sharpe Nova OS may use a frontier model as a reasoning, synthesis, drafting, and review engine.

Nova's coherence must not depend on:

- one model version
- one chat window
- one context window
- one memory implementation
- one provider feature
- one assistant's unaudited recollection

The model is an engine inside the operating loop.

The OS must preserve its own durable state.

## Core Rule

```text
The model may assist reasoning.

Canonical artifacts preserve the system.

The Architect retains authority.
```

## Model Layer

The model may:

- synthesize information
- compare documents
- identify contradictions
- draft implementation packets
- classify possible risks
- generate adversarial questions
- assist state reconciliation
- summarize chronology candidates

The model may not automatically:

- create doctrine
- accept chronology
- mutate Reflex Memory
- change authority boundaries
- authorize production changes
- create commercial commitments
- override current accepted state

## Durable State Hierarchy

```yaml
durable_state:
  canonical_doctrine:
    location: repository_or_accepted_governance_archive

  accepted_chronology:
    location: governed_chronology_store

  current_operating_state:
    location: current_state_record

  implementation_state:
    location: verified_repository_commits

  temporary_context:
    location: chat_or_model_session
    authority: none
```

## Context Handoff Requirement

Before moving between model sessions or chat windows, preserve:

- current phase
- active command
- canonical boundary
- accepted recent commits
- open decisions
- quiet watch items
- superseded state
- source limitations
- current non-claims

Use:

```text
docs/operations/templates/decision-state-handoff.md
```

## Model Upgrade Rule

When the underlying model changes, do not assume the OS improved automatically.

Evaluate:

```yaml
model_upgrade_review:
  reasoning_consistency:
  context_reconciliation:
  doctrine_adherence:
  implementation_precision:
  hallucination_or_overclaim_risk:
  tool_behavior:
  continuity_behavior:
```

A stronger model may improve throughput.

It does not change accepted Nova doctrine.

## Cross-Model Review

For material strategic questions, Jarvis-Nova may use an independent adversarial pass when available.

The purpose is not consensus.

The purpose is to expose:

- missed assumptions
- category drift
- confidence inflation
- model-specific framing bias
- stale context dependence

## Failure Handling

If a model session conflicts with canonical state:

```yaml
failure_handling:
  trust_session_memory: false
  inspect_canonical_sources: true
  create_reconciliation_record: true
  escalate_if_directional: true
```

## Final Rule

The intelligence engine may change.

Nova's accepted operating state must remain reconstructable.
