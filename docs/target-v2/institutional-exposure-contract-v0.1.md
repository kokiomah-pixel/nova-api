# Institutional Exposure Contract v0.1

## Status and authority boundary

```yaml
artifact: Gate_5_Entry_institutional_exposure_contract
status: authorized_design_workstream
canonical_target_contract: design-v2.1
Gate_5_started: false
institutional_pilot_authorized: false
institution_onboarded: false
tenant_created: false
runtime_activated: false
production_active: false
authority_effect: none
execution_effect: none
```

This is the contract that must be reviewable before an Architect can decide
whether to authorize a bounded Gate 5 pilot. It creates no present Gate 5,
deployment, tenant, institution, endpoint, identity-provider, or production
authority.

The governing sequence remains:

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Action boundary

Exactly one action class is permitted:
`agent_prepared_stablecoin_treasury_action`. The institution or its orchestrator
supplies an already prepared action reference, evidence, and an approved,
versioned review profile. Nova does not originate, amend, approve, sign, settle,
or execute the action.

Included material is limited to the prepared-action and exact proposal-version
identities, an externally supplied stable action identity when lineage is
claimed, attributable evidence, review-profile identity, governed target-v2
context, and its deterministic human presentation. General treasury operations,
portfolio management, trading, payments or settlement generally, wallet
operations, and every additional action class are excluded.

## Institutional ownership and authority

The institutional workflow owner defines the workflow, designates local
decision authority, owns fallback policy, and remains external to Nova. The
local decision authority interprets context under institutional policy and
makes the institutional decision. An institution-controlled external system is
the only conceptual execution path.

Nova structures and presents context. It is never approver, authorizer, veto
authority, signer, transaction initiator, settlement authority, or execution
authority. If institutional policy stops work when context is missing, the stop
is an institutional policy consequence—not a Nova decision.

A support/operator role has no domain authority. Any future support access must
be explicit, scoped, time-bounded, attributable, auditable, and revocable.

## Review-profile governance

An explicit institution owner, or attributable delegate, authors and versions
a profile. The institution approves, activates, replaces, and retires it. Every
revision is attributable and versioned. Nova may validate structural usability;
it may not silently invent requirements. A revision applies prospectively and
must never rewrite a prior review context retroactively.

## Evidence and source authority

`source_state`, `context_state`, and `review_completeness` remain separate. An
institution may classify a source for a specific workflow question or existing
evidence reference, but this exposure-layer classification does not add a new
target-v2 field or a global source ranking. It therefore does not incorporate
G3-R04.

Institution-provided and externally attributable evidence retain attribution;
contextual evidence remains non-authoritative; stale and unavailable evidence
remain explicit; unknown authority stays unknown. Contradictory material stays
visible even when the institution designates a source. Nova does not select a
winner.

## Identity and access design

No real tenant is provisioned and no identity provider is connected. A later
pilot would require externally attributable institution, tenant, human, and
service identities; explicit role assignment; least privilege; tenant
isolation; revocation; session expiry; and auditable access.

Authentication is not workflow authorization. Payment is not institutional
identity. Nova must not infer identity from payment, wallet ownership, an email
domain alone, API possession alone, or usage history. Cross-tenant access is
prohibited.

## Data governance

The institution controls submission and authorized use of institution-provided
data. Access to derived review context follows institution-approved policy.
The institution sets retention subject to applicable law and agreement; Nova is
a bounded service operator without institutional decision authority. These are
architectural control responsibilities, not unsupported claims of legal title.

A future pilot requires, before start: a retention authority and duration,
deletion triggers, termination behavior, a machine-readable export of governed
state plus trace manifest, portability, backup treatment, and post-withdrawal
disposition. The institution must be able to reconstruct context and continue
without Nova.

The following remain visible pre-pilot dependencies:

- legal title and licence terms require counsel or an explicit Architect decision;
- jurisdiction-specific retention duration requires institutional configuration;
- backup deletion timing requires institutional configuration.

## Failure, degradation, and incident behavior

The model fails explicitly without creating authority:

```text
Nova unavailable -> review context unavailable; no Nova decision.
Required source unavailable -> source/completeness state unresolved.
Conflict -> variants visible; no selected winner.
Stale evidence -> stale state reported.
Identity/access failure -> access denied or context unavailable.
Isolation or security concern -> Nova access may be isolated.
Reconstruction/integrity failure -> context unavailable and incident raised.
Export failure -> incomplete export is visible and escalated.
Withdrawal request -> the agreed withdrawal state machine applies.
```

None of these means `ALLOW`, `DENY`, `HALT`, or `VETO`. The institution owns
fallback and continuity consequences. Isolating Nova access for security does
not exercise capital authority.

## No-execution integration architecture

```text
institution/orchestrator
        -> prepared action + evidence + approved review profile
        -> Nova review-context layer
        -> machine context + deterministic human presentation
        -> local institutional authority
        -> institution-controlled external execution path
```

There is no Nova route to a wallet, signer, payment rail, settlement provider,
exchange, execution agent, smart-contract transaction, x402 payment, or capital
movement. Nova has no execution credential and makes no execution call. This
document does not activate `/v2/context`, an HTTP route, network integration, or
runtime.

## One governed state and two presentations

The canonical governed state is the sole input to the machine representation
and deterministic human presentation. Human statements carry a source path and
template identity. They cannot add approval, authority, policy, source ranking,
recommendation, or execution meaning. A separate analyst interpretation or
hidden Nova judgment layer is prohibited.

## Measurement and falsification

The future pilot measures decision continuity and review-context utility:
context reconstruction, source-attribution completeness, profile conformance,
machine/human parity, deterministic replay, change explanation, evidence
location time, stale/conflicted/unavailable distinction, local-authority
understanding of Nova's non-authority, proposal-revision continuity, and
withdrawal/export completeness.

Each metric must define `metric_id`, definition, source, method, success and
falsification thresholds, observation window, and owner. Where no governing
basis exists, thresholds are required pilot configuration—not invented numbers.
Approval counts, denial counts, volume, trading or asset returns, capital
deployed, and execution speed alone are prohibited success measures.

The design is falsified, and advancement stops, when operators treat Nova as
approval authority; presentations diverge; reconstruction fails; provenance is
routinely unclear; profiles require hidden judgment; isolation is not
demonstrable; export or withdrawal cannot complete; usefulness requires
execution credentials; Nova becomes hidden authorization; or context fails to
improve decision continuity.

## Withdrawal and disposition

The workflow owner or designated security authority may request withdrawal.
Nova may initiate safety isolation only, without domain authority. Withdrawal
revokes sessions and access, stops new processing, freezes pending contexts,
exports existing governed state and traces, applies the pre-agreed retention and
deletion policy, preserves only required audit evidence, revokes credentials,
and detaches integrations. Local institutional authority must continue without
Nova.

The contract distinguishes temporary suspension, incident isolation,
institution-initiated withdrawal, Nova-initiated safety withdrawal, pilot
completion, pilot failure, and pilot expiration. For every state the machine
contract defines access, new-context, export, retention, disposition, audit,
and detachment behavior. These behaviors are designed, not implemented.

## Dependency and mutation boundary

The incorporated set remains exactly G3-R01, G3-R03, G3-R08, G3-R11, and
G3-Q15. No other Gate 3 refinement is used. PR #33 is independent and supplies
no semantics. Chronology and accepted-memory references retain current
design-v2.1 meaning; this design adds no treatment, applicability, abstraction,
acceptance, or mutation semantics.

Legacy v1, design-v2.1, the Gate 4 adapter, runtime, routes, production crypto,
x402, payments, settlement, execution, chronology, and Reflex Memory are not
modified.

## Non-authorizing future decision template

> Expose one institution-owned review context to one bounded workflow for the
> purpose of evaluating decision continuity, under explicit non-authority,
> data, retention, access, incident, measurement and withdrawal boundaries.

This is a template only. It is not current authority, Gate 5 is not started,
and no institutional pilot is authorized.
