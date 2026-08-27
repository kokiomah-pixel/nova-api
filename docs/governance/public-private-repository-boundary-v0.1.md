# Public / Private Repository Boundary v0.1

**Status:** proposed transition contract  
**Authority:** Architect-approved workstream  
**Scope:** Sharpe Nova OS and Nova Infrastructure Systems Corporation repository exposure

## Governing principle

```text
Public = contract, doctrine, interoperability, and approved proof.
Private = production machinery, proprietary derivation, corporate state, and operating evidence.
Provider-only = secrets and live environment values.
```

The public repository must explain what Nova is, what it guarantees, how an external agent interacts with it, and how its non-authority boundary can be inspected without exposing the internal production system.

## Canonical boundary

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Repository exposure must never weaken that boundary.

## Repository roles

### Public Sharpe Nova OS repository

Purpose: approved external projection and integration surface.

Permitted content includes:

- category doctrine and non-authority boundary;
- public API and resource contracts;
- versioned response schemas;
- public pricing and payment semantics;
- client SDKs and integration examples;
- public x402 discovery metadata and marketplace manifests after activation;
- synthetic test vectors and approved proof artifacts;
- public security and responsible-disclosure policy;
- public changelog and externally supportable state claims.

The public repository must not become the authoritative corporate accepted-state store after private corporate-state migration is completed.

### Private Nova corporate / production repository

Purpose: authoritative corporate operating state and production implementation.

Private-by-default content includes:

- production server implementation;
- deployment manifests and provider topology;
- source-registry implementation and source-selection rules;
- materiality thresholds, weighting, reconciliation, and derivation logic;
- payment verification internals and settlement reconciliation;
- idempotency, recovery, control-store, rate-limit, and kill-switch implementation;
- production telemetry internals and incident evidence;
- corporate governance decisions and accepted-state records not approved for publication;
- institutional tenant implementation, authority maps, chronology, Reflex Memory stores, constraints, and private adapters;
- operator runbooks and internal failure procedures.

### Provider-only secret plane

Never commit secret values to either repository.

Provider-only state includes:

- private keys;
- API credentials;
- access tokens;
- production wallet credentials or signing material;
- live environment values;
- tenant secrets;
- provider account secrets.

## Transition authority rule

The current public repository remains the canonical repository governance surface until a private corporate repository is provisioned, the required state is migrated, validation passes, and the Architect explicitly accepts the authority transfer.

```text
private repository created
!= authority transferred

files copied
!= accepted-state migration complete

public projection updated
!= corporate state changed
```

After explicit migration acceptance:

```text
Private corporate repository
= authoritative corporate accepted state

Public sharpe-nova-os repository
= approved external projection
```

No authority gap is permitted during migration.

## Retail commercialization boundary

The later Architect authorization for the isolated retail-agent plane permits retail x402, public retail discovery, marketplace submission/listing, and retail production deployment within the authorized retail scope.

This does not authorize:

- institutional x402 as identity or authority;
- institutional production activation;
- shared retail/institutional data planes;
- Nova wallet or signing authority;
- automatic chronology or Reflex Memory mutation;
- execution, portfolio management, or buy/sell recommendations.

Therefore public-surface validation must distinguish retail commercialization authority from institutional authority rather than treating x402 or marketplace activity as globally prohibited.

## Publication test

Before publishing a file, ask:

1. Does an external integrator need this to use or verify Nova?
2. Does publication strengthen trust, interoperability, or category comprehension?
3. Does it reveal production topology, proprietary derivation, attack surface, or corporate accepted state unnecessarily?
4. Could a competitor reconstruct meaningful production intelligence from it?
5. Could the file expose institutional state or operational controls?

If 1 or 2 is true and 3-5 are false, publication is generally appropriate.
If 3, 4, or 5 is materially true, keep the artifact private or publish a sanitized contract instead.

## Migration rule for already-public material

Already-published material must be treated as historically disclosed. Moving future implementation private does not make prior Git history secret.

The objective is to protect future compounding intellectual property and production security, not to imply retroactive confidentiality.

## Required migration sequence

```text
1. inventory current public exposure
2. classify major paths as public / public-sanitized / private / provider-only
3. provision private corporate repository
4. copy and verify private-authority material before removing future public reliance
5. establish private repository accepted-state controls
6. migrate production/runtime/deployment internals
7. retain public contracts, SDKs, schemas, examples, and approved proof
8. update public CURRENT_STATE projection
9. update validators for plane-specific commercialization authority
10. perform public-history and PR exposure review
11. Architect explicitly accepts authority transfer
12. freeze ongoing publication policy
```

## Non-effects of this document

This document does not itself:

- create a private repository;
- transfer corporate accepted-state authority;
- remove any file from public Git history;
- deploy or change production;
- activate retail public service;
- advance institutional Gate 5;
- establish buyer demand, adoption, pricing power, or product-market fit.
