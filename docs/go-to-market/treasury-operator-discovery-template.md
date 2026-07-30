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

## Machine-Spending Review Context Module

### Research status

```yaml
research_status:
  subject: machine_spending_review_context
  hypothesis_status: unvalidated
  buyer_demand_established: false
  recurring_operator_need_established: false
  product_requirement: false
  runtime_implementation_authorized: false
```

Use this optional, clearly separated module when the recurring treasury action
includes an agent discovering, requesting, or relying on a paid machine
resource. The questions test a specification-level hypothesis derived in part
from market signal
[`MSE-2026-07-30-028`](../market/signals/2026/MSE-2026-07-30-028-fastly-x402-edge-payment.md).
Fastly is an example provider, not a Nova dependency. Answers are operator
research, not accepted product requirements.

### Wallet and mandate

- Who owns or controls the wallet used by the agent?
- Is spending authority defined by agent, task, provider, resource class,
  amount, or time period?
- Which purchases may occur under standing authority?
- Which purchases require local review?
- Who may change spending limits or provider permissions?
- Can a cryptographically valid x402 challenge be rejected for institutional
  reasons?
- Is Nova expected before wallet authorization, after authorization, or only
  during later review?
- What happens when the wallet or facilitator changes?

### Provider and resource governance

- May an agent purchase from any provider?
- How are approved and prohibited providers represented?
- Which data or resource classifications are permitted?
- Does payment create contractual obligations?
- Does the request disclose confidential task context?
- Can a low-cost purchase create jurisdictional or recurring obligations?
- Can the purchase grant the agent new capabilities or access?

### Evidentiary use

- May purchased information enter a financial review automatically?
- Which sources are institutionally authoritative?
- Must paid-resource provenance be visible to local authority?
- Can the institution permit the expenditure but reject the output as
  evidence?
- How are summaries, transformations, and agent-generated claims linked back
  to the paid source?
- Is the purchase amount material, or is the information's later use more
  important?

### Chronology

- Does the institution retain why the agent made the purchase?
- Can a purchase be linked to the action the resulting information supported?
- Which payment events are important enough to retain?
- Can the institution distinguish resource access from evidentiary reliance?
- What survives when the wallet, edge provider, facilitator, or resource
  provider changes?
- Can the institution reconstruct what was known before the wallet signed?

### Commercial validation

- Does the absence of this context delay, prevent, or weaken review?
- Would the institution require this context before certain machine purchases?
- Is the problem recurring within a defined action class?
- Who owns the budget for solving it?
- Is the value tied to transaction count, governed workflows, review
  environments, or chronology continuity?
- Would the institution refuse to review a machine-prepared action without
  this context?

Do not convert answers into product requirements without separate CCO and
Architect approval. Do not commit completed interview responses or paid
resource content to the public repository.

### Machine-spending category boundary

Nova is not a payment gateway, x402 facilitator, wallet-policy engine,
spending-control product, edge-enforcement service, signing service, settlement
service, transaction-authorization system, resource-access authority, or
paid-data marketplace.

> x402 and edge infrastructure determine whether a payment requirement was
> satisfied and whether a resource may be served. Sharpe Nova OS structures the
> institution-defined review context surrounding why a machine expenditure was
> proposed and how the resulting resource should be treated if it later
> influences a consequential capital review.

```text
Nova structures.
Institutional authority interprets.
External wallets and payment systems act.
```
