# Incident Closure Standard

## Purpose

This standard defines when the public discovery, documentation, x402, and
production-custody incident may be closed. Repository normalization and current
external containment are necessary evidence, but they do not by themselves
establish control-plane custody or reconstruct historical activity.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Closure Principles

- Closure is evidence-based and approved by the Architect after CCO review.
- Current control and historical reconstruction are evaluated separately.
- Missing retained logs are a disclosed historical limitation, not evidence of
  zero activity.
- A repository merge, successful deployment, or healthy response is not by
  itself incident closure.
- Any reappearance of a prohibited public surface reopens the incident.

## Outcome: CLOSED

```yaml
CLOSED:
  requirements:
    Render_access_restored: true
    deployed_commit_attested: true
    containment_flags_attested: true
    API_key_inventory_complete: true
    retained_route_logs_reviewed: true
    CDP_activity_reviewed: true
    successful_unexpected_settlement: false
    current_external_containment_verified: true
```

`CLOSED` requires an evidence receipt for every requirement. If the applicable
retention period contains gaps that prevent the required activity review, use
`CONTAINED_HISTORICALLY_UNATTESTED`.

## Outcome: CONTAINED_HISTORICALLY_UNATTESTED

```yaml
CONTAINED_HISTORICALLY_UNATTESTED:
  meaning: >
    Current production ownership and containment are attested, but historical
    consumer or payment activity cannot be fully reconstructed because retained
    records are unavailable.
```

Required current-control evidence:

```yaml
requirements:
  Render_access_restored: true
  current_deployed_commit_attested: true
  current_containment_flags_attested: true
  current_API_key_ownership_attested: true
  current_settlement_configuration_attested: true
  CDP_current_ownership_attested: true
  current_external_containment_verified: true
  historical_retention_gap_documented: true
  unsupported_zero_activity_claims: false
```

This outcome closes the active exposure while preserving the historical
unknown. It must not be represented as proof that no Legacy v1 consumer,
verification request, or settlement ever existed.

## Outcome: OPERATIONALLY_OPEN

Use this outcome while any of the following remain unknown:

```yaml
OPERATIONALLY_OPEN:
  conditions:
    - production_account_ownership
    - deployed_commit
    - effective_containment_flags
    - current_API_key_ownership
    - current_settlement_configuration
```

The current incident remains `OPERATIONALLY_OPEN` because Render and CDP
control-plane access, deployed source, effective flags, key ownership, route
activity, and settlement activity have not been fully attested.

## Required Closure Evidence

```yaml
incident_closure_receipt:
  incident_id:
  opened_at_UTC:
  closure_reviewed_at_UTC:
  outcome:

  production_custody:
    Render_owner:
    service_id:
    deployed_commit:
    expected_commit:
    commit_matches:
    effective_containment_flags:

  credentials:
    API_key_inventory_complete:
    unknown_owner_count:
    CDP_credential_custody_attested:

  activity_review:
    review_window:
    retention_limit:
    route_logs_reviewed:
    CDP_activity_reviewed:
    successful_unexpected_settlement:
    historical_gaps: []

  external_verification:
    observed_at_UTC:
    health:
    OpenAPI:
    Swagger:
    ReDoc:
    services_manifest:
    feed:
    context_without_key:
    proof_without_key:
    payment_metadata_present:

  authorization:
    CCO_classification:
    Architect_final_decision:
    decided_at_UTC:
```

The private receipt must not contain secrets, key prefixes, payment signatures,
wallet addresses, request bodies, action payloads, personal identifiers, or raw
provider-account data.

## Closure Procedure

1. Restore authenticated Render and CDP control-plane access.
2. Complete the production control-plane attestation.
3. Reconcile the deployed commit with the expected repository commit.
4. Verify all current containment flags and legacy aliases.
5. Inventory production keys and classify unknown ownership.
6. Review retained route and payment activity within the available window.
7. Record retention gaps without inferring absent history.
8. Run external public-boundary verification.
9. Select the evidence-supported outcome.
10. Obtain CCO classification and the Architect's final closure decision.
11. Update the production readiness register.

## Reopen Triggers

```yaml
reopen_incident_when:
  - OpenAPI_or_docs_return_200
  - services_manifest_returns_200
  - x402_feed_returns_402
  - payment_or_wallet_metadata_reappears
  - unauthenticated_v1_returns_domain_response
  - deployed_commit_becomes_unrecognized
  - successful_unexpected_settlement_is_discovered
  - credential_custody_becomes_uncertain
  - public_authentication_boundary_regresses
```

On a reopen trigger, use the emergency change and break-glass runbook. Suspend or
contain the affected surface when source, configuration, or custody cannot be
established promptly.

## Product Progression Effect

While the incident is `OPERATIONALLY_OPEN`:

- Legacy v1 consumer dependency remains unverified;
- v2 field derivation remains blocked;
- the private v2 adapter remains not started;
- institutional pilots remain not started;
- public machine discovery remains blocked;
- x402 and payment activation remain blocked.

`CONTAINED_HISTORICALLY_UNATTESTED` may permit the next design review only when
current custody is complete and the Architect explicitly accepts the disclosed
historical limitation. It does not authorize implementation or activation by
itself.
