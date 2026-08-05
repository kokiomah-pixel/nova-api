# Content performance evidence

The two CSV files in this directory are evidence ledgers. Append one performance
row per post and measurement window and one audience row per materially useful
engagement observation.

## Measurement discipline

- Measure at `24_hours`, `7_days`, and `30_days`.
- Do not compare unlike windows as equivalent.
- Use `unavailable` when LinkedIn does not expose a metric.
- Use `0` only when zero is directly observed.
- Classify `evidence_status`; separate observation from inference in notes.
- Preserve exact post IDs so ledger rows resolve to `posts/YYYY/MM/` records.

## Audience and privacy discipline

Record only information needed to assess target-market quality. Do not scrape
private data or store unnecessary personal details. Permitted relevance values
are `high`, `medium`, `low`, and `unknown`. Permitted understanding values are
`correct_Nova_understanding`, `partial_understanding`, `category_confusion`, and
`no_evidence`.

## Observational measurements

Measurements outside the controlled 24-hour, seven-day, and 30-day windows may
be preserved as `ad_hoc` when the measurement age is known or
`historical_unknown_age` when it is not known.

These rows are evidence-preservation records. They must not be compared as
equivalent to controlled windows and do not independently establish an
experiment result. Record age information in the `notes` field when an
observational measurement is used.

## Interpretation

Reach includes impressions, non-follower exposure, reposts, and profile
discovery. Resonance includes saves, thoughtful comments, target-role reactions,
correct restatements, and workflow DMs. Conversion includes relevant profile
visits/follows, qualified conversations, workflow discussions, design-partner
interest, and institutional inquiries. None of these alone proves demand or
product-market fit.
