# Model-Originated Claim and Validation Scope

## Status

```yaml
specification:
  name: Model-Originated Claim and Validation Scope
  version: design-v0.1
  status: proposed_specification
  implementation_status: not_implemented
  authority_model: non_authority
  runtime_effect: none
  production_effect: none
```

This document is a schema-design refinement. It creates no endpoint, runtime
schema, model-provider integration, formal-verification engine, institutional
decision, chronology event, or Reflex Memory object.

## Purpose

The specification extends Nova's existing material-claim and review-context
objects so a claim may be identified as source-derived, human-originated,
model-inferred, model-originated, jointly originated, or produced by an
external system.

It does not establish a separate scientific-discovery subsystem. Nova
preserves material contribution lineage and declared validation scope so local
authority can decide whether and how the institution may rely on a claim.

```text
Model-originated claim
does not mean
authoritative claim.
```

## Claim genesis object

```yaml
claim_genesis:
  origin_type:
    permitted_values:
      - source_derived
      - human_originated
      - model_inferred
      - model_originated
      - jointly_originated
      - external_system_determination

  originator_reference:
  originating_problem_or_request:
  generated_at:

  source_material_references: []
  tool_references: []

  model_environment_reference:
    provider:
    model_family:
    model_version:
    deployment_environment_class:
    environment_reference:
    observed_at:

  model_originated_claim_status:
    permitted_values:
      - not_applicable
      - declared_unreviewed
      - under_validation
      - validation_records_available
      - disputed
      - amended
      - superseded

  novelty:
    asserted:
    asserted_by:
    review_status:
      permitted_values:
        - not_claimed
        - asserted_unreviewed
        - internally_reviewed
        - externally_reviewed
        - disputed
        - superseded

  unrestricted_reasoning_trace_required: false
  authority_effect: none
```

`model_originated_claim_status` is a declared lifecycle status. It is not a
truth score, model ranking, certification, or authority state. Model identity
supports provenance only; it does not create model authority.

## Material-claim integration

The claim-genesis object extends a material claim. It does not replace Nova's
evidence, source-state, contradiction, or review-context objects.

```yaml
material_claim:
  claim_id:
  claim:
  claim_genesis:
  evidence_state:
  source_references: []
  assumptions: []
  unresolved_conditions: []
  validation_records: []
  institutional_applicability:
  result_lineage_reference:
```

A source-derived claim and a model-originated claim can express the same text
while retaining different genesis. A jointly originated claim preserves both
the material model contribution and the human contribution instead of
collapsing either origin.

## Validation record and scope

```yaml
validation_record:
  validation_id:

  validation_type:
    permitted_values:
      - formal
      - empirical
      - simulation
      - source_correspondence
      - expert_review
      - institutional_review
      - outcome_observation

  validator_reference:
  artifact_reference:
  formal_certificate_reference:
  statement_or_object_validated:

  assumptions_in_scope: []
  conditions_out_of_scope: []

  result:
    permitted_values:
      - passed
      - failed
      - partial
      - disputed
      - inconclusive
      - unavailable

  observed_at:
  external_review_status:

  authority_effect: none
  execution_effect: none
```

Validation scope is the combination of the exact statement or object
validated, validation type, artifact, assumptions in scope, conditions out of
scope, result, and observation time. A passed result applies only within that
declared scope. It does not silently validate unstated real-world conditions.

Independent external validation must be represented by its validator,
artifact, and scope. Source authenticity alone is not independent external
validation.

## Institutional applicability

```yaml
institutional_applicability:
  status:
    permitted_values:
      - not_reviewed
      - partially_applicable
      - applicable_with_conditions
      - disputed
      - accepted_by_local_authority
      - rejected_by_local_authority
      - superseded

  reviewed_by:
  reviewed_at:
  applicable_action_class:
  conditions: []
  excluded_conditions: []
  unresolved_questions: []

  authority_reference:
  execution_effect: none
```

`accepted_by_local_authority` records an external institutional decision. It
does not mean Nova approved the claim, and it creates no execution entitlement.
Institutional applicability must not be inferred automatically from a formal,
technical, empirical, or expert validation result.

## Human contextualization record

```yaml
human_contextualization_record:
  record_id:
  reviewer_reference:
  reviewer_role:
  reviewed_at:

  interpretation:
  scope_limits: []
  assumptions_added: []
  assumptions_rejected: []
  unresolved_questions: []

  responsibility_statement:
  authority_effect: none
```

Human contextualization records how a person interpreted and bounded the
claim. It neither upgrades the claim automatically nor transfers the person's
institutional authority to Nova.

## Result lineage

```yaml
result_lineage:
  result_id:

  versions:
    - version:
      representation_type:
        permitted_values:
          - initial_generated_result
          - revised_argument
          - human_prepared_representation
          - formalized_representation
          - externally_reviewed_representation
          - amended_result
          - superseded_result

      created_by:
      created_at:
      artifact_reference:
      validation_record_references: []
      human_contextualization_references: []
      supersedes:
      superseded_by:

  authority_reviewed_version:
  later_correction_reference:
```

Amendment and supersession are append-only relationships. A later correction
links to the affected version and preserves the result, assumptions,
validation artifacts, contextualization, and limitations that local authority
actually reviewed. Provider or model replacement does not erase this lineage.

## Formal verification boundary

```text
Machine-checkable correctness
does not automatically establish
institutional applicability.
```

A formal certificate may validate the encoded statement and proof. It does not
establish:

- that the institution framed the correct real-world question;
- that all operational conditions were encoded;
- that legal or contractual conditions were represented;
- that current market data is complete;
- that local authority should rely on the result; or
- that execution is authorized.

## No hidden reasoning requirement

```yaml
reasoning_trace_boundary:
  hidden_chain_of_thought_required: false
  unrestricted_reasoning_trace_retention: prohibited
  material_claims_required: true
  source_references_required_when_available: true
  assumptions_required: true
  tool_results_relied_upon_required_when_material: true
  validation_artifacts_required_when_claimed: true
```

Nova preserves material contribution lineage. It does not require or retain
unrestricted internal reasoning traces.

## Relationship to review context

Claim context is optional in the proposed external review-context contract.
When supplied, it remains subordinate to the contract's evidence, source,
chronology, and authority-handoff invariants.

```yaml
review_context_relationship:
  claim_context_is_permission_application: false
  model_origin_creates_authority: false
  validation_pass_creates_authority: false
  institutional_applicability_requires_local_review: true
  chronology_acceptance_automatic: false
  Reflex_Memory_mutation_automatic: false
```

## Documentation-level scenarios

These scenarios are specification proof obligations, not runtime tests or
evidence of an implemented capability.

```yaml
required_scenarios:
  - scenario: model_originated_claim_without_prior_document
    expected:
      claim_genesis_recorded: true
      unsupported_classification_automatic: false
      authority_effect: none

  - scenario: formally_validated_claim_with_unreviewed_applicability
    expected:
      formal_validation_recorded: true
      institutional_applicability: not_reviewed
      approval_effect: none

  - scenario: sophisticated_model_output_without_validation
    expected:
      model_identity_recorded: true
      validation_status: unavailable
      prestige_creates_authority: false

  - scenario: source_derived_claim_vs_model_originated_claim
    expected:
      origin_types_distinct: true

  - scenario: jointly_originated_human_model_claim
    expected:
      joint_origin_preserved: true
      human_contextualization_preserved: true

  - scenario: later_external_correction
    expected:
      original_review_state_preserved: true
      correction_linked: true
      silent_rewrite: false

  - scenario: validation_pass_but_business_conditions_excluded
    expected:
      excluded_conditions_visible: true
      institutional_applicability_not_automatic: true

  - scenario: model_provider_replaced
    expected:
      prior_reliance_history_preserved: true
      provider_change_does_not_erase_lineage: true
```

## Final boundary

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Nova records how a material claim originated, what was validated, what was not
validated, what human context was available, and which version local authority
reviewed. Nova does not certify the model, decide institutional reliance, or
execute an action.
