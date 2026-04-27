# Field Hierarchy

## Primary Decision Authority

- decision_status

## Proof Verification Fields

- constraint_effect
- intervention_type
- failure_class

These fields verify and explain the governed state. They do not override `decision_status`.

## Supporting Fields

- impact_on_outcomes
- adjustment
- internal constraint details

Integrations must bind execution behavior to `decision_status`.

Supporting fields may inform adjustment but must not define admission.

## Interpretation Rule

```json
{ "decision_status": "DENY" }
```

means:

> **This decision is not admissible. Execution must not proceed.**

It is not a signal to reinterpret.
