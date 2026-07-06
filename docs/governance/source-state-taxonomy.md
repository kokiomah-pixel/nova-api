# Source-State Taxonomy

## Status

Governance taxonomy
Architecture hardening artifact
Not production data-quality system
Not compliance review
Not audit reporting
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document defines source-state terms used by Sharpe Nova OS when structuring governed review context.

Source-state classification helps local authority understand the quality and limitations of context before deciding.

Source-state classification does not approve, deny, authorize, block, route, settle, sign, execute, certify compliance, produce audit reports, or replace local authority.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## Source-State Classes

Use the following classes:

```yaml
source_state_taxonomy:
  source_confirmed:
    meaning: source is available, current enough for review, and internally consistent
    review_effect: may support normal review context

  source_incomplete:
    meaning: source exists but lacks required fields, proof references, or supporting context
    review_effect: must surface missing fields or limitations

  source_conflict:
    meaning: two or more sources disagree or cannot be reconciled automatically
    review_effect: must surface contradiction before local authority reviews

  source_stale:
    meaning: source exists but may no longer reflect current review state
    review_effect: must surface freshness limitation

  source_unavailable:
    meaning: expected or required source is missing
    review_effect: must surface missing source and avoid implying completeness

  cco_reconciled:
    meaning: source issue has been reviewed and classified through governance review
    review_effect: may be used as reconciled review context but does not become authority
```

## Classification Discipline

Every source-state class should answer:

```yaml
classification_questions:
  what_is_known: required
  what_is_missing: required_if_applicable
  what_is_conflicting: required_if_applicable
  what_is_stale: required_if_applicable
  what_was_reconciled: required_if_applicable
  what_local_authority_still_decides: required
```

## Relationship to Review Completeness

A source problem does not always make a prepared action impossible to review.

It may make the action:

```yaml
review_state_effects:
  complete_for_review: source context is sufficient and visible
  incomplete_but_visible: source gaps are surfaced
  blocked_for_review_context: required source context is missing and not reconstructible
```

Nova does not decide the action.

Nova structures the source-state visibility.

## Relationship to Reflex Memory

Source-state stress may generate a chronology event.

A reviewed chronology event may produce a Reflex Memory candidate.

Only accepted Reflex Memory may condition future review posture.

Source-state classification alone does not become Reflex Memory automatically.

## Unsafe Interpretations

Do not interpret source-state classification as:

* compliance approval
* data certification
* audit opinion
* execution permission
* denial instruction
* authorization status
* risk score
* trading signal
* portfolio recommendation

## Safe Language

Use:

```text
Source state describes the condition of review context.
```

Use:

```text
Source-state limitations should be visible before local authority decides.
```

Use:

```text
Source-state classification does not create authority.
```

## Final Rule

Sources may be confirmed, incomplete, conflicting, stale, unavailable, or reconciled.

Nova structures that source-state context.

Local authority decides.

Execution happens elsewhere.
