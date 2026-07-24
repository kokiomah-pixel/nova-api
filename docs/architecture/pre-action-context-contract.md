# Pre-Action Context Contract

## Reviewer Summary

The Pre-Action Context Contract is the clearest integration surface for Sharpe Nova OS.

A local system submits an intended action and surrounding environmental context. Nova returns pre-action environmental state, classification context, reproducibility metadata, source segmentation, and non-authority telemetry.

The consuming system remains responsible for all local governance and execution decisions.

Nova emits context before action. It does not authorize action.

## Purpose

This contract is the canonical builder-facing explanation of how autonomous systems consume Nova before action. It describes the existing pre-action context surface and the meaning of the environmental state Nova emits.

Nova emits environmental state before execution; it does not decide whether execution occurs.

## Canonical Endpoint

`/v1/context` is the canonical pre-action context endpoint.

Builders should inspect this endpoint first. It accepts an intended action context through query parameters such as `intent`, `asset`, `size`, `venue`, `strategy`, telemetry fields, and governance evidence fields. It returns a signed coordination record with environmental state, classification context, reproducibility metadata, and proof material.

`/v1/proof/{decision_id}` verifies the derived coordination context after a context response creates a proof-bearing record.

## Specific Integration Profile

The [Agent-Prepared Stablecoin Treasury Integration Path](agent-prepared-stablecoin-treasury-integration-path.md) is one concrete profile of this existing contract.

It is:

- not a new endpoint;
- not a production deployment;
- not a replacement for `/v1/context`; and
- not an authorization protocol.

Its conceptual envelopes provide design and discovery vocabulary while preserving this contract as the canonical integration surface.

## What Pre-Action Context Means

Pre-action context is governance information produced before a local operator, agent, or orchestration system decides how to proceed. It can describe constraint pressure, timing pressure, retry escalation risk, classification state, source segmentation, proof reproducibility, and continuity posture.

## Flow

1. Local system prepares intended action.
2. Local system requests Nova pre-action context.
3. Nova returns environmental state and reproducibility metadata.
4. Local system applies local governance rules.
5. Any execution, delay, escalation, or cancellation happens outside Nova.

## What Nova Emits

Nova may emit:

- canonical governance identity
- environmental state
- classification context and classification path
- reproducibility metadata
- source segmentation
- conditioning guidance
- Reflex Memory chronology references
- non-authority boundary language

## What Nova Does Not Emit

Nova does not emit execution commands, trade recommendations, capital allocation guidance, custody instructions, local decision authority, or agent-control instructions.

## Input Shape

A pre-action context request describes an intended action and the surrounding environment. The input should be treated as context for environmental classification, not as a request for permission.

Current `/v1/context` inputs are query fields, not a JSON body. Common builder-facing inputs include:

- `intent`
- `asset`
- `size`
- `venue`
- `strategy`
- `telemetry_age_seconds`
- `telemetry_reliability`
- `telemetry_source_scores`
- `halt_release_authority_input`
- `halt_release_evidence_input`

### Conceptual Temporal Context Fields

Conceptual input and output profiles may use the following vocabulary:

```yaml
temporal_context:
  source_observed_at:
  source_received_at:
  review_context_created_at:
  intended_execution_window:
  maximum_evidence_age:
  known_pending_state:
  temporal_conflicts: []
  context_valid_until:
  invalidation_conditions: []
```

These fields are a design vocabulary for review-context discovery. They do not establish that the current endpoint implements automated temporal expiration, transaction blocking, or continuous monitoring.

## Output Shape

A pre-action context response returns environmental state and reproducibility metadata. The consuming system remains responsible for all local governance and execution decisions.

Current `/v1/context` responses include a signed coordination record with fields such as:

- `decision_admission_record`
- `decision_context`
- `constraint_analysis`
- `constraint_trace`
- `decision_status`
- `loop_classification`
- `telemetry_integrity_state`
- `permission_budget_class`
- `reflex_memory_class`
- proof and reproducibility fields attached by the proof layer
- `signature`

## Environmental State Fields

Common environmental fields may include:

- `constraint_pressure`
- `fragmentation`
- `timing_pressure`
- `retry_escalation_risk`
- `operator_review_available`
- `continuity_posture`
- `loop_classification`
- `telemetry_integrity_state`
- `permission_budget_class`

## Classification Context

Classification context explains how Nova categorized the environmental pressure. The classification path should be reproducible for equivalent normalized inputs unless a documented governance epoch, registry version, classification version, or proof schema version changes the result.

## Reproducibility Metadata

Reproducibility metadata can include canonical signature, proof schema version, classification path, and reproducibility hash. These fields support replay, auditability, and institutional review. They are not permission tokens.

## Source Segmentation

Source segmentation distinguishes synthetic, production-like, and live records so validation evidence does not collapse into operational claims.

## Non-Authority Boundary

Nova conditions the environment before execution; it does not authorize execution. The consumer retains local execution authority.

## Example Input

Conceptual JSON shape:

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

Equivalent current endpoint shape:

```text
GET /v1/context?intent=settlement&asset=USDC&size=1000&telemetry_reliability=0.91&telemetry_age_seconds=12
```

## Example Output

Conceptual response shape:

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

## Related GTM Context

- [Where Nova Sits](../go-to-market/where-nova-sits.md)
- [First Use Case: Agent-Prepared Treasury Action](../go-to-market/first-use-case-agent-prepared-treasury-action.md)

## Local Execution Responsibility

Consumers remain responsible for all local governance and execution decisions. Nova can inform review, pacing, delay, escalation, or cancellation logic, but those actions happen outside Nova.

## Related Concept

For a systems-level explanation of how Nova turns agent-prepared actions into review-ready context, see:

- `docs/architecture/review-context-loop.md`

## Final Boundary

Nova emits environmental state before execution; it does not decide whether execution occurs.

Consumers remain responsible for all local governance and execution decisions.
