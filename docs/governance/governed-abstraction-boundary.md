# Sharpe Nova OS — Governed Abstraction Boundary

## Purpose

This document defines how a reviewed chronology event may produce a proposed
reusable lesson without silently becoming Reflex Memory, policy, precedent,
constraint logic, or institutional authority.

## Core rule

```text
Chronology may support abstraction.

Abstraction remains a candidate until explicit review.

Only accepted Reflex Memory may condition later review context.

No memory object creates authority.
```

## Failure mode: implicit policy conversion

```yaml
failure_mode:
  name: implicit_policy_conversion

  definition: >
    An observed pattern, model-generated lesson, repeated operator behavior, or
    prior outcome is reused as though it were accepted institutional policy
    without explicit review and authority treatment.

  prohibited_transitions:
    - observed_behavior_to_policy
    - repeated_behavior_to_constraint
    - model_summary_to_accepted_memory
    - semantic_similarity_to_precedent
    - prior_success_to_future_authority
    - provider_identity_to_trust
```

## Required state separation

```yaml
governed_abstraction_state:
  lifecycle_status:
    question: Where is the object in its review lifecycle?
    examples:
      - candidate
      - reviewed
      - accepted
      - rejected
      - archived

  epistemic_status:
    question: How should the underlying proposition be treated?
    examples:
      - source_supported
      - source_limited
      - disputed
      - contradicted
      - unverified
      - superseded

  authority_treatment:
    question: What institutional authority, if any, has adopted the lesson?
    examples:
      - reference_only
      - accepted_for_review_use
      - exception_only
      - formally_adopted_by_local_authority
      - superseded

  precedent_treatment:
    question: How may the prior event relate to a current action?
    examples:
      - none
      - analogous
      - materially_distinguishable
      - exception_only
      - contradicted
      - superseded
```

These dimensions must not be collapsed into one generic `status` field.

An accepted memory object may preserve a disputed proposition.

A formally adopted rule may later be superseded.

An exception may be useful reference context without becoming precedent.

## Candidate requirements

Every abstraction candidate must preserve:

* source chronology IDs;
* evidence references;
* proposed lesson;
* knowledge class;
* action class;
* applicability conditions;
* material distinctions;
* known exceptions;
* contradictory cases;
* unresolved conditions;
* epistemic status;
* authority treatment;
* precedent treatment;
* reviewer and acceptance fields when applicable;
* supersession lineage;
* `authority_effect: none`;
* a non-authority statement.

## Retrieval rule

Accepted Reflex Memory may be surfaced only with an explanation of:

* why it is structurally relevant;
* which comparison dimensions match;
* which material differences remain;
* whether the prior case was disputed, exceptional, contradicted, or superseded;
* why no authority or automatic precedent follows.

## Self-improvement boundary

Sharpe Nova OS does not autonomously improve itself.

It supports a governed institutional process through which reviewed chronology
may become accepted, challengeable, and supersedable governance memory.

## Final rule

```text
Compression without lineage creates hidden doctrine.

Lineage without bounded abstraction creates unusable history.

Nova requires both, with authority remaining local.
```
