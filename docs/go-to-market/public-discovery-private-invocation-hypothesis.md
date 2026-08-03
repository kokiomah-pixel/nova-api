# Public Discovery, Private Invocation Hypothesis

## Status

```yaml
hypothesis:
  decision_reference: CCO-MARKET-2026-08-02-001
  status: specification_and_operator_research_only
  public_listing_authorized: false
  runtime_integration_authorized: false
```

## Hypothesis

Nova may benefit from machine-readable public capability discovery while institution-specific invocation remains private, authenticated, tenant-scoped, workflow-authorized, confidential, and governed by institution-defined retention controls.

```text
Public capability discovery
!= public access to institutional review context

Payment for access
!= institutional identity
!= workflow authorization
!= local decision authority
```

## Public discovery surface

A future public discovery profile may describe only:

- Nova's non-authority capability;
- supported review-context semantics;
- input and output classes;
- required authentication categories;
- confidentiality boundary;
- authority handoff; and
- explicit exclusions.

It must not expose institution-specific sources, constraints, chronology, Reflex Memory, identities, credentials, action details, or review records.

## Private institutional invocation

```yaml
private_invocation_requirements:
  authenticated_institution: required
  tenant_scope: required
  authorized_workflow: required
  recognized_action_class: required
  institution_specific_configuration: required
  confidentiality_controls: required
  retention_controls: required
  payment_sufficient_for_access: false
  payment_sufficient_for_authority: false
```

## Access classes

```yaml
access_classes:
  public_capability_discovery:
    institution_context_exposed: false
    callable: false_until_separately_authorized

  optional_noninstitutional_service:
    status: separate_business_case_required
    shared_institutional_data_plane: prohibited

  institutional_review_context:
    private: true
    authenticated: true
    tenant_scoped: true
    workflow_authorized: true
```

## Marketplace neutrality

Circle and other marketplaces may become example discovery channels. No marketplace may become the source of Nova's institutional authority, primary category definition, exclusive distribution, or entitlement to institution-owned chronology.

## Operator validation questions

- Do institutions want public service discovery with private invocation?
- Which service catalogs or allowlists govern agent access?
- Which identity binds an agent request to an institution and workflow?
- Which confidentiality and retention rules apply?
- Is contract-backed metering preferable to anonymous pay-per-call usage?
- Which commercial unit is understandable to the budget owner?

## Deferred actions

This hypothesis does not authorize:

- a public marketplace application;
- a public Nova manifest;
- anonymous invocation;
- Circle-specific routes;
- x402 metering;
- payment as authentication;
- payment as institutional permission;
- shared retail and institutional infrastructure; or
- production changes.
