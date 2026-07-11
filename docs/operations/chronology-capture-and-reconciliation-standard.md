# Chronology Capture and Reconciliation Standard

## Status

Internal chronology operating standard
Decision-state continuity discipline
Not execution history
Not performance history
Not audit trail
Not autonomous memory intake

## Purpose

This standard reduces fragmentation across:

- repository commits
- chat windows
- Internal Monitoring Console reports
- Architect-provided updates
- external-source reviews
- implementation confirmations
- private operating notes

The objective is to preserve one coherent decision-state lineage without treating every conversation or artifact as accepted chronology.

## Core Distinction

```text
Conversation is not chronology.

A commit is not automatically chronology.

A console report is not automatically current truth.

Chronology contains accepted decision-state events.
```

## Source Classes

Every candidate event must use one source class:

```yaml
source_confirmed:
  meaning: directly verified in an available source

Architect_provided:
  meaning: explicitly provided by the Architect but not independently verified during the review

CCO_reconciled:
  meaning: accepted after reviewing a source conflict or continuity limitation

source_unavailable:
  meaning: could not be verified during the current review

stale_internal_artifact:
  meaning: an internal document or console state is behind accepted current state

derived_interpretation:
  meaning: reasoned conclusion based on multiple accepted inputs
```

## Event Classes

```yaml
event_classes:
  implementation_event:
    example: accepted_repo_commit

  doctrine_event:
    example: canonical_boundary_change

  reconciliation_event:
    example: stale_console_state_corrected

  continuity_event:
    example: intentional_pause_or_revision_window

  inspection_event:
    example: repository_inspection_signal

  operating_event:
    example: phase_status_or_active_command_change

  commercial_boundary_event:
    example: monetization_or_open_source_boundary_hardening
```

## Minimum Event Fields

```yaml
chronology_event:
  event_id:
  date:
  event_class:
  title:
  source_class:
  source_references:
  summary:
  layer_affected:
  what_changed:
  what_did_not_change:
  authority_effect: none
  production_effect: none_unless_explicitly_approved
  CCO_status:
  Architect_status:
  supersedes:
  related_commit:
```

## Capture Rule

Create a chronology candidate when an event:

- changes accepted operating state
- closes a meaningful boundary ambiguity
- changes the active command
- resolves a source conflict
- marks a phase boundary
- materially changes public positioning
- creates or removes a commercial constraint
- is likely to affect future review posture

Do not create a chronology event for:

- routine drafting
- minor wording changes
- every question
- every market observation
- speculative ideas
- unaccepted recommendations
- duplicated implementation reports

## Reconciliation Sequence

```text
Collect current sources
-> identify conflicts
-> label each source
-> determine newest accepted state
-> record superseded state
-> obtain CCO reconciliation
-> obtain Architect confirmation when direction changed
-> preserve accepted event
```

## Current-State Authority

When sources disagree, use this order:

```yaml
state_authority_order:
  1: explicit_recent_Architect_decision
  2: accepted_CCO_reconciliation
  3: verified_repository_state
  4: canonical_current_state_record
  5: Internal_Monitoring_Console
  6: older_chat_or_working_note
```

This order does not make every Architect statement doctrine automatically.

Directional statements still require classification and acceptance.

## Stale Artifact Rule

Do not delete a stale artifact merely because it is stale.

Label it as superseded when preservation has value.

```yaml
stale_artifact_handling:
  retain_when: historical_lineage_matters
  mark_as: superseded
  link_to: current_accepted_state
  prevent_from: overriding_current_state
```

## Final Rule

Preserve the decision state, not the volume of discussion.
