# Gate 5 Entry Design Review v0.1

## Decision under review

```yaml
workstream: Gate_5_Entry_Design_Review
status: COMPLETE
artifact: institutional_exposure_contract_v0.1
scope: institutional_exposure_contract_only
canonicality_source: authoritative_repository_main
canonical_contract: design-v2.1
action_class: agent_prepared_stablecoin_treasury_action
additional_action_classes: false
authority_effect: none
execution_effect: none
Gate_5:
  status: NOT_STARTED
  authority: false
institutional_pilot:
  authorized: false
  started: false
```

This completed pre-Gate review makes one institutional-exposure architecture
reviewable.
It does not authorize Gate 5, an institution, tenant, endpoint, runtime,
identity-provider connection, production data, or production credentials.

## Review questions and dispositions

| Review question | Design disposition |
| --- | --- |
| Is the action boundary bounded? | Yes: one externally prepared stablecoin-treasury action class only. |
| Who owns the workflow decision? | The external institutional workflow owner and local decision authority. |
| What does Nova decide? | Nothing; Nova reports governed review-context state. |
| Who governs profiles? | An explicit institution owner or attributable delegate; Nova validates structure only. |
| Are source states collapsed? | No; authority is scoped, conflicts visible, unknown remains unknown, no winner is selected. |
| Is a tenant or IdP created? | No; future identity and access requirements are design-only. |
| Are data duties settled? | Architectural controls are defined; legal title and jurisdiction-specific values remain explicit pre-pilot dependencies. |
| Does failure create a decision? | No; failure degrades/unavailable context and the institution owns consequences. |
| Can Nova execute? | No; absence of credentials, calls, and execution targets is an architectural invariant. |
| Can human presentation add judgment? | No; both surfaces derive from one governed state with traceable templates. |
| What would disprove advancement? | The eleven falsification conditions in the exposure contract. |
| Can the institution leave? | Yes in design: export, revocation, disposition, detachment, and continuity are required before pilot. |

## Artifact map

- `institutional-exposure-contract-v0.1.md` is the human contract.
- `specs/gate5_institutional_exposure_contract_v0_1.json` is its machine form.
- `fixtures/target-v2/gate5-entry/design_cases.json` contains only synthetic
  design cases G5E-001 through G5E-020.
- `scripts/validate_gate5_entry_design_review.py` checks contract completeness,
  canonical dependencies, mutation boundaries, presentation parity, and the
  synthetic scenario inventory.
- `tests/test_gate5_entry_design_review.py` executes the required boundary and
  failure cases.

## Institutional exposure domains

The human and machine contracts jointly define:

1. one action class and its material inclusions/exclusions;
2. workflow owner, local authority, Nova, external executor, and support roles;
3. attributable review-profile lifecycle authority;
4. separate source, context, and completeness state;
5. future identity, least privilege, isolation, support, revocation, and audit;
6. data control, retention, export, portability, deletion, backup, and withdrawal;
7. fail-explicit degradation and incident handling;
8. an explicit non-execution integration architecture;
9. one governed state feeding machine and deterministic human views;
10. measurement, falsification, withdrawal, and termination contracts.

## Threshold and legal dependencies

No numerical pilot threshold is invented. Every metric carries a
`required_pilot_configuration` threshold placeholder owned by the institutional
workflow owner and Architect. Legal title/licence terms, jurisdiction-specific
retention duration, and backup deletion timing remain required counsel or
institutional configuration decisions before any pilot authorization. They do
not block completion of this architecture review and are not silently resolved
here.

## Gate 5 authorization preconditions

Entry Review completion does not satisfy or waive any Gate 5 authorization
precondition. The following 18 conditions remain unevidenced for a future
institution-specific authorization:

```yaml
Gate_5_authorization_preconditions:
  status: NOT_YET_SATISFIED
  preconditions_not_yet_evidenced: 18
  silently_resolved: false
  institutional_configuration:
    institution_and_workflow_owner_identified: required
    local_decision_authority_identified: required
    review_profile_owner_identified: required
    external_identity_authority_defined: required
  data_and_legal:
    legal_title_and_license_terms_resolved: required
    jurisdiction_specific_retention_duration_defined: required
    backup_deletion_timing_defined: required
    export_and_post_withdrawal_disposition_approved: required
  measurement:
    success_thresholds_agreed: required
    falsification_thresholds_agreed: required
    observation_windows_agreed: required
  operations:
    support_access_model_approved: required
    incident_and_degradation_process_approved: required
    withdrawal_requesters_and_process_approved: required
  architecture:
    one_action_class_only: required
    local_authority_external_to_Nova: required
    execution_path_through_Nova: prohibited
    production_execution_credentials_in_Nova: prohibited
```

## Canonical dependency audit

```yaml
canonical_target_contract: design-v2.1
incorporated_Gate_3_refinements:
  - G3-R01
  - G3-R03
  - G3-R08
  - G3-R11
  - G3-Q15
unapproved_Gate_3_gaps: []
PR_33_dependency: none
Legacy_v1_dependency: none
chronology_mutation: false
Reflex_Memory_mutation: false
```

Scoped source classification is an institutional governance requirement over
existing evidence references. It neither defines `authority_scope` nor adopts
G3-R04. Chronology and accepted-memory references remain opaque under current
canonical main semantics, so G3-R10 and PR #33 are not dependencies.

## Completion meaning

This Entry Design Review is `COMPLETE`, meaning only that institutional
exposure architecture is reviewable. Gate 5 remains `NOT_STARTED`; a pilot
remains `NOT_AUTHORIZED`.
Any later start requires a separate Architect decision after the named legal,
policy, metric-threshold, identity, retention, incident, and withdrawal
configuration is complete.
