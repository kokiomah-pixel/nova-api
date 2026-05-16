# Terminology Migration Summary

This document documents the approved, docs-first terminology mapping used during the pass. No schema key renames were performed; changes were applied to documentation, examples, and comments only.

Mapping (original -> doctrine-preferred)

- allow / approve / authorized -> admissibility environment / constraint state / coordination_state
- deny / reject -> constraint_pressure / threshold_exceeded / fragmentation_state
- execute / execution -> execution environment (referential) / avoid prescriptive language
- recommendation / signal / prediction -> pacing condition / pulse / drift / environmental state
- action / action_id -> coordination_state / pulse_id (in docs only)

Notes on application

- Where example payloads used legacy keys (e.g., "allowed"), the example descriptions were updated to explain the intended conditioning semantics while retaining the original fields unless doing so would imply a schema change.
- Any proposal to rename runtime schema keys is recorded in unresolved-risks-and-actions.md and not implemented in this pass.
