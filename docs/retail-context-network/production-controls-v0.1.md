# Nova Context Network — Retail Production Controls v0.1

**Gate:** RP7

**Scope:** durable retail operational containment required before a controlled
production proof. This repository implementation is not deployment or public
activation.

## Control boundary

```text
service admissibility
!= payment settlement
!= context epistemic state
!= decision authority
```

The control layer decides only whether the retail service may safely admit a
request and deliver an already-defined context resource. It never determines
whether evidence is true, context is resolved, confidence is high, an action
should occur, an action is approved, execution is authorized, or capital may
move.

The canonical Nova boundary remains:

```text
Agent prepares action.
Nova structures decision/review context.
Local authority or consuming agent decides.
External systems execute.
Nova does not execute.
```

## Persistence and operating mode

`SQLiteRetailProductionControlStore` provides transactional stdlib SQLite
persistence at the retail-owned configured path. The default path is derived
from the retail state namespace as
`.nova_retail/production_controls.sqlite3`.

The only modes are `disabled` and `controlled_proof`. Initialization is fail
closed at `disabled`; reopening the store preserves the last explicit operator
state. There is no public, live, or production-active mode and no HTTP control
route.

SQLite reference persistence provides durable single-node semantics. It is not
verified distributed or multi-instance persistence. RP8 must verify deployment
topology and durable storage before production operation can be claimed.

## Admission and rate limiting

Pre-payment admission runs before an x402 challenge. It requires:

- `controlled_proof` operating mode;
- a supported `state_ping` or `context_delta` resource;
- a healthy initialized control store;
- an available resource-aware fixed-window request allowance.

Only a SHA-256 domain-separated hash of the opaque retail subject is persisted.
Fixed-window counters use SQLite `BEGIN IMMEDIATE` transactions, persist across
reopen, and remain separate by subject, resource, and window.

Rate-limit denial means only that service availability was denied. It does not
reject context, deny an action, or deny a transaction.

## Payment consumption and delivery

RP7 accepts only RP6's successful process-local `RetailPaymentOutcome` access
capability. A copied or deserialized receipt remains audit evidence and is not a
bearer credential.

The first valid settlement claim creates one durable `pending` delivery record.
SQLite uniqueness constraints on `(network, transaction_reference)` and
`payment_receipt_id` atomically prevent duplicate eligibility. An exact replay
returns `payment_already_consumed`; conflicting reconciliation fields return
`payment_replay_conflict`.

Settlement and delivery remain separate:

```text
payment_settled != resource_delivered
```

Delivery transitions from `pending` to either `delivered` or `failed`. Completed
delivery stores only its timestamp, SHA-256 response digest, byte count, and
processing duration. The context body is never stored. A failure keeps the
payment consumed and creates no replacement entitlement.

Cross-process idempotent redelivery and full response replay/caching are RP8
integration concerns; RP7 does not claim those behaviors.

## Operational evidence and readiness

Retail telemetry and incidents use a dedicated namespace, bounded event types,
machine-readable timestamps, hashed transaction references in telemetry, and
`authority_effect: none`. They contain no raw payment payload, signature,
credential, authorization header, context body, institutional identifier,
chronology, or Reflex Memory state.

Payment telemetry is observational:

```text
payment event
!= buyer demand
!= adoption
!= pricing power
!= product-market fit
```

Readiness is limited to `not_ready` or `ready_for_controlled_proof`. It requires
the initialized store, explicit controlled-proof mode, valid rate limits,
payment-consumption persistence, and telemetry persistence. It never establishes
production readiness, deployment, public access, active settlement, or external
verification.

## Effects

```yaml
retail_runtime_effect: durable_production_control_contract_only
data_source_effect: none
payment_effect: durable_consumption_replay_and_delivery_reconciliation_controls
public_endpoint_effect: none
deployment_effect: none
facilitator_connection_effect: none
settlement_configuration_effect: none
public_activation_effect: none
marketplace_effect: none
institutional_Gate_5_effect: none
institutional_data_effect: none
chronology_effect: none
institutional_Reflex_Memory_effect: none
buyer_demand_effect: none
```
