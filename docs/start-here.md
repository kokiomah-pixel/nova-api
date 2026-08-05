# Start Here

## 1. What Nova does

Sharpe Nova OS preserves governed review context for agent-prepared financial
actions before local authority acts.

## 2. Where Nova sits

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## 3. One example

The first bounded workflow is an agent-prepared stablecoin treasury action.

An agent may prepare one proposal and then revise its amount, destination,
timing, or assumptions. The institution must preserve which exact proposal
version local authority reviewed, which evidence and sources were current, what
assumptions and constraints applied, and what was missing, stale, conflicting,
or unavailable at that moment.

Nova structures that review context. Local authority decides, and external
systems execute.

## 4. What exists today

See the authoritative [Current State](../CURRENT_STATE.md).

* Legacy v1 is implemented.
* Legacy v1 is not the canonical future external model.
* Target v2 is approved in design.
* Target v2 is not implemented or production-active.
* Phase 1 is offline and repository-validated.
* Institutional production readiness is not established.

## 5. Choose a review path

### Ten-minute public review

1. [Current State](../CURRENT_STATE.md)
2. [First bounded workflow](go-to-market/first-use-case-agent-prepared-treasury-action.md)
3. [Target v2](target-v2/README.md)
4. [Production readiness](operations/production-readiness-register.md)

### Developer review

1. [Current State](../CURRENT_STATE.md)
2. [Legacy v1](legacy-v1/README.md)
3. [Target v2 contract](architecture/external-review-context-contract-v2.md)
4. [Migration and isolation plan](migrations/v1-admission-isolation-plan.md)
5. [Tests and examples](../tests/)

### Governance review

1. [Current State](../CURRENT_STATE.md)
2. [Target v2](target-v2/README.md)
3. [Governance standards](governance/)
4. [Chronology standards](chronology/)
5. [Technical evidence map](validation/technical-evidence-map.md)

### Research and NSF review

Use the [NSF reviewer path](reviewer-paths.md#nsf-reviewer-path). Research
materials do not establish current production readiness or institutional use.

## 6. Important non-claims

This repository does not establish a deployed or production-active target v2
runtime, attested production custody, a completed Legacy v1 consumer inventory,
a live institutional pilot, operator dependency, buyer pull, adoption,
product-market fit, pricing power, production settlement, or authority to move,
approve, sign, or settle capital.
