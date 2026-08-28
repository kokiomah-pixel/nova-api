# Public-Surface Coherence Standard

## Public state precedence after accepted-state authority transfer

The accepted-state authority transfer to private
`nova-infrastructure-systems/nova-core` is effective and repository-verified.
This public repository is therefore a governed external projection, not the
canonical corporate accepted-state surface.

```yaml
public_projection_precedence:
  1: CURRENT_STATE.md
  2: docs/operations/production-readiness-register.md
  3: docs/target-v2/README.md
  4: README.md
  5: docs/start-here.md
  6: specialized_current_documents
  7: historical_or_Legacy_documents

canonical_corporate_accepted_state:
  repository: nova-infrastructure-systems/nova-core
  registry_path: governance/accepted-state/registry.yaml

public_repository_role:
  repository: nova-infrastructure-systems/sharpe-nova-os
  role: NON_AUTHORITATIVE_GOVERNED_PROJECTION
  retained_public_registry_role: historical_governed_projection_only
  current_accepted_state_claim_use: prohibited
```

Public precedence governs only which public projection should be read first.
It does not make `CURRENT_STATE.md`, public `origin/main`, or any retained public
registry authoritative for corporate accepted state.

The public projection must remain traceable to the authoritative private state
without exposing private operating evidence.

## Exposure rule

```text
Public = contract, doctrine, interoperability, approved proof.
Private = production machinery, proprietary derivation, corporate state, operating evidence.
Provider-only = secret values and live environment credentials.
```

Public files must not expose production topology, secret values, institutional tenant state, private source-selection logic, materiality thresholds, internal settlement-reconciliation logic, or private Reflex Memory stores merely to increase transparency.

## Current-state claim rules

1. “Ready” must name the exact gate or layer.
2. “Implemented” must name the product generation and component.
3. “Live” requires a dated deployment and control-plane evidence reference.
4. “Production” requires a dated production-attestation reference.
5. “Customer,” “adoption,” “buyer pull,” and “pricing power” require admissible external evidence.
6. Historical claims must remain inside clearly labeled historical documents.
7. Legacy implementation must not be presented as target v2 implementation.
8. Repository validation must not be presented as production validation.
9. Offline proof must not be presented as deployed integration.
10. Metering code must not be presented as current commercial validation.
11. Retail production authorization must not be presented as institutional production authority.
12. Retail payment must not be presented as institutional authentication, tenancy, workflow authorization, or capital authority.
13. Marketplace submission must not be presented as listing approval or discoverability.
14. Public repository content must not be presented as the complete production implementation after the private/public split is accepted.
15. Public `CURRENT_STATE.md` must be labeled as a governed public projection, not authoritative corporate accepted state.
16. Public `agent_files/state/accepted-state-registry.yaml` must be treated as historical governed projection only after transfer activation.
17. Public compatibility code must fail closed against current accepted-state claims and must not silently substitute public `origin/main`, a checkout, or a mirror for the private canonical registry.
18. Unavailability of the private canonical registry from the public repository must not create chronology, accepted-state, Reflex Memory, implementation, deployment, or capital authority.

## Accepted-state projection rule

The transfer activation is recorded in:

`docs/governance/canonical-authority-transfer-activation-2026-08-28.yaml`.

After activation:

```text
private canonical registry available to authorized private readers
→ current corporate accepted-state claims may be evaluated there

public retained registry or public checkout
→ bounded historical context only
→ no current corporate accepted-state claim
→ no mutation request solely because private state is unavailable
```

A public projection may repeat an externally supportable private-state claim
only when the claim is deliberately projected and bounded. Projection does not
make the public repository the source of corporate accepted-state authority.

## Commercialization by plane

Public-surface coherence must preserve this distinction:

```yaml
retail_agent_plane:
  x402_payment: authorized_within_retail_scope
  public_service: authorized_within_retail_scope
  marketplace_submission_and_listing: authorized_within_retail_scope
  live_external_validation: authorized_within_retail_scope

institutional_plane:
  Gate_5: not_advanced_by_retail_authority
  payment_as_identity_or_authority: prohibited
  shared_retail_institutional_plane: prohibited
  production_activation_from_retail_work: prohibited
```

Do not enforce a global prohibition on the words `x402` or `marketplace` when the surrounding state clearly identifies the authorized retail-agent plane.

## Prohibited unqualified current claims

Current public entry surfaces must not use these phrases without the evidence and layer qualification required above:

```text
GTM-Ready
operationally live
production-ready
institutionally production-ready
monetization implemented
technically operational
deployed and operational
customer validated
market validated
```

Historical archives may preserve those phrases only when an explicit supersession banner appears, the evidence period is identified, the current public projection is linked, and the claim cannot be mistaken for current status.

## Publication decision

Before publication, classify the artifact as:

```text
PUBLIC
PUBLIC_SANITIZED
PRIVATE
PROVIDER_ONLY
```

Publish only the minimum material required for external comprehension, interoperability, verification, or trust. Where a public contract is sufficient, do not publish the private production implementation.
