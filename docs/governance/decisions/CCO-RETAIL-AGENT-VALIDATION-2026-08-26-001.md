# CCO Decision — Retail Agent External Validation v0.1

**Decision ID:** CCO-RETAIL-AGENT-VALIDATION-2026-08-26-001  
**Date:** 2026-08-26  
**Authority:** Architect  
**Coherence review:** Jarvis-Nova CCO

## Decision

The Architect authorizes a bounded external-validation build for a separate retail-agent monetization surface derived from the completed hypothetical Nova Context Network simulations.

This decision supersedes the prior July 30, 2026 prohibition on retail runtime engineering only for the bounded retail validation scope defined here. It does not retroactively alter the earlier decision, and it does not authorize institutional Gate 5, institutional x402, institutional pilot activity, or target-v2 production activation.

## Governing commercial thesis

> Nova monetizes progressive reduction of decision-context uncertainty for autonomous agents.

The bounded retail service may expose machine-purchasable context resources. It must not become a trading system, signal engine, portfolio manager, payment gateway, wallet authority, signing service, settlement authority, or transaction-execution layer.

## Authorized scope

The following are authorized at design and bounded implementation level for the retail-agent validation plane:

- a separate non-institutional retail-agent data plane;
- machine-readable context-resource schemas;
- bounded x402 payment gating for the retail validation resources;
- USDC-denominated candidate test prices;
- Base as the default standard x402 settlement environment;
- Circle Gateway Nanopayments research and integration for sub-cent retail context where technically and economically appropriate;
- Circle Agent Marketplace discovery/listing preparation and submission only for the bounded retail-agent validation service after implementation checks pass;
- Coinbase Bazaar discovery/listing preparation and submission only for the bounded retail-agent validation service after implementation checks pass;
- direct Nova x402 discovery for the bounded retail-agent validation service;
- attribution from first discovery channel to later direct Nova access;
- bounded commercial telemetry required to measure voluntary purchase and repeat purchase behavior;
- external unaffiliated autonomous-agent validation;
- explicit unresolved/insufficient-evidence responses;
- read-only historical comparison against an approved retail historical-context corpus.

## Initial candidate resources and test prices

```yaml
retail_validation_resources:
  State_Ping:
    candidate_price: 0.002_USDC
    role: materiality_screen

  Context_Delta:
    candidate_price: 0.02_USDC
    role: core_recurring_unit

  Evidence_Contradiction_Pack:
    candidate_price: 0.02_USDC
    role: evidence_integrity

  Reflex_Compare:
    candidate_price: 0.05_USDC
    role: temporal_context

  Full_Context:
    candidate_price: 0.20_USDC
    role: deep_reconciliation
```

These prices are test parameters, not accepted market prices or pricing-power evidence.

## Payment-routing hypothesis

```yaml
retail_payment_routing:
  State_Ping:
    preferred: Circle_Gateway_Nanopayments
    fallback: standard_x402_when_supported

  Context_Delta:
    preferred: Base_x402
    Gateway_supported: true

  Evidence_Contradiction_Pack:
    preferred: Base_x402
    Gateway_supported: true

  Reflex_Compare:
    preferred: Base_x402
    Gateway_supported: true

  Full_Context:
    preferred: Base_x402
    Gateway_supported: true

  Arc:
    status: conditional_optional_rail
    default: false
    activation_condition: independently_verified_mainnet_and_relevant_product_support
```

Nova sells the context object, not the rail. Distribution and settlement providers remain replaceable external dependencies.

## Distribution hypothesis

```text
Circle Agent Marketplace + Coinbase Bazaar
                ↓
        discovery / acquisition
                ↓
         Nova proves useful
                ↓
        Direct Nova x402
                ↓
      recurring relationship
```

Circle and Coinbase are nonexclusive channels. Direct Nova access must remain possible.

## Required access-class separation

The following must remain separate:

```text
public discovery
!= retail-agent invocation
!= institutional review context
```

Retail validation must not share institutional tenant data, institutional credentials, institutional chronology, institution-owned Reflex Memory, or institution-specific constraints.

Payment does not create:

- institutional identity;
- enterprise tenancy;
- workflow permission;
- institutional authentication;
- capital authority;
- access to institution-owned information.

## Reflex boundary

Retail payment events and retail usage telemetry must not automatically create or mutate canonical Reflex Memory.

Reflex Compare is authorized only as a read-only historical-context comparison surface against an explicitly approved retail corpus.

```text
retail_usage_telemetry
!= accepted Reflex Memory

historical comparison
!= prediction
!= trading signal
```

## Explicit non-authorizations

This decision does not authorize:

- institutional Gate 5 progression;
- institutional pilot activation;
- target-v2 production activation;
- shared institutional and retail endpoints;
- retail access to institutional review context;
- retail access to institution-owned data;
- payment as identity or permission;
- Nova-managed user wallets;
- Nova signing authority;
- Nova settlement authority;
- transaction execution;
- portfolio management;
- buy/sell/long/short recommendations;
- automatic chronology mutation;
- automatic Reflex Memory mutation;
- claims of buyer demand, adoption, pricing power, PMF, or dependency before external evidence;
- broad retail launch;
- large GTM spend;
- marketplace exclusivity;
- Arc-specific Nova identity.

## External validation gates

The bounded build exists to test these gates sequentially:

1. **Technical commercial loop** — unaffiliated agents can discover, understand, pay, receive, and parse a resource without manual intervention.
2. **Independent willingness to pay** — non-subsidized external agent purchases occur.
3. **Repeat behavior** — independent agents purchase Nova again on a later context need.
4. **Context Delta centrality** — determine whether Delta becomes a recurring commercial unit.
5. **Commodity survival** — buyers may freely substitute cheap/free external sources.
6. **Marketplace-to-direct migration** — determine whether marketplace-acquired agents later call Nova directly.
7. **Trust under uncertainty** — unresolved and insufficient-evidence responses do not destroy repeat behavior.
8. **Reflex premium** — determine whether agents separately pay for historical-context comparison.
9. **Removal cost** — only after recurring usage exists, measure additional reconciliation burden when Nova is unavailable.

## Kill conditions

Materially reconsider the retail thesis if external evidence shows any of the following:

- purchases require subsidy;
- Context Delta fails to become recurring;
- generic summaries substitute Nova at negligible reconciliation cost;
- Full Context is the only meaningful paid resource;
- Reflex Compare creates no incremental value;
- marketplace-acquired agents never migrate direct;
- licensed-data economics destroy viable margins;
- x402/payment friction is materially worse than modeled;
- disciplined low-confidence outputs materially destroy retention;
- Nova removal creates no meaningful additional reconciliation burden.

## Evidence rule

Simulation results remain `hypothetical_simulation_only` and are not accepted buyer, adoption, pricing, dependency, or revenue evidence.

A real retail validation state must distinguish:

```text
observed purchase
!= repeat purchase
!= recurring workflow use
!= dependency
!= product-market fit
```

## State effects

```yaml
effects:
  retail_validation_design_authority: true
  bounded_retail_runtime_implementation_authority: true
  bounded_retail_external_validation_authority: true
  institutional_Gate_5_effect: none
  institutional_pilot_effect: none
  target_v2_production_effect: none
  accepted_buyer_demand_effect: none
  adoption_effect: none
  pricing_power_effect: none
  chronology_effect: none
  Reflex_Memory_effect: none
```
