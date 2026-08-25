# Gate 3 Field-Derivation Ledger v0.1

## Status and authority

```yaml
gate: Gate_3_v2_field_derivation_design
status: complete_for_design_v2.1_contract
artifact_status: design_review_complete_contract_revision_incorporated
CCO_review: approved
Architect_review: approved
approved_for_incorporation: [G3-R01, G3-R03, G3-R08, G3-R11, G3-Q15]
canonical_contract_revision: incorporated
contract_revision_target: design-v2.1
canonicality_source: authoritative_repository_main
design_only: true
target_v2_runtime_implemented: false
private_adapter_implemented: false
production_activation_authority: false
cryptographic_implementation_authority: false
merge_authority: false
deployment_authority: false
implementation_authority: false
authority_effect: none
execution_effect: none
```

This ledger uses the `design-v2.1` target-v2 contract and its machine
specification as semantic authorities. Canonicality is determined by
authoritative repository `main`. The approved Gate 3A cryptographic-agility and
post-quantum threat-model invariants are design input. Legacy v1 is migration
reference only and is never target-v2 semantic authority.

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Every required field in the approved response contract has one rule in
[`review_context_field_derivation_v0_1.json`](../../specs/review_context_field_derivation_v0_1.json).
The machine spec remains design-only. The contract revision creates
no runtime or implementation authority.

## Governing derivation rule

A target-v2 value may come only from attributable evidence, identified
institution configuration, a deterministic relationship, an approved contract
constant, or an explicit unresolved state. It may not come from an unstated Nova
judgment, a model-generated permission, or a Legacy v1 outcome.

Every field rule resolves these questions:

- derivation class, required inputs, source authority scope, rule and version;
- missing, unavailable, conflicting, and temporal behavior;
- source-environment segmentation;
- sensitivity, semantic-hash scope, proof-envelope scope, and disclosure;
- cryptographic-profile dependency and reconstruction requirement;
- proposed contract gaps and prohibited dependencies.

## Identity before classification

```text
action_id != proposal_version_id
```

`action_id` is stable across revisions only when an institution or orchestrator
supplies it. It is required whenever cross-revision lineage is claimed. Nova
must not derive it from mutable proposal content. If it is absent, lineage is
`unavailable`; two proposal versions must not be inferred to belong to the same
action.

`proposal_version_id` identifies the exact proposal reviewed and should likewise
prefer an external institution/orchestrator identifier. If that identifier is
absent, the proposal permits only an algorithm-qualified value explicitly
labeled `Nova_derived_proposal_fingerprint`, derived from canonical
prepared-action material alone. That fallback distinguishes proposal content;
it cannot establish action lineage. A proposal revision changes semantic
context and cannot replay under the proof of an earlier proposal.

The `design-v2.1` request now accepts optional `action_id` and
`proposal_version_id` inputs. The response binds the exact
`prepared_action_reference.proposal_version_identity` and an external `action_id`
when available; its existing `reference_id` remains a compatibility reference
and never substitutes for both identities. This is the incorporated `G3-R01`
contract revision, not runtime implementation.

## Profile-driven requirements

The identified institution-approved review profile, not Nova, defines required
evidence, maximum age and other thresholds, source hierarchy, constraint
applicability, required fields, and revalidation conditions. Its ID, version,
owner, and hash are preserved. A profile change may explain a completeness or
semantic-hash change even when evidence is unchanged.

Missing or conflicting profile rules remain unresolved. Incorporated `G3-R08`
places public enum meaning and precedence in the `design-v2.1` target-v2 contract rather than
institution profiles: `unavailable`, `conflicted`, `partial`, then `complete`.
`unavailable` means the profile or required-field inventory prevents evaluation;
`conflicted` means required context has unresolved material conflict; `partial`
means required context is missing/unavailable without a higher-priority
conflict; `complete` means every required dimension is represented, including
allowed explicit unresolved states, with no material conflict. This remains a
contract. Complete never means policy satisfied, safe, permitted, approved, or
executable.

## Scoped source authority

Authority is scoped to declared fields or questions. A proposed normalized
source reference carries source identity/version, observed and received times,
environment segment, and designation metadata (`designated_by`, `applies_to`,
and `authority_reference`). An institution designation does not erase contrary
evidence. Nova stable-collects conflicts and selects no winner.

## Separate state dimensions

These dimensions never collapse into one another:

```text
source_state
context_state
review_completeness
proof_verification_state
```

The source-state candidate order is `unavailable`, `conflicted`, `partial`, then
`complete`. Complete means complete only within profile-declared scope; it does
not mean true, correct, safe, approved, or executable.

The context-state candidate order is `superseded`, `stale`, `uncertain`, then
`current`. Staleness uses only an institution-defined profile threshold. A
missing timestamp is `uncertain`, never silently current. Traceability and
replayability do not establish temporal relevance.

Proof states (`verified`, `verified_with_deprecated_suite`, `unverifiable`,
`invalid`, and `unresolved`) describe cryptographic verification only. A proof
state change does not automatically change source, context, or completeness.

## Evidence-environment segmentation

`synthetic`, `production_like`, and `live` remain visible at field or source
reference level. Incorporated `G3-R03` adds aggregate value `mixed`, meaning that
more than one evidence-environment class is represented. `source_segmentation`
remains authoritative component provenance. No strongest/weakest heuristic is
used, `production_like` is never promoted to `live`, and `live` never means
true, accepted, or approved.

## Required response-field ledger

The table enumerates all 55 required leaf fields. Detailed missing,
unavailable, conflict, temporal, sensitivity, proof, and reconstruction metadata
is machine-readable in the companion spec.

| # | Required field path | Derivation summary |
|---:|---|---|
| 1 | `review_context_response.schema_version` | Exact approved contract constant. |
| 2 | `review_context_response.context_id` | Generated envelope ID; excluded from semantic identity. |
| 3 | `review_context_response.request_id` | Opaque request reference; excluded from semantic identity. |
| 4 | `review_context_response.created_at` | Nova record time; not independently trusted time. |
| 5 | `review_context_response.prepared_action_reference.reference_id` | Compatibility reference only; it is not both stable lineage and exact proposal identity. |
| 5a | `review_context_response.prepared_action_reference.proposal_version_identity` | Structured exact-proposal identity with visible external or Nova-derived genesis; Nova derivation carries algorithm qualification and prepared-action-only scope. |
| 6 | `review_context_response.prepared_action_reference.reference_type` | Contract constant `opaque_external_reference`. |
| 7 | `review_context_response.prepared_action_reference.payload_embedded` | Contract constant `false`. |
| 8 | `review_context_response.review_profile_reference.profile_id` | Exact institution profile ID. |
| 9 | `review_context_response.review_profile_reference.profile_version` | Exact version; never inferred latest. |
| 10 | `review_context_response.review_profile_reference.profile_owner` | Declared owner; no Nova policy authority. |
| 11 | `review_context_response.review_profile_reference.profile_hash` | Supplied digest; algorithm qualification proposed. |
| 12 | `review_context_response.record_source_type.value` | Incorporated G3-R03 aggregate: homogeneous environment or `mixed`; segmentation remains authoritative. |
| 13 | `review_context_response.record_source_type.source_segmentation` | Stable source/field environment segments without promotion. |
| 14 | `review_context_response.context_state.value` | Profile-temporal and supersession evaluation. |
| 15 | `review_context_response.context_state.reasons` | Stable reason codes, not generated prose. |
| 16 | `review_context_response.source_state.value` | Declared-coverage and conflict evaluation. |
| 17 | `review_context_response.source_state.sources` | Stable scoped source references. |
| 18 | `review_context_response.source_state.unresolved_source_conflicts` | All unresolved conflicts; no selected winner. |
| 19 | `review_context_response.constraint_context.observed_constraints` | Institution-declared constraint references only. |
| 20 | `review_context_response.constraint_context.constraint_sources` | Scoped source references and segmentation. |
| 21 | `review_context_response.constraint_context.unresolved_constraint_questions` | Stable unresolved codes without policy resolution. |
| 22 | `review_context_response.temporal_context.source_observed_at` | Normalized source time or explicit unknown. |
| 23 | `review_context_response.temporal_context.source_received_at` | Normalized receipt time or explicit unknown. |
| 24 | `review_context_response.temporal_context.review_context_created_at` | Nova record time, semantic-hash excluded. |
| 25 | `review_context_response.temporal_context.intended_action_window` | Normalize explicit `start`/`end` under G3-R11 timestamp rules or preserve structured unresolved boundaries; invalid boundaries fail without authority effect. |
| 26 | `review_context_response.temporal_context.temporal_conflicts` | Stable collection of all temporal conflicts. |
| 27 | `review_context_response.temporal_context.pending_state` | Explicit unresolved temporal conditions. |
| 28 | `review_context_response.contradiction_context.source_conflicts` | Normalized source conflicts. |
| 29 | `review_context_response.contradiction_context.constraint_conflicts` | Constraint conflicts without Nova resolution. |
| 30 | `review_context_response.contradiction_context.temporal_conflicts` | Normalized temporal conflicts. |
| 31 | `review_context_response.contradiction_context.chronology_conflicts` | Existing-reference conflicts; no chronology write. |
| 32 | `review_context_response.contradiction_context.unresolved_questions` | Stable union of unresolved questions. |
| 33 | `review_context_response.review_completeness.value` | Target-v2 contract precedence is `unavailable > conflicted > partial > complete`; profiles define requirements, evidence, thresholds, applicability, and revalidation, not enum meaning or precedence. |
| 34 | `review_context_response.review_completeness.missing_context` | Stable list of missing profile-required fields. |
| 35 | `review_context_response.review_completeness.unresolved_conditions` | Unresolved evaluation conditions and precedence. |
| 36 | `review_context_response.chronology_context.prior_review_references` | Existing references only. |
| 37 | `review_context_response.chronology_context.accepted_memory_references` | Already accepted references only. |
| 38 | `review_context_response.chronology_context.relevant_changes_since_prior_review` | Explicit versioned changes; no inferred precedent. |
| 39 | `review_context_response.authority_handoff.decision_owner` | Contract constant `local_institutional_authority`. |
| 40 | `review_context_response.authority_handoff.execution_owner` | Contract constant `external_system`. |
| 41 | `review_context_response.authority_handoff.Nova_authority_effect` | Contract constant `none`. |
| 42 | `review_context_response.reproducibility.schema_version` | Exact response schema version. |
| 43 | `review_context_response.reproducibility.source_versions` | Stable exact source versions/digests. |
| 44 | `review_context_response.reproducibility.classification_version` | Exact field-derivation version. |
| 45 | `review_context_response.reproducibility.review_profile_id` | Exact joined profile ID. |
| 46 | `review_context_response.reproducibility.review_profile_version` | Exact joined profile version. |
| 47 | `review_context_response.reproducibility.review_profile_hash` | Algorithm-qualified profile digest proposal. |
| 48 | `review_context_response.reproducibility.record_source_type` | Declared aggregate without promotion. |
| 49 | `review_context_response.reproducibility.source_segmentation` | Exact stable segmentation. |
| 50 | `review_context_response.reproducibility.context_hash` | Algorithm-qualified digest of canonical semantic bytes. |
| 51 | `review_context_response.reproducibility.signature` | Compatibility proof slot; plural attestations proposed. |
| 52 | `review_context_response.boundary.approval_effect` | Contract constant `none`. |
| 53 | `review_context_response.boundary.authorization_effect` | Contract constant `none`. |
| 54 | `review_context_response.boundary.execution_effect` | Contract constant `none`. |

Optional `claim_context_response` remains optional and source-driven. It is not
a Gate 3 completion dependency. Model genesis and validation scope do not create
authority or institutional applicability.

## Semantic identity and proof identity

Semantic context identity is separate from cryptographic attestation identity.
Changing a signing key, signature suite, key epoch, transition mode, or renewal
time does not silently change semantic meaning. The proposed semantic hash binds
canonical context bytes plus explicit derivation/profile identities. Generated
record IDs, request IDs, record time, signatures, signing algorithms, keys,
epochs, and renewal times are excluded.

A proposed versioned cryptographic profile carries algorithm and parameter
identity, permitted suites, transition behavior, key-reference policy, and
verification-policy version. Unknown suites are `unverifiable`; downgrades fail
closed. No production algorithm or PQC suite is selected by this design.

Plural proof attestations may represent `primary`, `parallel_transition`, and
`renewal`. Renewal preserves original context hash and prior attestations and
does not mean rereview, reapproval, reauthorization, or chronology acceptance.
Parallel digest migration binds all algorithm-qualified digest records to the
identical canonical semantic byte sequence. Semantic identity is not any one
digest. Historical evidence is preserved, successor digests do not replace it,
and different algorithms are never described as producing the same hash value.
This continuity rule is incorporated refinement `G3-Q15` in the contract
revision; it does not add the unapproved G3-Q13 plural transport.

## Canonical numeric and interoperability model

Incorporated refinement `G3-R11` adopts RFC 8785/JCS as the I-JSON structural
canonicalization baseline and adds a versioned application profile for exact
financial semantics. JCS's IEEE-754 number model is not used for semantic
financial values. Binary floats, NaN, and infinity are prohibited.

- exact integers use a typed canonical base-10 string, with no exponent,
  leading zeros, or negative zero;
- exact decimals use signed coefficient plus nonnegative scale, with exponent
  removed and no rounding; every field profile declares `max_precision`,
  `max_scale`, and `max_abs_exponent`, enforced before coefficient expansion;
- generic decimal trailing zeros are insignificant, while fixed-scale fields
  retain the institution-profile scale;
- monetary amounts bind explicit asset/unit, coefficient, and profile scale;
- RFC 3339 timestamps normalize to UTC with six fractional digits, reject
  sub-microsecond rounding, and reject `-00:00` as unknown offset rather than
  silently treating it as UTC `Z`;
- Unicode is preserved as-is per JCS and `null` differs from absent;
- every semantic array explicitly declares `ordered_sequence`, `set`, or
  `multiset` semantics. Every `deterministic_collection` has an executable
  rule; all current set-like response fields are sorted/deduplicated by their
  declared rule, and identity collisions fail until represented as conflicts.

The executable design-only reference semantics live in
`scripts/gate3_reference_semantics.py`. They are validation support, not target
v2 runtime code and do not select a production hash algorithm.

## Privacy, reconstruction, and time

Hashing is not redaction. Raw wallet addresses, account identifiers,
transaction payloads, credentials, institution secrets, and personal data are
not durable proof material by default. Stable identifier hashing requires an
appropriate external salt; when absent, redact rather than substitute the raw
value.

Reconstruction is classified as `full_reconstruction`,
`reference_integrity_only`, or `reconstruction_unavailable`. A valid digest does
not claim retained source availability. A Nova clock timestamp does not claim
independently trusted time; time evidence records its source and verification
status.

## Contract and implementation boundary

CCO and Architect design review is complete for `G3-R01`, `G3-R03`, `G3-R08`,
`G3-R11`, and `G3-Q15`. Their disposition is `approved_for_incorporation`, and
each is incorporated in the `design-v2.1` contract. Canonicality is determined
by authoritative repository `main`. They remain in the historical contract-gap
inventory with their prior blocker provenance. Other inventory records retain
their unapproved, review-required lifecycle state.

The contract revision creates no implementation, merge, deployment,
runtime, adapter, endpoint, production-crypto, chronology, Reflex Memory,
settlement, or capital-movement authority. Gate 3 design completion on revision
merge does not activate Gate 4.

This design does not establish that any system is quantum safe, quantum proof,
post-quantum secure, or future proof. Such a claim would require exact
implemented-suite, scope, verification-date, provider/library, and evidence
support at a later authorized gate.
