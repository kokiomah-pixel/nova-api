# Fresh-Context Handoff Test 001 - Completion Instructions

## If the Result Is Pass

Update:

```text
docs/operations/records/decision-state-handoff-001.md
```

Replace:

```yaml
status: pending_execution
```

With:

```yaml
status: completed
test_result: pass
test_record: docs/operations/tests/results/fresh-context-handoff-test-001-evaluation.md
```

Update:

```text
docs/operations/internal-integrity-exercise-001.md
```

Complete Exercise E:

```yaml
exercise_E_result:
  handoff_complete: true
  new_context_used_prior_memory: false
  questions_answered_correctly: true
  missing_context: []
  contradictory_context: []
  corrective_action: none
```

Do not mark the entire integrity exercise complete unless Exercises A-D and F have also been completed.

Update:

```text
docs/operations/current-system-state.md
```

Change:

```yaml
operational_exercise_status: pending_first_exercise
```

To:

```yaml
operational_exercise_status: partially_executed
fresh_context_handoff_test: passed
```

## If the Result Is Pass With Gaps

Do not add a new standard.

Correct only the specific ambiguous or missing fields in:

- `decision-state-handoff-001.md`
- `current-system-state.md`
- `current-authority-and-escalation-map.md`

Then rerun the strict test in another fresh session.

Record both test runs.

## If the Result Is Fail

Do not claim model-independent continuity.

Create a reconciliation record identifying:

- missing state
- conflicting state
- misunderstood authority
- misunderstood chronology
- misleading non-claims
- unclear console trigger

Correct canonical files only after CCO review.

Then run a new numbered test:

```text
fresh-context-handoff-test-002
```

Do not overwrite the failed result.

## If the Test Is Contaminated

Preserve the contaminated result.

Mark:

```yaml
result: contaminated_rerun_required
```

Run the same test in another isolated session.

## Final Rule

Preserve every result.

Do not convert a failed or contaminated test into a pass through editing.
