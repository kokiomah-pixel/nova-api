# Gate 3 Contract-Gap Report v0.1

## Status

```yaml
artifact_status: proposed_not_canonical
approved_target_v2_contract_modified: false
authority_effect: none
execution_effect: none
requires_CCO_review: true
requires_Architect_review: true
implementation_authority: false
```

This report separates approved target-v2 invariants from proposed schema
refinements discovered while defining field derivation and applying the approved
Gate 3A cryptographic-agility design input. A proposal here is not contract
authority. The machine register is
[`review_context_contract_gaps_v0_1.json`](../../specs/review_context_contract_gaps_v0_1.json).

## Existing Gate 3 refinement family

| ID | Approved invariant | Current gap | Proposed refinement |
|---|---|---|---|
| G3-R01 | Stable action identity differs from exact proposal identity. | One `reference_id` cannot express both. | Separate opaque `action_id` and `proposal_version_id`; label any Nova fingerprint. |
| G3-R02 | Institution-approved profiles define requirements. | Age, source, applicability, and revalidation rules lack normalized shapes. | Add versioned profile requirement structures; preserve missing rules as unresolved. |
| G3-R03 | Mixed evidence environments preserve segmentation. | One aggregate source value cannot cleanly express mixed packets. | Define a mixed aggregate or make segmentation authoritative with a reviewed compatibility rule. |
| G3-R04 | Source authority is scoped and conflicts remain visible. | Source references lack designation scope. | Add `designated_by`, `applies_to`, and authority reference metadata. |
| G3-R05 | Semantic material differs from proof-envelope material. | Neither scope is explicit. | Declare separate canonical scopes. |
| G3-R06 | Visible versions explain deterministic changes. | Derivation and canonicalization versions are absent. | Add both to reproducibility/proof material. |
| G3-R07 | Digest integrity differs from reconstruction availability. | Reconstruction scope is absent. | Add full, reference-only, and unavailable classifications. |
| G3-R08 | Review completeness is profile-relative. | Exact state precedence is unspecified. | Require a reviewed profile precedence; otherwise preserve unresolved. |
| G3-R09 | Hashing is not redaction. | Identifier salt and fallback rules are absent. | Require external scoped salt; redact on absence, with no raw fallback. |
| G3-R10 | Prior records do not imply current applicability. | Chronology treatment and applicability are not independently qualified. | Add explicit treatment/applicability status including `unknown`. |

## Gate 3A cryptographic-agility refinement family

Gate 3A approves the separation principles as design input, not these schema
changes as canonical contract fields.

| ID | Approved design invariant | Current gap | Proposed refinement |
|---|---|---|---|
| G3-Q01 | Crypto configuration has versioned identity. | No cryptographic profile reference exists. | Add profile ID, version, hash, and verification-policy version. |
| G3-Q02 | Digest identity includes algorithm and parameters. | Hashes are unqualified scalars. | Add algorithm, parameter set, encoding, and digest. |
| G3-Q03 | One semantic context may have multiple attestations. | `signature` is singular. | Add ordered primary, parallel-transition, and renewal attestations. |
| G3-Q04 | Attestations identify key and epoch. | Neither is bound. | Add opaque key reference and required key epoch. |
| G3-Q05 | Crypto operations bind algorithms and parameters. | Signature/digest parameter identity is absent. | Normalize and require explicit suite/parameter binding. |
| G3-Q06 | Renewal preserves semantic identity and predecessors. | No renewal semantics exist. | Add predecessor, reason, and preservation fields. |
| G3-Q07 | Verification results name their policy. | Verification-policy version is absent. | Bind state to `verification_policy_version`. |
| G3-Q08 | Nova clock time is not automatically trusted time. | Timestamps lack evidence qualification. | Add time source, reference, and verification status. |
| G3-Q09 | Proof integrity differs from reconstruction. | Proof has no reconstruction scope. | Bind proof records to G3-R07 classification. |
| G3-Q10 | Migration needs a secret-free dependency inventory. | Crypto dependencies are not categorized. | Record semantic, authenticity, confidentiality, access, supply-chain, and external categories. |
| G3-Q11 | Unknown suites are unverifiable and downgrade fails closed. | Transition behavior is absent. | Add explicit unknown and downgrade behavior. |
| G3-Q12 | Design cannot claim implemented quantum resistance. | Claim-evidence requirements are absent. | Require exact suite, scope, verification date, provider/library, and evidence. |
| G3-Q13 | Digest migration binds one semantic byte sequence. | `context_hash` is singular. | Allow parallel algorithm-qualified digests over identical canonical bytes. |
| G3-Q14 | Proof state is separate from context state. | No proof-verification object exists. | Add versioned verified/deprecated/unverifiable/invalid/unresolved states. |

## Additional gaps discovered

No additional gap beyond G3-R01–G3-R10 and G3-Q01–G3-Q14 was required to
complete this design ledger. The known G3-R08 precedence ambiguity remains
explicit and prevents an implementation from inventing a completeness policy;
it does not prevent the other field rules from being reviewed.

## Review and adoption rule

Every record above has:

```yaml
authority_effect: none
execution_effect: none
requires_CCO_review: true
requires_Architect_review: true
silently_canonical: false
```

Adoption requires an explicit contract revision after both reviews. Until then,
the existing approved contract wins. No runtime, endpoint, private adapter,
cryptographic implementation, chronology entry, Reflex Memory entry, or
production configuration follows from this report.
