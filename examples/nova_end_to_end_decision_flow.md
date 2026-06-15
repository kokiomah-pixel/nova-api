# Sharpe Nova OS — End-to-End Pre-Action Context Flow

This example demonstrates how Sharpe Nova OS emits pre-action decision context before execution and produces verifiable proof.

This example does not execute trades, move capital, approve payments, route transactions, or authorize action. Local systems remain responsible for all execution decisions.

---

## Important Note

Nova outcomes depend on current system state.

This example demonstrates both possible paths:

- ALLOW (normal conditions)
- CONSTRAIN (elevated or stressed conditions)

---

## Scenario

A system proposes:

- Intent: allocate
- Asset: ETH
- Size: 10,000

---

## Step 1 — Submit Decision

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=allocate&asset=ETH&size=10000"
```

---

## Step 2 — Interpret Response

### Case A — ALLOW (Normal Conditions)

```json
{
  "decision_status": "ALLOW",
  "system_state": "NORMAL",
  "impact_on_outcomes": {
    "adjusted_size": 10000.0
  }
}
```

**Meaning:**

* Conditions are stable
* No constraint applied
* The local system remains responsible for deciding how to proceed

---

### Case B — CONSTRAIN (Elevated Conditions)

```json
{
  "decision_status": "CONSTRAIN",
  "system_state": "ELEVATED_FRAGILITY",
  "impact_on_outcomes": {
    "adjusted_size": 4000.0
  }
}
```

**Meaning:**

* Conditions require discipline
* Nova reports a conditioned size for local review
* The local system remains responsible for any downstream adjustment

---

## Step 3 — Decision State Rule (Always Applies)

```text
ALLOW -> local system may inspect and decide

CONSTRAIN -> local system may inspect conditioned context before acting

DENY / DELAY / HALT / VETO -> local system may delay, escalate, cancel, or apply its own governance rules
```

---

## Step 4 — Retrieve Proof

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/proof/<decision_id>"
```

---

## Step 5 — Proof Verifies Decision State

Proof will include:

* decision_id
* decision_status
* constraint_effect
* intervention_type
* reproducibility_hash

---

## What This Demonstrates

Nova does not always constrain.

Nova:

> **emits pre-action context for each proposed decision before execution**

---

## What Changed

Without Nova:

```text
Decision → Execution (always full size)
```

With Nova:

```text
Decision -> Nova -> Pre-Action Context -> Local Decision
```

---

## Authority Model

* `/v1/context` -> emits pre-action context
* `decision_status` -> describes Nova's non-authority context state
* `/v1/proof/{decision_id}` -> verifies the emitted context state

Proof does not grant permission.

Proof confirms the state Nova returned.

---

## Final Principle

Sharpe Nova OS does not force constraint.

It emits context about:

> the environmental posture around a proposed decision before any local system decides whether capital moves.
