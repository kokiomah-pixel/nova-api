# Retail Context Object Schema v0.1

The Retail Context Object is the authority-neutral, machine-readable envelope
shared by retail context resources. Its canonical JSON Schema is
`specs/retail_context_object_v0_1.schema.json` and uses JSON Schema Draft
2020-12.

## Scope

The object carries resource identity, a subject, generation time, resolution
state, freshness, confidence, source provenance, evidence, contradictions,
evidence gaps, limitations, and an explicit `authority_effect: none` boundary.
`resource_type` is a constrained slug rather than a resource-specific enum so
the envelope can be reused by `state_ping`, `context_delta`, later evidence and
contradiction resources, later reflex comparison resources, and full context.
This schema defines their common representation only; it does not implement
their business logic.

## Required envelope

Every object requires:

- `resource_id` and `resource_type`
- structured `subject`
- `schema_version`, fixed to `0.1.0`
- RFC 3339 `generated_at`
- `context_status`
- structured `freshness` and `confidence`
- arrays for `provenance`, `evidence`, `contradictions`,
  `unresolved_evidence`, and `limitations`
- `authority_effect`, fixed to `none`

The canonical context states are `resolved`, `partially_resolved`, `unresolved`,
and `insufficient_evidence`.

A `resolved` object must contain at least one provenance item and at least one
evidence item. This prevents a structurally valid object from representing
resolution without positive supporting evidence.

An `insufficient_evidence` object must name at least one unresolved, missing, or
unavailable evidence gap, but its provenance and evidence arrays may be empty.
This makes absence explicit without manufacturing a positive observation.

## Independent state dimensions

Freshness records `observed_at`, non-negative `source_age_seconds`, and one of
`fresh`, `aging`, `stale`, or `unknown`.

`fresh`, `aging`, and `stale` require both a non-null observation time and a
non-null, non-negative source age. `unknown` may use null observation time and
age. The schema intentionally defines no production age thresholds; threshold
policy belongs to later resource and data gates.

Confidence records a bounded level (`high`, `medium`, `low`, or
`indeterminate`) and a written basis. It is descriptive and is not a
probability forecast.

Each provenance item separately records source availability/verification and
claim reconciliation. `present_unverified` is not `verified`, and neither state
means a claim is reconciled. Evidence has its own status and references its
source by `source_id`; evidence state never substitutes for confidence.

Contradictions are structured, reference at least two evidence identifiers, and
may remain `unresolved`. No reconciliation is forced. Missing and unresolved
evidence is represented separately from positive evidence.

## Non-authority and isolation

The object is descriptive context only. It does not approve, deny, authorize,
execute, instruct a trade, sign a transaction, settle, express institutional
policy or accepted state, or mutate institutional chronology or institutional
Reflex Memory. Strict objects reject fields outside the contract, including
institutional state-bearing identifiers or credentials. No pricing, payment,
wallet identity, execution recommendation, or directional trading output is
part of this schema.

RP2 adds no endpoint, runtime acquisition, payment, deployment, or institutional
state integration.

## Validation

Use `retail_context.schema.validate_retail_context_object` for Python callers.
It applies a Draft 2020-12 validator and format checking for timestamps. Valid
examples live in `fixtures/retail_context/context_object/`.
