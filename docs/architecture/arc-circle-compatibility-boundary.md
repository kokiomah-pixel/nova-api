---
record_type: architecture_boundary_hypothesis
subject: Arc_Circle_compatibility
evidence_state: externally_observed
review_state: governed_watch
authority_effect: none
execution_effect: none
production_effect: none
accepted_state_effect: none
chronology_effect: none
Reflex_Memory_effect: none
runtime_implemented: false
external_integration: false
---

# Arc / Circle Compatibility Boundary

## Status

This memo is a non-authoritative architecture hypothesis attached to the
`ARC_AGENTIC_FINANCE_2026` governed watch. It documents how Arc or Circle could
eventually relate to Sharpe Nova OS without moving Nova into custody,
authorization, or execution. It is not a product requirement, roadmap
decision, integration plan, accepted state, or runtime design.

## Canonical boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Sharpe Nova OS remains a chain-agnostic pre-execution decision-context layer.
Arc remains an external economic execution and settlement environment.

## Possible future relationship

```text
Arc / Circle / treasury evidence
            ↓
bounded Nova source adapter
            ↓
Sharpe Nova OS constructs review context
            ↓
local institutional authority
            ↓
Circle wallet / Arc / external execution
            ↓
settlement evidence
            ↓
separately governed chronology retention, if authorized
            ↓
possible later governed learning, if separately accepted
```

Every arrow is conceptual and future-facing. No adapter, connection,
chronology write, or learning transition is implemented or authorized here.

```yaml
possible_future_roles_for_Arc_or_Circle:
  - telemetry_source
  - execution_environment
  - settlement_evidence_source
  - transaction_outcome_source

Nova_role:
  - bounded_review_context
  - evidence_state_preservation
  - temporal_context
  - constraint_context
  - decision_lineage
  - chronology
  - governed_Reflex_Memory_process

prohibited_Nova_roles:
  - wallet_custody
  - private_key_control
  - transaction_signing
  - transaction_broadcasting
  - settlement
  - execution
  - transaction_approval
  - transaction_denial
  - payment_authorization
  - Arc_validator_authority
  - Circle_wallet_policy_control
```

The possible external roles are classification hypotheses. They do not
authorize Nova to ingest telemetry or settlement evidence. Nova chronology
remains governed and selective; external settlement never enters chronology
automatically. Reflex Memory remains a separately accepted governance-memory
process and never mutates from market or settlement evidence automatically.

## Institutional decision-object principle

> Nova should govern institutional decision objects, not blockchain
> transaction objects.

For example:

```text
Institutional decision:
Rebalance $5M of treasury liquidity

Technical consequences:
    transfer
    bridge
    FX conversion
    contract interaction
    settlement

Multiple transactions.
One institutional decision.
```

This is a design principle and hypothesis, not current implemented runtime
behavior. It avoids coupling decision lineage to a specific chain, wallet,
rail, or transaction schema. Transaction and settlement evidence could later
be referenced as consequences of a decision object, but they do not become the
institutional decision or carry its authority.

## Non-authority assertions

```yaml
boundary_assertions:
  Nova_executes: false
  Nova_signs: false
  Nova_controls_wallet: false
  local_authority_decides: true
  external_system_executes: true
```

An external wallet policy, valid signature, successful broadcast, or settled
transaction does not establish that Nova approved, denied, or authorized an
action. A Nova review context does not instruct Arc or Circle to execute.

This memo creates no Arc API client, RPC client, Circle API client, wallet,
signer, transaction path, event listener, indexer, x402 capability, live
telemetry source, scheduled monitor, production configuration, Legacy v1
change, or target-v2 runtime behavior.
