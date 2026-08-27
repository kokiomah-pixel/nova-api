# Public File Review Checklist

Use this checklist before adding or revising files in the public Sharpe Nova OS repository.

## Boundary Check

Does the file preserve the canonical boundary?

- Agent prepares action.
- Nova structures review context.
- Local authority decides.
- External systems execute.
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
- investment recommendation system
- compliance product
- audit system
- treasury management system
- agent supervisor

## Plane Check

Does the file distinguish:

```text
retail-agent plane
!= institutional plane
```

Retail x402, retail marketplace activity, and retail public service may be authorized without granting institutional production, identity, tenancy, workflow authority, or capital authority.

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

Does the file avoid claiming unsupported:

- production readiness;
- institutional adoption;
- buyer validation;
- market validation;
- customer usage;
- live capital control;
- automatic Reflex Memory mutation?

## Product Generation Checks

```yaml
product_generation_checks:
  - Does the file identify Legacy v1, retail-agent runtime, or target v2 institutional design when describing implementation?
  - Could Legacy implementation be misread as target v2 implementation?
  - Could retail production authority be misread as institutional authority?
  - Does the file link to the current public state projection when making a system-status claim?
```

## Readiness Checks

```yaml
readiness_checks:
  - Does every readiness claim name its layer?
  - Is production evidence dated and attributable?
  - Is repository validation distinguished from deployment validation?
  - Is offline proof distinguished from live integration?
  - Are historical readiness claims labeled as historical?
  - Is marketplace submission distinguished from listing/discoverability?
  - Is payment configuration distinguished from verified settlement?
```

## Commercialization Checks

```yaml
commercialization_checks:
  - Is the relevant plane identified?
  - Does metering code get mistaken for customer validation?
  - Does marketplace authorization get mistaken for listing evidence?
  - Does pricing authorization get mistaken for pricing power?
  - Does payment get mistaken for demand, adoption, or authority?
```

## Exposure Classification

Classify the artifact before publishing:

- `PUBLIC`
- `PUBLIC_SANITIZED`
- `PRIVATE`
- `PROVIDER_ONLY`

Use these tests:

```yaml
exposure_checks:
  external_need:
    - Does an external integrator need this to invoke, verify, or understand Nova?
    - Does publication materially strengthen trust or interoperability?

  private_risk:
    - Does it reveal production topology or environment-variable inventory?
    - Does it reveal proprietary source selection, materiality thresholds, weighting, or reconciliation logic?
    - Does it expose payment-verification, settlement-reconciliation, idempotency, recovery, kill-switch, or incident internals?
    - Does it expose corporate accepted state that has not been approved for publication?
    - Does it expose institutional tenant data, constraints, authority maps, chronology, Reflex Memory stores, or private adapters?
    - Could a competitor reconstruct meaningful production intelligence from it?
```

If `private_risk` is materially true, keep the implementation private and publish only the minimum external contract or sanitized proof required.

## Secrets Check

Never publish:

- private keys;
- credentials;
- access tokens;
- signing material;
- live environment values;
- tenant secrets;
- provider account secrets.

Secret values belong in provider secret stores, not Git.

## Comprehension Checks

```yaml
comprehension_checks:
  - Can a new reader identify what Nova does within the first screen?
  - Can the reader identify what exists and what is not implemented?
  - Is the canonical boundary stated plainly?
  - Are deep internal terms deferred until after the product explanation?
  - Is the public surface sufficient to integrate without exposing private machinery?
```

## Transition Check

Until the private corporate repository is provisioned, migration is verified, and the Architect explicitly accepts authority transfer, do not imply that the public repository has ceased to be the canonical repository governance surface.

After transfer, do not imply that the public repository contains the complete corporate or production state.

## Final Decision

Only publish if the artifact strengthens Nova's public contract, proof, interoperability, or trust surface without unnecessarily exposing private operating memory, production machinery, proprietary derivation, institutional state, secrets, or creating authority confusion.
