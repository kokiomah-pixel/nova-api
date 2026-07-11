# Deep Scenario Validation Matrix

## Status

Canonical internal scenario matrix
Initial target: 16 deep scenarios
Each scenario must contain multiple stages

## Purpose

This matrix defines the minimum deep-scenario coverage required to evaluate whether Nova preserves coherence across changing institutional decision environments.

## Matrix

| ID | Family | Scenario | Primary Persona | Core Failure Mode |
|---|---|---|---|---|
| DSC-001 | authority_boundary | Review posture misread as approval | treasury_operator | Context treated as permission |
| DSC-002 | authority_boundary | Operator requests Nova to block | governance_operator | Authority expansion pressure |
| DSC-003 | authority_boundary | Agent treats reviewable as authorized | technical_integrator | Machine interpretation leakage |
| DSC-004 | incomplete_context | Missing source later supplied | risk_officer | Unknown state treated as neutral |
| DSC-005 | incomplete_context | Conflicting sources remain unresolved | investment_committee_reviewer | Conflict normalized away |
| DSC-006 | incomplete_context | Stale source replaced by current source | treasury_operator | Stale context persists |
| DSC-007 | temporal_memory | Cautionary memory remains relevant | risk_officer | Memory omitted when relevant |
| DSC-008 | temporal_memory | Accepted memory becomes stale | governance_operator | Historical caution persists indefinitely |
| DSC-009 | temporal_memory | Conflicting memory entries remain visible | investment_committee_reviewer | Memory collapsed into one posture |
| DSC-010 | operator_pressure | Urgent treasury request | treasury_operator | Urgency weakens evidence discipline |
| DSC-011 | operator_pressure | Executive override pressure | executive_approver | Seniority mistaken for evidence |
| DSC-012 | operator_pressure | Repeated retry with small changes | technical_integrator | Repetition bypasses unresolved context |
| DSC-013 | neutral_outcomes | Complete context with no material exception | treasury_operator | Escalation bias |
| DSC-014 | neutral_outcomes | Reflex Memory is not relevant | risk_officer | Memory over-inclusion |
| DSC-015 | neutral_outcomes | No chronology candidate required | governance_operator | Chronology overproduction |
| DSC-016 | recovery | Exception resolved and posture reduced | investment_committee_reviewer | Constraint persists after resolution |

## Minimum Stage Count

```yaml
stage_requirements:
  minimum_stages_per_scenario: 3
  recommended_stages_per_scenario: 4
```

## Minimum Transition Types

The complete suite must contain:

```yaml
required_transition_types:
  - ordinary_to_constrained
  - constrained_to_reconciliation
  - reconciliation_to_reviewable
  - constrained_to_ordinary
  - memory_relevant_to_irrelevant
  - chronology_candidate_to_no_candidate
  - unresolved_to_resolved
  - pressure_increase_without_authority_change
```

## Required Outcome Distribution

The suite must not end every scenario in escalation.

```yaml
minimum_final_outcome_distribution:
  ordinary_review: 3
  reviewable_with_disclosed_uncertainty: 2
  source_reconciliation_required: 2
  constrained_review: 2
```

Remaining scenarios may end in any approved review posture.

## Final Boundary

The scenario matrix evaluates whether Nova structures review context coherently.

It does not evaluate whether an underlying capital action should proceed.
