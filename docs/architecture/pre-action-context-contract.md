# Pre-Action Context Contract
## Sharpe Nova OS

## Purpose

This contract describes what autonomous systems consume from Nova before action. It is a reviewer-facing interface artifact, not a runtime schema migration.

Nova emits environmental state before execution; it does not decide whether execution occurs.

## What Pre-Action Context Means

Pre-action context is governance information produced before a local operator, agent, or orchestration system decides how to proceed. It can describe constraint pressure, timing pressure, classification state, source segmentation, and proof reproducibility.

## What Nova Emits

Nova may emit:

- canonical governance identity
- environmental state
- classification path
- reproducibility metadata
- source segmentation
- conditioning guidance
- Reflex Memory chronology references
- non-authority boundary language

## What Nova Does Not Emit

Nova does not emit execution commands, trade recommendations, capital allocation guidance, custody instructions, or local decision authority.

## Input Shape

A pre-action context request describes an intended action and the surrounding environment. The input should be treated as context for environmental classification, not as a request for permission.

## Output Shape

A pre-action context response returns environmental state and reproducibility metadata. The consuming system remains responsible for all local governance and execution decisions.

## Environmental State Fields

Common environmental fields may include:

- `constraint_pressure`
- `fragmentation`
- `timing_pressure`
- `retry_escalation_risk`
- `operator_review_available`
- `continuity_posture`

## Classification Path

The classification path explains how Nova categorized the environmental pressure. It should be reproducible for equivalent normalized inputs unless a documented governance epoch or schema version changes the result.

## Reproducibility Hash

The reproducibility hash supports replay, auditability, and institutional review. It is not a permission token.

## Source Segmentation

Source segmentation distinguishes synthetic, production-like, and live records so validation evidence does not collapse into operational claims.

## Non-Authority Boundary

Nova conditions the environment before execution; it does not authorize execution. The consumer retains local execution authority.

## Example Input

```json
{
  "request_id": "example_request_001",
  "actor_type": "orchestrator",
  "intent": {
    "asset": "USDC",
    "requested_action": "settlement",
    "intent_type": "machine_payment",
    "urgency": "high"
  },
  "environment": {
    "recent_retry_count": 4,
    "settlement_path": "machine_native",
    "operator_review_available": true
  }
}
```

## Example Output

```json
{
  "context_id": "ctx_example_001",
  "canonical_signature": "example_canonical_signature",
  "classification": "settlement_environment_pressure",
  "record_source_type": "production_like",
  "environmental_state": {
    "constraint_pressure": "elevated",
    "fragmentation": "moderate",
    "timing_pressure": "high",
    "retry_escalation_risk": "elevated"
  },
  "conditioning_guidance": {
    "posture": "increase_review",
    "pacing": "slow_retry_cadence",
    "chronology": "record_context"
  },
  "reproducibility": {
    "proof_schema_version": "v1",
    "reproducibility_hash": "example_hash"
  },
  "non_authority_boundary": "Consumer remains responsible for all execution decisions."
}
```

This output is environmental state, not an execution instruction.

## Orchestration Use Case

A local orchestrator can request context before retrying a machine-native workflow. If Nova reports elevated timing pressure, the orchestrator may apply its own local rules for review, pacing, delay, or cancellation.

## Agent Use Case

An autonomous agent can request pre-action context before routing an intended action to its local policy layer. Nova provides environmental state; the agent's governance stack decides locally.

## Offline Continuity Use Case

If model-provider access is unavailable, an operator can use offline decision intake and chronology records to preserve governance context until normal review resumes.

## Final Boundary

Nova emits environmental state before execution; it does not decide whether execution occurs.
