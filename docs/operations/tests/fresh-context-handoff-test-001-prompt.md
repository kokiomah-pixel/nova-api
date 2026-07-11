# Fresh-Context Handoff Test 001

## Role

You are reviewing Sharpe Nova OS with no prior conversational knowledge.

You must use only the three source files provided with this test:

1. `docs/operations/records/decision-state-handoff-001.md`
2. `docs/operations/current-system-state.md`
3. `docs/operations/current-authority-and-escalation-map.md`

Do not use:

- outside knowledge
- assumptions
- prior conversation memory
- external web sources
- unstated project context

If the files do not answer a question, state that the context is insufficient.

## Questions

Answer the following:

1. What phase is Sharpe Nova OS currently in?
2. Is Phase 2 approved?
3. What is the active operating command?
4. Who has directional authority?
5. What is the current role of chronology?
6. What claims remain unvalidated or explicitly unclaimed?
7. What event should trigger review of whether the Internal Monitoring Console needs a canonical repository location?

## Required Evidence Discipline

For each answer:

- identify the source file
- quote or paraphrase only the relevant state
- do not infer beyond the files
- identify any contradictions
- identify any missing context

## Required Output

```yaml
fresh_context_answers:
  current_phase:
    answer:
    source:

  Phase_2_approved:
    answer:
    source:

  active_operating_command:
    answer:
    source:

  directional_authority:
    answer:
    source:

  chronology_role:
    answer:
    source:

  unvalidated_or_unclaimed:
    answer:
    source:

  console_canonicalization_trigger:
    answer:
    source:

test_assessment:
  all_seven_questions_answered:
  contradictions_detected:
  missing_context:
  prior_context_required:
  external_context_used:
  result:
    - pass
    - pass_with_gaps
    - fail
```

## Result Rules

Use `pass` only when:

- all seven questions are answered correctly
- the three files are sufficient
- no prior context is required
- no material contradictions are present
- no external context is used

Use `pass_with_gaps` when:

- the core operating state is reconstructable
- one or more answers require minor inference
- one or more fields are incomplete
- the gaps do not materially change current state

Use `fail` when:

- the current phase cannot be determined
- Phase 2 approval status is unclear
- directional authority is unclear
- active command is unclear
- chronology role is materially misunderstood
- material contradictions exist
- prior context is required

## Final Rule

Reconstruct the accepted state.

Do not recommend new development.

Do not initialize Phase 2.

Do not create new doctrine or authority.
