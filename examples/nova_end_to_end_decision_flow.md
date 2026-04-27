# Sharpe Nova OS — End-to-End Decision Admission Flow

This example demonstrates how Sharpe Nova OS defines the admissible state of a decision before execution and produces verifiable proof.

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
* Execution proceeds as proposed

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
* Exposure is reduced before execution
* Execution must follow adjusted size

---

## Step 3 — Decision State Rule (Always Applies)

```text
ALLOW → proceed

CONSTRAIN → adjust BEFORE execution

DENY / DELAY / HALT / VETO → DO NOT EXECUTE
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

> **defines the admissible state of each proposed decision before execution**

---

## What Changed

Without Nova:

```text
Decision → Execution (always full size)
```

With Nova:

```text
Decision -> Nova -> Decision Admitted -> Execution
```

---

## Authority Model

* `/v1/context` → determines decision admission
* `decision_status` → authoritative decision state
* `/v1/proof/{decision_id}` → verifies the governed decision state

Proof does not grant permission.

Proof confirms the state Nova returned.

---

## Final Principle

Sharpe Nova OS does not force constraint.

It determines:

> whether a proposed decision is admissible before capital moves.
