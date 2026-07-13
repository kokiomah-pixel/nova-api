# Chronology Status Semantics

- `implemented`: code or a bounded record exists.
- `executed`: a runtime event occurred and has execution evidence.
- `validated`: evidence checks passed.
- `accepted`: an authorized reviewer accepted the evidence.
- `blocked`: a required dependency is unavailable; this is not failure.
- `superseded`: a later governed state replaced an earlier state without deleting it.
- `unresolved`: evidence is insufficient and the unknown is explicit.
- `verified`: available evidence supports the claim.
- `inferred`: reasonable but not proven.

Cleanliness may be `clean_intact`, `clean_reconciled`, `clean_with_explicit_unknowns`, `partially_clean`, or `not_fully_clean`. A report with errors cannot claim a clean state. Gate 4B implementation acceptance does not imply execution acceptance or final gate acceptance. Gate 5 is not authorized.
