# Integration Entry

Sharpe Nova OS integrates through a machine-readable API contract.

## Integration Pattern

1. Submit a decision candidate to `/v1/context`.
2. Parse `decision_status`, `decision_id`, and `system_state`.
3. Retrieve `/v1/proof/{decision_id}` when you need the proof-backed audit surface.
4. Feed returned context into local governance before any execution step.

## Required Binding

- `ALLOW`: inspect and decide locally
- `CONSTRAIN`: review returned limits before acting
- `DELAY`: consider holding and re-evaluating later
- `DENY`: consider refusing locally
- `HALT`: consider suspending local downstream action

`decision_status` is non-authority context. Supporting fields explain why the state was returned; they do not create permission.

## Integration Boundary

No integration should reinterpret Nova output as execution authority.

The response contract is an audit and review surface, and proof fields should be read from the proof endpoint rather than inferred from internal traces.

The correct integration posture is:

```text
Decision Proposed -> Nova -> Pre-Action Context -> Local Decision
```

The local system remains responsible for any execution, delay, escalation, or cancellation.
