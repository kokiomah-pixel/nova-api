# Legacy v1 Local Inspection

> **Historical product-generation boundary**
>
> This quickstart runs the implemented Legacy v1 runtime.
>
> Legacy v1 is not the canonical future external integration model. Do not use
> this quickstart as evidence that target v2 is implemented, production-active,
> or authorized for new external integrations.

## 1. Start Nova locally

```bash
NOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

## 2. Submit one context request

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=allocate&asset=ETH&size=10000"
```

## 3. Read the Legacy v1 coordination fields

Bind orchestration behavior to the emitted environmental context rather than
treating Nova as an execution authority.

Key emitted fields include:

```text
coordination_state         # descriptive label of environmental posture
constraint_pressure        # summary of constraint intensity (low/medium/high)
drift_score                # derivative telemetry metric (0.0 - 1.0)
review_context_metadata    # structured context to inform pacing/adjustment
```

Supporting fields may explain telemetry and constraint analysis. These fields
are conditioning inputs for upstream orchestration logic. They do not grant
execution authority and do not implement the target v2 contract.

## 4. Retrieve proof

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/proof/<decision_id>"
```

Proof verifies the emitted Legacy v1 coordination context and the integrity of
derived environmental telemetry. It is an audit artifact, not a permission
grant or evidence of target v2 implementation.
