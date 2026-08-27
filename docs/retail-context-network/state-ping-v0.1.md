# State Ping v0.1

State Ping is the first retail context resource. It answers what current
material state is supportable for a subject from supplied RP3 normalized retail
observations. It is a deterministic evidence transformation, not a narrative
summary, action recommendation, forecast, or authority decision.

`build_state_ping(subject, observations, generated_at=...)` is a pure Python
function. It performs no network call, clock read, HTTP handling, persistence,
payment, pricing, deployment, or institutional access. The caller supplies the
generation time explicitly, and identical semantic inputs produce identical
output and identifiers.

## Input and validation

Every input observation is validated under the RP3 normalized source
observation contract. All observations must match the requested subject and
have unique observation identifiers. Raw provider payloads and extra
institutional fields fail RP3 validation before construction.

The builder sorts observations and claims before deriving identifiers and
output arrays. It validates the completed State Ping with the RP2 validator
before returning it.

## Evidence treatment

Only `observed` and `stale` RP3 observations contribute positive evidence.
`unavailable`, `rejected`, and `unknown` observations become limitations and
unresolved-evidence records; they do not create positive provenance or
evidence. Each normalized claim maps conservatively to RP2 `observed` evidence,
or to `unresolved` when its RP3 claim state is not observed. Matching claims are
never automatically upgraded to corroborated.

Source identifiers, observation times, verification treatment, claim scope,
and contribution are preserved. RP3 does not carry the registry provider
`source_type`, and State Ping does not reconstruct it. The immediate normalized
observation's `retrieval_mode` is used as the RP2 provenance `source_type`.
Joining provider classification from the retail registry remains later work.
Successful RP3 schema validation never upgrades provider truth.

Unverified input maps to `present_unverified`, verification failure remains
`verification_failed`, and explicit stale source status becomes RP2 stale
freshness plus a material limitation and evidence gap.

## Bounded status rules

- No positive observation produces `insufficient_evidence`, indeterminate
  confidence, unknown/null freshness, empty provenance/evidence, and at least
  one explicit evidence gap.
- Cross-source contradiction produces `unresolved`.
- Positive support with an excluded source, stale/unverified contribution,
  unresolved claim, or material input limitation produces
  `partially_resolved`.
- Verified non-stale support with no material gap or contradiction produces
  `resolved`.

Resolved confidence is `medium`. Partial confidence is `medium` only when all
positive contributions are verified and non-stale, otherwise `low`.
Contradictory context is `low`, and insufficient evidence is `indeterminate`.
Confidence is descriptive and never determines context status.

Freshness uses the greatest supplied RP3 source age and its associated
observation time. It is `stale` only when an input explicitly says stale and is
otherwise `unknown`; State Ping does not invent fresh/aging thresholds or label
recent input fresh.

## Deterministic contradiction rule

RP4 uses one narrow structural rule: the same RP3 `claim_id` is a bounded claim
scope. If at least two distinct sources emit different normalized statements
for that scope, every involved evidence item is marked contradicted and one
unresolved RP2 contradiction is emitted. No semantic interpretation or
reconciliation is attempted.

State Ping always emits `resource_type: state_ping` and
`authority_effect: none`. It contains no public endpoint, payment surface,
marketplace metadata, provider networking, action instruction, or
institutional state mutation.
