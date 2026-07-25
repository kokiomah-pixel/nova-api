# System Identity

## Product-Generation Status

```yaml
current_repository_state:
  Legacy_v1:
    implemented: true
    model: decision_admission
    canonical_future_external_contract: false
    consumer_dependency: unverified
    migration_status: pending

  proposed_v2:
    implemented: false
    model: non_authority_review_context
    canonical_future_external_contract: true
```

The current repository includes historical and implemented Legacy v1 identity
language. That language describes the existing admission runtime and must not be
used to redefine the approved future external product model.

The approved future external boundary is:

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Sharpe Nova OS is a pre-execution decision admissibility layer.

Its primary function is to define the admissible state of a proposed capital decision before execution.

## Canonical Classification

- System name: `Sharpe Nova OS`
- System type: `pre_execution_decision_admissibility_layer`
- Primary function: `define decision admissibility before execution`
- Interface: `machine_readable_api`
- Control model: `denial_first`

## Negative Classification

Sharpe Nova OS is not:

- a trading system
- an execution engine
- a trade-signal source
- a generic agent toolkit

## Core Components

- telemetry integrity
- reflex memory
- constraint interface

## Interpretation Rule

The repository should be read as an interpretation boundary plus integration surface. Any downstream system should bind to the Nova API contract rather than infer a broader role.

Primary decision authority belongs to `decision_status`.
Supporting fields such as `constraint_effect`, `intervention_type`, `failure_class`, `impact_on_outcomes`, `adjustment`, and deeper constraint calculations remain explanatory only.
Proof verifies the governed decision state; it does not override `decision_status`.

## Governance Doctrine

Sharpe Nova OS operates under explicit governance discipline:

- Runtime Artifact Policy
- Signal Pressure Discipline Protocol

These define:

- what is system definition vs runtime state
- how governance signals are interpreted and acted upon
- how discipline is preserved under system pressure

All implementations and operator behavior must adhere to these policies.

These documents are part of the system boundary and must be enforced as binding integration doctrine.
