# Controlled Coordination Loop Pilot

This example shows how orchestration can consume Sharpe Nova OS context without treating Nova as an execution authority.

It does not trade.
It does not route orders.
It does not move capital.

It derives conditioned exposure and proof coverage from Nova context.

---

## Flow

Coordination Proposal  
-> `/v1/context`  
-> `decision_status`  
-> conditioned exposure derivation  
-> `/v1/proof/{decision_id}`  
-> pilot report  

---

## Conditioning Rules

- `ALLOW` -> proposed size remains available as conditioned context
- `CONSTRAIN` -> adjusted size becomes the conditioned context
- `DENY / DELAY / HALT / VETO` -> conditioned size is zero

If Nova is unavailable:

-> fail closed  
-> no conditioned exposure  

---

## Run Locally

Start Nova:

```bash
NOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

Run pilot:

```bash
NOVA_API_URL=http://127.0.0.1:8000 NOVA_API_KEY=mytestkey \
./.venv/bin/python examples/controlled_execution_loop.py
```

---

## What Success Looks Like

The pilot should produce:

```text
Total decisions: N
ALLOW: X
CONSTRAIN: Y
DENY / DELAY / HALT / VETO: Z

Total proposed exposure: A
Total conditioned exposure: B
Reduced exposure: C

Proof coverage: 100%
Category drift count: 0
```

---

## What This Demonstrates

Sharpe Nova OS emits environmental context for orchestration stabilization.

The example preserves proof chronology, retry discipline, and conditioned exposure accounting without granting downstream permission.

---

## Boundary Rule

If a decision is not environmentally admissible, the example derives zero conditioned exposure.

Downstream systems retain their own execution responsibility outside Nova.
