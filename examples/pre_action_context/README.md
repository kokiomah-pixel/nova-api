# Pre-Action Context Example

This example shows how a local orchestrator or agent workflow can request Nova context before taking action.

Nova returns environmental state and non-authority telemetry. The local system remains responsible for deciding whether to proceed, slow down, escalate, delay, or cancel.

This example does not execute trades, move capital, approve payments, route transactions, or authorize action.

## Flow

1. Prepare intended action locally.
2. Request Nova pre-action context.
3. Inspect environmental state.
4. Apply local governance rules.
5. Decide locally.

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

The final decision remains outside Nova.

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

## Synthetic Stablecoin Treasury Illustration

- [agent_prepared_stablecoin_treasury_action.yaml](agent_prepared_stablecoin_treasury_action.yaml)

Classification:

```text
synthetic interface illustration
not runtime behavior
not production integration
not authority logic
```

The example shows different source-observation times, known pending activity, an unresolved source conflict, an institution-defined temporal condition, Nova-structured review context, and a local-authority handoff. It contains no executable transaction data.
