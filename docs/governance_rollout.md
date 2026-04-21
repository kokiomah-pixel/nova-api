# Governance Rollout

Sharpe Nova OS exposes governance as part of the control-plane interface.

## Rollout Logic

Governance layers may be activated in phases, but the interpretation boundary remains stable:

- Nova is still a pre-execution decision layer
- the API remains authoritative
- refusal states remain binding

## Active-Layer Discipline

Governance profiles can expose layers such as:

- temporal governance
- loop integrity
- telemetry integrity
- system state
- permission budgeting
- halt release governance

These layers should be understood as control surfaces, not as trading features.

## Operational Reading

Use governance rollout to understand which control surfaces are active for a key or environment, not to infer a broader system identity.

Governance still resolves into the same authoritative interaction:

- submit the decision to `/v1/context`
- bind behavior to `decision_status`
- retrieve `/v1/proof/{decision_id}` for the auditable outcome
