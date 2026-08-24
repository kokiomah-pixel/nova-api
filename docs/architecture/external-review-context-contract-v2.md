# Nova External Review-Context Contract

## Status

```yaml
contract:
  name: Nova External Review-Context Contract
  version: design-v2.1
  canonicality_source: authoritative_repository_main
  implementation_status: proposed_not_implemented
  runtime_implemented: false
  approved_for_runtime_implementation: false
  endpoint_exists: false
  private_adapter_started: false
  Gate_4_authority: false
  authority_model: non_authority
  execution_effect: none
  incorporated_Gate_3_refinements:
    - G3-R01
    - G3-R03
    - G3-R08
    - G3-R11
    - G3-Q15
```

This `design-v2.1` document incorporates only `G3-R01`, `G3-R03`, `G3-R08`,
`G3-R11`, and `G3-Q15`. Canonicality is determined by presence on authoritative
repository `main`, not by permanent branch-relative metadata in this document.
It remains a design gate, not an implemented endpoint, public capability, or
production contract. It does not change `/v1/context`,
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
    action_id:
    proposal_version_id:
    action_type:
    asset_or_resource:
    amount_or_scope:
    destination_or_venue:
    intended_time_window:

  evidence:
    sources: []
    observed_at:
    received_at:

  claim_context:
    material_claims:
      - claim_id:
        claim:
        claim_genesis:
        evidence_state:
        assumptions: []
        validation_records: []
        institutional_applicability:

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

`action_id` and `proposal_version_id` are optional request inputs with distinct
meanings. An externally supplied `action_id` is required only when
cross-revision action lineage is claimed. Nova never derives stable action
lineage from mutable proposal content. If `action_id` is absent, lineage is
unavailable and Nova must not infer that two proposals concern the same action.
`proposal_version_id` identifies the exact proposal under review and should be
supplied by the institution or orchestrator. If it is absent, Nova may produce
only an algorithm-qualified value explicitly labeled
`Nova_derived_proposal_fingerprint` over canonical prepared-action material.
That fingerprint identifies proposal content and cannot establish action
lineage.

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
    action_id:
    proposal_version_identity:
      value:
      source_type:
      algorithm_qualification:
      material_scope:
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
      - mixed
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
      - unavailable
      - conflicted
      - partial
      - complete
    missing_context: []
    unresolved_conditions: []

  chronology_context:
    prior_review_references: []
    accepted_memory_references: []
    relevant_changes_since_prior_review: []

  claim_context_response:
    claim_statuses: []
    validation_scope: []
    unresolved_validation_questions: []
    applicability_statuses: []
    result_lineage_references: []

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
- `claim_context_response` preserves declared claim genesis, validation scope,
  applicability status, and result-lineage references without determining a
  claim's truth or institutional treatment.
- `authority_handoff` makes the local decision and external execution owners
  explicit.

`requested_context.contradiction_visibility` maps to
`review_context_response.contradiction_context`. This context is descriptive:
Nova does not choose a winning source or resolve a policy dispute. An empty
conflict list means only that no conflict was identified within the declared
scope; it does not establish that no external conflict exists.

## Optional Claim Context

Claim context is an optional design extension for material claims that may be
source-derived, human-originated, model-inferred, model-originated, jointly
originated, or produced by an external system. Its focused schema is defined
in
[`Model-Originated Claim and Validation Scope`](model-originated-claim-and-validation-scope.md).

```yaml
claim_context_invariants:
  model_origin_creates_authority: false
  validation_pass_creates_authority: false
  formal_certificate_creates_execution_entitlement: false
  institutional_applicability_requires_local_review: true
```

Claim context does not replace source state, contradiction context, review
completeness, or authority handoff. A validation record describes only the
statement, assumptions, method, conditions, and artifact within its declared
scope. A local institution remains responsible for reviewing applicability.

No current endpoint, runtime schema, application code, or deployed behavior
supports these optional fields. Their presence in this design contract creates
no implementation authority.

## Prepared Action Reference Boundary

The prepared action originates outside Nova. Its response reference has these
semantics:

```yaml
prepared_action_reference_semantics:
  action_origin: external_to_Nova
  action_and_proposal_identity_distinct: true
  action_id:
    meaning: stable_action_lineage_identity_when_externally_supplied
    required_when_cross_revision_lineage_is_claimed: true
    Nova_content_derivation_permitted: false
    missing_behavior: lineage_unavailable_and_no_same_action_inference
  proposal_version_identity:
    meaning: identity_of_exact_proposal_reviewed
    required_in_response: true
    source_genesis_machine_visible: true
    value: opaque_external_id_or_Nova_derived_fingerprint
    source_type:
      - external_institution_or_orchestrator
      - Nova_derived_proposal_fingerprint
    when_Nova_derived:
      algorithm_qualification: required
      material_scope: canonical_prepared_action_material_only
    establishes_action_lineage: false
  reference_id: compatibility_reference_not_a_substitute_for_both_identities
  Nova_owns_action: false
  full_action_payload_required_in_response: false
  sensitive_action_data_embedded_by_default: false
  reference_grants_execution_authority: false
```

The response binds the exact proposal-version identity and, when supplied, the
external stable action-lineage identity. Its structured
`proposal_version_identity` makes genesis deterministic: an external value
preserves its opaque origin, while a Nova-derived fingerprint visibly carries
its source type, algorithm qualification, and
`canonical_prepared_action_material_only` scope. Neither form can establish
stable action lineage. A revised proposal cannot reuse proof identity from an
earlier proposal. The response must not reproduce destination addresses, full transaction
payloads, policy-sensitive details, personal data, or institution secrets
unless a separately approved review profile explicitly requires them.

## Evidence Environment Segmentation

`record_source_type` identifies the environment from which evidence originated:

- `synthetic` means generated or constructed for testing.
- `production_like` means realistic but not verified live institutional
  evidence.
- `live` means observed from an authorized live source under the declared
  scope.
- `mixed` means more than one evidence-environment class is represented.

Production-like evidence must never be represented as live. `live` describes
the source environment; it does not establish truth, correctness, approval, or
acceptance. A homogeneous packet emits its single environment class; a packet
containing more than one class emits `mixed`. `source_segmentation` remains the
authoritative component provenance. Nova must not reduce mixed evidence using a
strongest/weakest ranking, promote `production_like` to `live`, or let a proof
or signature upgrade the evidence environment.

## Review Completeness Boundary

Complete review context does not mean approved action.

The target-v2 contract owns the public enum meanings and this precedence:

```text
unavailable > conflicted > partial > complete
```

- `unavailable` means completeness cannot be evaluated because the applicable
  profile or required-field inventory is unavailable.
- `conflicted` means required context contains unresolved material conflict.
- `partial` means required context is missing or unavailable without a
  higher-priority material conflict.
- `complete` means every required dimension is represented, including allowed
  explicit unresolved states, and no material conflict exists.

The identified institution-approved profile defines required fields and
evidence, thresholds and maximum age, source hierarchy, constraint
applicability, and revalidation conditions. It cannot redefine the enum names,
their public meanings, or their precedence.

It does not describe whether institutional policy is satisfied.

It does not mean:

- institutional policy is satisfied;
- risk has been accepted;
- an action is executable;
- legal review has been completed;
- compliance review has been completed; or
- the institution has decided how to proceed.

In particular, `complete` does not mean policy satisfied, safe, permitted,
approved, or executable.

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

## Canonical Numeric and Interoperability Profile

`G3-R11` is incorporated in this target-v2 design contract revision. Canonical
semantic material uses RFC 8785/JCS as its I-JSON structural baseline without
redefining or deviating from JCS. Before JCS serialization, the versioned
`nova-jcs-exact-financial-json-design-v0.1` application profile converts exact
financial and temporal values to representations that preserve their meaning.
No production hash, signature, PQC suite, provider, or library is selected.

```yaml
canonicalization:
  structural_baseline: RFC_8785_JCS
  JCS_deviation: false
  exact_financial_application_profile: nova-jcs-exact-financial-json-design-v0.1
  production_hash_algorithm_selected: false
```

Canonical strings preserve Unicode code points exactly as supplied. There is no
silent NFC/NFD normalization. Invalid Unicode and lone surrogates fail; object
keys follow JCS UTF-16 code-unit ordering; enums are case-sensitive and are not
alias-coerced. Duplicate object members fail. `null` and absence are distinct,
and missing values are never silently converted to `null`.

Binary floating-point financial values, NaN, infinity, rounding, and truncation
are prohibited. Exact numeric representations are:

```yaml
exact_integer:
  numeric_type: integer
  value: canonical_base10_string

exact_decimal:
  numeric_type: decimal
  coefficient: signed_base10_string
  scale: nonnegative_integer

monetary_amount:
  numeric_type: monetary_amount
  asset_id: explicit_opaque_asset_or_unit
  coefficient: signed_base10_string
  scale: profile_declared_nonnegative_integer
```

Exact integers prohibit exponents, plus signs, decimal points, and leading
zeros other than `0`; negative zero becomes `0`. Exponent notation for decimals
may appear only at the normalization boundary and never in canonical material.
Generic decimals trim insignificant trailing zeros before applying the
canonical resulting `max_scale`; fixed-scale fields preserve the declared
scale. Every decimal profile declares `max_precision`, `max_scale`,
`max_abs_exponent`, and `max_input_characters`. Input length and absolute
exponent are checked before coefficient expansion. Values requiring rounding
fail. Monetary asset/unit and scale are explicit and never inferred; missing
metadata remains unresolved and uncanonicalizable.

Semantic timestamps require RFC 3339 with an explicit known offset, normalize
to UTC `Z`, and contain exactly six fractional digits. Whole seconds gain
`.000000`; shorter fractions right-pad; sub-microsecond input fails rather than
rounds. RFC 3339 `-00:00`, invalid calendars, and leap seconds fail. Each
explicit `intended_action_window.start` and `.end` boundary follows the same
rule or remains an explicit unresolved state under its declared field rule.
Normalization does not make a timestamp independently trusted.

Every semantic response array declares exactly one of `ordered_sequence`,
`set`, or `multiset`; undeclared arrays fail projection. The following arrays
are sets under this revision:

```text
record_source_type.source_segmentation
context_state.reasons
source_state.sources
source_state.unresolved_source_conflicts
constraint_context.observed_constraints
constraint_context.constraint_sources
constraint_context.unresolved_constraint_questions
temporal_context.temporal_conflicts
temporal_context.pending_state
contradiction_context.source_conflicts
contradiction_context.constraint_conflicts
contradiction_context.temporal_conflicts
contradiction_context.chronology_conflicts
contradiction_context.unresolved_questions
review_completeness.missing_context
review_completeness.unresolved_conditions
chronology_context.prior_review_references
chronology_context.accepted_memory_references
chronology_context.relevant_changes_since_prior_review
reproducibility.source_versions
reproducibility.source_segmentation
```

Set values normalize and sort by declared field/type-specific tuples before JCS
serializes the normalized result. JCS canonical bytes are not a universal
semantic set-order key:

```yaml
source_reference_sort:
  - source_id
  - source_version_or_digest
  - authority_scope
  - observed_at
  - received_at
  - record_source_type

constraint_reference_sort:
  - constraint_id_or_digest
  - source_id
  - applicability_scope

chronology_reference_sort:
  - reference_type
  - reference_id
  - version_or_digest
  - treatment_status
  - applicability_status

digest_record_sort:
  - algorithm
  - parameter_set
  - output_encoding
  - digest
```

Source references and segmentation use `source_reference_sort`; constraint
references use `constraint_reference_sort`; chronology, prior-review, and
accepted-memory references use `chronology_reference_sort`; digest records use
`digest_record_sort`. Other set-like fields declare their own stable scalar or
identity tuple. Byte-identical duplicates collapse only for a declared set. The
same identity with different content is a conflict, not a duplicate. Distinct
content with the same declared sort tuple is likewise rejected as an unresolved
conflict; input iteration order is never used as a tie-breaker.

## Semantic Identity Continuity Across Digest Migration

`G3-Q15` is incorporated as a contract invariant:

```text
semantic context identity != one individual digest value
```

Semantic context identity is grounded in the identical canonical semantic byte
sequence under the governing contract and canonicalization context. An
algorithm-qualified digest is evidence about those bytes; it is not their
meaning. A later authorized digest migration must preserve historical digest
evidence and add successor or parallel evidence bound to the identical bytes or
a verifiable preserved reference. Different algorithms must never be described
as producing the same hash value. If the bytes cannot be reconstructed or
referenced verifiably, continuity is unresolved.

This invariant does not incorporate `G3-Q13`. The compatibility
`reproducibility.context_hash` remains singular in the current response shape.
A plural digest transport representation requires a separate contract review.
No production hash algorithm is selected here.

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

Contract revision and Gate 3 design completion do not authorize Gate 4 or
runtime work:

```yaml
Gate_3:
  field_derivation_design: complete

Gate_4_private_synthetic_adapter:
  status: not_authorized
  implementation_started: false

target_v2_runtime:
  status: not_implemented
  implementation_authority: false
```

No `/v2/context` endpoint, private adapter, signer, cryptographic deployment,
payment, settlement, execution, chronology mutation, or Reflex Memory mutation
is authorized by this contract revision.

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
