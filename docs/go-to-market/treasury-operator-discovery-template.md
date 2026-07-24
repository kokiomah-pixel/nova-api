# Treasury Operator Discovery Template

## Status

Blank operator-discovery instrument
Private evidence-capture guide
Not completed interview evidence
Not buyer-pull evidence
Not adoption evidence
Not runtime implementation authority

## Use Boundary

Use this blank template to investigate review-context needs in recurring stablecoin or treasury workflows.

Do not commit completed interview notes or identifiable operator data to the public repository.

Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.

## Workflow

- Describe one recurring stablecoin or treasury action that reaches local review.
- What system or person prepares the action?
- What systems hold relevant evidence?
- Which system is considered authoritative when sources disagree?
- What activity can remain pending when the review begins?
- How much time typically passes between preparation, review, decision, and execution?

## Review Context

- What must local authority review before deciding whether the action should proceed?
- Which evidence is assembled manually?
- Which context is commonly missing, stale, or contradictory?
- Can a review packet become stale before execution?
- How is that detected today?
- Does the current approval remain meaningful if the underlying evidence changes?
- Which prior decisions should influence a later review?

## Ownership

- Who operates the workflow?
- Who holds local authority?
- Which function is accountable for incomplete or obsolete review context?
- Who owns integration?
- Who owns the review record?
- Which budget could fund improvement?

## Vendor Independence

- What context would need to survive replacement of the model?
- What context would need to survive replacement of the agent runtime?
- What context would need to survive replacement of the wallet, custodian, or settlement provider?
- Is institution-controlled review chronology important?

## Dependency

- Would the institution delay a decision if the review context could not be reconstructed?
- Would this context be required for every action or only defined action classes?
- What would make the structured packet operationally necessary rather than optional?
- What would degradation look like if the context layer disappeared?

## Evidence-Capture Schema

```yaml
operator_interaction:
  interaction_id:
  observed_at:
  evidence_class: direct_operator_discovery

  participant:
    role:
    organization_type:
    identifiable_information_committed_to_public_repo: false

  workflow:
    action_class:
    recurrence:
    preparing_system:
    local_authority_role:
    external_execution_systems: []

  current_review_process:
    evidence_sources: []
    manual_stitching:
    authority_source_rules:
    pending_state:
    review_to_execution_delay:
    stale_context_risk:
    contradiction_handling:
    chronology_owner:

  ownership:
    operational_owner:
    local_authority:
    risk_owner:
    integration_owner:
    pain_owner:
    budget_owner:

  signals:
    exact_operator_language: []
    integration_request:
    temporal_validity_requested:
    portable_chronology_requested:
    required_context_behavior:
    buyer_pull_claim_supported: false
    adoption_claim_supported: false

  follow_up:
    requested:
    next_action:
```

Completed discovery records must be stored in an approved private evidence environment. This public template does not authorize the storage of confidential operator information in the repository.

## Temporal Implementation Gate

Documenting temporal context does not authorize runtime implementation. A later engineering cycle requires explicit approval and evidence meeting this gate:

```yaml
temporal_implementation_gate:
  direct_operator_interactions: at_least_2

  required_evidence:
    - operator_reports_review_context_becoming_stale
    - workflow_has_material_review_to_execution_delay
    - institution_defines_evidence_age_or_revalidation_condition
    - operator_requests_machine_readable_temporal_state
    - temporal_state_changes_review_behavior

  required_ownership:
    pain_owner_identified: true
    workflow_owner_identified: true

  CCO_review_required: true
  separate_engineering_cycle_required: true
```

Market commentary alone does not satisfy this gate. One operator mentioning timing is a signal, not sufficient implementation authority.
