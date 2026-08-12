# Jarvis-Nova Command Contract v0.1

## Purpose and boundary

This contract defines a bounded deterministic command layer around the CCO
Operating Spine. Jarvis-Nova constructs the reasoning artifact. The repository
command validates that artifact against the governed contract.

```text
reasoning layer
        ↓
structured assessment or evidence record
        ↓
deterministic challenge
```

The command layer does not generate assessments, select priorities, route
natural-language requests, execute work, or authenticate external production
systems.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Jarvis-Nova remains outside the Nova product plane.

## Canonical command intents

```yaml
commands:
  what_does_system_need:
    intent: >
      Determine the highest-leverage unresolved uncertainty and recommend
      one bounded action class.
    valid_actions:
      - build
      - test
      - research
      - reconcile
      - wait
      - stop
    creates_authority: false

  review_completion:
    intent: >
      Determine whether submitted evidence satisfies the structural terminal-
      evidence contract and is eligible for separate terminal review.
    creates_authority: false

  compare_state:
    intent: >
      Calculate decision-relevant movement between verified assessment states.
    creates_authority: false
```

## Command semantics

`what-does-system-need` accepts YAML or JSON. It requires
`record_source_type: operational_assessment` and
`operational_evidence_eligible: true`. A synthetic fixture may validate the
static schema in repository tests, but it cannot pass as a live assessment.
The command validates the supplied assessment and emits a bounded summary; it
does not invent its binding uncertainty, action class, owner, authority need,
material delta, or completion condition.

`review-completion` validates the structural terminal-evidence contract and
determines whether the supplied evidence package is eligible for separate
terminal review. It does not independently authenticate the evidence, determine
that an arbitrary semantic completion condition is true, mutate the priority
register, or automatically move an item into terminal state. A populated
`independently_verified_at` field is reported only as an independent-
verification claim in the supplied metadata; it is not external truth verified
by this generic command.

`compare-state` requires live operational assessments and a current assessment
that identifies the supplied prior assessment as its
`prior_verified_assessment`. A valid initial operational assessment may use
`explicit_initial_baseline` with `material_delta: unknown`. Once validated,
that assessment may serve as the prior assessment for a later assessment; the
later assessment must reference its assessment ID using
`prior_verified_assessment`. The command reports deterministic structural
differences separately from governed state-movement fields. Missing, stale,
unavailable, or unknown current evidence is reported and is not represented as
established no-change.

## Non-equivalences

```text
chat phrase
!=
execution authority

command invocation
!=
product runtime invocation

command validation
!=
production attestation

reasoning
!=
machine validation
!=
authority
!=
assignment
!=
implementation
!=
completion
!=
independent verification

structural difference
!=
accepted-state movement

terminal evidence contract satisfied
!=
semantic completion verified
!=
item closed
```

Passing command validation means the supplied artifact satisfies the stated
repository contract. It does not mean that the command independently verified
source truth. Recommendation is not authorization, assignment is not
authorization, and completion is not independent verification.

## Explicit non-effects

```yaml
authority_effect: none
product_runtime_effect: none
production_effect: none
accepted_state_effect: none
chronology_effect: none
Reflex_Memory_effect: none
constraint_effect: none
pricing_effect: none
capital_authority_effect: none
external_integration_effect: none
```
