# Nova External Review-Context Contract

## Status

```yaml
contract:
  name: Nova External Review-Context Contract
  version: design-v2
  implementation_status: proposed_not_implemented
  authority_model: non_authority
  execution_effect: none
```

This document is a design gate, not an implemented endpoint, public capability,
or production contract. It does not change `/v1/context`,
`/v1/proof/{decision_id}`, or any current runtime behavior.

## Purpose

The proposed contract separates Nova's external review-context packet from the
Legacy v1 term `decision admission` model. It defines what a future external
consumer may submit, what Nova may describe, and where responsibility passes
back to local institutional authority.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Nova can describe what context exists, what is missing, which sources conflict,
which constraints are visible, which chronology is relevant, and what remains
unresolved. It does not decide whether an institution should act.

## Contract Invariants

```yaml
contract_invariants:
  prepared_action_origin: external_to_Nova
  request_is_permission_application: false
  local_decision_owner: local_institutional_authority
  external_execution_owner: external_system
  Nova_authority_effect: none
  Nova_execution_effect: none
  domain_state_changes_HTTP_status: false
  outcome_dependent_billing: prohibited
```

The contract is useful before local authority without replacing that authority.
No field is a transaction command, policy result, legal conclusion, compliance
conclusion, or execution entitlement.

## Conceptual Request

```yaml
review_context_request:
  request_id:

  prepared_action:
    action_type:
    asset_or_resource:
    amount_or_scope:
    destination_or_venue:
    intended_time_window:

  evidence:
    sources: []
    observed_at:
    received_at:

  institution_context:
    institution_id_or_policy_profile:
    relevant_constraints: []
    prior_review_references: []

  review_profile:
    profile_id:
    profile_version:
    profile_owner:
    required_context_fields: []
    profile_hash:

  requested_context:
    - source_state
    - contradiction_visibility
    - constraint_context
    - chronology_context
    - temporal_context
    - review_completeness
```

The prepared action originates in an agent, operator, workflow, or other system
outside Nova. The request asks Nova to construct review context; it is not an
application for permission.

Nova does not select the institution's controlling policy, resolve an
institutional source hierarchy, or decide which external system should act.
The request may identify institution-provided profiles and constraints so Nova
can preserve their provenance and make unresolved relationships visible.

The review profile defines the fields required for a complete review-context
packet. It is supplied or selected under institution-approved configuration;
Nova does not invent institutional requirements. A profile change may change
the packet's completeness classification without changing its evidence. The
profile identity, version, owner, and hash are therefore preserved for proof
and reproducibility.

Institution identifiers, source material, policy references, and action details
may be sensitive. A future implementation must support scoped transmission,
data minimization, access control, retention limits, and private deployment when
the institution's risk model requires them.

## Conceptual Response

```yaml
review_context_response:
  schema_version:
  context_id:
  request_id:
  created_at:

  prepared_action_reference:
    reference_id:
    reference_type: opaque_external_reference
    payload_embedded: false

  review_profile_reference:
    profile_id:
    profile_version:
    profile_owner:
    profile_hash:

  record_source_type:
    permitted_values:
      - synthetic
      - production_like
      - live
    value:
    source_segmentation: []

  context_state:
    value:
      - current
      - uncertain
      - stale
      - superseded
    reasons: []

  source_state:
    value:
      - complete
      - partial
      - conflicted
      - unavailable
    sources: []
    unresolved_source_conflicts: []

  constraint_context:
    observed_constraints: []
    constraint_sources: []
    unresolved_constraint_questions: []

  temporal_context:
    source_observed_at:
    source_received_at:
    review_context_created_at:
    intended_action_window:
    temporal_conflicts: []
    pending_state: []

  contradiction_context:
    source_conflicts: []
    constraint_conflicts: []
    temporal_conflicts: []
    chronology_conflicts: []
    unresolved_questions: []

  review_completeness:
    value:
      - complete
      - partial
      - conflicted
      - unavailable
    missing_context: []
    unresolved_conditions: []

  chronology_context:
    prior_review_references: []
    accepted_memory_references: []
    relevant_changes_since_prior_review: []

  authority_handoff:
    decision_owner: local_institutional_authority
    execution_owner: external_system
    Nova_authority_effect: none

  reproducibility:
    schema_version:
    source_versions: []
    classification_version:
    review_profile_id:
    review_profile_version:
    review_profile_hash:
    record_source_type:
    source_segmentation: []
    context_hash:
    signature:

  boundary:
    approval_effect: none
    authorization_effect: none
    execution_effect: none
```

Each state is descriptive:

- `context_state` describes temporal fitness of the packet's inputs.
- `source_state` describes evidence availability and disagreement.
- `constraint_context` preserves observed institution-provided constraints and
  unresolved questions without selecting a policy result.
- `contradiction_context` describes conflicts visible within the declared
  source and review scope.
- `review_completeness` describes the presence or explicit unresolved state of
  fields required by the identified and versioned profile.
- `chronology_context` identifies relevant prior records and changes without
  accepting a new chronology event.
- `authority_handoff` makes the local decision and external execution owners
  explicit.

`requested_context.contradiction_visibility` maps to
`review_context_response.contradiction_context`. This context is descriptive:
Nova does not choose a winning source or resolve a policy dispute. An empty
conflict list means only that no conflict was identified within the declared
scope; it does not establish that no external conflict exists.

## Prepared Action Reference Boundary

The prepared action originates outside Nova. Its response reference has these
semantics:

```yaml
prepared_action_reference_semantics:
  action_origin: external_to_Nova
  Nova_owns_action: false
  full_action_payload_required_in_response: false
  sensitive_action_data_embedded_by_default: false
  reference_grants_execution_authority: false
```

The response must not reproduce destination addresses, full transaction
payloads, policy-sensitive details, personal data, or institution secrets
unless a separately approved review profile explicitly requires them.

## Evidence Environment Segmentation

`record_source_type` identifies the environment from which evidence originated:

- `synthetic` means generated or constructed for testing.
- `production_like` means realistic but not verified live institutional
  evidence.
- `live` means observed from an authorized live source under the declared
  scope.

Production-like evidence must never be represented as live. `live` describes
the source environment; it does not establish truth, correctness, approval, or
acceptance. Mixed-source packets must identify the record source type at the
field or source-reference level. Proof and reproducibility preserve that source
segmentation. A signature protects the defined signed material; it does not
upgrade the source type or evidentiary meaning.

## Review Completeness Boundary

Complete review context does not mean approved action.

Review completeness describes whether the fields required by the identified
and versioned review profile are present or explicitly unresolved.

It does not describe whether institutional policy is satisfied.

It does not mean:

- institutional policy is satisfied;
- risk has been accepted;
- an action is executable;
- legal review has been completed;
- compliance review has been completed; or
- the institution has decided how to proceed.

`partial`, `conflicted`, and `unavailable` are valid review-context observations.
They do not encode softened versions of Legacy v1 outcomes.

## Field and Value Exclusions

The future external response excludes these Legacy v1 or directive-bearing
fields:

```yaml
prohibited_external_fields:
  - decision_status
  - decision_admission_record
  - permission_budget
  - permission_budget_class
  - adjusted_size
  - conditioned_size
  - execution_posture
  - halt_release_authority
  - prevented_action
  - intervention_type
  - recommended_action
```

The following may be named in migration analysis only as Legacy v1 terms. They
must not be external domain outcomes:

```yaml
prohibited_external_values:
  - ALLOW
  - CONSTRAIN
  - VETO
  - DENY
  - HALT
  - REDUCE
  - RETRY_BLOCKED
  - RETRY_DELAYED
  - PRESSURE_ESCALATED
  - approved
  - authorized
  - executable
  - cleared
  - blocked
```

## HTTP Semantics

```yaml
HTTP_semantics:
  valid_context_response: 200
  incomplete_context: 200
  conflicted_context: 200
  stale_context: 200
  unavailable_source_context:
    status: 200
    condition: request_processed_and_unavailability_can_be_described
  malformed_request:
    - 400
    - 422
  authentication_failure:
    - 401
    - 403
  rate_limit: 429
  Nova_service_unavailable: 503
```

A domain-state observation does not itself produce `402`, `409`, `422`, or
`429`. Those codes are reserved for payment transport if separately designed,
malformed input, authentication, quota, or infrastructure conditions.

> A valid response describes review context. Its HTTP status does not
> authorize, deny, delay, block, reduce, halt, or permit the prepared action.

## Narrow Meaning of Authoritative

Nova may provide:

```yaml
permitted_authority:
  authoritative_source_identity: identity_of_the_source_Nova_recorded
  authoritative_schema_version: exact_packet_schema_used
  authoritative_record_hash: integrity_hash_over_defined_packet_material
  authoritative_Nova_observation: faithful_record_of_what_Nova_observed
```

Nova may not provide:

```yaml
prohibited_authority:
  authoritative_execution_permission: prohibited
  authoritative_transaction_decision: prohibited
  authoritative_institutional_approval: prohibited
  authoritative_denial: prohibited
```

Nova may provide an authoritative record of what Nova observed and how the
packet was constructed. Nova does not provide an authoritative institutional
decision about whether the action may proceed.

## Context-Integrity Proof

```yaml
context_proof:
  proof_type: review_context_integrity
  authority_effect: none
  verifies:
    - packet_integrity
    - schema_identity
    - source_reference_integrity
    - classification_version
    - context_hash
    - creation_time
    - chronology_references
    - reproducibility_inputs
    - review_profile_identity
    - review_profile_hash
    - record_source_type
    - source_segmentation
  does_not_verify:
    - approval
    - authorization
    - execution_permission
    - institutional_acceptance
    - transaction_validity
```

The proof verifies the identity and reproducibility of review context,
including the profile identity, version, and hash and the evidence source
segmentation. It does not verify a Legacy v1 governed decision state, favorable
outcome, or local institutional decision.

## Internal Classification Separation

Internal classifiers may continue to exist during a future migration, subject
to a separate implementation review:

```yaml
internal_classification:
  may_exist: true
  may_be_exposed_as_external_permission: false
  may_directly_determine_local_execution: false
  may_be_used_to_construct_descriptive_context: only_with_field_level_mapping_review
```

The response must be constructed from source condition, telemetry integrity,
constraint evidence, chronology state, unresolved questions, and temporal
condition. It must not be generated solely by translating a Legacy v1 outcome
into a softer label.

In particular, these transformations are invalid:

```text
Legacy v1 ALLOW -> current
Legacy v1 DENY -> conflicted
Legacy v1 HALT -> stale
```

Field-level mapping review must demonstrate the provenance of each external
observation independently of any Legacy v1 status.

## Billing and Payment Boundary

Initial v2 billing is disabled. A later, separately authorized design may bill
for packet construction, proof construction, telemetry access, retained
chronology services, or private institutional integration. Price must not
depend on whether context is complete, partial, conflicted, stale, or
unavailable.

A payment receipt has no authority effect and grants no transaction or
execution entitlement.

Public x402 remains disabled. x402 is not part of the initial v2 implementation
design.

## Local Decision Boundary

The receiving institution is responsible for:

- establishing identity and delegated scope;
- choosing applicable policy and source hierarchy;
- interpreting the packet under local rules;
- deciding whether more evidence or review is required;
- deciding how to proceed, pause, narrow, escalate, or stop; and
- operating any external execution system.

Nova is responsible for accurately constructing and proving the context packet
within the declared schema and input scope. This responsibility does not
transfer institutional decision ownership.

## Implementation Evidence Gate

No `/v2/context` implementation should begin until review establishes:

1. CCO approval of this semantic contract and machine-readable specification.
2. Architect approval of the product and external-interface boundary.
3. Field-level derivation rules independent of Legacy v1 outcomes.
4. Synthetic tests for incomplete, conflicted, stale, and unavailable context.
5. Context-proof canonicalization and redaction rules.
6. Authentication, tenant isolation, retention, and sensitive-field handling.
7. A bounded inventory of possible v1 consumers and Render request evidence.
8. A migration and rollback plan for any identified consumer.
9. Outcome-independent billing invariants.
10. A separate accepted-state and chronology review for implementation.

## Design Review Answers

1. The external contract can operate without `decision_status` because its
   objects derive from evidence and context condition.
2. Incomplete and conflicted context are valid HTTP 200 responses.
3. Proof can verify packet construction without verifying permission.
4. Internal classification can remain only behind a reviewed separation layer;
   it cannot govern local execution.
5. v1 can be isolated in stages after consumer evidence is collected.
6. Billing can be based on packet or proof construction rather than outcome.
7. The bounded NSF demonstration can remain explicitly separate from v1.
8. The implementation evidence gate above must be satisfied before endpoint
   work begins.
9. Adoption of v2 as implemented canonical behavior requires accepted-state
   review.
10. Activation, deprecation, retirement, or a material authority-boundary
    transition requires chronology review.
