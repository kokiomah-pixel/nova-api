# Legacy v1 Isolation Plan

## Status

Architecture and migration design only. No isolation level is implemented or
authorized by this document.

```yaml
legacy_v1:
  endpoint: /v1/context
  contract: specs/decision_admission_contract.json
  model: authoritative_admission
  current_status: implemented
  future_status: deprecated_internal_or_isolated
  deletion_authorized: false
  runtime_change_authorized: false
```

Throughout this document, `decision_status`, `ALLOW`, `CONSTRAIN`, `VETO`,
`DENY`, `HALT`, `REDUCE`, `RETRY_DELAYED`, `RETRY_BLOCKED`, and
`PRESSURE_ESCALATED` are Legacy v1 terms. They are named for migration
traceability and are not proposed v2 response values.

## Objective

Separate the implemented Legacy v1 decision-admission behavior from the
proposed v2 external review-context profile without silently changing v1,
relabeling its outcomes, or breaking an unobserved consumer.

The migration must preserve this future external boundary:

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Known Evidence and Unknowns

```yaml
compatibility_evidence:
  verified_external_integrators: none
  verified_external_consumers: none
  public_v1_contract_exists: true
  same_owner_historical_developer_docs_exist: true
  fail_closed_v1_tests_exist: true
  Render_request_history: unknown
  production_consumers: unknown
  private_or_unobserved_consumers: possible
```

No arbitrary deprecation date should be selected until the unknowns have been
investigated. Absence of a verified consumer lowers expected migration cost but
does not establish that no consumer exists.

## Non-Substitution Rule

The proposed v2 profile must not be a renamed projection of Legacy v1.

Invalid mapping examples:

```text
Legacy v1 ALLOW -> current
Legacy v1 DENY -> conflicted
Legacy v1 HALT -> stale
```

Each future v2 field must be derived from source condition, telemetry
integrity, constraint evidence, chronology state, unresolved questions, or
temporal condition. A field-level mapping review must show those inputs and
must not use a Legacy v1 outcome as the sole derivation source.

## Isolation Level 1 — Discovery Isolation

### Scope

- Keep v1 out of public machine discovery.
- Keep public x402 and the services manifest disabled.
- Prohibit MCP or public registry publication.
- Exclude v1 from future public capability metadata.
- Mark v1 clearly as legacy in current integration documentation.
- Preserve the endpoint and runtime behavior during evidence collection.

```yaml
isolation_assessment:
  behavior_change: none_to_v1_domain_behavior
  compatibility_risk: low
  implementation_cost: low
  external_consumer_risk: >
    Existing authenticated consumers continue to function, but consumers that
    rely on public discovery would no longer discover v1.
  rollback_path: >
    Restore only approved documentation or metadata exposure after a separate
    authority-boundary review; public payment and discovery remain independently
    gated.
  required_evidence:
    - current_public_surface_inventory
    - OpenAPI_and_capability_metadata_inventory
    - registry_and_MCP_search
    - Render_route_and_request_history
    - confirmation_that_containment_flags_remain_effective
```

### Design determination

This level is already partially supported by the containment defaults, but the
current deployment SHA, environment, and request history remain unattested.
Containment observations do not by themselves complete discovery isolation.

## Isolation Level 2 — Interface Isolation

### Scope

- Exclude v1 from future public OpenAPI output.
- Restrict v1 to authenticated internal or migration consumers.
- Add deprecation and legacy-contract response headers.
- Prevent new integrations from selecting v1.
- Publish v2 documentation as the only prospective external integration path.
- Preserve a bounded compatibility window only if consumers are found.

```yaml
isolation_assessment:
  behavior_change: transport_and_visibility_change_without_v1_domain_redefinition
  compatibility_risk: medium
  implementation_cost: medium
  external_consumer_risk: >
    Undiscovered clients may depend on OpenAPI discovery, current authentication
    rules, or the absence of deprecation headers.
  rollback_path: >
    Re-enable the prior authenticated interface visibility for identified
    migration consumers while preserving public discovery containment.
  required_evidence:
    - bounded_v1_consumer_inventory
    - authenticated_route_usage_counts
    - client_and_user_agent_classification_without_private_payloads
    - OpenAPI_dependency_review
    - same_owner_developer_docs_review
    - proposed_header_and_access_policy_tests
```

### Design determination

Level 2 should not begin until Render logs and any available API-key ownership
records have been reviewed. If consumers exist, the compatibility window should
be tied to observed migration progress rather than an arbitrary calendar date.

## Isolation Level 3 — Runtime Isolation

### Scope

- Move Legacy v1 classification and permission-budget mechanics behind an
  internal interface.
- Expose only the v2 review-context profile to future external consumers.
- Remove future billing and external integration dependence on Legacy v1
  outcomes.
- Decide through separate review whether the legacy runtime is retained for
  internal analysis, archived, or retired.
- Preserve replay fixtures required to explain prior v1 records.

```yaml
isolation_assessment:
  behavior_change: high
  compatibility_risk: high_until_consumer_evidence_is_complete
  implementation_cost: high
  external_consumer_risk: >
    Any consumer that currently uses v1 response fields, refusal HTTP codes,
    proof semantics, permission budgets, or status-dependent billing requires
    explicit migration.
  rollback_path: >
    Keep a versioned, access-restricted v1 runtime available to identified
    migration consumers while v2 is privately validated; never restore public
    machine discovery as a rollback mechanism.
  required_evidence:
    - completed_consumer_inventory
    - approved_v2_contract
    - field_level_adapter_design
    - synthetic_non_authority_validation
    - context_integrity_proof_design
    - outcome_independent_billing_design
    - v1_and_v2_security_review
    - accepted_state_review
    - chronology_review
```

### Design determination

Level 3 is the target separation boundary, not an authorization to implement.
It requires its own engineering cycle, rollback design, and governance review.

## Staged Migration Sequence

```text
1. Approve the v2 semantic contract.
2. Build an internal adapter behind a disabled feature flag.
3. Run synthetic equivalence and non-authority tests.
4. Identify any v1 consumers.
5. Isolate v1 from public discovery.
6. Offer a bounded migration window if consumers exist.
7. Activate v2 privately.
8. Validate local-authority handoff.
9. Review accepted-state and chronology change.
10. Consider production activation.
```

Sequence details:

1. **Contract approval.** CCO and Architect review the response objects,
   exclusions, HTTP semantics, proof boundary, and local authority handoff.
2. **Disabled adapter.** A later implementation derives descriptive fields
   behind a default-off flag without changing v1.
3. **Synthetic validation.** Fixtures prove that incomplete, conflicted, stale,
   and unavailable packets remain descriptive and return successful domain
   responses.
4. **Consumer inventory.** Review Render logs, API-key ownership, same-owner
   documentation, public code references, and any private integration register.
5. **Discovery isolation.** Complete Level 1 before any v2 public positioning.
6. **Migration window.** Create one only for an observed consumer; define exit
   by migration evidence.
7. **Private activation.** Permit only named synthetic or internal callers.
8. **Authority handoff validation.** Demonstrate that local policy determines
   consequences independently of the packet state.
9. **Governance review.** Reconcile accepted state and determine the required
   chronology record.
10. **Production decision.** Treat activation as a separate authorization.

## Test Migration

Existing v1 tests that encode status binding or fail-closed behavior remain
valid tests of Legacy v1 until its disposition is approved. They must not be
silently rewritten to assert v2 semantics.

Future test lanes should be separated:

```yaml
test_lanes:
  legacy_v1:
    purpose: preserve_and_explain_existing_behavior_during_migration
    status: legacy
  v2_specification:
    purpose: validate_non_authority_contract_invariants
    status: design_only
  v2_runtime:
    purpose: future_implementation_validation
    status: not_authorized
```

## Consumer Evidence Plan

Collect only bounded metadata:

- request counts by route and review window;
- authenticated actor or account identifiers in pseudonymous form;
- client-version or user-agent categories;
- response-code distributions;
- proof retrieval counts linked only through scoped identifiers;
- explicit owner confirmations for known internal integrations; and
- public package, SDK, fork, and code-reference evidence.

Do not collect private payloads, API keys, payment signatures, payer identities,
or institutional action details for this migration inventory.

## Billing Separation Gate

No future external price may depend on a Legacy v1 favorable or unfavorable
outcome. The v2 profile begins with billing disabled. A later billing design may
price packet construction, proof construction, telemetry access, retained
chronology service, or private integration.

## Proof Separation Gate

Legacy v1 proof continues to describe existing v1 records until migration.
The future v2 proof verifies packet integrity, schema identity, source
references, chronology references, and reproducibility. It does not carry
forward Legacy v1 decision-proof meaning.

## Governance Gates

Accepted-state review is required before:

- v2 is declared implemented or canonical runtime behavior;
- v1 changes from implemented public contract to isolated legacy interface;
- billing semantics change; or
- the external product model changes in production.

Chronology review is required for:

- the first authorized v2 implementation;
- private or production activation;
- formal v1 deprecation;
- v1 archival or retirement;
- a material authority-boundary transition; or
- a consumer migration milestone deemed governance-significant.

This plan does not itself change accepted state or create a chronology event.
