# CCO Decision — Retail Agent Production Preparation v0.2

**Decision ID:** CCO-RETAIL-AGENT-VALIDATION-2026-08-26-001  
**Date:** 2026-08-26  
**Authority:** Architect  
**Coherence review:** Jarvis-Nova CCO

## Decision

The Architect authorizes production preparation and live external validation for a separate retail-agent monetization surface derived from the completed Nova Context Network simulations.

This decision explicitly supersedes the July 30, 2026 retail prohibitions, but only for the separately isolated retail-agent plane described here. The following are no longer prohibited for that retail plane:

- retail Nova runtime engineering;
- x402 payment for Nova retail context resources;
- public retail-agent service activation;
- public machine-readable service manifests;
- Circle Agent Marketplace submission/listing;
- Coinbase Bazaar submission/listing;
- direct public Nova x402 discovery;
- retail production deployment;
- retail USDC settlement through approved external payment infrastructure.

The July decision remains historically valid for the state that existed when it was made. It is not erased or retroactively rewritten. This decision is the later Architect authority that changes the retail operating posture.

This decision does **not** advance institutional Gate 5, authorize an institutional pilot, activate target-v2 institutional production, or grant Nova capital authority.

## Production objective

Nova should now be built for real external use rather than another closed simulation.

```yaml
retail_agent_production_objective:
  status: AUTHORIZED_FOR_PRODUCTION_PREPARATION
  Nova_controlled_live_target: 2026-09-09
  external_validation: live_in_production
  market_validation_required_after_launch: true
```

The September 9 target applies to surfaces controlled by Nova. Marketplace approval, indexing, or publication controlled by third parties may occur later and must be reported as provider-dependent rather than treated as a Nova deployment failure.

Arc is not a dependency for the September 9 launch. Arc may be activated only after public mainnet and required support are independently verified.

## Governing commercial thesis

> Nova monetizes progressive reduction of decision-context uncertainty for autonomous agents.

The retail service may expose machine-purchasable context resources. It must not become a trading system, signal engine, portfolio manager, wallet authority, signing service, settlement authority, or transaction-execution layer.

## Authorized production scope

The following are authorized for the retail-agent plane:

- a physically and logically separate non-institutional retail-agent data plane;
- production runtime engineering for retail context resources;
- production machine-readable context-resource schemas;
- production x402 payment gating;
- USDC-denominated test prices used with real buyers;
- Base as the default standard x402 settlement environment;
- Circle Gateway Nanopayments seller integration for sub-cent context where verified and cost-effective;
- Circle Agent Marketplace submission and listing for approved retail resources;
- Coinbase Bazaar submission and listing for approved retail resources;
- direct Nova x402 discovery and paid invocation;
- marketplace-to-direct attribution;
- production commercial telemetry required to measure voluntary purchase and repeat behavior;
- unaffiliated autonomous-agent access;
- explicit unresolved and insufficient-evidence responses;
- read-only historical comparison against an approved retail historical-context corpus;
- production rollback, rate limiting, incident controls, and kill switches for the retail plane.

## Minimum launch scope

The Nova-controlled production launch must not be delayed until every simulated resource is implemented.

Minimum viable live surface:

```yaml
minimum_live_surface:
  required:
    - State_Ping
    - Context_Delta
    - direct_x402_discovery
    - Base_USDC_payment_path
    - payment_and_delivery_telemetry
    - source_freshness_and_provenance
    - unresolved_and_insufficient_evidence_states
    - retail_institutional_isolation
  optional_at_initial_launch:
    - Evidence_Contradiction_Pack
    - Reflex_Compare
    - Full_Context
    - Circle_Gateway_Nanopayments
    - Circle_Agent_Marketplace_listing
    - Coinbase_Bazaar_listing
```

Optional does not mean strategically unimportant. It means failure to complete a third-party integration or later resource must not unnecessarily block the first live economic loop.

## Initial real-market test prices

```yaml
retail_production_test_prices:
  State_Ping:
    price: 0.002_USDC
    role: materiality_screen

  Context_Delta:
    price: 0.02_USDC
    role: core_recurring_unit

  Evidence_Contradiction_Pack:
    price: 0.02_USDC
    role: evidence_integrity

  Reflex_Compare:
    price: 0.05_USDC
    role: temporal_context

  Full_Context:
    price: 0.20_USDC
    role: deep_reconciliation
```

These are authorized production test prices. They are not evidence of pricing power. Price changes require cohort/version attribution so willingness to pay can be measured honestly.

## Payment architecture

```yaml
retail_payment_routing:
  standard_x402:
    default_network: Base
    asset: USDC

  State_Ping:
    preferred_long_term: Circle_Gateway_Nanopayments
    launch_fallback: Base_x402

  Context_Delta:
    preferred: Base_x402
    Gateway_supported_when_verified: true

  Evidence_Contradiction_Pack:
    preferred: Base_x402
    Gateway_supported_when_verified: true

  Reflex_Compare:
    preferred: Base_x402
    Gateway_supported_when_verified: true

  Full_Context:
    preferred: Base_x402
    Gateway_supported_when_verified: true

  Arc:
    status: post_launch_optional_rail
    launch_dependency: false
    activation_condition: independently_verified_public_mainnet_and_required_support
```

Nova sells the context object, not the rail. Circle, Coinbase, Base, Gateway, and Arc are external infrastructure or distribution dependencies and must remain replaceable where practical.

## Distribution architecture

```text
Circle Agent Marketplace + Coinbase Bazaar + other compatible discovery
                          ↓
                    acquisition
                          ↓
                 Nova proves useful
                          ↓
                  Direct Nova x402
                          ↓
               recurring relationship
```

Circle and Coinbase are nonexclusive channels. Direct Nova access must remain available.

Marketplace submission is authorized. Marketplace acceptance or publication is not assumed until independently observed.

## Retail / institutional separation

The following remain separate:

```text
public discovery
!= retail-agent invocation
!= institutional review context
```

Retail production must not share:

- institutional tenant data;
- institutional credentials;
- institution-specific constraints;
- institutional chronology;
- accepted institutional Reflex Memory;
- institutional action proposals;
- institution-owned data not separately licensed for retail use.

Payment does not create institutional identity, enterprise tenancy, workflow permission, capital authority, or access to institution-owned information.

## Reflex boundary

Retail payments and retail usage telemetry must not automatically create or mutate canonical institutional Reflex Memory.

Reflex Compare is authorized only as read-only comparison against an explicitly approved retail historical corpus.

```text
retail_usage_telemetry
!= accepted institutional Reflex Memory

historical comparison
!= prediction
!= trading signal
```

## Production controls required before public activation

Public activation requires evidence of:

1. retail/institutional data-plane isolation;
2. valid deterministic resource schemas;
3. x402 challenge/payment/delivery success in controlled production tests;
4. settlement destination configuration and reconciliation;
5. source freshness and provenance treatment;
6. rate limiting and abuse controls;
7. observability for payment, delivery, latency, and resource failure;
8. rollback or disable control for each paid resource;
9. no buy/sell/long/short or execution semantics;
10. no automatic chronology or institutional Reflex Memory mutation;
11. pricing-version attribution;
12. a production incident owner and evidence path.

These are release-safety controls. They are not substitutes for market validation.

## Live-market validation gates

After public activation, observe sequentially:

1. unaffiliated agents discover, understand, pay, receive, and parse a resource;
2. non-subsidized willingness to pay occurs;
3. repeat purchase occurs on a later independent need;
4. Context Delta either becomes or fails to become a recurring unit;
5. Nova survives free/cheap commodity substitution;
6. marketplace-acquired agents either migrate or fail to migrate to direct Nova;
7. unresolved/low-confidence responses either preserve or weaken trust;
8. Reflex Compare either earns a real premium or remains internal capability;
9. after genuine recurring use exists, Nova absence either creates or fails to create reconciliation cost.

## Kill conditions

Escalate for Architect review if external evidence shows:

- purchases occur only with subsidy;
- Context Delta does not recur;
- commodity substitutes eliminate material Nova value;
- only Full Context has willingness to pay;
- Reflex Compare creates no incremental value;
- marketplace-acquired agents never establish direct Nova access;
- licensed-data economics destroy viable margin;
- payment friction exceeds context value;
- unresolved responses destroy trust;
- after recurring use exists, Nova removal creates no meaningful reconciliation burden.

A kill condition does not automatically take the service offline unless it is also a safety, legal, economic-loss, or integrity condition. Commercial kill conditions trigger Architect review.

## Explicit non-authorizations

This decision still does not authorize:

- institutional Gate 5 progression;
- institutional pilot activation;
- target-v2 institutional production activation;
- shared institutional and retail endpoints or credentials;
- retail access to institution-owned data or context;
- payment as institutional identity or permission;
- Nova-managed customer wallets;
- Nova signing authority;
- Nova settlement authority over customer capital;
- transaction execution;
- portfolio management;
- buy/sell/long/short recommendations;
- automatic chronology mutation;
- automatic institutional Reflex Memory mutation;
- claims of buyer demand, adoption, pricing power, PMF, or dependency before evidence;
- marketplace exclusivity;
- Arc-specific Nova identity.

## Evidence rule

The completed simulation remains `hypothetical_simulation_only`.

Production availability is an implementation fact, not a market-success claim.

```text
live endpoint
!= buyer demand

observed purchase
!= repeat purchase

repeat purchase
!= recurring workflow use

recurring workflow use
!= dependency

revenue
!= product-market fit
```

## State effects

```yaml
effects:
  retail_production_design_authority: true
  retail_runtime_implementation_authority: true
  retail_x402_payment_authority: true
  retail_marketplace_submission_authority: true
  retail_public_service_authority: true
  retail_production_deployment_authority: true
  retail_live_external_validation_authority: true

  institutional_Gate_5_effect: none
  institutional_pilot_effect: none
  target_v2_institutional_production_effect: none
  capital_authority_effect: none
  accepted_buyer_demand_effect: none
  adoption_effect: none
  pricing_power_effect: none
  chronology_effect: none
  institutional_Reflex_Memory_effect: none
```
