# Context-Proof Canonicalization Design v0.1

## Status and boundary

```yaml
status: proposed_not_canonical
design_only: true
canonicalization_version: gate3-canonical-json-v0.1
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
- stable action identity and exact proposal-version identity once G3-R01 is
  approved, or an explicitly labeled fallback state;
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
execution permission.

## Canonical JSON rules

The proposed `gate3-canonical-json-v0.1` byte representation uses these rules:

1. Objects use JSON and sort member names by Unicode code point after NFC
   normalization. Duplicate keys are rejected before canonicalization.
2. Strings and object keys are Unicode NFC. Control characters use required
   JSON escapes. Equivalent composed/decomposed text produces identical bytes.
3. Output encoding is UTF-8; the canonical test representation may use JSON
   `ensure_ascii=true` only when the canonicalization version explicitly fixes
   that representation. Implementations may not mix encodings under one
   version.
4. Whitespace outside JSON strings is absent. Object separators are `,` and
   name/value separators are `:`.
5. `null` and absent are different. Absent means the schema permits omission;
   `null` means an explicitly represented unknown only when the field schema
   permits it. Required fields cannot silently disappear. An unresolved object
   or stable reason code is preferred when the contract requires explicit state.
6. Booleans are lowercase JSON `true` and `false`.
7. Numbers reject NaN, infinity, negative zero ambiguity, locale formatting,
   leading plus signs, and insignificant trailing zeros. A future implementation
   must choose and version one shortest exact decimal representation before
   numeric values enter semantic material. Monetary values should remain
   externally normalized references until that rule is approved.
8. Timestamps use RFC 3339 date-time strings normalized to UTC `Z`, with a
   versioned fractional-second precision. Missing offsets are invalid, not local
   time. A normalized timestamp still does not claim trusted time.
9. Enum values are exact, case-sensitive contract tokens. Aliases and unknown
   enums are rejected or represented as explicit unresolved state; they are not
   silently coerced.
10. Unknown fields are rejected from canonical semantic material unless a
    reviewed extension namespace and ordering rule covers them. They may remain
    in a noncanonical transport wrapper without affecting the semantic digest.

## Array ordering and duplicate references

Array semantics are declared per field, never inferred from incidental input
order.

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
a duplicate, and both variants remain visible. Duplicate attestations remain
separate only when their IDs or signed scope differ; exact byte duplicates may
be rejected.

## Algorithm and digest identity

Every digest or signature reference normalizes an algorithm identifier,
parameter set, and output encoding under a versioned cryptographic profile.
Bare names such as `hash` or `signature` are insufficient. Unknown signature
suites yield `unverifiable`. Profile downgrades are detectable and fail closed;
there is no silent fallback.

Parallel digest migration computes multiple algorithm-qualified digests over
the identical canonical `semantic_context_material` byte sequence. It does not
serialize separate semantic variants. This design names no production
algorithm, parameter set, provider, or library.

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
