# Nova Context Network — Retail Plane Isolation v0.1

**Gate:** RP1  
**Authority:** Architect through merged PR #45  
**Scope:** isolated retail-agent production plane only

## Purpose

Establish the implementation boundary required before State Ping, Context Delta,
or retail x402 activation.

```text
public discovery
!= retail invocation
!= institutional review context
```

The retail plane may reuse authority-neutral protocol or utility primitives, but
it must not inherit institutional state, identity, credentials, persistence, or
authority.

## Retail-owned namespaces

```yaml
retail_context_plane:
  code_namespace: retail_context
  endpoint_namespace: /retail/v1/context
  environment_prefix: NOVA_RETAIL_
  persistence_default: .nova_retail
  telemetry_namespace: retail_context
  source_namespace: retail_public_sources
  credential_namespace: retail_context
```

These names establish separation. They do not activate a public endpoint,
payment path, or production deployment.

## Prohibited institutional access

Retail code must not read, import, or derive runtime state from:

- accepted institutional state;
- accepted institutional chronology;
- institutional Reflex Memory;
- institutional constraints;
- institutional action proposals;
- institutional credentials;
- institution-owned telemetry unless separately licensed and explicitly
  authorized for the retail source layer.

Payment does not create institutional identity, tenancy, workflow permission,
or capital authority.

## Shared primitive rule

A shared primitive is eligible for later retail reuse only if it is:

1. authority-neutral;
2. state-neutral;
3. credential-neutral between planes;
4. persistence-neutral between planes;
5. unable to convert retail usage into institutional chronology or Reflex Memory.

Legacy v1 x402 code is therefore a protocol reference implementation, not the
retail product contract. Legacy feed pricing, cadence tiers, feed identity, and
constraint-pressure semantics must not be inherited by default.

## Enforcement

`retail_context.boundaries` provides deterministic import and path guards.

The RP1 test suite verifies that the retail package does not import known
institutional state-bearing modules and that accepted-state, chronology, Reflex
Memory, and institutional paths are rejected.

The deny list is intentionally explicit. A newly identified institutional state
surface must be added before retail code may depend on it.

## RP1 effects

```yaml
PR_effects:
  retail_runtime_effect: isolation_boundary_scaffolding_only
  payment_effect: none
  public_endpoint_effect: none
  deployment_effect: none
  institutional_Gate_5_effect: none
  institutional_data_effect: none
  chronology_effect: none
  institutional_Reflex_Memory_effect: none
```

## Completion condition

RP1 is complete only when repository validation passes and the PR evidence shows:

- the dedicated retail package exists;
- retail configuration uses the `NOVA_RETAIL_` environment namespace;
- negative access tests pass;
- institutional Gate 5 remains unchanged;
- no public endpoint, payment, settlement, or deployment has been activated.

RP1 completion authorizes no new state beyond the authority already established
by PR #45. It only proves the retail isolation prerequisite for subsequent
implementation gates.
