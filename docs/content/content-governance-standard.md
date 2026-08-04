# Content governance standard

## Scope

This standard governs content assignments, drafts, publication records,
performance evidence, experiments, reviews, and durable-rule proposals. It does
not govern runtime execution or change corporate accepted state.

## Authority

- The Daily Coherence Agent controls the operating loop and may prepare work.
- The Content Production Engine drafts and revises within assigned rules.
- The Architect or explicitly authorized operator controls publication.
- Only the Architect or Jarvis-Nova CCO may approve durable rule movement or
  canonical-rule mutation.
- A monthly review is interpretation, not approval.

```text
Daily Coherence proposes.
Jarvis-Nova reviews.
Architect or Jarvis-Nova CCO approves durable rule movement.
```

An approval must separately record `status`, `authority_role`,
`approval_reference`, and `approved_at`. A nonblank name or provenance string
does not establish authority. The Daily Coherence Agent, Content Production
Engine, and monthly review process cannot approve durable rule movement.

```yaml
approval_schema:
  status:
    - not_requested
    - approved
    - accepted
    - rejected
  authority_role:
    - Architect
    - Jarvis-Nova_CCO
  approval_reference:
  approved_at:
```

## Evidence states

Use `observed`, `reported`, `inferred`, `unavailable`, or `unverified` where an
evidence field needs classification. Keep raw observation separate from
interpretation. Record measurement windows, dates, and sources. Never coerce
unknown values to zero or compare unlike windows without disclosure.

## Publication records

Published copy is immutable in its post record. Corrections or rewrites become
new, linked records or clearly labeled annotations. Every published post must
have a measurement schedule for 24 hours, 7 days, and 30 days.

## Audience evidence and privacy

Record only details materially useful for audience-quality evaluation. Do not
scrape private LinkedIn data, store unnecessary personal information, automate
DMs, use fake accounts, purchase engagement, or automate engagement
manipulation.

## Evidence ingestion

Architect-supplied evidence is normalized before persistence. Daily Coherence
must preview the exact write set, resolve the post without guessing, preserve
source provenance and uncertainty, detect duplicates, and validate every
affected artifact before a durable write. Raw screenshots remain in
Architect-controlled storage by default; the repository stores normalized
values, a source reference, and a fingerprint.

Unavailable data is recorded as `unavailable`; numeric zero is permitted only
when directly observed. Performance corrections are append-only and name the
earlier `evidence_record_id`. Same-window conflicts without correction lineage
remain unresolved. Ingestion alone creates no interpretation, publication
authority, durable rule movement, accepted state, chronology, or Reflex Memory.

## Experiment integrity

One experiment changes one primary variable. Record the control, test, metrics,
audience-quality measure, and narrative-accuracy measure before interpreting a
result. Completion requires measurement evidence. Promotion requires explicit
approval at the canonical threshold.

## Learning and change control

Single posts are observations. Three comparable posts may establish a
provisional pattern. Repetition across multiple pillars or two months may
establish a candidate rule. Only a structured approval from the Architect or
Jarvis-Nova CCO establishes a canonical rule. Superseded instructions are
archived.

## Prohibited inferences

Do not infer demand from impressions, willingness to pay from likes,
product-market fit from follower growth, institutional dependency from
comments, or accepted-state movement from content performance. Content evidence
does not create chronology or Reflex Memory.

## Escalation

Escalate category-confusing high reach, repeated tool framing, two months of
declining target-market engagement, recurring new operator language, material
qualified-inbound movement, pricing or buyer language, repeated production-rule
violations, incomplete monthly data, or production volume above measurement
capacity. Quietly track signals that do not yet affect audience strategy,
narrative architecture, GTM, workflow wedge, monetization, category, or
implementation priority.
