# Telemetry Semantics Update Summary

Overview

This pass updates documentation and example payloads to reflect telemetry language aligned with environmental governance doctrine. No schema key renames were performed.

Preferred telemetry vocabulary

- coordination_state (descriptive label)
- constraint_pressure (low/medium/high)
- drift_score (0.0 - 1.0)
- pulse_id / pulse_timestamp
- fragmentation_state

Example migration guidance

Original example payload (docs only):

```json
{
  "allowed": true,
  "reason": "risk_limits",
  "signal_score": 0.82
}
```

Documentation-framed guidance (keys preserved in schema unless a migration is approved):

```json
{
  "allowed": true,                        // schema key retained for continuity
  "reason": "risk_limits",              // description updated: reason pertains to constraint analysis
  "signal_score": 0.82                    // described as a derivative telemetry metric (drift_score equivalent)
}
```

Recommendation

- For any external migration of telemetry keys, adopt a staged aliasing strategy and coordinate with integrators. Documented in unresolved-risks-and-actions.md.
