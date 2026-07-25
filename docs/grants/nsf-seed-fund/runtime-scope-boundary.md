# NSF Runtime Scope Boundary

## Status

Controlled scope clarification for later NSF drafting review.

This document does not rewrite the NSF packet, change the bounded
demonstration, alter runtime behavior, or claim that the proposed v2 contract
has been implemented.

```yaml
NSF_scope:
  bounded_demo:
    non_authority: true
    suitable_for_research_claim: true

  full_v1_runtime:
    non_authority: false_or_materially_mixed
    suitable_for_repository_wide_non_authority_claim: false

  proposed_v2_contract:
    status: target_architecture_not_yet_implemented
```

## Safe Research Scope

The bounded NSF demonstration may support the claim that:

- an agent-prepared action can be operationally executable but not yet
  institutionally review-ready;
- Nova can structure missing, stale, conflicting, and unresolved context;
- Nova can preserve source disagreement without choosing the institution's
  winning source;
- local institutional authority remains responsible for its decision; and
- the demonstration does not execute, route, sign, settle, or move capital.

The research may investigate whether structured review context improves
reconstruction, classification stability, source-state recognition,
authority-scope comprehension, and review quality without transferring
institutional decision ownership into Nova.

## Legacy v1 Boundary

The full current runtime contains Legacy v1 decision-admission behavior,
authority-bearing status language, status-dependent HTTP responses,
permission-budget behavior, decision-proof semantics, and status-dependent
prepaid billing.

The runtime also contains newer non-authority descriptions and Reflex Memory
paths with `authority_effect: none`. These newer fields do not make the full
v1 runtime uniformly non-authority.

Therefore, NSF materials must not claim:

- the full current runtime is already non-authority;
- Legacy v1 does not deny, delay, halt, or otherwise constrain requests;
- all current proofs are context-integrity proofs;
- the public repository is fully aligned with the target architecture; or
- the proposed v2 external profile is implemented or publicly available.

Legacy v1 terms are included here only to state the scope exclusion.

## Proposed v2 Boundary

The proposed Nova External Review-Context Contract is a target architecture.
It is designed to:

- describe context rather than return an institutional action outcome;
- expose source state, constraint context, temporal context, unresolved
  conditions, review completeness, and chronology references;
- make local decision and external execution ownership explicit;
- use context-integrity proof semantics; and
- separate billing from domain outcomes.

Until implementation, validation, and governance review are complete, NSF
materials must label v2 as proposed architecture or Phase I design work rather
than repository-observed runtime behavior.

## Safe NSF Claims

```yaml
safe_claims:
  - the_bounded_demonstration_is_non_authority
  - the_research_investigates_useful_review_context_without_execution_control
  - the_proposed_architecture_preserves_local_authority
  - the_repository_contains_a_testable_foundation_and_an_unresolved_migration_boundary
```

Recommended wording:

> The bounded demonstration tests whether Nova can construct reviewable,
> reproducible context while local institutional authority retains the
> decision. The proposed v2 contract extends that research boundary but is not
> yet implemented. The existing v1 runtime remains outside the bounded
> non-authority claim pending isolation and migration review.

## Unsafe NSF Claims

```yaml
unsafe_claims:
  - current_full_runtime_is_already_non_authority
  - v1_does_not_deny_or_constrain
  - public_repository_is_fully_aligned_with_target_architecture
  - v2_is_implemented
  - production_usage_or_adoption_is_verified
```

## Repository Reference Rule

If the public repository is linked:

1. Point reviewers first to the bounded demonstration and this scope boundary.
2. Label the v2 contract as proposed and not implemented.
3. Identify v1 as a legacy runtime pending isolation.
4. Do not use current v1 tests as evidence that the external v2 boundary exists.
5. Do not use the live health endpoint as proof of v2 deployment.
6. Preserve the distinction between internally validated artifacts and
   proposed Phase I research.

## Evidence Required to Expand the Claim

A repository-wide non-authority runtime claim requires:

- an approved external v2 semantic contract;
- a separately authorized implementation;
- field-level derivation independent of Legacy v1 outcomes;
- context-integrity proof validation;
- local-authority comprehension testing;
- v1 isolation evidence;
- outcome-independent billing evidence;
- exact deployment attestation;
- accepted-state review; and
- chronology review.

Until then, the bounded demonstration remains the safe research evidence unit.
