# Fresh-Context Handoff Test 001 - Execution Instructions

## Purpose

These instructions define how to run the test in a genuinely isolated model context.

## Isolation Requirement

The test must be run in one of the following:

- a new ChatGPT conversation with no prior Sharpe Nova OS context
- a separate model workspace with no Nova memory
- a clean local model session with no prior Nova prompt history
- a new API conversation containing only the system instruction, test prompt, and three canonical files

Do not run the strict test inside a conversation that already contains Nova history.

## Input Package

Provide only:

```text
docs/operations/tests/fresh-context-handoff-test-001-prompt.md
docs/operations/records/decision-state-handoff-001.md
docs/operations/current-system-state.md
docs/operations/current-authority-and-escalation-map.md
```

Do not provide expected answers.

Do not explain Nova beforehand.

Do not correct the model during the test.

## Execution Sequence

1. Open a genuinely fresh model session.
2. Paste the contents of `fresh-context-handoff-test-001-prompt.md`.
3. Attach or paste the three canonical source files.
4. Ask the model to complete the test.
5. Save the complete response without editing it.
6. Record the model and session metadata.
7. Evaluate the response using the scoring standard.
8. Preserve the raw result before making any corrections.

## Session Metadata

Record:

```yaml
test_session:
  test_id: fresh-context-handoff-test-001
  execution_date:
  model_name:
  model_version_if_visible:
  platform:
  memory_enabled:
  prior_Nova_context_present: false
  external_tools_enabled:
  external_tools_used: false
  executed_by:
```

## Contamination Rule

The test is contaminated and must be rerun if:

- the model session previously discussed Nova
- project memory supplied Nova context
- the model browsed the repo beyond the three files
- the operator coached the expected answers
- the response was corrected before preservation
- hidden context was known to be injected

Record contaminated tests, but do not score them as passes.

## Final Rule

Isolation is part of the evidence.

A correct answer from a contaminated session does not prove model-independent continuity.
