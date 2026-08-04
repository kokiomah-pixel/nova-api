# Content evidence ingestion protocol

## Status and capability gate

This protocol is proposed until its ingestion-bridge pull request merges. It
does not activate evidence operations by being present in a branch.

```yaml
content_ingestion_capability:
  structured_extraction_available: required
  repository_write_tool_available: checked_at_runtime
  repository_validation_available: checked_at_runtime
  outcomes:
    connected:
      status: persisted_to_evidence_branch
    disconnected:
      status: prepared_not_persisted
```

```text
Evidence pasted != evidence structured.
Evidence structured != evidence persisted.
Evidence persisted to branch != evidence merged to main.
Evidence merged to main != performance interpreted.
Performance interpreted != canonical learning.
```

## Operating flow

```text
LinkedIn evidence
-> Content Production Engine intake
-> normalized evidence object
-> Daily Coherence validation
-> dry-run write preview
-> transactional repository update
-> affected-artifact validation
-> persistence receipt
-> weekly and monthly interpretation
```

The CLI defaults to dry run. An apply is permitted only on a monthly branch
matching `ops/content-evidence-YYYY-MM`, or on the exact branch supplied through
`--expected-branch`. Raw screenshots remain in Architect-controlled storage by
default; the repository receives normalized values, a source reference, a
fingerprint, and uncertainty.

## Identity and provenance

- Post: `POST-YYYY-MM-DD-HASH8`, stable across windows.
- Intake: `INTAKE-YYYYMMDDTHHMMSS-HASH8`.
- Performance evidence: `EVID-<POST-ID>-<WINDOW>-<SOURCE-HASH8>`.
- Audience evidence: `ENGAGE-<POST-ID>-<DATE>-<HASH8>`.

IDs never depend on row position. Duplicate protection uses `post_id`,
`classified_window`, and `source_fingerprint`.

## Measurement windows

Controlled windows are `24_hours`, `7_days`, and `30_days`. A valid explicit
window is preserved. Otherwise, publication and measurement timestamps are
used with configured tolerances. Known nonstandard ages become `ad_hoc`; an
unknown age becomes `historical_unknown_age`. Only controlled windows may be
routed to an active experiment.

## Post resolution

Resolve in this order: exact post ID, exact URL, existing record URL,
publication date plus exact copy, publication date plus working title, then
unresolved. Never choose between multiple candidates. A new published record
requires exact published copy, publication date or timestamp, publication URL,
intended audience, narrative pillar, and governed distinction. Exact published
copy is immutable after creation.

## Preview and persistence

Preview reports post resolution, window, observed/unavailable/uncertain fields,
material audience observations, exact planned paths, and blockers. It creates
no files.

Apply builds every affected artifact in a temporary workspace, runs intake,
post, ledger, experiment, current-state, and receipt validation, and only then
atomically replaces repository files. A failure restores every original file
and returns `rolled_back`; no success receipt may survive rollback.

A successful local transaction records a `transaction:<sha256>` durable
transaction reference in the receipt. Daily Coherence then creates the focused
monthly-branch commit:

```text
ops(content): ingest <post-id> <measurement-window> evidence
```

The monthly branch is committed and reviewed separately from `main`. The
receipt continues to report `main_merge_verified: false` until the evidence PR
is merged.

## Append-only evidence and corrections

Performance rows are never overwritten or deleted. `observation` creates an
ordinary row. `correction` or `supersession` appends a new row and must name an
existing `supersedes_record_id`. Same-window conflicting values without that
lineage are held as `conflict_requires_review`. A repeated source fingerprint
is `duplicate_noop`.

Audience rows are created only for materially useful audience-quality evidence
with a relevance basis and an identifiable role, company, or minimally needed
person/company reference. A changed total reaction count alone creates no
audience row.

## Routed artifacts

A successful transaction may create or update:

- `intake/YYYY/MM/<intake-id>.yaml`;
- `posts/YYYY/MM/<post-id>.md`;
- the append-only performance ledger;
- the audience ledger when material evidence exists;
- `content-current-state.yaml`;
- only `posts_included` and `measurement_evidence` for an active experiment;
- `receipts/YYYY/MM/<intake-id>.yaml`.

Results, interpretation, evidence strength, recommended actions, promotion
status, canonical rules, accepted state, chronology, and Reflex Memory are not
changed by ingestion.

## Historical evidence

Prospective August evidence remains separate from pre-August retrospective
evidence. Historical evidence uses `historical_unknown_age` unless reliable age
evidence exists and is not controlled-experiment evidence by default.

## Rolling evidence branch

For August 2026, use `ops/content-evidence-2026-08` and a rolling draft PR titled
`ops: ingest August 2026 content evidence`. Routine merge cadence is weekly,
with final reconciliation at month end. Repository merge remains an explicit
governed action.
