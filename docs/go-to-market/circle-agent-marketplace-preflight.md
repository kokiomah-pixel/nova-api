# Circle Agent Marketplace Preflight

## Status

```yaml
status:
  classification: internal_research_and_preflight
  evidence_reference: MSE-2026-07-30-029
  public_application_authorized: false
  listing_authorized: false
  metadata_publication_authorized: false
  runtime_integration_authorized: false
  x402_integration_authorized: false
```

## Objective

This preflight determines whether Circle can serve as a future,
nonexclusive discovery channel without weakening Nova's institutional
position, confidentiality boundaries, authority boundary, pricing logic,
or institution-owned chronology.

Completion of this worksheet does not authorize an application or listing.

Circle is an example channel, not a Nova dependency. Buyer demand, recurring
operator need, retail-service demand, and Circle channel preference are
unvalidated.

## Source verification

```yaml
source_verification:
  exact_Circle_program_name:
  exact_source_title: Turn Your API Into an Agent-Ready Revenue Stream
  exact_source_url:
  publication_date:
  listing_application_url:
  documentation_url:
  current_program_status:
  verified_at:
  verified_by:

  rule: >
    Do not infer requirements from promotional copy alone. Record exact
    first-party documentation before recommending an application.
```

The exact first-party URL corresponding to the approved evidence title has not
been confirmed. Current Circle materials corroborate an Agent Marketplace, but
they do not resolve that provenance field. No URL or program requirement is
inferred here.

## Marketplace access model

```yaml
marketplace_access_model:
  public_listing_supported:
  private_listing_supported:
  unlisted_service_supported:
  organization_scoped_catalog_supported:
  tenant_scoped_credentials_supported:
  contract_backed_access_supported:
  confidential_invocation_supported:
  enterprise_allowlisting_supported:
  nonexclusive_distribution_permitted:
```

## Identity and authorization

```yaml
identity_and_authorization:
  how_agent_identity_is_established:
  how_organization_identity_is_established:
  whether_wallet_identity_is_treated_as_service_identity:
  whether_enterprise_contract_identity_is_supported:
  whether_marketplace_identity_can_bind_to_Nova_tenant_identity:
  whether_workflow_authorization_is_external_to_payment:
  whether_action_class_restrictions_are_supported:
```

Marketplace identity must not be assumed to bind to a Nova tenant. Institution
identity and workflow authorization must precede institution-owned source
access.

## Payment and metering

```yaml
payment_and_metering:
  x402_required_for_listing:
  USDC_required:
  payment_optional:
  contract_billing_supported:
  usage_metering_supported:
  institution_scoped_metering_supported:
  post_contract_metering_supported:
  payment_metadata_confidential:
  payment_success_creates_service_entitlement:

  required_Nova_answer:
    payment_success_creates_institutional_authority: false
```

Payment is not authentication, permission, enterprise tenancy, or authority.
No x402 or payment integration is authorized.

## Confidentiality and data

```yaml
confidentiality_and_data:
  request_content_visible_to_Circle:
  response_content_visible_to_Circle:
  payment_metadata_visible_to_marketplace:
  provider_metadata_public:
  tenant_identity_public:
  data_residency_options:
  retention_controls:
  deletion_controls:
  logging_controls:
  subcontractor_visibility:
```

Retail access must not reach institution-owned data. Retail and institutional
planes may not share an invocation endpoint, credentials, data store, source
registry, cache, chronology, or Reflex Memory namespace.

## Chronology and ownership

```yaml
chronology_and_ownership:
  who_owns_invocation_history:
  who_retains_service_use_records:
  whether_marketplace_can_access_institutional_context:
  whether_marketplace_can_replay_requests:
  whether_marketplace_can_use_request_data_for_training:
  whether_Nova_can_preserve_institution_owned_chronology_independently:
  what_survives_when_the_distribution_channel_changes:
```

Circle must not become the owner of institutional context or chronology.
Automatic retail-to-institutional chronology migration and cross-plane Reflex
Memory are prohibited.

## Internal listing draft

```yaml
internal_listing_draft:
  service_name: Sharpe Nova OS Review Context

  service_class: institutional_private

  capability: >
    Structures institution-defined review context around a proposed
    capital action and surfaces what appears present, missing, stale,
    conflicting, unavailable, or unresolved for local authority.

  intended_user: >
    Authenticated institutional workflows preparing consequential
    capital actions for local review.

  access_model: >
    Public capability discovery may be considered separately.
    Institution-specific invocation is private, tenant-scoped,
    workflow-authorized, and governed by enterprise agreement.

  authority_boundary: >
    Nova does not approve, decline, authorize, sign, settle, route,
    underwrite, or execute financial actions. Local institutional
    authority remains responsible for the decision.

  data_boundary: >
    Retail or anonymous marketplace access does not provide access to
    institution-owned evidence, chronology, authority maps, constraints,
    source connections, or tenant configuration.

  does_not:
    - approve
    - decline
    - authorize
    - execute
    - settle
    - sign
    - route
    - underwrite
    - certify_compliance
    - grant_transaction_permission
    - create_enterprise_tenancy_through_payment

  publication_authorized: false
  marketplace_submission_authorized: false
```

This draft is internal research only. It is not public metadata and creates no
listing authority.

## Prohibited public metadata

```yaml
prohibited_public_metadata:
  - institution_names
  - tenant_identifiers
  - institution_specific_constraints
  - authority_maps
  - private_source_names
  - connector_details
  - chronology_identifiers
  - Reflex_Memory_content
  - private_action_classes
  - client_pricing
  - confidential_retention_terms
  - credential_patterns
  - infrastructure_secrets
```

## Commercial research boundary

```text
Retail commercial object:
A separately approved bounded service using public, synthetic,
or user-supplied non-institutional information.

Institutional commercial object:
A private configured review environment covering recurring
institutionally governed action classes, approved sources,
constraint applicability, authority handoff, and institution-owned chronology.
```

```yaml
commercial_research_boundary:
  marketplace_as_discovery_channel: approved_for_research
  enterprise_license: approved_for_research
  enterprise_license_plus_usage: approved_for_research
  private_machine_invocation: approved_for_research
  institution_scoped_metering: approved_for_research
  Circle_as_nonexclusive_channel: required

  anonymous_public_context_sales: rejected_for_now
  public_access_to_institutional_chronology: prohibited
  payment_as_authentication: prohibited
  payment_as_enterprise_tenancy: prohibited
  retail_price_as_institutional_anchor: prohibited
```

No pricing, revenue, buyer-demand, or product-market-fit claim is approved.

## Gating sequence

```text
1. Credible institutional operator identified.
2. Recurring capital-action workflow identified.
3. Named workflow owner identified.
4. Named local authority identified.
5. Institutional permission model documented.
6. Machine invocation requested by the operator.
7. Data ownership and classification documented.
8. Confidentiality and retention boundaries documented.
9. Public discovery versus private invocation resolved.
10. Retail and institutional isolation requirements documented.
11. Synthetic restricted test resource prepared.
12. Exact Circle marketplace requirements verified.
13. Circle marketplace preflight completed.
14. Separate CCO approval for controlled test listing.
15. Separate Architect authorization.
16. Separate runtime engineering authorization.
17. Separate security and production-readiness review.
```

No step may be skipped because Circle is accepting applications or because
x402 makes payment technically simple.

## Category protection

Nova is not a generic risk API, retail investment-recommendation API, public
compliance check, public transaction-clearance service, marketplace
authorization service, x402 entitlement service, wallet-controlled governance
service, Circle-native governance product, or marketplace-owned institutional
context layer.

```text
Marketplace discovery may identify the capability.

Retail usage, if separately authorized, remains non-institutional.

Institutional Nova remains private, tenant-scoped decision-context
infrastructure before local authority acts.
```

> Circle may provide a marketplace, machine customer, wallet, payment rail, or
> discovery surface. Nova must preserve institutional context, source
> authority, constraint applicability, unresolved conditions, local-authority
> handoff, and institution-owned chronology independently of Circle.

## Current disposition

```yaml
current_preflight_disposition:
  Circle_strategic_relevance: high
  internal_preflight: approved
  operator_research: approved
  internal_listing_draft: approved
  public_discovery_private_invocation_hypothesis: approved_for_validation
  three_access_class_architecture: required
  public_application: deferred
  controlled_test_listing: not_authorized
  runtime_engineering: not_authorized
  x402_metering: not_authorized
```
