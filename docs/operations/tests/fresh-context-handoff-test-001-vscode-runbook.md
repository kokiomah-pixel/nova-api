# Fresh-Context Handoff Test 001 — VS Code Runbook

## Status

Strict isolated execution runbook
Internal continuity test
Not external validation
Not buyer validation
Not market validation
Not production failover certification
Not model certification
Not authority delegation

## Purpose

This runbook defines how to execute Fresh-Context Handoff Test 001 from VS Code while preventing broader Sharpe Nova OS context from entering the model session.

VS Code coordinates the test.

A genuinely isolated model session performs the test.

The evidence bundle records:

- what files were supplied
- what exact prompt was sent
- what model returned
- what controls were applied
- how the result was scored

## Approved Inputs

Only these files may be supplied to the model under test:

```text
docs/operations/tests/fresh-context-handoff-test-001-prompt.md
docs/operations/records/decision-state-handoff-001.md
docs/operations/current-system-state.md
docs/operations/current-authority-and-escalation-map.md
```

## Isolation Requirements

The strict test must use:

```yaml
isolation_requirements:
  new_model_session: true
  prior_Nova_context_present: false
  persistent_memory_enabled: false
  repository_indexing_enabled: false
  full_repository_exposed: false
  web_access_enabled: false
  external_tools_enabled: false
  additional_files_supplied: false
  expected_answers_supplied: false
  operator_coaching_supplied: false
```

## Prohibited Execution Surfaces

Do not run the strict test in:

* an existing Nova chat
* a project chat with Sharpe Nova OS memory
* a repository-aware coding agent with full-workspace access
* a model session that has previously reviewed Nova
* a VS Code extension that injects repository context automatically
* a session with browsing or external retrieval enabled
* a session where the operator corrects or coaches the model before preserving the response

## Recommended Execution Surface

Use one of:

1. a stateless API request launched from the VS Code terminal
2. a clean local model session with no persistent state
3. a new ChatGPT conversation outside the Nova project with memory disabled
4. a separate model workspace containing only the isolated test directory

The strongest repeatable option is a stateless single-request API call.

## Stateless API Execution

After preparing the isolated workspace, run the strict test using:

```text
scripts/run_stateless_fresh_context_request_001.py
```

The script sends one OpenAI Responses API request with:

```yaml
request_controls:
  prior_messages: none
  previous_response_id: absent
  conversation_id: absent
  tools: []
  tool_choice: none
  store: false
```

The script preserves:

* a safe request record without the API key
* the complete API response
* the first model answer
* input and response hashes
* an execution receipt

The first successful model answer is the test result.

Do not rerun it to improve the answer.

## Execution Sequence

```text
canonical repository
→ export approved files
→ create isolated temporary workspace
→ record hashes
→ build exact model input
→ launch one clean model request
→ preserve raw response
→ record execution metadata
→ attest isolation conditions
→ score separately
→ commit evidence to repository
```

## Contamination Conditions

The test is contaminated if:

* the model has prior Nova history
* project memory is enabled
* the full repository is available
* additional files are visible
* repository search or indexing is available
* web access or external retrieval is used
* expected answers are supplied
* the operator corrects the response before preservation
* a follow-up prompt is used to repair the first answer
* the raw answer is edited before hashing

A contaminated test must not be scored as a pass.

## Final Rule

Isolation is part of the evidence.

A correct answer from a contaminated session does not prove model-independent continuity.
