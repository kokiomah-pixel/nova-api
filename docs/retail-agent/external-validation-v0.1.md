# Nova Context Network — Production Validation v0.2

## Purpose

This document defines the production-preparation and live-market-validation surface for agent-native retail monetization.

The build objective is now:

> Put the minimum coherent Nova retail-agent economic loop into production, then determine whether independent autonomous agents repeatedly decide that Nova context is worth purchasing when they are free to proceed without it.

This is a retail production surface with live external validation. It is not an institutional pilot and does not activate institutional target-v2 production.

## Canonical retail boundary

```text
Agent encounters uncertainty.
Nova offers structured decision context at an explicit machine-readable price.
Agent decides whether the context is worth purchasing.
External payment infrastructure settles the purchase.
Nova returns context.
The consuming agent reasons independently.
Nova does not execute a financial action.
```

## Production target

```yaml
production_target:
  Nova_controlled_live_target: 2026-09-09
  primary_launch_network: Base
  primary_asset: USDC
  Arc_launch_dependency: false
  marketplace_publication_dependency: false
```

The September 9 target applies to Nova-controlled production surfaces. Third-party marketplace approval or indexing is provider-controlled and may complete later.

Arc should be integrated after its public mainnet and relevant product support are independently verified. Arc must not delay the first Nova retail launch.

## Retail plane isolation

The retail-agent production plane must be physically and logically separable from institution-owned review context.

It must not read or reuse:

- institutional tenant data;
- institution-owned telemetry not separately licensed for retail use;
- institution-specific constraint sets;
- institutional credentials;
- institutional chronology;
- accepted institutional Reflex Memory;
- institutional action proposals.

## Launch resource catalog

### State Ping

Production test price: `0.002 USDC`

Question answered:

> Has Nova's decision-relevant context materially changed?

Required output fields:

```yaml
resource_type: state_ping
subject:
material_change: true_or_false
confidence:
freshness:
material_domains:
generated_at:
schema_version:
```

State Ping must not simply report raw price movement.

### Context Delta

Production test price: `0.02 USDC`

Question answered:

> What materially changed in the current context?

Required output fields:

```yaml
resource_type: context_delta
subject:
material_change:
changed_domains:
unchanged_material_domains:
confidence:
freshness:
contradictions:
missing_evidence:
provenance_summary:
generated_at:
schema_version:
```

State Ping and Context Delta are the minimum required paid resources for initial production activation.

## Post-launch candidate resources

### Evidence / Contradiction Pack

Production test price when activated: `0.02 USDC`

Question answered:

> Why can the available evidence not currently be reconciled?

Allowed `context_status` values:

```text
resolved
partially_resolved
unresolved
insufficient_evidence
```

### Reflex Compare

Production test price when activated: `0.05 USDC`

Question answered:

> How does the current state compare with genuinely similar prior contexts?

Reflex Compare must not emit buy, sell, long, short, expected-return, or trade recommendation language.

### Full Context

Production test price when activated: `0.20 USDC`

Question answered:

> What is the deepest responsible reconciliation of the current state warranted by available evidence?

## Common response rules

Every resource must:

- expose a schema version;
- expose generation time;
- expose freshness treatment;
- preserve source/provenance boundaries;
- support unresolved and insufficient-evidence states where applicable;
- fail closed rather than manufacture certainty;
- remain informational context rather than authority or execution.

## Pricing contract

Prices are deterministic during each live experimental cohort.

Do not dynamically price based on:

- wallet balance;
- perceived wealth;
- market volatility alone;
- token holdings;
- identity inference.

Every price change must carry pricing/cohort attribution so actual elasticity can be measured.

## Payment architecture

### Base standard x402

Base is the first production settlement environment and the required launch path for the initial Nova-controlled live surface.

### Circle Gateway Nanopayments

Gateway Nanopayments should be integrated for State Ping when seller-side availability, cost, operational behavior, and reconciliation are verified.

Gateway is an optimization and expansion path, not a blocker for first production activation.

### Arc

Arc is a post-launch optional rail.

It may be enabled only after verification of:

- public mainnet availability;
- required USDC support;
- required x402/payment support;
- acceptable settlement cost;
- operational reliability.

No Nova resource is Arc-dependent.

### Consumer abstraction

The consumer purchases a Nova resource. Internal payment routing must not redefine the resource or Nova category.

## Discovery architecture

Production discovery is nonexclusive:

- direct Nova x402 discovery;
- Circle Agent Marketplace;
- Coinbase Bazaar;
- future compatible x402 discovery surfaces.

Direct Nova discovery is required for launch.

Marketplace manifests and submission are authorized, but marketplace approval and indexing are not prerequisites for the Nova-controlled launch date.

For every first encounter, capture when technically supportable:

```yaml
agent_acquisition:
  first_discovery_channel:
  first_purchase_channel:
  first_purchase_at:
  subsequent_purchase_channel:
  first_direct_Nova_call:
  direct_return_count:
```

Do not infer durable identity when the payment or discovery layer does not support it.

## Production telemetry

Track only what is required for economics, quality, integrity, and validation.

```yaml
discovery:
  unique_agents:
  channel:
  endpoint_discovery_events:

conversion:
  discovery_to_first_purchase:
  Ping_to_Delta:
  Delta_to_Full:
  Delta_to_Reflex:
  contradiction_purchase_rate:

economics:
  gross_USDC:
  actual_data_cost:
  actual_compute_cost:
  actual_payment_cost:
  gross_margin:
  revenue_per_agent:

behavior:
  repeat_agents:
  purchases_per_agent:
  budget_exhaustion:
  marketplace_to_direct_migration:

quality:
  stale_response_rate:
  unresolved_context_rate:
  contradiction_detection:
  latency:
  rejection_or_refund_rate:

dependency_evidence:
  repeated_same_workflow_calls:
  recovery_attempts_after_failure:
  alternative_source_calls_when_Nova_missing:
  reconciliation_latency_without_Nova:
```

Commercial telemetry is observation state, not accepted buyer-demand state by itself.

## Pre-launch production gates

### Gate P1 — Retail/institutional isolation

Evidence required:

- separate retail data-access configuration;
- no institution-owned data path;
- no shared institutional credentials;
- no institutional Reflex Memory or chronology access.

### Gate P2 — Resource contract

Evidence required:

- State Ping and Context Delta schemas validate deterministically;
- unresolved and insufficient-evidence behavior is tested;
- prohibited execution/recommendation semantics are absent.

### Gate P3 — Paid delivery loop

Evidence required:

- valid x402 challenge;
- successful controlled USDC payment on the configured production path;
- payment verification;
- context delivery;
- settlement/reconciliation record;
- failed-payment behavior fails closed.

### Gate P4 — Production controls

Evidence required:

- rate limiting;
- abuse control;
- endpoint disable/rollback control;
- payment and delivery observability;
- latency/error monitoring;
- incident owner and evidence path.

### Gate P5 — Public discovery

Evidence required:

- direct Nova machine-readable discovery is available;
- prices and resource schemas are inspectable by agents;
- marketplace manifests are prepared or submitted without making marketplace availability a launch blocker.

## Live-market validation gates

After production activation:

### R1 — Independent willingness to pay

At least one non-internal, non-subsidized agent voluntarily purchases context.

Do not count founder wallets, Nova-controlled agents, internal QA agents, or reimbursed transactions as buyer demand.

### R2 — Repeat behavior

The same bounded external identifier makes a later paid purchase arising from a later context need.

### R3 — Delta centrality

Observe whether Context Delta becomes a recurring machine unit.

### R4 — Commodity survival

Agents remain free to use cheap/free alternatives.

### R5 — Marketplace to direct

Measure whether agents discovered through marketplaces later invoke Nova directly.

### R6 — Trust under uncertainty

Preserve real unresolved states. Measure whether agents return after low-confidence or unresolved outputs.

### R7 — Reflex premium

After Reflex Compare is activated, measure whether agents separately pay for historical comparison.

### R8 — Removal cost

Only after recurring real usage exists, measure whether normal outages or bounded approved availability tests create additional reconciliation burden.

## Production implementation order

1. freeze retail/institutional isolation contract;
2. implement common context-object schema;
3. implement production State Ping;
4. implement production Context Delta;
5. implement Base x402 challenge/payment/delivery;
6. configure and verify settlement destination and reconciliation;
7. implement observability, rate limits, kill switches, rollback, and incident path;
8. publish direct machine-readable Nova discovery;
9. deploy the minimum live surface;
10. submit Circle Agent Marketplace and Coinbase Bazaar manifests;
11. integrate Gateway Nanopayments when verified useful;
12. add Contradiction Pack;
13. add read-only Reflex Compare against approved retail corpus;
14. add Full Context;
15. evaluate Arc after verified public-mainnet readiness.

No later resource should delay the minimum first live economic loop unless its absence creates a safety or integrity defect.

## Kill conditions

Escalate for Architect review if external evidence shows:

1. purchasing occurs only with subsidies;
2. Delta is not recurring;
3. commodity substitutes eliminate material Nova value;
4. only Full Context has willingness to pay;
5. Reflex Compare has no incremental value;
6. marketplace users never establish direct Nova access;
7. licensed-data costs destroy viable gross margin;
8. payment friction exceeds useful context value;
9. unresolved responses destroy trust rather than preserve it;
10. after genuine recurring use, Nova removal creates no meaningful reconciliation burden.

Operational safety, integrity, legal, or uncontrolled-loss conditions may require immediate resource disablement. Commercial kill conditions require Architect review rather than automatic shutdown.

## Prohibited claims

Production deployment does not permit the system to claim:

- product-market fit;
- adoption;
- pricing power;
- buyer pull;
- dependency;
- recurring revenue quality;
- institutional production readiness.

Those require separate real evidence and acceptance.

## Success condition

The first meaningful market sequence is:

```text
real agent encounters uncertainty
        ↓
agent independently discovers or recalls Nova
        ↓
agent evaluates explicit price
        ↓
agent voluntarily purchases context
        ↓
Nova reduces reconciliation burden
        ↓
agent returns on a later independent task
```

The strategic question is not whether Nova can put an API in production.

It is whether decision context becomes a recurring economic dependency because repeated reasoning is more costly without it.
