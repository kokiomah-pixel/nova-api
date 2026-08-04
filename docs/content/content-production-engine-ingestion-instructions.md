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
9. Return the governed persistence receipt.

Do not ask the Architect to format YAML, CSV, or Markdown. Ask one concise post
identity question only when the repository and current context cannot uniquely
resolve the post. Do not request metrics that LinkedIn did not expose.

## Screenshot discipline

Extract only visible values. Mark unclear values as uncertain. A cropped or
missing screen section is unavailable or unresolved, never zero. Preserve that
the source was a screenshot, but do not commit the raw screenshot by default.

## Persistence honesty

Conversation-only normalization returns:

```yaml
status: prepared_not_persisted
```

Only a validated durable write on an authorized evidence branch returns:

```yaml
status: persisted_to_evidence_branch
```

After persistence, state: “The evidence is persisted to the monthly evidence
branch. No performance or demand conclusion has been created.”

## Authority boundary

Ordinary ingestion creates no strategic interpretation, buyer-demand finding,
product-market-fit finding, institutional-dependency finding, publication
authority, canonical-rule movement, accepted state, chronology, Reflex Memory,
or product-runtime effect. A separate monthly review interprets accumulated
evidence; only the Architect or Jarvis-Nova CCO may approve durable learning.
