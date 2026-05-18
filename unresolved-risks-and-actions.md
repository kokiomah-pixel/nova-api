# Unresolved Risks and Actions

This file records optional follow-ups, risks, and items not changed due to the docs-first, non-breaking constraint.

Actions recommended (optional follow-up, not implemented in this pass):

1. Schema key migration: Transition legacy keys (e.g., "allowed", "decision_status") to doctrine-preferred keys (e.g., "coordination_state", "constraint_pressure"). This requires coordination and a migration window with aliases.
2. SDK updates: Update SDK examples and client libraries to align naming and reduce framing as execution authority.
3. Deeper telemetry harmonization: Standardize telemetry enums across the stack (would require careful testing).
4. Internal hardening: Move sovereign data files to an internal-only location or repository and restrict access.
5. Doctrine lint adoption: Wire `./.venv/bin/python scripts/doctrine_lint.py` into the preferred CI path once the protected branch workflow is confirmed.
6. Chronology records: Add new governance epoch records only when doctrine posture materially changes.

Risks identified

- External integrators may have code that treats certain existing fields as directives; communications and migration guidance are required before any schema changes.
- Some example materials still reference older terminology in archived or legacy directories; these were marked in the audit and should be pruned or updated in follow-up work.

This pass did not change any runtime behavior, endpoints, or schema keys. All follow-ups are optional and documented for the Jarvis-Nova Chief Coherence Officer to consider.
