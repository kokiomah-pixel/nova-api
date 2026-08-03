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
  exact_Circle_program_name: Circle Agent Marketplace

  canonical_first_party_article:
    title: Turn Your API into a Storefront for Agents
    url: https://www.circle.com/blog/turn-your-api-into-a-storefront-for-agents
    publication_date: 2026-05-18

  source_label_as_supplied:
    title: Turn Your API Into an Agent-Ready Revenue Stream
    exact_title_match: false

  source_match_status: first_party_content_match_with_title_mismatch

  supporting_sources:
    - title: Agent Marketplace
      url: https://agents.circle.com/services
      role: corroborates_machine_discovery_service_catalog_and_paid_API_access

    - title: Circle for Agents
      url: https://agents.circle.com/
      role: corroborates_payment_as_authentication_public_framing

  listing_application_url:
  technical_documentation_url:
  private_listing_documentation_url:

  current_program_status: live_public_marketplace_surface
  verified_at: 2026-07-30
  verified_by: Jarvis-Nova_CCO

  verification_limit: >
    Public first-party materials confirm the article, marketplace, x402 and
    USDC payment direction, and payment-as-authentication framing. They do not
    establish private listing support, institution-scoped tenancy,
    confidential invocation, contract-backed metering, or suitability for
    Sharpe Nova OS.
```

The original Market-Signal Extraction title does not exactly match Circle's
canonical article title.

Both are preserved in the verification record.

The Circle article, Agent Marketplace, and Circle for Agents surfaces confirm
the general machine-discovery and payment direction. They do not resolve the
private-invocation, institutional-identity, confidentiality, retention,
enterprise-contract, or tenant-isolation questions in this preflight.

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
  whether_Circle_payment_is_described_as_authentication: true
  whether_that_authentication_is_sufficient_for_Nova_tenancy: false
  what_additional_enterprise_identity_binding_is_required:
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
  Circle_public_payment_framing: payment_as_authentication
  Nova_institutional_interpretation: commercial_access_only

  required_Nova_answer:
    payment_success_creates_institutional_authority: false
```

Payment is not authentication, permission, enterprise tenancy, or authority.
No x402 or payment integration is authorized.

### Payment-as-authentication category boundary

Circle publicly uses the phrase “Payment as authentication.”

For this preflight, that phrase is treated as a commercial machine-resource
access pattern, not as an institutional identity or authority model.

Required Nova interpretation:

```yaml
payment_authentication_boundary:
  payment_may_satisfy_commercial_access_condition: true

  payment_establishes:
    institutional_identity: false
    enterprise_tenancy: false
    workflow_authorization: false
    action_class_permission: false
    institution_owned_data_entitlement: false
    private_chronology_access: false
    institutional_Reflex_Memory_access: false
    source_authority: false
    review_completeness: false
    local_decision_authority: false
    capital_action_approval: false
```

A successful marketplace payment without prior institutional authentication
and workflow authorization must not proceed as an institution-specific Nova
request.

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

## Initial marketplace SKU claim-field refinement

The initial marketplace SKU remains:

```text
Review Context Packet Validator
```

This is a bounded design refinement of the internal listing draft, not a public
listing, manifest, callable marketplace service, or replacement SKU.

```yaml
marketplace_SKU_refinement:
  SKU_name: Review Context Packet Validator
  status: internal_schema_design_only
  public_listing_authorized: false
  runtime_implementation_status: not_implemented

  optional_claim_fields:
    claim_origin_type:
    originator_reference:
    novelty_asserted:
    novelty_review_status:
    validation_records: []
    institutional_applicability_status:
    result_lineage_reference:

  service_behavior:
    validates_field_presence: true
    validates_declared_status_structure: true
    identifies_missing_validation_scope: true
    identifies_unreviewed_applicability: true

    verifies_mathematical_truth: false
    determines_actual_novelty: false
    certifies_model_reliability: false
    ranks_models: false
    decides_institutional_reliance: false
    approves_actions: false
    executes_actions: false
```

> The service records how a claim originated, how it was validated, which
> assumptions remain, and whether institutional applicability has been
> reviewed. It does not determine whether a model is generally trustworthy or
> whether the institution should rely on the claim.

The SKU must not be presented as AI truth verification, hallucination
elimination, frontier-model certification, a model trust score, a
scientific-proof engine, guaranteed correctness, or an institutional approval
API.

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
