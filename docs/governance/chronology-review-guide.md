# Chronology Review Guide

## Status

Reviewer guide  
Public-facing governance companion  
Non-authority documentation layer

## Purpose

This guide explains how to read Sharpe Nova OS chronology.

Nova chronology exists to preserve decision-state lineage: what was known, what changed, what was corrected, what was accepted, what was paused, what sources were available, what sources were missing, and what boundary was active at the time.

Chronology helps future reviewers understand the context around Nova's evolution.

Chronology does not create execution authority.

---

## Canonical Boundary

Agent prepares action.  
Nova structures review context.  
Local authority decides.  
Nova does not execute.

All chronology should be read through this boundary.

Chronology does not imply that Nova approves, denies, authorizes, blocks, permits, routes, settles, executes, processes payments, moves capital, supervises agents, performs compliance review, performs audit reporting, or replaces local authority.

---

## How to Read Nova Chronology

Nova chronology should be read as decision-state context, not as a performance timeline.

A chronology entry may help answer:

- What changed?
- Why did it matter?
- What layer did it affect?
- What source supported it?
- What source was unavailable?
- What boundary was active?
- Was the event source-confirmed, Architect-provided, or CCO-reconciled?
- Did the event change Nova's doctrine, or only clarify it?
- Did the event expand capabilities, or only improve governance discipline?

The purpose is reviewability.

The purpose is not persuasion.

---

## What Chronology Can Show

Chronology can show:

- material repo events
- proof-chain milestones
- governance corrections
- source limitations
- stale connector artifacts
- continuity gaps
- public framing changes
- content engine operating-rule changes
- controlled discoverability updates
- CCO-reconciled events
- manual acceptance before chronology movement
- boundary state at the time of a change

Chronology can help reviewers understand how Nova preserved coherence while the system changed.

---

## What Chronology Does Not Prove

Chronology does not prove:

- customer adoption
- buyer validation
- market validation
- production readiness
- external dependency
- investment performance
- trading performance
- execution capability
- compliance approval
- audit completion
- payment capability
- settlement capability
- institutional deployment
- that Nova is required infrastructure today

Chronology may become strategically valuable if continuity becomes relied upon.

That dependency is not assumed.

---

## Source Classifications

Chronology entries may use the following source classifications.

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

These classifications protect the chronology from false certainty.

They also prevent stale connector output from becoming a doctrine blocker.

---

## How to Interpret Source-Incomplete Entries

A source-incomplete entry means the system could not see every relevant source during that run.

It does not automatically mean the entry is wrong.

It means the entry should be read with its source limitations attached.

For example, a run may have access to:

- public repo state
- prior memory
- current CCO boundary

while lacking access to:

- local working tree
- live portal state
- current chronology file
- underlying proof artifacts
- external archive state

In that case, the entry may still be useful, but it should not be treated as complete operating truth.

---

## How to Interpret CCO-Reconciled Events

A CCO-reconciled event occurs when Jarvis-Nova CCO accepts or corrects an event after reviewing source limitations, source conflict, or stale connector state.

CCO reconciliation helps preserve coherence when different sources do not line up cleanly.

It does not turn an event into adoption evidence, market validation, production readiness, or execution authority.

It means the event has been reviewed for boundary coherence and source-status clarity.

---

## How to Interpret Stale Connector Artifacts

A stale connector artifact occurs when a connector-visible source appears behind a known Architect-provided or CCO-resolved state.

Example:

```yaml
source_classification: stale_connector_artifact
connector_visible_state: older_commit_or_file_state
architect_provided_state: newer_commit_or_corrected_file_state
cco_interpretation: source freshness limitation, not doctrine blocker
chronology_action: preserve both states with reconciliation note
```

Stale connector artifacts should be recorded.

They should not automatically override newer CCO-reconciled context.

---

## How to Interpret Continuity Gaps

A continuity gap is a meaningful pause, deactivation window, missing source interval, or workspace discontinuity that could create ambiguity later.

A continuity gap is not automatically a failure.

It becomes a risk when it is not recorded.

Example:

```yaml
event_type: continuity_gap
classification: intentional_deactivation_and_revision_window
meaning: public posting or operating activity paused while OS materials were revised
risk: external observers may see silence without understanding internal system revision
cco_interpretation: not drift if properly logged
chronology_requirement: preserve as continuity event, not performance failure
```

Continuity gaps should be read as review-context events, not as performance periods.

---

## Generated, Reviewed, Accepted, Archived, Public

Not every generated artifact becomes chronology.

Nova chronology should distinguish between:

- generated artifact
- reviewed artifact
- accepted artifact
- archived artifact
- public artifact

This prevents automatic memory mutation.

A draft, test output, agent note, or scenario may be useful without becoming accepted chronology.

Chronology should preserve material decision-state events, not every artifact the system produces.

---

## Capability Change vs. Governance Clarification

Reviewers should distinguish between capability changes and governance clarifications.

A governance clarification may:

- improve documentation
- clarify boundaries
- add source classification
- improve reviewability
- preserve chronology discipline
- reduce misinterpretation risk

A capability change would affect what Nova does.

Most chronology governance updates should be read as coherence improvements unless the entry explicitly states that API behavior, harness behavior, product scope, or execution behavior changed.

---

## Reading Chronology Safely

When reviewing a chronology entry, ask:

```yaml
review_questions:
  - What changed?
  - What did not change?
  - What source supports the entry?
  - What source was unavailable?
  - Was the boundary preserved?
  - Did this expand Nova's capabilities?
  - Did this only clarify governance?
  - Does this imply authority, adoption, readiness, or validation?
  - Is a CCO reconciliation note attached?
```

If the entry does not show capability expansion, do not infer it.

If the entry describes source limitations, preserve them when citing or summarizing the entry.

---

## Public Interpretation Rule

Chronology can support public understanding of Nova's discipline.

Chronology should not be used to claim:

- Nova is adopted
- Nova is production-ready
- Nova has buyers
- Nova controls capital movement
- Nova has market validation
- Nova has institutional deployment
- Nova provides compliance or audit approval
- Nova is a trading, payment, settlement, wallet, or execution system

Correct public interpretation:

```text
Nova preserves decision-state lineage to improve future review context.
```

Incorrect public interpretation:

```text
Nova's chronology proves the system is externally validated or operationally required.
```

---

## Relationship to the Chronology Preservation Standard

This guide explains how to read chronology.

The Chronology Preservation Standard defines how chronology should be preserved.

Use this guide when interpreting chronology entries.

Use the standard when creating or maintaining chronology entries.

---

## Final Principle

Chronology protects coherence over time.

It should be complete enough to reconstruct decision context, but selective enough to remain reviewable.

The operating compression is:

```text
Preserve events.
Label sources.
Log gaps.
Separate doctrine from interpretation.
Protect the boundary.
Maintain signal quality.
```

Chronology is not yet Nova's moat.

Chronology is the condition under which a moat could form if continuity becomes relied upon.

Until then, chronology should be treated as institutional review-context discipline.

---

## Related Governance Concepts

- [Governance-Context Rot](governance-context-rot.md)
- [Institution-Owned Governance Chronology](institution-owned-governance-chronology.md)
- [Source Reconciliation Runbook](source-reconciliation-runbook.md)
