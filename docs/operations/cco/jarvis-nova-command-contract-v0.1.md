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
      Determine whether submitted evidence satisfies the previously defined
      completion condition.
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

`review-completion` applies the existing priority-register and terminal
completion-evidence rules. Submitted evidence without independent verification
remains non-terminal. The command reports a derived review result without
mutating the register or independently authenticating the supplied evidence.

`compare-state` requires live operational assessments, a prior assessment with
a distinct verified basis, and a current assessment that identifies the
supplied prior assessment as its `prior_verified_assessment`. It reports
deterministic structural differences separately from governed state-movement
fields. An explicit initial baseline cannot be used as a prior verified
comparison state. Missing, stale, unavailable, or unknown current evidence is
reported and is not represented as established no-change.

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
