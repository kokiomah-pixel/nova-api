# Sharpe Nova OS — Commercialization Sequence

## Current posture

Legacy v1 contains metering, quota, and pricing-related implementation artifacts.

Their existence does not establish:

- current customer demand;
- willingness to pay;
- target v2 institutional monetization readiness;
- institutional marketplace readiness;
- institutional production payment readiness.

A later Architect decision separately authorized production preparation and live external validation for the isolated retail-agent plane. That authorization supersedes the earlier retail prohibitions only for that isolated retail plane.

## Institutional sequence

```text
Product-generation coherence
→ production custody attestation
→ Legacy v1 dependency inventory
→ target v2 field derivation
→ private target v2 adapter
→ bounded operator rehearsal
→ controlled production candidate
→ institutional pilot evidence
→ institutional pricing validation
→ institutional distribution-channel validation
```

## Retail sequence

```text
Retail/institutional isolation
→ public resource contract
→ retail data foundation
→ State Ping / Context Delta
→ x402 paid-delivery loop
→ production controls
→ controlled production proof
→ public activation
→ live external validation
```

## Current authorization by plane

```yaml
commercialization_authority:
  institutional:
    new_pricing_expansion: false
    public_marketplace_listing: false
    marketplace_activation: false
    x402_activation: false
    payment_activation: false
    customer_contracting: false

    permitted:
      - bounded_pricing_research
      - operator_discovery
      - cost_and_metering_architecture_review

  retail_agent_plane:
    production_preparation_authorized: true
    runtime_engineering_authorized: true
    x402_payment_authorized: true
    public_service_authorized: true
    marketplace_submission_authorized: true
    marketplace_listing_authorized: true
    direct_x402_discovery_authorized: true
    Base_USDC_authorized: true
    live_external_validation_authorized: true

    evidence_limits:
      - authorization_does_not_establish_implementation
      - implementation_does_not_establish_deployment
      - deployment_does_not_establish_buyer_demand
      - payment_does_not_establish_adoption
      - usage_does_not_establish_pricing_power_or_product_market_fit
```

## Retail boundary

Retail commercialization does not authorize:

- institutional Gate 5;
- institutional pilot activation;
- target-v2 institutional production;
- payment as institutional identity or workflow authority;
- shared retail/institutional credentials, data plane, chronology, or Reflex Memory;
- Nova-managed wallets, signing authority, or customer-capital settlement authority;
- execution, portfolio management, or buy/sell recommendations;
- automatic chronology or Reflex Memory mutation.

## Institutional unfreeze conditions

New institutional commercialization implementation requires evidence of:

* a clearly defined buyer and operator;
* repeated workflow need;
* a deployed bounded target v2 workflow;
* measured operational value or burden reduction;
* production custody;
* data and retention boundaries;
* support and incident processes;
* pricing that purchases context access rather than authority or outcomes.
