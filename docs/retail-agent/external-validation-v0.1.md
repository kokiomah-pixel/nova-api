# Nova Context Network — External Validation v0.1

## Purpose

This document defines the bounded external-validation surface for agent-native retail monetization.

The build objective is singular:

> Determine whether independent autonomous agents repeatedly decide that Nova context is worth purchasing when they are free to proceed without it.

The validation surface is not a broad retail launch and is not an institutional pilot.

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

## Retail plane isolation

The retail-agent validation plane must be physically and logically separable from institution-owned review context.

It must not read or reuse:

- institutional tenant data;
- institution-owned telemetry not separately licensed for retail use;
- institution-specific constraint sets;
- institutional credentials;
- institutional chronology;
- accepted institutional Reflex Memory;
- institutional action proposals.

## Resource catalog

### State Ping

Candidate price: `0.002 USDC`

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

Candidate price: `0.02 USDC`

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

### Evidence / Contradiction Pack

Candidate price: `0.02 USDC`

Question answered:

> Why can the available evidence not currently be reconciled?

Required output fields:

```yaml
resource_type: evidence_contradiction_pack
subject:
context_status:
source_conflicts:
stale_sources:
unavailable_sources:
missing_evidence:
confidence:
provenance_summary:
generated_at:
schema_version:
```

Allowed `context_status` values:

```text
resolved
partially_resolved
unresolved
insufficient_evidence
```

### Reflex Compare

Candidate price: `0.05 USDC`

Question answered:

> How does the current state compare with genuinely similar prior contexts?

Required output fields:

```yaml
resource_type: reflex_compare
subject:
current_context:
similar_historical_contexts:
similarities:
differences:
subsequent_conditions:
confidence:
limitations:
corpus_version:
generated_at:
schema_version:
```

Reflex Compare must not emit buy, sell, long, short, expected-return, or trade recommendation language.

### Full Context

Candidate price: `0.20 USDC`

Question answered:

> What is the deepest responsible reconciliation of the current state warranted by available evidence?

Required output fields:

```yaml
resource_type: full_context
subject:
context_status:
state:
material_change:
confidence:
freshness:
contradictions:
missing_evidence:
provenance_summary:
historical_context:
limitations:
generated_at:
schema_version:
```

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

Candidate prices are deterministic during each experimental cohort.

Do not dynamically price based on:

- wallet balance;
- perceived wealth;
- market volatility alone;
- token holdings;
- identity inference.

Price experiments must preserve cohort attribution so elasticity can be measured without silently changing price mid-observation.

## Payment architecture

### Standard x402

Base is the preferred default standard x402 settlement environment for Delta, Contradiction Pack, Reflex Compare, and Full Context.

### Nanopayments

State Ping should preferentially use a batched nanopayment path when that path is independently verified and cost-effective.

### Arc

Arc is optional and conditional. No resource is Arc-dependent.

Arc may be enabled only after verification of:

- mainnet availability;
- required USDC support;
- required x402/payment support;
- acceptable settlement cost;
- operational reliability.

### Consumer abstraction

The consumer purchases a Nova resource. Internal routing must not require the consumer to understand Nova's settlement decision unless the payment protocol requires disclosure.

## Discovery architecture

Prepare nonexclusive machine-readable discovery for:

- Circle Agent Marketplace;
- Coinbase Bazaar;
- direct Nova discovery.

For every first encounter, capture:

```yaml
agent_acquisition:
  first_discovery_channel:
  first_purchase_channel:
  first_purchase_at:
  subsequent_purchase_channel:
  first_direct_Nova_call:
  direct_return_count:
```

Do not infer durable identity when the payment or discovery layer does not support it. Use bounded pseudonymous identifiers where necessary.

## Commercial telemetry

Track only what is required to answer the validation thesis.

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
  data_cost:
  compute_cost:
  payment_cost:
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

## Validation sequence

### Gate R1 — Technical commercial loop

Completion evidence:

- an unaffiliated external agent discovers a Nova resource;
- receives a valid payment requirement;
- completes payment without manual Nova intervention;
- receives a parseable response conforming to the published schema.

### Gate R2 — Independent willingness to pay

Completion evidence:

- at least one non-internal, non-subsidized external agent voluntarily purchases a resource.

Do not count:

- founder wallets;
- Nova-controlled agents;
- internal QA agents;
- incentive-funded purchases where Nova directly reimburses the buyer.

### Gate R3 — Repeat behavior

Completion evidence:

- the same bounded external agent identifier makes a later independent paid purchase arising from a later context need.

### Gate R4 — Delta centrality

Evaluate whether Context Delta becomes a recurring machine unit.

No pass threshold is predeclared. Report actual behavior.

### Gate R5 — Commodity survival

Agents must remain free to use cheap or free alternatives. Nova must not block substitution.

### Gate R6 — Marketplace to direct

Measure whether an agent first discovered in a marketplace subsequently calls Nova directly.

### Gate R7 — Trust under uncertainty

Deliberately preserve real unresolved states when they occur. Do not manufacture failures.

Measure whether external agents return after receiving low-confidence or unresolved context.

### Gate R8 — Reflex premium

Measure whether external agents voluntarily pay separately for Reflex Compare.

### Gate R9 — Removal cost

Do not run until recurring external usage exists.

Measure normal operational outages or bounded approved availability tests without manipulating financial outcomes.

Dependency remains unproven unless external evidence shows recurring reconciliation burden when Nova is absent.

## Kill conditions

Escalate for Architect review if any of these become supported by external evidence:

1. purchasing occurs only with subsidies;
2. Delta is not recurring;
3. commodity substitutes eliminate material Nova value;
4. only Full Context has willingness to pay;
5. Reflex Compare has no incremental value;
6. marketplace users never establish direct Nova access;
7. licensed-data costs destroy viable gross margin;
8. payment friction exceeds useful context value;
9. unresolved responses destroy trust rather than preserve it;
10. Nova removal creates no meaningful reconciliation burden after genuine recurring use.

## Prohibited claims

Do not label the validation state as:

- product-market fit;
- adoption;
- pricing power;
- buyer pull;
- dependency;
- recurring revenue quality;
- production-grade institutional readiness.

until separately supported and accepted through the appropriate evidence process.

## Implementation order

1. freeze retail/institutional isolation contract;
2. implement common context-object schema;
3. implement State Ping and Context Delta first;
4. implement bounded x402 challenge/payment/delivery instrumentation;
5. verify actual payment economics;
6. add Contradiction Pack;
7. add read-only Reflex Compare against approved retail corpus;
8. add Full Context;
9. prepare nonexclusive marketplace manifests;
10. conduct external validation gates sequentially.

No later step should be used to excuse failure of an earlier gate.

## Success condition

The validation effort is successful enough to continue when external evidence begins showing the following loop without subsidy or coercion:

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

The strategic question is not whether Nova can generate API traffic.

It is whether decision context becomes an economic dependency because repeated reasoning is more costly without it.
