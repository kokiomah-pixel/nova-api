# Adjacent Layer Map

## Status

Neutral architecture map
Bounded integration support
Not a competitor comparison
Not a control-plane claim
Not production integration

## Purpose

This map locates Sharpe Nova OS among the systems involved in an agent-prepared financial workflow. It describes functional boundaries without ranking vendors or implying that Nova replaces another layer.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Adjacent systems determine how agents operate, who may act, and how value can move.

Nova structures and evaluates the institution-defined review context presented to local authority before it decides.

## Layer Map

| Layer | Primary question | Typical responsibilities | Relationship to Nova |
|---|---|---|---|
| Agent runtime | How does the agent operate? | Sessions, tools, memory, scheduling, isolation | Upstream preparation |
| Identity and authorization | Who may act and within what limits? | Identity, credentials, delegation, permissions | Review-context input |
| Wallet and payment infrastructure | How can value move? | Signing, custody, routing, settlement | Downstream execution |
| Observability and audit systems | What did the system record? | Logs, traces, events, metrics | Evidence source |
| Sharpe Nova OS | What must be assembled and surfaced for institutional review? | Evidence, constraints, contradictions, chronology, temporal context | Pre-execution decision context |
| Local authority | Should the institution proceed? | Review, decision, escalation, refusal | Retains final authority |

Adjacent systems may place a person into a workflow.

Nova structures what that person must be able to review.

## Boundary Notes

- Agent runtimes prepare actions; Nova does not control agents, tools, sessions, or schedules.
- Identity and authorization systems establish identity, credentials, delegation, and permissions; Nova receives relevant state as review-context input and does not enforce it.
- Wallet and payment infrastructure signs, routes, settles, or otherwise executes outside Nova.
- Observability and audit systems can supply evidence; Nova does not replace their logging, tracing, assurance, compliance, or audit capabilities.
- Nova structures evidence, constraints, contradictions, chronology, and temporal context; it does not determine whether capital should move.
- Local authority retains the institutional decision.

## Disclaimer

This map describes functional boundaries.

It does not claim that adjacent platforms lack governance, evidence, observability, policy, or approval capabilities. It explains the specific institutional decision-context layer Nova is designed to occupy.

Nova does not replace any adjacent layer.

## Final Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
