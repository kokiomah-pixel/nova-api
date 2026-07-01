# Chronology Preservation Standard

## Status

Governance standard  
Boundary-preserving chronology discipline  
Non-authority documentation layer

## Purpose

Sharpe Nova OS preserves chronology to improve future review context.

Chronology records decision-state lineage: what was known, what changed, what was corrected, what was accepted, what was paused, and what boundary was active at the time.

Chronology is part of Nova's review-context discipline.

It is not execution authority.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

Chronology must preserve this boundary.

Chronology must never imply that Nova approves, denies, authorizes, blocks, routes, settles, executes, processes payments, moves capital, supervises agents, performs compliance review, performs audit reporting, or replaces local authority.

---

## What Chronology Is

Chronology is preserved decision-state lineage.

It may include:

- material repo events
- proof-chain milestones
- governance corrections
- boundary clarifications
- source limitations
- continuity gaps
- CCO-reconciled events
- manual acceptance events
- archive movements
- public framing changes
- controlled discoverability updates

Chronology exists to help future reviewers understand the state of the system at the time a decision, correction, or proof movement occurred.

---

## What Chronology Is Not

Chronology is not:

- performance history
- marketing sequence
- adoption evidence
- buyer validation
- market validation
- production-readiness evidence
- external dependency proof
- automatic memory mutation
- automatic acceptance
- authority over execution
- evidence that Nova is required infrastructure today

Chronology may become strategically valuable over time if users rely on Nova's continuity record, but external dependency is not assumed.

---

## Source Classification

Chronology entries must distinguish the source status of each event.

Use the following classifications:

```yaml
source_confirmed_event:
  meaning: directly observed in an available source during the run

architect_provided_event:
  meaning: provided by the Architect but not independently surfaced by connector

cco_reconciled_event:
  meaning: accepted by Jarvis-Nova CCO after reviewing a source conflict or source limitation

source_unavailable:
  meaning: cannot be confirmed during the run

stale_connector_artifact:
  meaning: connector-visible state appears behind known Architect-provided or CCO-resolved state
```

Do not let a stale connector artifact overwrite a CCO-reconciled event.

Do not treat Architect-provided evidence as connector-confirmed unless it is independently visible.

---

## Continuity Gaps

Continuity gaps must be logged explicitly.

A continuity gap is any meaningful pause, deactivation window, missing source interval, or workspace discontinuity that could later create ambiguity.

Continuity gaps are not automatically failures.

They become risks when they are not recorded.

Example classification:

```yaml
event_type: continuity_gap
classification: intentional_deactivation_and_revision_window
meaning: public posting or operating activity paused while OS materials were revised
risk: external observers may see silence without understanding internal system revision
cco_interpretation: not drift if properly logged
chronology_requirement: preserve as continuity event, not performance failure
```

---

## Manual Acceptance Before Chronology Movement

Where applicable, chronology movement should preserve manual acceptance before lifecycle movement.

A review artifact, proof packet, or operating note should not automatically become chronology.

Chronology should distinguish:

- generated artifact
- reviewed artifact
- accepted artifact
- archived artifact
- public artifact

This prevents automatic memory mutation and protects the local authority boundary.

---

## Minimum Entry Requirements

Each material chronology entry should include:

```yaml
date:
event_type:
source_classification:
summary:
layer_affected:
boundary_state:
evidence_anchor:
source_limitations:
cco_interpretation:
decision_impact:
chronology_action:
```

---

## Layer Classification

Chronology entries should identify the layer affected.

Allowed layer examples:

- repo
- governance
- proof_workflow
- chronology
- archive
- content_engine
- market_signal
- nsf_grant
- public_framing
- api_context
- controlled_discoverability
- reflex_memory

---

## Boundary Language Requirement

Every chronology entry touching execution-adjacent domains must preserve the canonical boundary.

Use:

```text
Nova structures review context before local authority acts.
```

Do not use:

```text
Nova approves.
Nova denies.
Nova authorizes.
Nova blocks.
Nova permits.
Nova executes.
Nova routes.
Nova settles.
Nova controls agents.
```

---

## Stale Connector Handling

If a connector returns stale repo or document state, classify the issue explicitly.

Example:

```yaml
source_classification: stale_connector_artifact
connector_visible_state: old_commit_or_old_file_state
architect_provided_state: newer_commit_or_corrected_file_state
cco_interpretation: source freshness limitation, not doctrine blocker
chronology_action: preserve both states with reconciliation note
```

This protects chronology from false conflict.

---

## Chronology Preservation Rule

The correct chronology discipline is:

```text
Preserve events.
Label sources.
Log gaps.
Separate doctrine from interpretation.
Protect the boundary.
```

Chronology should make Nova easier to review later without making Nova appear broader, more operational, or more authoritative than it is.

---

## Final Principle

Chronology is not yet Nova's moat.

Chronology is the condition under which a moat could form if continuity becomes relied upon.

Until then, chronology should be treated as institutional review-context discipline.
