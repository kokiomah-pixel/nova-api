# Gate 3 Contract-Gap Report v0.1

## Status

```yaml
artifact_status: contract_revision_candidate_present_not_canonical_on_main
approved_target_v2_contract_modified: true
authority_effect: none
execution_effect: none
CCO_review: approved
Architect_review: approved
design_review_status: design_review_complete_contract_revision_candidate_present
canonical_contract_revision: candidate_present
contract_revision_target: design-v2.1
canonical_on_main: false_until_merge
merge_authority: false
deployment_authority: false
implementation_authority: false
```

This report preserves the historical gap inventory discovered while defining
field derivation and applying the approved Gate 3A cryptographic-agility design
input. Exactly `G3-R01`, `G3-R03`, `G3-R08`, `G3-R11`, and `G3-Q15` are present
in the `design-v2.1` contract revision candidate. The other 21 records remain
unapproved and are not incorporated. The machine register is
[`review_context_contract_gaps_v0_1.json`](../../specs/review_context_contract_gaps_v0_1.json).

## Existing Gate 3 refinement family

| ID | Approved invariant | Current gap | Proposed refinement |
|---|---|---|---|
| G3-R01 | Stable action lineage differs from exact proposal identity on both request and response. | The request lacks both identities and one response `reference_id` cannot express them. | Require externally supplied `action_id` for cross-revision lineage; prefer external `proposal_version_id`, with only an algorithm-qualified, explicitly labeled Nova fingerprint over canonical prepared-action material as fallback. |
| G3-R02 | Institution-approved profiles define requirements. | Age, source, applicability, and revalidation rules lack normalized shapes. | Add versioned profile requirement structures; preserve missing rules as unresolved. |
| G3-R03 | Mixed evidence environments preserve authoritative component segmentation. | One aggregate source value cannot express mixed packets. | Add `mixed` for more than one environment class; retain segmentation as authoritative and prohibit ranking or promotion. |
| G3-R04 | Source authority is scoped and conflicts remain visible. | Source references lack designation scope. | Add `designated_by`, `applies_to`, and authority reference metadata. |
| G3-R05 | Semantic material differs from proof-envelope material. | Neither scope is explicit. | Declare separate canonical scopes. |
| G3-R06 | Visible versions explain deterministic changes. | Derivation and canonicalization versions are absent. | Add both to reproducibility/proof material. |
| G3-R07 | Digest integrity differs from reconstruction availability. | Reconstruction scope is absent. | Add full, reference-only, and unavailable classifications. |
| G3-R08 | Profiles define requirements, while the contract owns stable completeness enum meaning. | Contract-level state meanings and precedence are unspecified. | Propose contract precedence `unavailable > conflicted > partial > complete`; profiles continue to define requirements, evidence, thresholds, applicability, and revalidation. |
| G3-R09 | Hashing is not redaction. | Identifier salt and fallback rules are absent. | Require external scoped salt; redact on absence, with no raw fallback. |
| G3-R10 | Prior records do not imply current applicability. | Chronology treatment and applicability are not independently qualified. | Add explicit treatment/applicability status including `unknown`. |
| G3-R11 | Canonical bytes preserve exact numeric, monetary, temporal, Unicode, null, and ordering meaning. | Exact-financial bounds, exhaustive semantic-array rules, and unknown-offset behavior were incomplete. | Keep RFC 8785/JCS plus the exact-financial application profile; require precision/scale/exponent bounds, reject `-00:00`, and classify every semantic array with executable rules. |

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
| G3-Q15 | Semantic identity is not an individual digest. | Continuity across successor digest algorithms and historical evidence preservation were not explicit. | Bind historical and successor digest records to identical canonical semantic bytes; preserve history and prohibit “same hash value” language across algorithms. |

## Additional gaps discovered

```yaml
newly_discovered:
  - G3-R11 canonical_numeric_and_interoperability_profile
  - G3-Q15 semantic_identity_continuity_across_digest_migration
```

`G3-R11` completes the design-level numeric and collection model. `G3-Q15`
preserves semantic identity across digest migration. CCO and Architect design
review is complete for both; they are present in the contract revision candidate
and remain non-canonical on `main` until merge.

## CCO remediation decisions within the existing gap family

- `G3-R01` covers request input and response reference semantics. `action_id`
  is externally supplied and required for any cross-revision lineage claim; it
  is never derived from mutable content. An absent `action_id` means lineage is
  unavailable. `proposal_version_id` prefers an external identifier; the sole
  fallback is an algorithm-qualified value labeled
  `Nova_derived_proposal_fingerprint` over canonical prepared-action material.
- `G3-R03` resolves the former either/or: the aggregate is `mixed` whenever
  more than one evidence-environment class appears. Segmentation remains
  authoritative, without strongest/weakest reduction or promotion to `live`.
- `G3-R08` supplies the stable target-v2 contract meanings and precedence
  incorporated in the revision candidate:
  `unavailable`, `conflicted`, `partial`, then `complete`. Institution profiles
  determine what must be evaluated, but cannot redefine the public enum.
  `complete` never means policy satisfied, safe, permitted, approved, or
  executable.
- `G3-R11` requires `max_precision`, `max_scale`, and `max_abs_exponent`, rejects
  excessive bounds before coefficient expansion, rejects RFC 3339 `-00:00`,
  and gives every semantic array an executable `ordered_sequence`, `set`, or
  `multiset` declaration.

## Gate 3 design-review disposition

```yaml
semantic_completion:
  status: design_review_complete_contract_revision_candidate_present
  active_review_blockers: []
  historical_review_blockers:
    - G3-R01
    - G3-R03
    - G3-R08
    - G3-R11
    - G3-Q15
  approved_for_incorporation:
    - G3-R01
    - G3-R03
    - G3-R08
    - G3-R11
    - G3-Q15
  canonical_contract_revision: candidate_present
  contract_revision_target: design-v2.1
  canonical_on_main: false_until_merge
```

The five records remain in the historical contract-gap inventory with their
prior blocker provenance. Their active review-blocker status is cleared because
CCO and Architect approved their design disposition. Presence in the revision
candidate does not make them canonical on `main` before merge and creates no
runtime or implementation authority.

## Review and adoption rule

The five approved records have:

```yaml
CCO_review: approved
Architect_review: approved
design_disposition: approved_for_incorporation
contract_revision_target: design-v2.1
contract_revision_candidate: present
canonical_on_main: false_until_merge
canonical_contract_status: contract_revision_candidate_present
authority_effect: none
execution_effect: none
silently_canonical: false
implementation_authority: false
```

Canonical adoption on `main` requires review and merge of the explicit contract
revision candidate. No deployment, runtime, endpoint, private adapter,
cryptographic implementation, chronology entry, Reflex Memory entry, or
production configuration follows from this report. The other 21 gap records
retain their unapproved, review-required lifecycle metadata.
