# Production Readiness Register

## Purpose

This register is the canonical readiness view for repository governance,
production custody, Legacy v1 dependency, v2 progression, institutional use,
monetization, and machine discovery. Readiness is evidence-based and does not
convert unknown production history into a favorable claim.

## Public current-state authority

For the compressed public system status, see:

- [Current State](../../CURRENT_STATE.md)

This register provides gate-level detail.

It does not permit a reader to combine a `READY` subcomponent with blocked
production controls and conclude that Sharpe Nova OS is system-wide
production-ready.

```yaml
public_claim_summary:
  repository_governance: ready
  Legacy_v1_runtime: implemented
  target_v2_contract: approved
  target_v2_runtime: not_implemented
  target_v2_production: not_active
  institutional_pilot: not_started
  production_custody_attestation: not_complete
  system_wide_production_readiness: not_established
```

## Canonical Boundary

Sharpe Nova OS is a pre-execution decision discipline layer that conditions
capital through telemetry, Reflex Memory, and constraint logic before execution.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Readiness States

```yaml
readiness_states:
  READY:
    meaning: evidence_complete_and_gate_satisfied

  CONDITIONALLY_READY:
    meaning: safe_for_bounded_internal_use_with_known_limitations

  BLOCKED:
    meaning: a_required_dependency_or_control_is_missing

  NOT_STARTED:
    meaning: work_has_not_begun
```

## Current State

The following state is a point-in-time governance snapshot, not live telemetry.
It must be refreshed only from a named evidence receipt.

```yaml
state_snapshot:
  as_of_UTC: "2026-07-25T14:17:27Z"
  evidence_scope:
    - GitHub_repository_governance
    - externally_observed_public_runtime_behavior
  excluded_from_attestation:
    - Render_control_plane_custody
    - deployed_commit
    - effective_production_flags
    - production_API_keys
    - retained_route_activity
    - CDP_activity
```

```yaml
current_state:
  GitHub:
    main_protected: true
    pull_requests_required: true
    required_CI_enabled: true
    force_pushes_blocked: true
    branch_deletion_blocked: true
    required_approvals: 0
    Architect_admin_bypass: true

  public_runtime:
    health: available
    OpenAPI: contained
    Swagger: contained
    ReDoc: contained
    services_manifest: contained
    public_x402: contained
    unauthenticated_v1: blocked

  production_control:
    primary_owner: Kome_Okiomah
    Render_control_plane_attested: false
    CDP_control_plane_attested: false
    deployed_commit_attested: false
    production_keys_inventoried: false
    route_activity_reviewed: false
    settlement_activity_reviewed: false

  Legacy_v1:
    implemented: true
    model: decision_admission
    consumer_dependency: unverified
    new_external_integrations: prohibited

  proposed_v2:
    contract_approved: true
    implemented: false
    production_active: false
```

A later reader must not treat this snapshot as evidence that the current
production deployment still matches these observations. Production state
requires a newer control-plane attestation and external verification receipt.

## Production Readiness

```yaml
production_readiness:
  repository_governance:
    status: READY
    evidence:
      - main_protected
      - required_CI
      - product_generation_labeling
      - force_push_blocked

  public_runtime_containment:
    status: CONDITIONALLY_READY
    limitation: external_behavior_verified_but_control_plane_not_attested

  Render_custody:
    status: BLOCKED

  CDP_custody:
    status: BLOCKED

  deployed_commit_attestation:
    status: BLOCKED

  production_key_inventory:
    status: BLOCKED

  route_activity_inventory:
    status: BLOCKED

  settlement_activity_inventory:
    status: BLOCKED

  incident_closure:
    status: BLOCKED

  Legacy_v1_dependency:
    status: BLOCKED

  v2_contract_design:
    status: READY

  v2_field_derivation:
    status: BLOCKED

  v2_adapter:
    status: NOT_STARTED

  v2_public_endpoint:
    status: NOT_STARTED

  institutional_pilot:
    status: NOT_STARTED

  public_marketplace_discovery:
    status: BLOCKED

  x402_or_payment_activation:
    status: BLOCKED
```

`READY` for repository governance does not mean production is fully governed.
The Architect's administrator bypass remains a documented sole-operator
limitation, and no independent human approval is presently required.

## Product Progression Gates

```yaml
product_progression:
  Gate_1:
    name: production_custody
    requirement:
      - Render_attested
      - CDP_attested
      - credentials_under_Architect_control

  Gate_2:
    name: Legacy_v1_dependency
    requirement:
      - keys_inventoried
      - logs_reviewed
      - consumers_classified

  Gate_3:
    name: v2_field_derivation_design
    requirement:
      - Gate_1_complete
      - Gate_2_complete
      - canonical_derivation_rules_defined
      - proof_canonicalization_defined

  Gate_4:
    name: private_v2_adapter
    requirement:
      - design_approved
      - synthetic_only
      - no_public_endpoint
      - no_production_activation

  Gate_5:
    name: bounded_institutional_pilot
    requirement:
      - local_authority_handoff_verified
      - non_authority_contract_preserved
      - data_retention_defined
      - support_and_incident_process_defined
      - one_bounded_workflow

  Gate_6:
    name: monetization
    requirement:
      - pricing_buys_context_access_not_authority
      - billing_not_conditioned_on_ALLOW_DENY_or_HALT
      - usage_metering_verified
      - customer_terms_reviewed

  Gate_7:
    name: machine_discovery
    requirement:
      - v2_is_the_public_contract
      - Legacy_v1_isolated
      - marketplace_metadata_reviewed
      - MCP_OpenAPI_x402_and_registry_surfaces_reviewed
```

Gates are sequential unless a later gate explicitly states otherwise. Design
work may be prepared privately only within its authorized change class; no gate
permits public activation by implication.

## Monetization Boundary

Commercial expansion follows the evidence-gated
[Commercialization Sequence](../go-to-market/commercialization-sequence.md).

Payment may purchase access, coverage, retention, evidence packaging,
reproducibility, review-profile support, or institutional service levels.

Payment must not purchase approval, admission, authorization, permission,
execution, or a favorable decision outcome.

```yaml
pricing_anchors:
  prohibited:
    - price_per_ALLOW
    - price_per_DENY
    - price_per_admission
    - price_per_permission
    - outcome_conditioned_billing

  eligible:
    - review_context_volume
    - review_profile_count
    - telemetry_coverage
    - chronology_retention
    - evidence_reproducibility
    - institutional_support_level
    - deployment_environment
```

Billing and payment grant service access only. They do not alter review context,
local authority, execution behavior, or the decision outcome.

## Institutional Readiness

These are future gates, not current completion claims:

```yaml
institutional_readiness:
  required_before_enterprise_pilot:
    - data_flow_inventory
    - data_retention_policy
    - security_and_access_control_summary
    - incident_response_process
    - service_availability_target
    - customer_support_boundary
    - local_authority_responsibility_statement
    - non_custody_statement
    - non_execution_statement
    - appropriate_data_processing_terms
    - limitation_and_reliance_disclosures
```

No institutional pilot may be described as ready merely because repository
tests, a synthetic demonstration, or external route containment passes.

## GTM and Claim Controls

```yaml
GTM_claim_controls:
  may_claim:
    - repository_governance_controls_exist
    - current_public_containment_has_been_externally_observed
    - Legacy_v1_is_implemented
    - v2_contract_design_is_approved

  must_not_claim_without_evidence:
    - production_control_plane_is_attested
    - Legacy_v1_has_no_consumers
    - v2_is_implemented_or_available
    - institutional_adoption
    - buyer_validation
    - successful_paid_usage
    - production_settlement_history_is_clear
    - enterprise_readiness
```

## Review and Update

Update this register only when a named evidence receipt satisfies or invalidates
a gate. Every update must identify the evidence source, observer, UTC time, and
remaining limitation. Do not silently promote `BLOCKED` or `NOT_STARTED` states.
