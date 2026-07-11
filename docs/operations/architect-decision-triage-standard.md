# Architect Decision Triage Standard

## Status

Internal operating standard
Decision-load containment
Not delegated authority
Not autonomous governance
Not execution authority
Not doctrine automation

## Purpose

This standard reduces unnecessary concentration of routine operating decisions on the Architect while preserving the Architect's authority over direction, doctrine, commercialization, and material system change.

The goal is not to remove the Architect.

The goal is to ensure the Architect is engaged when judgment is direction-changing rather than when classification is routine.

## Core Rule

Jarvis-Nova may classify and prepare.

The Architect decides when the issue changes:

- Nova's category
- authority boundary
- product direction
- monetization direction
- public positioning
- institutional commitments
- material architecture
- accepted governance memory
- production scope

## Decision Classes

### Class A - Routine Operating Classification

Jarvis-Nova may complete without Architect approval.

Examples:

- classify an observation as interesting but not decision-relevant
- identify duplicate documentation
- flag stale internal state
- prepare a non-directional console refresh
- correct formatting
- identify an existing doctrine conflict
- recommend no action
- update an internal watch item
- classify a source as unavailable or stale

Required output:

```yaml
decision_class: A
Architect_action_required: false
direction_changed: false
doctrine_changed: false
```

### Class B - Bounded Maintenance Recommendation

Jarvis-Nova may prepare an implementation packet, but the Architect approves implementation.

Examples:

- clarify an already accepted boundary
- reconcile stale console state
- add an internal operating template
- improve chronology cleanliness
- update reviewer navigation
- add a negative-language containment rule
- improve existing evidence mapping

Required output:

```yaml
decision_class: B
Architect_action_required: true
approval_type: implementation_approval
direction_changed: false
```

### Class C - Directional Decision

The Architect must decide before implementation.

Examples:

- change Nova's category
- change public positioning
- change pricing or monetization logic
- begin a new phase
- add a commercial service
- change the authority boundary
- add runtime integration
- alter Reflex Memory acceptance rules materially
- create an external pilot
- expose proprietary operating logic

Required output:

```yaml
decision_class: C
Architect_action_required: true
approval_type: directional_decision
implementation_before_approval: prohibited
```

### Class D - Sovereign Boundary Decision

The Architect must decide explicitly and the decision must be preserved in chronology.

Examples:

- grant Nova approval or blocking authority
- allow autonomous Reflex Memory mutation
- make Nova an execution controller
- expose sovereign thresholds or weighting logic
- transfer institutional decision rights
- approve production capital integration
- authorize compliance or audit claims

Default posture:

```yaml
decision_class: D
default_recommendation: reject_or_hold
Architect_action_required: true
CCO_review_required: true
chronology_required: true
```

## Escalation Test

Escalate to the Architect when any answer is yes:

```yaml
escalation_test:
  changes_category: false
  changes_authority: false
  changes_monetization: false
  creates_external_commitment: false
  changes_doctrine: false
  exposes_sovereign_logic: false
  changes_production_scope: false
  accepts_governance_memory: false
```

## Architect Attention Protection

Do not escalate merely because an issue is:

- interesting
- novel
- well worded
- externally visible
- mentioned by another model
- theoretically important

Escalate when the issue becomes:

- repeated
- consequential
- direction-changing
- boundary-relevant
- commercially material
- operationally blocking

## Final Rule

Protect the Architect from classification load.

Do not protect the Architect from directional decisions.
