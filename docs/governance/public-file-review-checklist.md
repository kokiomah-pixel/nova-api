# Public File Review Checklist

Use this checklist before adding or revising public repo files.

## Boundary Check

Does the file preserve the canonical boundary?

- Agent prepares action.
- Nova structures review context.
- Local authority decides.
- Nova does not execute.

## Role Check

Does the file avoid framing Nova as:

- approval engine
- authorization layer
- execution layer
- payment rail
- wallet
- signing tool
- settlement layer
- trading system
- portfolio optimizer
- compliance product
- audit system
- treasury management system
- agent supervisor

## Memory Check

If the file discusses memory, does it preserve the distinction?

- Logs are operational residue.
- Working memory is current operating context.
- Chronology is accepted decision-state lineage.
- Reflex Memory is accepted governance memory that may condition future review posture.
- API output remains review context, not authority.

## Reflex Memory Check

If the file discusses Reflex Memory, does it preserve the following?

- Reflex Memory is accepted governance memory.
- Reflex Memory may condition future review posture.
- Reflex Memory cannot mutate automatically.
- Reflex Memory cannot approve, deny, authorize, block, route, settle, sign, or execute.
- Reflex Memory must reference source chronology.
- API output remains review context, not authority.

Unsafe phrasing to avoid:

- Reflex Memory powers live API decisions.
- Nova's API decides based on memory.
- Nova learns from capital actions.
- Reflex Memory restores authority.
- Reflex Memory blocks execution.

## Evidence Check

Does the file avoid claiming:

- production readiness
- institutional adoption
- buyer validation
- market validation
- customer usage
- live capital control
- automatic Reflex Memory mutation

## Product Generation Checks

```yaml
product_generation_checks:
  - Does the file identify Legacy v1 or target v2 when describing implementation?
  - Could Legacy implementation be misread as target v2 implementation?
  - Does the file link to CURRENT_STATE.md when making a system-status claim?
```

## Readiness Checks

```yaml
readiness_checks:
  - Does every readiness claim name its layer?
  - Is production evidence dated and attributable?
  - Is repository validation distinguished from deployment validation?
  - Is offline proof distinguished from live integration?
  - Are historical readiness claims labeled as historical?
```

## Commercialization Checks

```yaml
commercialization_checks:
  - Does metering code get mistaken for customer validation?
  - Does marketplace research get mistaken for listing authority?
  - Does pricing research get mistaken for pricing power?
  - Is monetization sequenced after bounded workflow evidence?
```

## Comprehension Checks

```yaml
comprehension_checks:
  - Can a new reader identify what Nova does within the first screen?
  - Can the reader identify what exists and what is not implemented?
  - Is the canonical boundary stated once, plainly?
  - Are deep internal terms deferred until after the product explanation?
```

## Visibility Check

Classify the file before publishing:

- public
- controlled_public
- private_or_not_public_by_default

## Final Decision

Only publish if the file strengthens Nova's public proof surface without exposing private operating memory or creating authority confusion.
