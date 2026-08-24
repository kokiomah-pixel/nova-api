# Context-Proof Canonicalization Design v0.1

## Status and boundary

```yaml
status: approved_for_incorporation_not_yet_canonical
design_only: true
canonicalization_design_defined: true
semantic_completion: design_review_complete_pending_contract_revision
active_review_blockers: []
historical_review_blockers: [G3-R01, G3-R03, G3-R08, G3-R11, G3-Q15]
CCO_review: approved
Architect_review: approved
canonical_contract_revision: not_started
canonicalization_version: nova-jcs-exact-financial-json-design-v0.1
derivation_version: gate3-field-derivation-v0.1
production_algorithm_selected: false
runtime_implementation_authority: false
authority_effect: none
execution_effect: none
```

This draft defines deterministic material boundaries for design review. It does
not implement target v2, select a production signature/hash suite, alter the
approved contract, or authorize production cryptography.

## Two identities and two scopes

```yaml
semantic_context_material:
  purpose: deterministic_meaning_of_review_context
  produces: algorithm_qualified_semantic_context_digest

proof_record_envelope:
  purpose: identity_and_attestation_of_a_specific_constructed_record
  produces: one_or_more_proof_attestations
```

Semantic context identity remains stable when record-generation or attestation
metadata changes. Cryptographic attestation identity may change independently.

### Semantic material includes

- exact schema, derivation, and canonicalization identities;
- externally supplied stable action identity when lineage is claimed, plus the
  exact proposal-version identity once G3-R01 is approved. If action identity
  is absent, lineage is explicitly unavailable; a proposal-version fallback is
  algorithm-qualified, labeled `Nova_derived_proposal_fingerprint`, and limited
  to canonical prepared-action material;
- exact review-profile identity/version/hash;
- normalized source, constraint, temporal, contradiction, completeness, and
  existing chronology-reference context;
- source-environment segmentation;
- authority-handoff and non-authority boundary constants;
- explicit missing, unavailable, conflict, and unresolved state;
- qualified digest/reference values needed to reproduce meaning.

### Semantic material excludes by default

- `context_id`, `request_id`, and record `created_at`;
- `review_context_created_at` when it only mirrors record generation time;
- signature bytes, signature algorithm, signature parameter set;
- key reference, key epoch, signing time, and proof-renewal time;
- attestation ID/type/status and verification time;
- transport, storage, retrieval, and local diagnostics;
- unconstrained human-readable prose.

An exclusion may change only through reviewed contract/canonicalization
revision. Generated prose may be rendered from stable reason codes but never
become integrity-critical because of wording.

### Proof envelope includes

- the semantic digest object with algorithm, parameter set, encoding, and
  digest;
- canonicalization and derivation versions;
- record IDs and creation time;
- reconstruction classification;
- cryptographic-profile and verification-policy identities;
- ordered attestation records, keys/epochs, time-evidence references,
  predecessor references, status references, and signature values;
- the signed-material scope and any parallel digest bindings.

The proof envelope verifies construction and integrity. It does not verify
approval, authorization, transaction validity, institutional acceptance, or
authority to execute.

## Standards evaluation and adoption decision

[RFC 8785, JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
provides the baseline. It constrains inputs to I-JSON, rejects duplicate object
names, uses ECMAScript primitive serialization, sorts object names by UTF-16
code units, preserves array order, preserves Unicode strings as-is, emits no
inter-token whitespace, and encodes the result as UTF-8.

Nova adopts those JCS rules. It does not redefine JCS. It adds an explicitly
versioned **application profile** before JCS serialization because RFC 8785 JSON
numbers use IEEE-754 double precision. That representation cannot preserve
arbitrary financial decimal precision or field-specific scale semantics. RFC
8785 itself recommends string representation for values requiring greater
precision; Nova uses typed objects containing canonical base-10 strings so the
resulting document remains valid JCS/I-JSON.

```yaml
G3-R11:
  name: canonical_numeric_and_interoperability_profile
  status: approved_for_incorporation_not_yet_canonical
  CCO_review: approved
  Architect_review: approved
  design_disposition: approved_for_incorporation
  canonical_contract_status: pending_contract_revision
  silently_canonical: false
  implementation_authority: false
  base_standard: RFC_8785_JCS
  JCS_deviation: false
  application_profile: nova-jcs-exact-financial-json-design-v0.1
```

## Canonical JSON and interoperability rules

1. Objects reject duplicate names and recursively sort raw property names by
   unsigned UTF-16 code units as RFC 8785 specifies.
2. Strings and keys preserve Unicode code points **as supplied**. There is no
   NFC/NFD normalization inside canonicalization. Composed and decomposed forms
   therefore remain different semantic bytes unless a field-specific,
   pre-canonical normalization rule is separately reviewed.
3. Invalid Unicode and lone surrogates fail. JCS string escaping is used and the
   final representation is UTF-8.
4. Arrays retain order by JCS default. Only field rules explicitly declaring set
   semantics are normalized and sorted before JCS serialization.
5. Whitespace outside strings is absent. Booleans and `null` use JSON literals.
6. `null` and absent are different. Required absence fails semantic projection.
   `null` is retained only where the reviewed field model declares nullable
   meaning; otherwise explicit unresolved state is required.
7. Unknown fields are excluded and rejected from semantic material unless a
   reviewed extension namespace covers them.
8. Enums are exact, case-sensitive contract tokens; no alias coercion occurs.

## Canonical numeric model

Binary floating-point values are prohibited in Nova semantic material. NaN and
infinity fail. A bare JSON integer is permitted only when its field schema calls
for an integer and its value is within the exact I-JSON range
`[-9007199254740991, 9007199254740991]`. Exact-domain values use typed objects.

### Exact integer

```yaml
numeric_type: integer
value: canonical_base10_string
```

The value has no leading zeros except `0`, no plus sign, decimal point, or
exponent. Negative zero normalizes to `0`. The field profile fixes maximum digit
precision; overflow fails rather than rounds or truncates. Integers outside the
I-JSON exact range must use this typed form.

### Exact decimal

```yaml
numeric_type: decimal
coefficient: signed_base10_string
scale: nonnegative_integer
```

The mathematical value is `coefficient × 10^-scale`. Exponent notation may be
accepted only at the normalization boundary and is eliminated from canonical
material. Negative zero becomes coefficient `0`. A generic exact decimal trims
insignificant trailing zeros to its minimum scale, so `1.2300` becomes
coefficient `123`, scale `2`. A field with fixed-scale semantics retains exactly
the profile-declared scale. Every exact-decimal field profile must supply
`max_precision`, `max_scale`, and `max_abs_exponent`. Exponent and resulting
scale bounds are checked before coefficient expansion. No rounding is
permitted.

### Monetary amount

```yaml
numeric_type: monetary_amount
asset_id: explicit_opaque_asset_or_unit
coefficient: signed_base10_string
scale: profile_declared_nonnegative_integer
```

Asset/unit and scale are never inferred. Monetary profiles also require
`max_precision`, `max_scale`, and `max_abs_exponent`. For a scale-2 asset, `1`,
`1.0`, and `1.00` normalize to coefficient `100`, scale `2`; `1.001` fails
because rounding would be required. Missing asset/scale metadata leaves the
amount unresolved and not canonicalizable. Normalization has no approval,
pricing, settlement, or execution effect.

## Timestamp model

Semantic timestamps require RFC 3339 input with an explicit offset. They
normalize to UTC `Z` with exactly six fractional-second digits:

```text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

Whole seconds are padded with `.000000`; shorter fractions are right-padded.
Sub-microsecond input is rejected rather than rounded. RFC 3339 `-00:00` denotes
an unknown local offset and is rejected by this proposed profile; it is never
silently normalized to UTC `Z`. Leap-second or invalid calendar input fails.
This fixed precision is part of the reviewed G3-R11 design, approved for
incorporation but not canonical until contract revision. Normalization does not
turn a Nova clock value into independently trusted time.

## Array ordering and duplicate references

Array semantics are declared per field as exactly one of `ordered_sequence`,
`set`, or `multiset`; undeclared semantic arrays fail projection. JCS preserves
array order structurally, while the application profile normalizes each
declared set or multiset before JCS. The current response semantic-array
inventory classifies every listed field as `set`:

| Area | Set-valued semantic fields |
|---|---|
| Source and state | `record_source_type.source_segmentation`, `context_state.reasons`, `source_state.sources`, `source_state.unresolved_source_conflicts` |
| Constraints and time | `constraint_context.observed_constraints`, `constraint_context.constraint_sources`, `constraint_context.unresolved_constraint_questions`, `temporal_context.temporal_conflicts`, `temporal_context.pending_state` |
| Contradictions | `contradiction_context.source_conflicts`, `constraint_conflicts`, `temporal_conflicts`, `chronology_conflicts`, `unresolved_questions` |
| Completeness and chronology | `review_completeness.missing_context`, `review_completeness.unresolved_conditions`, `chronology_context.prior_review_references`, `accepted_memory_references`, `relevant_changes_since_prior_review` |
| Reproducibility | `reproducibility.source_versions`, `reproducibility.source_segmentation` |

This covers every `deterministic_collection` and every other current set-like
semantic response field. A future array must choose one of the three classes
before entering canonical material; it does not inherit set semantics by
analogy.

- Sets of source, constraint, conflict, unresolved-question, chronology,
  digest, and reference objects are normalized then sorted by a declared tuple.
- Source references sort by `(source_id, source_version_or_digest,
  authority_scope, observed_at, received_at, record_source_type)`.
- Constraint references sort by `(constraint_id_or_digest, source_id,
  applicability_scope)`.
- Chronology/review/memory references sort by `(reference_type, reference_id,
  version_or_digest, treatment_status, applicability_status)`.
- Digest records sort by normalized `(algorithm, parameter_set,
  output_encoding, digest)`.
- Attestations sort by `(attestation_type_rank, cryptographic_profile_id,
  cryptographic_profile_version, key_reference, key_epoch, signed_at,
  attestation_id)`, where type rank is explicitly versioned.
- Arrays whose order is institution-meaningful preserve an explicit position or
  sequence value supplied under the profile. Input iteration order alone is not
  meaning.

Byte-identical duplicate references collapse to one only when the field rule
declares set semantics. Same identity with different content is a conflict, not
a duplicate; the reference canonicalizer rejects the unqualified set until the
conflict is explicitly represented in the contract's conflict fields, where all
variants remain visible. Duplicate attestations remain separate only when their
IDs or signed scope differ; exact byte duplicates may be rejected.

## Algorithm and digest identity

Every digest or signature reference normalizes an algorithm identifier,
parameter set, and output encoding under a versioned cryptographic profile.
Bare names such as `hash` or `signature` are insufficient. Unknown signature
suites yield `unverifiable`. Profile downgrades are detectable and fail closed;
there is no silent fallback.

### Semantic identity continuity across digest migration

`G3-Q15` makes semantic context identity distinct from every individual digest.
Identity is the identical canonical `semantic_context_material` byte sequence
under the same canonicalization, derivation, schema, and profile identities. An
algorithm-qualified digest is evidence about those bytes, not the semantic
identity itself.

Parallel or successor digest migration preserves the historical digest record,
adds a new algorithm/parameter-qualified record, and verifies both against the
identical retained canonical bytes (or a verifiable preserved reference to
them). The new digest does not replace history. Different algorithms are not
described as producing “the same hash value”; their digest values are expected
to be algorithm-specific. If the canonical bytes cannot be reconstructed or
referenced verifiably, continuity is `unresolved`.

```yaml
G3-Q15:
  status: approved_for_incorporation_not_yet_canonical
  CCO_review: approved
  Architect_review: approved
  design_disposition: approved_for_incorporation
  canonical_contract_status: pending_contract_revision
  silently_canonical: false
  implementation_authority: false
  semantic_identity_is_individual_digest: false
  historical_digest_evidence_preserved: true
  successor_digest_replaces_history: false
  same_hash_value_claim: prohibited
```

This design names no production algorithm, parameter set, provider, or library.

## Proof attestations and renewal

A proposed proof record supports `primary`, `parallel_transition`, and `renewal`
attestations. Each binds profile/version, algorithm/parameters, key
reference/epoch, signed time and time evidence, signed-material scope,
predecessor/status references, and signature value.

Renewal:

```yaml
semantic_context_mutated: false
original_context_hash_preserved: true
original_attestation_preserved: true
predecessor_reference_required: true
renewal_reason_required: true
```

Key rotation, compromise response, algorithm deprecation, parameter/profile
migration, and long-term validation refresh may motivate renewal. Renewal does
not mean institutional reapproval, context rereview, execution reauthorization,
or chronology acceptance.

## Time evidence

Time evidence distinguishes `Nova_clock`, `external_timestamp`,
`archive_anchor`, and `unresolved`. It records source reference and verification
status. A Nova-written time alone is not independently trusted time. Missing
external evidence therefore produces no trusted-time claim.

## Reconstruction

Every proof declares one scope:

- `full_reconstruction`: retained material and versions permit reconstruction
  under declared access controls;
- `reference_integrity_only`: references/digests can be checked but full source
  material is not promised;
- `reconstruction_unavailable`: required reconstruction material is unavailable.

A valid digest never upgrades `reference_integrity_only` or
`reconstruction_unavailable` to full reconstruction.

## Privacy, sensitivity, and redaction

Each field rule declares sensitivity, hash inclusion, envelope inclusion,
disclosure, redaction, and reference-only handling. Hashing sensitive material
does not make disclosure acceptable. Raw wallet addresses, account identifiers,
transaction payloads, credentials, institution secrets, and personal data are
excluded by default.

Stable identifier hashing requires a profile-approved external salt with
appropriate tenant/scope handling. If the salt is unavailable, the identifier
is redacted; raw content is never substituted. Proofs should bind minimized
opaque references or approved digests and keep protected source material behind
separate access/retention controls.

## Long-term and quantum claim boundary

The dependency inventory covers semantic identity, proof authenticity,
confidentiality, access identity, software supply chain, and external rails.
Proof renewal and parallel transitions make cryptographic change representable;
they do not prove security of an implementation.

This design does not establish that a deployed system is quantum safe, quantum
proof, post-quantum secure, or future proof. Any later claim requires exact
implemented suite/parameters, scope, verification date, provider/library, and
supporting evidence under an authorized implementation/security gate.
