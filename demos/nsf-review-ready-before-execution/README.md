# NSF Demo — Review-Ready Before Execution

> A bounded NSF demonstration of pre-execution review-state construction for an agent-prepared treasury action.

## Demo positioning

- **Short name:** `review-ready-before-execution`
- **Scenario:** synthetic collateral top-up request
- **Status:** bounded research-surface demonstration
- **Audience:** NSF, technical, and commercial reviewers, plus the Architect
- **Primary question:** Can a system construct a minimum sufficient, reconstructable pre-execution review state from heterogeneous agent-prepared financial workflow evidence without becoming the approval or execution authority?

## Purpose

This bounded demonstration makes the Sharpe Nova OS Phase I research surface concrete.

It shows how an agent-prepared treasury action can appear operationally executable while still lacking governed pre-execution review context.

## What the demo shows

- A synthetic collateral top-up request prepared by an agent.
- The difference between operational executability and institutional review readiness.
- A bounded review-state object structured by Nova.
- Missing, stale, contradictory, or unresolved context.
- The local authority boundary preserved outside Nova.

## What the demo does not show

- Production readiness.
- Live financial workflow operation.
- Buyer validation.
- Institutional adoption.
- Stage B activation.
- Execution, routing, signing, settlement, approval, or denial.
- Completion of the proposed NSF Phase I research.

## Canonical boundary

Agent prepares the action.
Nova structures the review context.
Local authority decides.
Nova does not execute.

## Relationship to NSF

This demo supports the NSF application by making the research problem testable and understandable.

It does not replace the NSF research plan.

The proposed Phase I research remains focused on minimum sufficient context, temporal coherence, contradiction handling, deterministic reconstruction, and authority-boundary comprehension.

## Five-stage demo flow

1. **Agent prepares action.** A synthetic request has an account reference, asset, amount range, and supporting inputs; it can look operationally executable.
2. **Review gap.** The synthetic scenario contains stale source data, missing constraint context, an unresolved chronology reference, and an unresolved source contradiction; executable is not review-ready.
3. **Nova structures context.** The compiler places position, provenance, freshness, classification, constraint, chronology, replay, and authority-boundary context in one bounded object.
4. **Review-state object.** The generated machine-readable package preserves missing-context, stale-source, contradiction, and authority-boundary fields without resolving them as a decision.
5. **Boundary.** Nova does not recommend, approve, deny, route, sign, settle, or execute; local authority remains external.

The demonstration preserves a disagreement between two synthetic sources. Nova surfaces the contradiction without deciding which source is correct.

`review_ready` means only that the bounded context package has no flagged unresolved conditions. It does not mean approved, authorized, safe to execute, compliant, recommended, or institutionally accepted.

## How to run

```bash
./.venv/bin/python demos/nsf-review-ready-before-execution/src/app.py
```

## How to test

```bash
./.venv/bin/python -m pytest demos/nsf-review-ready-before-execution/tests
```
