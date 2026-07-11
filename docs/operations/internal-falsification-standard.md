# Internal Falsification Standard

## Status

Internal adversarial review discipline
Not external validation
Not market validation
Not buyer validation
Not production testing
Not compliance assessment

## Purpose

Sharpe Nova OS must be capable of testing whether its own assumptions are wrong.

Internal coherence is necessary but insufficient.

This standard requires material claims to be tested against plausible failure conditions before they are hardened into stronger doctrine, positioning, or commercial logic.

## Core Rule

```text
Do not ask only whether Nova is coherent.

Ask what would have to be true for Nova's current position to be wrong, unnecessary, or commercially weak.
```

## Required Falsification Questions

For each material claim, test:

1. What evidence would contradict this claim?
2. What alternative explanation fits the same evidence?
3. What buyer or operator would reject this value?
4. What existing system could absorb this function?
5. What happens if review context is useful but not required?
6. What happens if institutions prefer active enforcement?
7. What happens if chronology is not perceived as valuable?
8. What happens if Nova's non-authority stance is seen as insufficient?
9. What happens if the open core is copied?
10. What happens if the model provider changes behavior or availability?

## Claim Test Record

```yaml
falsification_test:
  claim:
  claim_class:
  supporting_evidence:
  contradictory_evidence:
  alternative_explanation:
  strongest_counterargument:
  failure_condition:
  current_confidence:
  action:
```

## Confidence Classes

```yaml
confidence_classes:
  architecture_defined:
    meaning: internally specified and inspectable

  fixture_supported:
    meaning: supported by repository fixtures or tests

  internally_demonstrated:
    meaning: shown in a bounded internal example

  externally_observed:
    meaning: observed externally but not validated broadly

  externally_validated:
    meaning: repeated external evidence exists

  commercially_validated:
    meaning: payment_or_operational_commitment_exists
```

Do not promote a claim beyond its evidence class.

## Adversarial Roles

An internal review may assign these roles:

```yaml
adversarial_roles:
  skeptical_buyer:
    question: why_pay_for_non_authority_context

  platform_competitor:
    question: why_not_absorb_this_into_existing_workflow

  developer:
    question: why_is_this_not_just_an_API_or_schema

  institutional_operator:
    question: how_does_this_change_my_review_process

  risk_officer:
    question: what_does_this_prove_and_not_prove

  open_source_competitor:
    question: what_cannot_be_copied_from_the_repo
```

## Decision Rule

A failed internal falsification test does not automatically invalidate Nova.

It may reveal:

- unsupported confidence
- missing evidence
- category ambiguity
- commercial weakness
- dependency on assumptions
- need for no action yet

## Final Rule

Nova must be allowed to discover that an internal belief is premature.

That is not drift.

That is coherence under pressure.
