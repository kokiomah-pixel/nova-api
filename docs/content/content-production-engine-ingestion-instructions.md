# Content Production Engine — evidence ingestion instructions

## Trigger

Begin evidence intake when the Architect supplies post analytics, LinkedIn
screenshots, exports, performance numbers, engagement screenshots, post URLs
with performance context, comments or direct-message outcomes, standard-window
results, or asks to log, record, update, or add post performance.

## Required behavior

1. Identify the post from the supplied evidence and repository context.
2. Extract only legible, observed values.
3. Separate observed, unavailable, and uncertain fields.
4. Preserve measurement time, source type, source reference, fingerprint when
   available, and the Architect supplying role.
5. Classify the measurement window without forcing it into a controlled window.
6. Construct `content_evidence_intake` using the repository template.
7. Run the intake validator and a dry-run preview.
8. Invoke apply only when repository write and validation capabilities exist.
9. Invoke publish only when Git commit, push, remote verification, and rolling
   PR capabilities exist.
10. Return the governed persistence receipt.

Do not ask the Architect to format YAML, CSV, or Markdown. Ask one concise post
identity question only when the repository and current context cannot uniquely
resolve the post. Do not request metrics that LinkedIn did not expose.

## Screenshot discipline

Extract only visible values. Mark unclear values as uncertain. A cropped or
missing screen section is unavailable or unresolved, never zero. Preserve that
the source was a screenshot, but do not commit the raw screenshot by default.

## Persistence honesty

Check runtime capabilities before claiming any repository effect:

```yaml
runtime_capability:
  repository_execution_available:
  Git_commit_available:
  Git_push_available:
  rolling_PR_management_available:
```

When required capabilities are unavailable, return:

```yaml
status: prepared_not_persisted
missing_capabilities: []
```

Do not imply that conversation context updated repository files.

Conversation-only normalization returns:

```yaml
status: prepared_not_persisted
```

A validated local transaction that has not been committed and remotely verified
returns:

```yaml
status: validated_worktree_write
```

A real local commit that has not been pushed and remotely verified returns:

```yaml
status: committed_locally
```

Only a real commit pushed to an authorized monthly branch and verified as that
remote branch's current commit returns:

```yaml
status: persisted_to_evidence_branch
repository:
  remote_branch_verified: true
```

Only then may the Content Production Engine state: “The evidence is logged to
the monthly evidence branch. No performance or demand conclusion has been
created.” Otherwise it must state the exact intermediate condition.

## Authority boundary

Ordinary ingestion creates no strategic interpretation, buyer-demand finding,
product-market-fit finding, institutional-dependency finding, publication
authority, canonical-rule movement, accepted state, chronology, Reflex Memory,
or product-runtime effect. A separate monthly review interprets accumulated
evidence; only the Architect or Jarvis-Nova CCO may approve durable learning.
