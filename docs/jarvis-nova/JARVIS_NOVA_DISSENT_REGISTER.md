# Jarvis-Nova Dissent Register

## Status

```yaml
register:
  version: 1.0
  status: active_after_merge
  initial_records: none
  retroactive_fabrication_permitted: false
```

## Purpose

This register preserves material disagreements between the Architect and
Jarvis-Nova when the disagreement affects architecture, authority, production,
capital, category, monetization, accepted risk, or institutional continuity.

The purpose is not to constrain the Architect.

The purpose is to preserve the actual decision environment.

## Recording rule

Record dissent when:

- the CCO recommends against a material action;
- the Architect deliberately proceeds;
- the CCO identifies a material risk the Architect accepts;
- uncertainty is significant enough that later review will need the original
  positions.

Do not record ordinary brainstorming, stylistic preferences, minor drafting
disagreement, or every rejected suggestion.

## Record template

```yaml
dissent_record:
  dissent_id:
  date:
  issue:

  Architect_position:
  CCO_position:

  evidence_available_at_the_time:
  assumptions:
  uncertainty:

  decision_taken:
  decision_authority:
  risk_accepted:

  immediate_consequences:
  revisit_trigger:

  later_outcome:
  lesson:

  source_references:
  controlling_commit:
```

## Historical integrity rule

Do not rewrite a prior position because later evidence made another position
look correct.

Preserve what was known, what was uncertain, what each party believed, who had
authority, what risk was accepted, and what later occurred.

## Initial state

No historical dissent entry is created by this implementation.

Future backfilling requires source evidence and Architect review.
