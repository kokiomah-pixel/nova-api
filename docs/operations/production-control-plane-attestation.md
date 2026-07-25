# Production Control-Plane Attestation

## Purpose

This document is the evidence template for attesting Render, production API-key,
route-activity, and Coinbase Developer Platform control. Empty fields are not
attested facts. Complete the template from the relevant control planes without
copying secret values or sensitive request data.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Attestation Rules

- The Architect performs or directly supervises authenticated control-plane
  inspection.
- Record presence, counts, effective states, identifiers needed for custody,
  and bounded timestamps only.
- Never store secret values, key prefixes, payment signatures, request bodies,
  action payloads, IP addresses, wallet addresses, account numbers, personal
  identifiers, or private provider data.
- Use `unknown` when the relevant view, log, or retention period is unavailable.
- External HTTP observations may support route behavior but cannot substitute
  for deployed-commit, environment, credential, or account-ownership evidence.

## Render Ownership

```yaml
Render_attestation:
  account_owner: Kome_Okiomah
  workspace:
  service_name:
  service_id:
  public_origin:
  repository:
  deployment_branch:
  deployed_commit_SHA:
  expected_commit_SHA:
  commit_matches:
  deployment_id:
  deployed_at_UTC:
  auto_deploy_enabled:
  access_verified_at_UTC:
```

Required evidence:

- authenticated Render account and workspace view;
- service identity and repository binding;
- deployment branch and exact deployed commit;
- deployment event identifier and timestamp;
- current auto-deploy posture;
- confirmation that the observer has the authority claimed.

## Render Environment

Record presence and effective state only. Do not record values for secrets.

```yaml
Render_environment:
  NOVA_PUBLIC_API_DOCUMENTATION_ENABLED:
    present:
    effective_value:

  NOVA_PUBLIC_SERVICE_DISCOVERY_ENABLED:
    present:
    effective_value:

  NOVA_PUBLIC_X402_ENABLED:
    present:
    effective_value:

  NOVA_X402_SETTLEMENT_ENABLED:
    present:
    effective_value:

  NOVA_RUNTIME_MODE:
    present:
    effective_value:

  NOVA_KEYS_JSON:
    present:

  NOVA_API_KEY:
    present:

  CDP_API_KEY_ID:
    present:

  CDP_API_KEY_SECRET:
    present:
```

```yaml
required_containment:
  public_API_documentation: false
  public_service_discovery: false
  public_x402: false
  settlement: false
```

The attestation fails if a current or legacy environment variable overrides a
required containment state. Secret presence does not prove use, ownership,
rotation status, or settlement inactivity.

## Production API-Key Inventory

```yaml
production_API_key_inventory:
  storage_type:
  total_active:
  suspended:
  expired:

  owner_classification:
    Architect_internal:
    development:
    test:
    external:
    unknown:

  endpoint_scope:
    with_v1_context_access:
    with_v1_proof_access:
    with_billing_access:
    with_admin_access:

  activity_metadata:
    with_last_seen:
    without_last_seen:
```

Do not store:

- key values or prefixes;
- names or email addresses;
- wallet addresses;
- Stripe or provider customer identifiers;
- free-form notes that identify a consumer.

Counts must reconcile to the provider or application source. A key with unknown
ownership remains an unresolved custody risk even when it has no recorded
activity.

## Route Activity

```yaml
route_activity:
  review_window:
    from_UTC:
    through_UTC:
    retention_limit:

  v1_context:
    total:
    authenticated:
    unauthenticated:
    successful:
    failed:
    unique_pseudonymous_actors:

  v1_proof:
    total:
    authenticated:
    unique_pseudonymous_actors:

  discovery:
    OpenAPI:
    Swagger:
    ReDoc:
    services_manifest:
    constraint_pressure:

  payment:
    payment_headers_received:
    facilitator_verify_attempts:
    facilitator_settle_attempts:
    successful_settlements:
```

Do not record request bodies, response bodies, IP addresses, payment signatures,
action payloads, raw API keys, or other direct identifiers. If the available
logs cannot distinguish authentication or pseudonymous actors, record that
limitation instead of estimating.

## CDP Attestation

```yaml
CDP_attestation:
  account_owner: Kome_Okiomah
  organization:
  project:
  access_verified_at_UTC:

  review_window:
    from_UTC:
    through_UTC:

  verification_requests:
  successful_verifications:
  failed_verifications:

  settlement_requests:
  successful_settlements:
  failed_settlements:
```

The CDP review must distinguish current credential custody from historical
verification or settlement activity. Zero retained events must not be presented
as proof that no historical event occurred when retention is incomplete.

## External Route Cross-Check

After control-plane inspection, externally verify:

```yaml
expected_public_boundary:
  health: 200
  OpenAPI: 404
  Swagger: 404
  ReDoc: 404
  services_manifest: 404
  constraint_pressure_feed: 404
  v1_context_without_key: 401
  v1_proof_without_key: 401
  payment_metadata_present: false
```

A mismatch triggers the emergency change and break-glass runbook. Matching
responses complete only the external cross-check, not the control-plane
attestation.

## Attestation Outcome

```yaml
production_control_plane_attestation:
  Render_ownership_attested:
  deployed_commit_attested:
  containment_flags_attested:
  API_key_inventory_complete:
  route_activity_review_complete:
  CDP_ownership_attested:
  CDP_activity_review_complete:
  successful_unexpected_settlement:
  external_boundary_verified:
  historical_retention_complete:
  remaining_unknowns: []
  attested_by: Kome_Okiomah
  attested_at_UTC:
  CCO_review_status:
```

The outcome remains incomplete while any required fact is blank, unknown, or
unsupported by its named control plane.
