# Public / Private Repository Boundary v0.1

**Status:** effective repository boundary  
**Authority:** Architect-approved and transfer-completed  
**Scope:** Sharpe Nova OS and Nova Infrastructure Systems Corporation repository exposure  
**Accepted-state authority transfer:** effective and repository-verified on August 28, 2026

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

Current authority role: `NON_AUTHORITATIVE_GOVERNED_PROJECTION`.

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

The public repository is not the authoritative corporate accepted-state store.
Its retained accepted-state artifacts are historical governed projections only
and must not be used to create current corporate accepted-state claims.

### Private Nova corporate / production repository

Purpose: authoritative corporate operating state and production implementation.

Current accepted-state role: `CANONICAL_CORPORATE_ACCEPTED_STATE_AUTHORITY`.

Canonical accepted-state repository:

```text
nova-infrastructure-systems/nova-core
governance/accepted-state/registry.yaml
```

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

## Accepted-state authority transfer

The transition rule was:

```text
private repository created
!= authority transferred

files copied
!= accepted-state migration complete

public projection updated
!= corporate state changed
```

That separate transfer has now been explicitly authorized and completed under:

```yaml
authorization_reference: ARCHITECT-AUTH-CANONICAL-TRANSFER-2026-08-28-B3FB1A8-F50BC42
authorized_starting_public_head: b3fb1a8fc0c395759c46e4cdc9c9fe4b07006317
authorized_starting_private_head: f50bc4295b0463779f34c22219a64fc578656abd
public_projection_merge_commit: 2b7c5361090f04de95b898f2bb8746ae86f305af
private_effective_transfer_merge_commit: 037a24c68c0ecb4cb4a98354c5ec2667a1f75672
private_completion_evidence_merge_commit: 052cdaf256c846489bc12b54a5b698411247fc90
```

Current topology:

```text
Private corporate repository
= authoritative corporate accepted state

Public sharpe-nova-os repository
= approved non-authoritative governed projection
```

No authority gap or dual undisputed authority was created by the transfer.
Authority reversion would require a separate explicit Architect decision.

## Public projection compatibility rule

Historical public files may preserve pre-transfer facts and provenance, but
active public current-state and compatibility surfaces must fail closed against
current accepted-state claims.

The retained public accepted-state registry may be used only for bounded
historical context. Public compatibility code must not:

- identify public `origin/main` as the current corporate accepted-state source;
- create or imply current corporate accepted state;
- create chronology or Reflex Memory acceptance;
- request accepted-state mutation merely because private state is unavailable;
- silently substitute a public mirror or checkout for the private canonical registry.

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

## Completed migration sequence and remaining hygiene

The authority-bearing sequence is complete through explicit Architect transfer
and repository verification. Remaining work is bounded projection hygiene and,
separately, any future deletion-bearing sanitization that receives its own
authority.

```text
1. inventory current public exposure                         complete
2. classify major paths                                      complete
3. provision private corporate repository                    complete
4. copy and verify private-authority material                complete
5. establish private repository accepted-state controls      complete
6. migrate production/runtime custody                        operator-observed complete
7. retain public contracts and approved proof                ongoing
8. update public CURRENT_STATE projection                    ongoing hygiene
9. update validators for projection authority                ongoing hygiene
10. perform public-history and PR exposure review             bounded follow-up
11. Architect explicitly accepts authority transfer           complete
12. freeze ongoing publication policy                         continuing control
```

## Non-effects of this document

This boundary document did not itself effect the accepted-state transfer. The
transfer was separately authorized and repository-verified as recorded above.
This document does not itself:

- remove any file from public Git history;
- authorize public-runtime deletion;
- deploy or change production;
- activate retail public service;
- create chronology or Reflex Memory acceptance;
- advance institutional Gate 5;
- create payment, settlement, signing, or capital authority;
- establish buyer demand, adoption, pricing power, or product-market fit.
