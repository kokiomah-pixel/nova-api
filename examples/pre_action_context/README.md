# Pre-Action Context Example
## Local Orchestrator Consuming Nova Environmental State

## Purpose

This conceptual example shows how a local orchestrator can consume Nova environmental state before applying its own governance rules. It does not implement execution behavior.

This example does not execute trades, move capital, approve payments, route transactions, or authorize action.

## Flow

1. Local orchestrator prepares an intended action.
2. Orchestrator requests pre-action context from Nova.
3. Nova returns environmental state and reproducibility metadata.
4. Orchestrator applies local governance rules.
5. Execution, delay, escalation, or cancellation happens outside Nova.

## Example Request

Conceptual shape:

```json
{
  "actor_type": "local_orchestrator",
  "intent": {
    "requested_action": "settlement",
    "intent_type": "machine_payment",
    "urgency": "high"
  },
  "environment": {
    "recent_retry_count": 4,
    "operator_review_available": true
  }
}
```

Current endpoint shape:

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=settlement&asset=USDC&size=1000&telemetry_reliability=0.91&telemetry_age_seconds=12"
```

## Example Response

Conceptual subset:

```json
{
  "environmental_state": {
    "constraint_pressure": "elevated",
    "timing_pressure": "high",
    "retry_escalation_risk": "elevated"
  },
  "reproducibility": {
    "proof_schema_version": "v1",
    "reproducibility_hash": "example_hash"
  },
  "non_authority_boundary": "Consumer remains responsible for all execution decisions."
}
```

## Local Decision Pseudocode

```python
context = nova.get_pre_action_context(intent)

if context["environmental_state"]["constraint_pressure"] == "elevated":
    local_orchestrator.increase_review()
    local_orchestrator.slow_retry_cadence()

local_orchestrator.decide_locally()
```

## Non-Authority Boundary

Nova does not execute.
Nova does not authorize.
Nova does not decide for the orchestrator.

The local orchestrator remains responsible for any delay, escalation, cancellation, or downstream action.

## Related Contract

See [docs/architecture/pre-action-context-contract.md](../../docs/architecture/pre-action-context-contract.md) for the canonical builder-facing contract.

Sample conceptual payloads:

- [sample_request.json](sample_request.json)
- [sample_response.json](sample_response.json)
