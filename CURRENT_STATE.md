# Sharpe Nova OS — Current State

**Effective date:** August 5, 2026
**Authority:** Architect
**Coherence review:** Jarvis-Nova CCO

## What Nova is

Sharpe Nova OS preserves governed review context for agent-prepared financial
actions before local authority acts.

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Current product state

```yaml
current_product_state:
  canonical_direction: target_v2_non_authority_review_context

  Legacy_v1:
    implemented: true
    canonical_future_external_model: false
    new_external_integrations_permitted: false
    consumer_dependency: unverified
    production_custody: unattested

  target_v2:
    contract_approved: true
    runtime_implemented: false
    private_adapter_implemented: false
    production_active: false

  Phase_1:
    offline_proof_chain: completed
    repository_validation: passed
    production_readiness: not_established
    market_validation: not_established
    buyer_validation: not_established

  institutional_use:
    bounded_pilot: not_started
    operator_dependency: not_established
    adoption: not_established

  commercialization:
    Legacy_v1_metering_code_present: true
    current_pricing_authority: none
    public_marketplace_activation: false
    x402_activation: false
```

## What exists today

The repository contains:

* the implemented Legacy v1 runtime;
* the approved non-authority target v2 contract;
* an offline Phase 1 proof chain;
* deterministic repository validation;
* governance, chronology, source, and authority specifications;
* a bounded stablecoin-treasury workflow definition;
* production-readiness and incident-control gates;
* an initialized content operating system.

## What does not exist today

The repository does not establish:

* a deployed target v2 runtime;
* a production-active target v2 endpoint;
* institutionally attested production custody;
* a completed Legacy v1 consumer inventory;
* a live institutional pilot;
* demonstrated operator dependency;
* buyer pull;
* adoption;
* product-market fit;
* pricing power;
* production x402 or settlement;
* authority to move, approve, sign, or settle capital.

## Current implementation priority

The current implementation priority is one bounded private target v2 production
candidate for an agent-prepared stablecoin treasury action.

The production candidate must preserve:

* stable action identity;
* proposal-version identity;
* source authority and observation time;
* constraint context;
* missing, stale, conflicting, and unavailable state;
* the local-authority boundary;
* reconstructable review context.

It must not approve, authorize, sign, settle, or execute the action.

## Product generations

* [Legacy v1](docs/legacy-v1/README.md)
* [Target v2](docs/target-v2/README.md)

## Readiness detail

See:

* [Production Readiness Register](docs/operations/production-readiness-register.md)
* [Phase 1 Inspection Status](docs/inspection/phase-1-inspection-status.md)

## Claim rule

A repository artifact, passing test suite, design approval, or offline proof does
not independently establish deployment, production readiness, institutional
use, buyer demand, adoption, pricing power, or product-market fit.
