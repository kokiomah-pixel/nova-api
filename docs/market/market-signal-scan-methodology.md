---
record_type: market_signal_scan_methodology
contract_version: market_signal_run_v0_1
review_state: monitoring_governance_contract
authority_effect: none
execution_effect: none
production_effect: none
accepted_state_effect: none
chronology_effect: none
Reflex_Memory_effect: none
runtime_implemented: false
external_integration: false
---

# Market-Signal Scan Methodology

## Purpose and boundary

This contract keeps active governed watches visible whenever a Market Signal
Agent run is performed. It governs run discipline and repository validation;
it does not run searches, poll sources, schedule work, alert reviewers, route
attention, create signals, or change any Nova state automatically.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

The operating principles are:

> Every eligible governed watch is a mandatory scan seed for every applicable
> Market Signal Agent run.

> Absence of new evidence is itself a watch result; omission of the watch is
> not.

```text
watch checked + no material delta
≠
watch not checked

source unavailable
≠
no material change
```

## Governed-watch eligibility

Eligibility is read from
[`market-signal-watch-register.yaml`](market-signal-watch-register.yaml).
A signal is mandatory when all configured `eligible_when_all` fields match.
Version `governed_watch_eligibility_v0_1` currently requires:

```yaml
review_state: governed_watch
lifecycle_status: observed_watch
```

The repository does not yet define a canonical inactive lifecycle vocabulary
for governed market watches. This contract therefore does not invent one. A
watch remains mandatory while the positive eligibility fields match. It may be
excluded only after a separate governed change gives it an explicit inactive
lifecycle state. Time, a quiet scan, source unavailability, or omission cannot
expire it implicitly.

## Mandatory two-pass method

### Pass 0 — run bounds

Record the observation date, reporting window, source classes, material source
limits, and known access gaps. The bounds describe what was attempted; they do
not imply complete internet coverage.

### Pass 1 — governed-watch scan

For every eligible watch:

1. load the stored thesis;
2. load thesis-strengthening and category-compression conditions;
3. perform bounded external research outside Nova runtime;
4. preserve source availability and evidence provenance;
5. classify the delta or explicit source limitation;
6. evaluate every stored escalation family; and
7. emit one coverage object.

Pass 1 is complete only when every mandatory signal ID has exactly one coverage
object. A positive finding is not required. Explicit `no_material_delta` is a
valid result only when material sources were available. An attempted scan with
unavailable material sources must remain `source_incomplete` or
`source_unavailable`.

### Coverage gate

```text
eligible governed watch + missing run coverage
= invalid / incomplete market-signal run

eligible governed watch + attempted scan + unavailable material sources
= represented source-incomplete run
```

Broad discovery cannot satisfy or replace this gate.

This gate applies to `direct_market_signal_run` artifacts. A
`retrospective_reconciliation` can preserve and evaluate omitted historical
context, but it cannot retroactively satisfy the direct-run coverage gate.

### Pass 2 — broad discovery

After the coverage gate, perform bounded discovery for observations outside
the stored watch seeds. Each observation must be reconciled before it can be a
new-signal candidate:

```text
new observation
      ↓
materially related to an active governed watch?
      ↓
YES → related evidence or supporting context; test stored escalation conditions
NO  → genuinely distinct new-signal candidate for separate review
```

Related context keeps its own provenance. It does not automatically mutate the
watch record, enter chronology, create Reflex Memory, or become accepted state.

## Evidence-coverage classification

```yaml
sufficient:
  meaning: >
    Every mandatory watch has completed coverage and bounded discovery work
    was completed within the declared source scope.

source_incomplete:
  meaning: >
    Every mandatory watch is represented and attempted, but one or more
    material required sources were unavailable.

invalid:
  meaning: >
    One or more mandatory governed watches were omitted or a coverage object
    contradicts its source-availability state.
```

`Sufficient` describes coverage of the declared method, not truth, source
quality, buyer evidence, or market validation.

## Escalation review

Every coverage object must show that both stored trigger families were checked
and must separately state whether evidence supports:

- repeated institutional behavior;
- structural category movement;
- material competitive compression; and
- an escalation condition.

The Market Signal Agent reports evidence state only. Jarvis-Nova or other local
governance determines attention routing. This contract creates no automated
notification or escalation.

```text
repeated market language
≠
repeated institutional behavior
```

Language about authorization, policy, auditability, agentic payments,
transaction controls, or wallet guardrails may strengthen category
compression, problem legibility, or narrative pressure. It does not alone
establish institutional workflow dependency, buyer pull, Nova demand, or
operator urgency.

## Output contract

The machine-readable contract is
[`market_signal_run_v0_1.schema.json`](../../schemas/market/market_signal_run_v0_1.schema.json).
It defines two distinct evidence objects.

### Direct market-signal run

A `direct_market_signal_run` records contemporaneous Pass 1 coverage. It must
contain one mandatory coverage object for every eligible governed watch,
including scan status, delta state, source availability, and escalation review.
Its aggregate `evidence_coverage` is derived from those direct-run facts.

### Retrospective reconciliation

A `retrospective_reconciliation` records a later governance review of a prior
specialist output. It preserves whether the original output made governed-watch
coverage explicit and whether the original run complied with the direct-run
coverage contract. It may map prior observations to active watches and evaluate
stored escalation conditions, but it has no `governed_watch_coverage`, scan
status, delta state, source-availability claim, or aggregate direct-run evidence
coverage.

```text
successful retrospective reconciliation
≠
successful contemporaneous governed-watch scan
```

The validator
[`validate_market_signal_scan_coverage.py`](../../scripts/validate_market_signal_scan_coverage.py)
discovers every YAML artifact under `docs/market/runs/` when invoked without a
`--run` argument. Each direct run must independently satisfy mandatory coverage;
a valid retrospective artifact cannot cover a deficient direct run. A targeted
`--run` remains available for focused validation. The generic validator owns
eligibility, mode semantics, source-state consistency, reconciliation and
escalation completeness, and non-authority invariants. Historical content
assertions belong in narrowly scoped regression tests.

The existing Arc validator remains separate:

```text
Arc watch validator
= is the Arc watch structurally safe?

Governed-watch scan validator
= did this market-sensing run examine every active governed watch?
```

## Non-effects

```yaml
accepted_state_change: false
chronology_change: false
Reflex_Memory_change: false
constraint_change: false
policy_change: false
roadmap_change: false
runtime_change: false
production_change: false
external_integration: false
architecture_authority_created: false
engineering_authority_created: false
buyer_demand_established: false
```
