# Chronology Governance Standard

This standard extends the existing preservation and reconciliation doctrine with four append-only lanes: Reflex, archive, operations, and governance. Operational events describe what occurred; governance events describe authority transitions. Neither a commit nor CI result grants authority, and implementation is never execution.

Events use immutable lane-prefixed IDs, explicit occurred/recorded/effective timestamps, evidence references, review and acceptance states, and confidence classifications. Verified claims require evidence. Inferred or unresolved claims cannot be accepted as underlying fact. Supersession preserves both records; corrections are new events that identify their target and reason. Accepted entries are never edited in place.

Reflex admits only governed Reflex lineage. CI, commits, raw telemetry, and unreviewed operational or governance records cannot enter Reflex automatically. The existing Reflex candidate schema remains separate and untouched.

Generated indexes, cleanliness reports, and monitoring-console status are derived views, not authority sources. The console may read only the generated report and must show unavailable, invalid, or stale states visibly. Gate 4B execution remains blocked and unaccepted; Gate 5 remains unauthorized.
