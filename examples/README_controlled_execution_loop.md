# Controlled Execution Loop Pilot

This example proves that execution is downstream of Sharpe Nova OS.

It does not trade.
It does not route orders.
It does not move capital.

It simulates execution only after Nova returns an admitted decision state.

---

## Flow

Decision Proposal  
-> `/v1/context`  
-> `decision_status`  
-> simulated execution only if admitted  
-> `/v1/proof/{decision_id}`  
-> pilot report  

---

## Enforcement Rules

- `ALLOW` -> simulated execution at proposed size
- `CONSTRAIN` -> simulated execution at adjusted size
- `DENY / DELAY / HALT / VETO` -> no simulated execution

If Nova is unavailable:

-> fail closed  
-> no execution  

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
Total admitted exposure: B
Prevented exposure: C

Proof coverage: 100%
Bypass count: 0
```

---

## What This Demonstrates

Sharpe Nova OS is not advisory.

It is a pre-execution decision admission layer.

Execution occurs only after Nova admits the decision.

---

## Non-Bypass Rule

If a decision is not admitted by Nova, execution does not occur.

If a system ignores this rule, it is outside Nova governance.
