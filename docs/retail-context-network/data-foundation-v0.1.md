# Retail Data Foundation v0.1

RP3 defines the retail-only source registry, normalized observation contract,
and provider-neutral adapter boundary consumed by later retail resources. It
does not implement State Ping, Context Delta, live provider access, public
endpoints, payment, pricing, deployment, or institutional integration.

## Registry contract

`specs/retail_source_registry_v0_1.schema.json` records configuration and
eligibility state. A source entry separates:

- retail source and namespace identity
- public or retail-licensed access class
- authorization and licensing states
- configuration state
- credential requirement and retail-only credential namespace
- freshness-policy reference and mandatory provenance requirement
- enablement and `authority_effect: none`

The canonical interpretation is strict: listed is not authorized; authorized
is not configured; configured is not reachable; reachable is not observed;
observed is not verified; verified is not current; and current is not
reconciled.

`is_source_usable` is a fail-closed configuration eligibility check. It requires
enablement, explicit authorization, configuration, provenance, and a matching
non-fixture namespace/access/licensing/credential combination. Public sources
must use `retail_public_sources`; retail-licensed sources must use
`retail_licensed_sources`. Entries in `retail_fixture_sources` remain
schema-valid test evidence but are never configuration-eligible for runtime
consumption. The helper does not assert runtime reachability, availability,
observation, verification, freshness, or reconciliation.

The repository fixture registry contains only named fixtures/candidates. It
carries no historical reliability scores, real credentials, live-provider
claims, or production-readiness claim. Institutional source/access and
credential namespaces are outside the schema enums and therefore rejected.

## Observation contract

`specs/retail_source_observation_v0_1.schema.json` defines bounded evidence, not
a provider payload mirror. Every normalized record contains source identity,
subject, observation and receipt times, independent source and verification
states, deterministic freshness input, claim records, provenance, limitations,
bounded integrity identity, and `authority_effect: none`. Additional fields,
including `raw_payload`, are rejected.

Positive `observed` or `stale` records require an observation time, a
deterministically derived non-negative age input, at least one normalized
claim, a provider observation reference, and a SHA-256 identity over the
canonical normalized claims. When `derivation_status` is
`derived_from_timestamps`, runtime validation requires `received_at` not to
precede `observed_at` and requires `source_age_seconds` to equal the actual
`received_at - observed_at` delta. The digest establishes content identity
only; it does not establish source trust, authorization, currentness, or
reconciliation.

`unavailable` and `unknown` records require a null observation time, no claims,
no content digest, and no freshness age. Rejected, unavailable, and unknown
records cannot claim verified status. Verification status is bound to an
explicit provenance basis, preventing an unverified record from being relabeled
verified without corresponding verification evidence.

RP3 records freshness inputs only. It does not classify an observation as
fresh or aging and introduces no provider-specific thresholds. A later
authorized contract must govern any threshold-based interpretation. The
`stale` source status may preserve an upstream or separately authorized state;
the RP3 fixture adapter does not derive it.

## Adapter boundary

`RetailSourceAdapter` defines `observe(subject, as_of=None)` returning one
normalized retail observation. `FixtureRetailSourceAdapter` proves the boundary
with deterministic fixture data, validates its output, copies rather than
mutates its input, and performs no network or institutional access.

The adapter and observation are evidence inputs only. They do not make a
decision, recommend an action, grant authority, mutate state, or carry
institutional chronology or Reflex Memory identifiers.
