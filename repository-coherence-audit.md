# Repository Coherence Audit

Purpose

This audit captures repository surfaces that were reviewed during the doctrine alignment pass, the semantic inconsistencies found, and actions taken or recommended.

Reviewed surfaces

- README and top-level documentation
- docs/overview.md and related docs
- examples directory (documented; examples preserved; keys unchanged)
- specs/decision_admission_contract.json (preserved; no schema key renames)
- inline comments and docstrings (selected non-behavioral edits applied where safe)

Key findings and actions

1. Execution-centric language found in README and docs. Action: rephrased to emphasize environmental governance.
2. References to authoritative decision_status and ALLOW/DENY semantics present in docs and examples. Action: replaced with coordination/conditioning language in documentation; schema keys left intact.
3. Telemetry naming in fixtures and example payloads often used "allowed/denied" vocabulary. Action: updated example descriptions to prefer "constraint_pressure", "coordination_state", and "drift_score" while keeping schema keys stable when required.

Outstanding recommendations

- Consider a future, staged migration to align schema keys with doctrine (requires coordination with integrators). Documented in unresolved-risks-and-actions.md.
- Review SDKs and client integrations for language that assumes execution authority.

Conclusion

The coherence pass was limited to documentation and non-breaking text edits. The repository now communicates environmental governance framing across primary documentation surfaces.
