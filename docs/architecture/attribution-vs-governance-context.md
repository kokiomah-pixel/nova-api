# Attribution vs Governance Context

## Status

Architecture boundary note  
Category hardening artifact  
Not product expansion  
Not onchain analytics positioning  
Not attribution product claim  
Not production claim  
Not adoption evidence  
Not market validation  
Not buyer validation

## Purpose

This document clarifies the difference between transaction records, attribution layers, governed pre-action review context, and institution-owned governance chronology.

Sharpe Nova OS should not be confused with an onchain analytics platform, wallet-labeling system, transaction attribution layer, stablecoin monitoring product, compliance tool, audit system, wallet control layer, payment rail, or execution system.

## Core Distinction

The chain records movement.

Attribution explains activity.

Nova preserves governed review context before capital moves.

A sharper internal distinction:

```text
Onchain history is not governance chronology.
```

## Layer Model

Institutional programmable-capital systems may require multiple context layers.

```yaml
context_layers:
  level_1_transaction_record:
    question_answered: "What moved?"
    examples:
      - transaction hash
      - asset
      - amount
      - timestamp
      - wallet addresses
      - settlement path
    nova_layer: false

  level_2_attribution_layer:
    question_answered: "Who, what, or where may be behind the activity?"
    examples:
      - entity labeling
      - geography
      - wallet clustering
      - use-case classification
      - corridor analysis
      - counterparty inference
    nova_layer: false

  level_3_explainability_layer:
    question_answered: "What does the activity appear to represent?"
    examples:
      - stablecoin flow interpretation
      - tokenized-asset activity classification
      - market or corridor context
      - activity segmentation
    nova_layer: adjacent_input

  level_4_governed_pre_action_review_context:
    question_answered: "What must local authority review before deciding?"
    examples:
      - prepared action intent
      - authority path
      - source context
      - constraint pressure
      - attribution inputs if available
      - proof metadata
      - review completeness
      - exception visibility
    nova_layer: true

  level_5_institution_owned_governance_chronology:
    question_answered: "What governance memory should persist across actions, agents, rails, and custodians?"
    examples:
      - accepted decision-state lineage
      - prior exceptions
      - prior non-actions
      - prior source-state stress
      - prior boundary-language drift
      - accepted Reflex Memory
    nova_layer: true
```

## Why This Matters

Stablecoin and tokenized-asset systems can make movement faster and more visible.

Onchain data can show that value moved.

Attribution can help explain who or what may be connected to that movement.

But neither raw transaction history nor attribution is the same as governance readiness.

Before local authority decides, the institution still needs governed review context.

That context may include:

* prepared action intent
* asset and rail context
* wallet or custody state
* counterparty or corridor context
* attribution inputs if available
* source-state classification
* constraint pressure
* proof references
* prior similar actions
* prior non-actions
* prior exceptions
* relevant chronology
* accepted Reflex Memory
* authority path
* review completeness

## Nova's Layer

Nova sits before local authority decides.

Nova structures governed review context around a prepared action.

Nova may use attribution data as an input if available.

Nova does not produce attribution as its core function.

Nova does not label wallets.

Nova does not explain all stablecoin activity.

Nova does not monitor all onchain movement.

Nova does not decide whether capital should move.

Nova does not execute.

## Complementary Input Relationship

Attribution infrastructure can be complementary to Nova.

Example flow:

```text
Agent prepares stablecoin treasury action.
v
Nova receives prepared-action package.
v
Attribution data may inform wallet, corridor, entity, or use-case context.
v
Nova retrieves relevant governance chronology.
v
Nova surfaces constraint pressure, source-state limitations, proof gaps, prior stress, and review readiness.
v
Local authority decides.
v
Execution happens elsewhere.
v
Accepted records may enter chronology.
```

Attribution improves the context available to Nova.

It does not replace governance chronology.

## Safe Language

Use:

```text
Onchain attribution can inform review context.
```

Use:

```text
Nova structures governed pre-action context.
```

Use:

```text
The chain records movement. Attribution explains activity. Nova preserves governance chronology before capital moves.
```

Use:

```text
Volume is not attribution. Attribution is not review readiness. Review readiness is not authority.
```

Use:

```text
Local authority decides. Execution happens elsewhere.
```

## Unsafe Language

Do not say:

```text
Nova is an onchain analytics platform.
```

Do not say:

```text
Nova competes with attribution platforms.
```

Do not say:

```text
Nova provides stablecoin attribution.
```

Do not say:

```text
Nova labels wallets.
```

Do not say:

```text
Nova explains all stablecoin activity.
```

Do not say:

```text
Nova is the command center for onchain finance.
```

Do not say:

```text
Nova has authority over stablecoin movement.
```

Do not say:

```text
Nova controls tokenized-asset flows.
```

## Review-Readiness Distinction

Attribution may improve what is known about an activity.

Review readiness requires more.

A prepared action becomes review-ready only when the institution can inspect the governed context around that action before deciding.

That includes:

* action intent
* source context
* authority scope
* constraint pressure
* proof metadata
* chronology
* Reflex Memory context where applicable
* exception visibility
* local authority boundary

## Relationship to Existing Architecture

This boundary note supports:

* `docs/architecture/governed-context-flow.md`
* `docs/architecture/review-context-loop.md`
* `docs/architecture/pre-action-context-contract.md`
* `docs/governance/reflex-memory-specification.md`
* `docs/validation/technical-evidence-map.md`

It does not replace those documents.

It clarifies the boundary between attribution inputs and governance context.

## Final Rule

The chain records movement.

Attribution explains activity.

Nova structures governed review context before local authority decides.

Execution happens elsewhere.
