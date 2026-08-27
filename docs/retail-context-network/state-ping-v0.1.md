# State Ping v0.1

State Ping is the first retail context resource. It answers what current
material state is supportable for a subject from supplied RP3 normalized retail
observations whose sources are also configuration-eligible under the RP3 source
registry contract. It is a deterministic evidence transformation, not a
narrative summary, action recommendation, forecast, or authority decision.

`build_state_ping(subject, observations, source_entries, generated_at=...)` is a
pure Python function. It performs no network call, clock read, HTTP handling,
persistence, payment, pricing, deployment, or institutional access. The caller
supplies the generation time and bounded source-entry eligibility context
explicitly, and identical semantic inputs produce identical output and
identifiers.

## Input and validation

Every input observation is validated under the RP3 normalized source
observation contract. All observations must match the requested subject and
have unique observation identifiers. Raw provider payloads and extra
institutional fields fail RP3 validation before construction.

State Ping also receives bounded RP3 source entries. Source-entry identity must
be unique. For an `observed` or `stale` observation to contribute positive
evidence, its `source_id` must have a matching source entry that passes the
existing RP3 `is_source_usable(...)` fail-closed eligibility check. Registry
presence alone is not sufficient.

Missing, invalid, unauthorized, unconfigured, unlicensed, or fixture-namespace
source entries cannot contribute positive provenance or evidence. Their
observations are preserved only as explicit limitations and unresolved evidence.
Source eligibility does not establish runtime reachability, provider truth,
verification, freshness, corroboration, or reconciliation.

The builder sorts source entries, observations, and claims before deriving
identifiers and output arrays. It validates the completed State Ping with the
RP2 validator before returning it.

## Evidence treatment

Only `observed` and `stale` RP3 observations from configuration-eligible sources
contribute positive evidence. `unavailable`, `rejected`, and `unknown`
observations become limitations and unresolved-evidence records; they do not
create positive provenance or evidence. Positive-status observations whose
sources fail eligibility are treated the same way for context construction:
they remain visible as evidence gaps but do not condition the positive state.

Each normalized claim maps conservatively to RP2 `observed` evidence, or to
`unresolved` when its RP3 claim state is not observed. Matching claims are never
automatically upgraded to corroborated.

Source identifiers, observation times, verification treatment, claim scope,
and contribution are preserved. RP3 observations do not carry the registry
provider `source_type`, and State Ping does not reconstruct it. The immediate
normalized observation's `retrieval_mode` is used as the RP2 provenance
`source_type`. Successful RP3 schema validation or source eligibility never
upgrades provider truth.

Unverified input maps to `present_unverified`, verification failure remains
`verification_failed`, and explicit stale source status becomes RP2 stale
freshness plus a material limitation and evidence gap.

## Bounded status rules

- No eligible positive observation produces `insufficient_evidence`,
  indeterminate confidence, unknown/null freshness, empty positive
  provenance/evidence, and at least one explicit evidence gap.
- Cross-source contradiction among eligible positive sources produces
  `unresolved`.
- Eligible positive support with an excluded source, stale/unverified
  contribution, unresolved claim, or material input limitation produces
  `partially_resolved`.
- Verified non-stale eligible support with no material gap or contradiction
  produces `resolved`.

Resolved confidence is `medium`. Partial confidence is `medium` only when all
positive contributions are verified and non-stale, otherwise `low`.
Contradictory context is `low`, and insufficient evidence is `indeterminate`.
Confidence is descriptive and never determines context status.

Freshness uses the greatest supplied source age among eligible positive RP3
observations and its associated observation time. It is `stale` only when an
eligible contributing observation explicitly says stale and is otherwise
`unknown`; State Ping does not invent fresh/aging thresholds or label recent
input fresh.

## Deterministic contradiction rule

RP4 uses one narrow structural rule: the same RP3 `claim_id` is a bounded claim
scope. If at least two distinct eligible sources emit different normalized
statements for that scope, every involved evidence item is marked contradicted
and one unresolved RP2 contradiction is emitted. No semantic interpretation or
reconciliation is attempted.

State Ping always emits `resource_type: state_ping` and
`authority_effect: none`. It contains no public endpoint, payment surface,
marketplace metadata, provider networking, action instruction, or
institutional state mutation.
