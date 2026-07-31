# Agent Access-Class Separation

## Status

```yaml
status:
  classification: approved_specification_level_concept
  primary_evidence_reference: MSE-2026-07-30-029
  related_evidence_reference: MSE-2026-07-30-028
  product_requirement_validated: false
  operator_need_validated: false
  public_listing_authorized: false
  retail_service_authorized: false
  runtime_implementation_authorized: false
```

## Purpose

This specification defines a clean architectural break between:

1. public machine discovery;
2. optional future retail agent usage;
3. private institutional review-context infrastructure.

The specification protects institution-owned data, private chronology,
tenant configuration, authority mappings, constraints, evidence sources,
commercial value, and category coherence.

It does not authorize implementation.

Circle is one example channel referenced by market signal
[`MSE-2026-07-30-029`](../market/signals/2026/MSE-2026-07-30-029-circle-agent-marketplace.md).
The specification is provider-neutral and applies to agent marketplaces, API
directories, MCP catalogs, service registries, wallet discovery systems,
gateway catalogs, and future machine-service distribution venues.
Distribution must remain nonexclusive.

## Governing boundary

> Public discovery, retail agent usage, and institutional review context are
> separate access classes. Retail agents may never reach institution-owned
> data, private chronology, authority maps, constraints, evidence sources, or
> tenant configuration through payment, endpoint reuse, credential upgrades,
> subscription upgrades, wallet ownership, metadata submission, or shared
> infrastructure.

```text
Marketplace discovery may identify Nova.

Marketplace payment does not authenticate an institution.

Retail access does not create enterprise tenancy.

Institution-owned review context remains private,
tenant-scoped, workflow-authorized, and institution-controlled.
```

Agent prepares action. Nova structures review context. Local authority decides.
External systems execute. Nova does not execute.

## Access classes

```yaml
access_classes:
  public_discovery:
    purpose:
      - expose_boundary_safe_capability_metadata
      - allow_agents_to_identify_Nova
      - describe_access_requirements
      - direct_qualified_institutions_to_onboarding

    callable: false
    payment_required: false
    institution_specific_data_access: false
    institutional_chronology_access: false
    authority_effect: none

  retail_agent_service:
    status: future_separate_approval_required

    permitted_data:
      - public_information
      - synthetic_information
      - explicitly_user_supplied_non_institutional_information
      - bounded_public_telemetry

    prohibited_data:
      - institution_owned_evidence
      - institution_specific_constraints
      - authority_maps
      - private_policy_documents
      - institutional_chronology
      - tenant_source_connections
      - confidential_action_context
      - institution_private_Reflex_Memory
      - institution_specific_configuration

    output_status:
      institution_specific_review_context: false
      institutionally_authoritative: false
      local_authority_ready: false
      capital_action_approved: false

  institutional_review_context:
    access:
      - private
      - authenticated
      - tenant_scoped
      - workflow_authorized
      - action_class_restricted
      - contract_and_policy_governed

    permitted_data:
      - institution_owned_evidence
      - institution_approved_sources
      - institution_specific_constraints
      - institution_defined_authority_maps
      - private_chronology
      - tenant_configuration
      - institution_governed_Reflex_Memory

    ownership:
      configuration: institution_controlled
      chronology: institution_owned
      retention: contract_and_policy_defined
      local_authority: preserved

    marketplace_payment_sufficient: false
```

Public discovery is non-callable metadata. A retail service would require a
separate business case, service identity, data plane, approval, and runtime
review. Institutional context remains private and institution-controlled.

## Hard-separation rule

```text
Shared capability description may be acceptable.

Shared credentials, tenant identities, data stores, caches,
source registries, encryption keys, logs, retention policies,
chronology namespaces, Reflex Memory namespaces, and billing
entitlements are not acceptable between retail and institutional planes.
```

```yaml
separation_standard:
  shared_public_capability_description: conditionally_permitted

  shared_invocation_endpoint: prohibited
  shared_tenant_credentials: prohibited
  shared_API_keys: prohibited
  shared_data_store: prohibited
  shared_vector_store: prohibited
  shared_cache: prohibited
  shared_source_registry: prohibited
  shared_encryption_keys: prohibited
  shared_chronology: prohibited
  shared_Reflex_Memory: prohibited
  shared_retention_policy: prohibited
  shared_training_corpus: prohibited_by_default
  cross_plane_querying: prohibited
  payment_based_tier_escalation: prohibited
  subscription_based_tenant_escalation: prohibited
  wallet_based_tenant_escalation: prohibited
  silent_request_rerouting: prohibited
```

## Identity and routing

```yaml
routing_boundary:
  retail_request:
    may_enter_institutional_plane: false
    automatic_upgrade: false
    payment_triggered_upgrade: false
    API_key_tier_upgrade: false
    wallet_triggered_upgrade: false
    institution_name_triggered_upgrade: false

  institutional_request:
    required_before_source_access:
      - recognized_institution
      - authenticated_tenant_identity
      - authorized_workflow
      - permitted_action_class
      - approved_source_scope
      - retention_policy
```

> Classification and authorization must occur before institution-owned sources,
> tenant configuration, chronology, or Reflex Memory are accessed.

Payment, wallet ownership, marketplace identity, an API-key tier, or a
subscription does not establish institutional identity or workflow authority.

## Request-data classification

```yaml
request_data_classes:
  public:
    permitted_surface:
      - public_discovery
      - separately_authorized_retail_service
    institutional_routing: prohibited

  synthetic:
    permitted_surface:
      - separately_authorized_retail_service
      - bounded_internal_testing
    institutional_claims: prohibited

  user_owned_non_institutional:
    permitted_surface:
      - separately_authorized_retail_service
    institutional_review_status: none
    automatic_institutional_migration: prohibited

  institution_owned:
    permitted_surface:
      - institutional_review_context
    tenant_identity_required: true
    workflow_authorization_required: true

  ambiguous:
    default_treatment:
      - reject
      - request_clarification
    automatic_routing: prohibited
    source_access: prohibited
```

Data supplied to a retail plane does not become institutional merely because
an institution is named or payment succeeds.

## Endpoint discipline

```yaml
endpoint_boundary:
  institutional:
    canonical_endpoint: /v1/context
    current_status: private_authenticated_Legacy_v1_surface
    retail_use: prohibited
    public_marketplace_use: prohibited

  public_discovery:
    future_surface_type:
      - static_boundary_safe_metadata
      - non_callable_manifest
    institution_context_access: false
    publication_authorized: false

  retail:
    use_v1_context: false
    separate_service_identity_required: true
    separate_endpoint_review_required: true
    current_authorization: none

  Circle_specific_endpoint:
    permitted: false
```

The current private authenticated Legacy v1 surface is not the approved future
external contract. This specification preserves the repository's architecture
transition notice and does not authorize a replacement contract, endpoint,
manifest, or public exposure.

## Chronology separation

```yaml
chronology_boundary:
  retail_activity:
    may_enter_institutional_chronology: false
    may_influence_institutional_Reflex_Memory_automatically: false
    retention: separate_policy
    institutional_significance: none_by_default

  institutional_activity:
    chronology_owner: institution
    tenant_scoped: true
    cross_tenant_access: prohibited
    marketplace_access: prohibited
    retail_access: prohibited

  cross_plane_migration:
    automatic: false
    payment_triggered: false
    subscription_triggered: false
    wallet_triggered: false

    requires:
      - recognized_institution
      - explicit_institutional_authorization
      - provenance_review
      - data_classification_review
      - separate_governed_acceptance
```

No chronology candidate, event, migration, or ingestion behavior is created by
this specification.

## Reflex Memory separation

```yaml
Reflex_Memory_boundary:
  retail_memory:
    institution_specific: false
    may_read_institutional_memory: false
    may_write_institutional_memory: false

  institutional_memory:
    tenant_scoped: true
    institution_governed: true
    retail_access: prohibited
    marketplace_access: prohibited

  cross_plane_learning:
    default: prohibited
    payment_authorizes_transfer: false
    aggregate_training_authorized: false
    requires_separate_governance_review: true
```

No Reflex Memory learning object or runtime mutation is created.

## Authentication, payment, and authority

```text
Discoverable
≠ callable
≠ retail-accessible
≠ institutionally authenticated
≠ tenant-authorized
≠ paid
≠ institutionally permitted
≠ source-authoritative
≠ review complete
≠ capital-action approval
```

```text
Marketplace payment
≠ authentication
≠ enterprise tenancy
≠ institutional authorization
≠ access to institution-owned data
≠ access to institutional chronology
≠ authority
```

## Commercial separation

```yaml
commercial_separation:
  retail_surface:
    status: separate_business_case_required
    possible_future_models:
      - bounded_subscription
      - bounded_usage
      - public_metering
    institutional_entitlement_created: false

  institutional_surface:
    primary_value_units:
      - governed_action_class
      - institutional_review_environment
      - private_configuration
      - approved_source_connectivity
      - authority_handoff
      - institution_owned_chronology
      - recurring_workflow_coverage

    anonymous_access: prohibited
    marketplace_payment_as_authentication: prohibited
    retail_price_anchor: prohibited
```

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

```text
Weak interpretation:
Nova is an API call that any paying agent can purchase.

Stronger institutional interpretation:
Nova is a configured review-context environment that becomes required
within recurring institutionally governed action classes.
```

Pricing, buyer demand, product-market fit, and channel preference remain
unvalidated.

## Failure behavior

```yaml
failure_behavior:
  ownership_unclear:
    action: reject_or_request_clarification

  tenant_identity_absent:
    institution_source_access: deny

  workflow_authorization_absent:
    institution_source_access: deny

  payment_successful_but_institutional_permission_absent:
    institution_specific_invocation: deny

  retail_request_contains_institution_reference:
    automatic_upgrade: deny
    institution_lookup: deny

  cross_plane_data_request:
    action: deny_and_record_security_event_if_runtime_is_ever_built
```

The security-event language is conceptual only. It does not authorize logging
or runtime implementation.

## Category protection

Nova is not:

- a generic retail intelligence API;
- a marketplace compliance check;
- a payment-authenticated authority service;
- an x402 entitlement layer;
- a wallet-policy engine;
- a public financial recommendation endpoint;
- a transaction-clearing service;
- a marketplace-owned institutional data layer.

Public discovery may describe Nova.

Retail access, if separately authorized, may operate only on non-institutional
data.

Institutional Nova remains private decision-context infrastructure before local
authority acts.

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

## Authorization boundary

```yaml
authorization_boundary:
  specification_only: true
  runtime_behavior_authorized: false
  public_listing_authorized: false
  public_manifest_authorized: false
  retail_service_authorized: false
  Circle_integration_authorized: false
  x402_authorized: false
  chronology_mutation_authorized: false
  Reflex_Memory_mutation_authorized: false
```
