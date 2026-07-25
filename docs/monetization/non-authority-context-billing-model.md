# Non-Authority Context Billing Model

## Status

Proposed design only. This document does not change billing code, pricing,
payment configuration, x402 behavior, or production state.

```yaml
v2_billing:
  implementation_status: proposed_not_implemented
  initial_state: disabled
  outcome_dependent: false
  status_dependent: false
  payment_receipt_authority_effect: none
```

## Principle

Nova may eventually charge for constructing, proving, retaining, or privately
delivering review context. It must not charge for an institutional decision or
make payment a prerequisite for a favorable action outcome.

Payment for review context does not create institutional permission,
transaction approval, authorization, or execution entitlement.

## Permitted Billable Objects

```yaml
permitted_billable_objects:
  - context_packet_generation
  - proof_generation
  - telemetry_access
  - retained_chronology_service
  - private_institutional_integration
```

These objects are priced by measurable service work:

| Object | Potential unit | Authority effect |
|---|---|---|
| Context packet generation | Packet, request, or contracted capacity | None |
| Context-integrity proof generation | Proof artifact or proof capacity | None |
| Telemetry access | Request, volume, cadence, or subscription | None |
| Retained chronology service | Retention, retrieval, or institutional namespace | None |
| Private institutional integration | Deployment, support, or contracted capacity | None |

## Prohibited Billable Objects

The following are prohibited as v2 pricing units or product promises:

```yaml
prohibited_billable_objects:
  - approval
  - authorization
  - admission
  - permission
  - favorable_status
  - execution_entitlement
  - transaction_clearance
```

Legacy v1 terms such as `ALLOW` and `CONSTRAIN` may be referenced when
explaining the migration, but no future price, invoice, quota, credit, or
payment requirement may depend on those outcomes.

## Outcome Independence

The same packet-generation price applies when review context is:

- current or stale;
- complete or partial;
- consistent or conflicted; or
- available or unavailable when the unavailability itself can be described.

Charges may vary by compute, retention, proof scope, source volume, service
level, or delivery cadence. They may not vary based on the institution's likely
action or whether an internal classifier produced a favorable result.

```yaml
outcome_independence:
  context_state_changes_price: false
  source_state_changes_price: false
  review_completeness_changes_price: false
  internal_legacy_status_changes_price: false
  local_institutional_decision_changes_price: false
```

## Receipt Semantics

A payment receipt may prove only that:

- a defined service charge was paid;
- a packet, proof, telemetry unit, retention period, or integration service was
  purchased; and
- the payer may access that paid service within its access policy.

```yaml
payment_receipt:
  access_effect: scoped_service_access_only
  approval_effect: none
  authorization_effect: none
  execution_effect: none
  policy_satisfaction_effect: none
```

The receipt is not included in authority handoff as an institutional decision
artifact.

## Initial v2 Posture

Billing remains disabled for the initial private implementation and validation
cycle. This permits evaluation of:

- field derivation;
- local-authority comprehension;
- context-proof integrity;
- sensitive-data handling;
- tenancy isolation;
- completeness and conflict semantics; and
- operational cost.

Pricing should be considered only after those properties are validated and a
real service unit can be measured without reference to a domain outcome.

## Relationship to Legacy v1

Legacy v1 currently contains status-dependent prepaid billing and a separate
usage-accounting path. This document does not modify either path.

A later migration must:

1. inventory consumers of both billing paths;
2. separate legacy billing records from v2 records;
3. prevent a v2 charge from changing review-context state;
4. prevent an internal classification from changing v2 price;
5. define invoices and receipts in service-delivery terms; and
6. validate that nonpayment affects only service access, not the institution's
   authority over its prepared action.

## x402 Boundary

```yaml
x402:
  public_surface: disabled
  production_reopening: not_authorized
  v2_integration: not_part_of_initial_implementation
```

If separately authorized in the future, x402 may purchase:

- a context packet;
- telemetry access; or
- a context-integrity proof artifact.

It may not purchase permission, approval, transaction admission, or execution
authority. The existing public-containment defaults remain unchanged.

## Evidence Required Before Billing Design Implementation

- Approved v2 semantic and machine-readable contract.
- Demonstrated outcome-independent packet construction.
- Measured compute, proof, storage, or delivery cost.
- Consumer discovery and buyer evidence for the proposed unit.
- Tenant isolation and data-retention design.
- Invoice and receipt schema review.
- Clear behavior for quota, nonpayment, and infrastructure failure.
- Confirmation that billing errors cannot alter domain-state fields.
- Separate CCO, Architect, accepted-state, and chronology review as applicable.
