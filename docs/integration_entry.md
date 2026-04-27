# Integration Entry

Sharpe Nova OS integrates through a machine-readable API contract.

## Integration Pattern

1. Submit a decision candidate to `/v1/context`.
2. Parse `decision_status`, `decision_id`, and `system_state`.
3. Retrieve `/v1/proof/{decision_id}` when you need the authoritative audit surface.
4. Bind downstream execution behavior to the returned decision state before any execution step.

## Required Binding

- `ALLOW`: proceed
- `CONSTRAIN`: proceed only with returned limits
- `DELAY`: hold and re-evaluate later
- `DENY`: refuse
- `HALT`: suspend downstream admission

`decision_status` is authoritative. Supporting fields explain why the state was returned; they do not create alternate permission.

## Integration Boundary

No integration should reinterpret Nova output as a bypassable suggestion.

The response contract is authoritative, and proof fields should be read from the proof endpoint rather than inferred from internal traces.

The correct integration posture is:

```text
Decision Proposed -> Nova -> Decision Admitted -> Execution
```

If the decision is not admitted, execution does not occur.
