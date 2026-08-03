# Reflex Memory Specification

## Status

Specification draft
Non-authority mechanism
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document defines Reflex Memory as an inspectable governance-memory mechanism for Sharpe Nova OS.

Reflex Memory is not an execution engine, approval system, denial system, authorization layer, trading signal, compliance system, audit product, wallet control layer, payment-control system, or autonomous learning system.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

## Definition

Reflex Memory is accepted governance memory derived from reviewed chronology events.

It may condition future API-emitted review context by surfacing prior governance stress, source-state deterioration, boundary risk, or recurring review-context patterns.

Reflex Memory does not approve, deny, authorize, block, route, settle, sign, execute, or replace local authority.

## Core Distinction

Logs are operational residue.
Working memory is current operating context.
Chronology is accepted decision-state lineage.
Reflex Memory is accepted governance memory that may condition future review posture.
API output remains review context, not authority.

## Reflex Memory Is Not Agent Memory

Reflex Memory should not be interpreted as agent self-reflection, episodic agent memory, vector recall, prompt memory, or autonomous learning.

Reflex Memory is governed institutional memory.

It is derived from reviewed chronology events and accepted through governance process.

It may condition future review posture.

It does not improve an agent by itself.

It does not become the memory of an external agent framework.

It does not approve, deny, authorize, block, route, settle, sign, execute, perform compliance review, produce audit reports, supervise agents, manage wallets, or replace local authority.

For the architecture boundary distinction, see:

- `docs/architecture/reflex-memory-vs-agent-memory.md`

## Relationship to Chronology

Chronology preserves decision-state lineage.

Reflex Memory is not raw chronology.

Reflex Memory is accepted governance memory derived from reviewed chronology events.

A chronology event may become a Reflex Memory candidate only after review.

A Reflex Memory candidate becomes active only after explicit acceptance.

Generated does not mean reviewed.
Reviewed does not mean accepted.
Accepted does not mean public.
Public does not mean production.

## Reflex Memory v0.1 Scope

The v0.1 Reflex Memory mechanism is intentionally narrow.

```yaml
reflex_memory_v0_1:
  detection: explicit_rule_based
  source: accepted_chronology_events_only
  mutation: manual_acceptance_required
  influence: api_review_context_only
  authority: none
  output: reflex_memory_context_field
  proof: replayable_fixture
```

## Non-Goals

Reflex Memory v0.1 does not:

- use autonomous learning
- use model-driven memory mutation
- approve actions
- deny actions
- grant payment permission
- serve as an execution checkpoint
- route transactions
- settle value
- sign transactions
- manage wallets
- supervise agents
- perform compliance review
- perform audit reporting
- replace local authority
- predict market outcomes
- generate trading signals
- optimize portfolios

## Reflex Memory Entry Schema

A Reflex Memory entry should preserve the following fields:

```yaml
reflex_memory_entry:
  reflex_id:
  version:
  status:
  source_chronology_event_ids:
  created_at:
  reviewed_at:
  accepted_at:
  accepted_by:
  source_state:
    classification:
    limitations:
  trigger_pattern:
  stress_type:
  boundary_risk:
  review_posture_effect:
  evidence_refs:
  expiration_or_review_after:
  non_authority_statement:
```

## Allowed Status Values

```yaml
status_values:
  - candidate
  - reviewed
  - accepted
  - archived
  - rejected
```

## Source-State Classifications

```yaml
source_state_classifications:
  - source_confirmed
  - architect_provided
  - cco_reconciled
  - source_incomplete
  - source_conflict
  - stale_connector_artifact
  - unverified_external_summary
  - blocked_pending_reconciliation
```

## Allowed Review Posture Effects

Reflex Memory may only condition review context.

Allowed review posture effects include:

```yaml
allowed_review_posture_effects:
  - surface_prior_stress
  - require_source_reconciliation_context
  - flag_boundary_language_risk
  - mark_context_as_source_limited
  - preserve_manual_review_attention
  - add_chronology_reference
  - require_proof_reference
  - highlight_recurring_context_pattern
```

Forbidden review posture effects include:

```yaml
forbidden_review_posture_effects:
  - approve_action
  - deny_action
  - grant_payment_permission
  - block_execution
  - route_transaction
  - settle_value
  - sign_transaction
  - manage_wallet
  - supervise_agent
  - perform_compliance_review
  - perform_audit_reporting
```

## Invariants

Reflex Memory must preserve these invariants:

```yaml
reflex_memory_invariants:
  - Reflex Memory can only be created from reviewed chronology events.
  - Reflex Memory cannot mutate automatically.
  - Reflex Memory cannot approve, deny, authorize, block, route, settle, sign, or execute.
  - Reflex Memory can only condition review context.
  - Every Reflex Memory entry must reference source chronology.
  - Every Reflex Memory entry must preserve source-state classification.
  - Every Reflex Memory entry must include a non-authority statement.
  - Every API exposure of Reflex Memory must preserve local authority.
  - Every replay must reconstruct why Reflex Memory appeared in review context.
  - Reflex Memory must not be used as a trading signal, compliance determination, audit report, or execution instruction.
```

## API Review-Context Exposure

Reflex Memory may appear in API-emitted review context as a transparent field.

Example:

```yaml
reflex_memory_context:
  present: true
  entries:
    - reflex_id: RM-0001
      source_chronology_event_ids:
        - CHR-2026-07-03-001
      reason: prior source-state conflict required reconciliation before review
      review_posture_effect: require_source_reconciliation_context
      authority_effect: none
```

The API output remains review context.

It is not an approval, denial, authorization, block, route, settlement, signature, or execution command.

## Validation-History Learning Boundary

Reflex Memory may preserve an accepted lesson about future review requirements
only after the underlying chronology event and candidate complete the existing
manual review and acceptance flow.

```yaml
Reflex_Memory_prohibitions:
  - model_prestige_as_future_trust
  - provider_identity_as_authority
  - prior_validation_pass_as_automatic_acceptance
  - universal_model_reliability_ranking
  - automatic_policy_change
```

```yaml
validation_learning:
  problem_or_action_class:
  claim_origin_type:
  validation_methods_used: []
  assumptions_that_failed: []
  assumptions_that_held: []
  authority_treatment:
  later_confirmation_or_correction:
  outcome_relevance:
  proposed_future_review_requirement:
  formal_acceptance_status:
```

An accepted lesson concerns the evidence, assumptions, validation methods, and
future review requirements relevant to a problem or action class. It must not
be reduced to:

```text
Model X was correct before,
therefore trust Model X next time.
```

A model or provider name remains provenance, not authority. A prior validation
pass cannot create automatic institutional applicability, future acceptance,
or policy change.

This documentation change creates no Reflex Memory candidate, accepted entry,
or other Reflex Memory object.

## Acceptance Flow

```text
chronology_event
-> reflex_memory_candidate
-> CCO or local governance review
-> accepted_reflex_memory_entry
-> API review-context reference
-> local authority decision
-> execution elsewhere
```

## Failure Modes

Known failure modes include:

- over-trusting Reflex Memory as a decision system
- treating Reflex Memory as autonomous learning
- allowing stale source state to condition future review posture
- failing to preserve source chronology references
- collapsing logs, chronology, and Reflex Memory into generic memory
- using Reflex Memory as approval, denial, compliance, audit, trading, or execution logic

## Safe Language

Use:

- Reflex Memory informs the review context emitted by the API.
- Accepted governance memory may condition future review posture.
- Memory conditions review.
- Authority remains local.
- Execution happens elsewhere.

## Unsafe Language

Do not use:

- Reflex Memory powers live API decisions.
- Nova's API decides based on memory.
- Nova learns from capital actions.
- Nova autonomously updates financial posture.
- Reflex Memory restores authority.
- Reflex Memory denies actions.
- Reflex Memory blocks execution.

## Evidence Needed Before Stronger Claims

Before Reflex Memory can be described as production-reviewable, Sharpe Nova OS should have:

- formal fixtures
- schema validation
- replay tests
- non-authority tests
- source-state conflict tests
- candidate-to-accepted lifecycle tests
- API context output examples
- documentation showing how local authority remains responsible

## Reference Fixture

A non-production Reflex Memory v0.1 fixture is available at:

- `docs/governance/reflex-memory-v0-1-fixture.md`

The fixture demonstrates:

- reviewed chronology event
- Reflex Memory candidate
- accepted Reflex Memory entry
- API review-context exposure
- `authority_effect: none`

The fixture does not demonstrate production readiness, adoption, market validation, buyer validation, live deployment, approval, denial, authorization, blocking, routing, settlement, signing, execution, compliance review, audit reporting, wallet control, or agent supervision.

## Final Rule

Reflex Memory is valuable only if it improves review continuity without becoming authority.

Memory conditions review.
Authority remains local.
Execution happens elsewhere.
