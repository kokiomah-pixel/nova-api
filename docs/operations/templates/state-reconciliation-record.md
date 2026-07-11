# State Reconciliation Record

## Reconciliation Metadata

```yaml
reconciliation_id:
date:
prepared_by:
issue:
```

## Conflicting States

```yaml
conflicting_states:
  - source:
    source_class:
    state_claimed:
    date:
    current_or_stale:
```

## Accepted Current State

```yaml
accepted_current_state:
  statement:
  basis:
  source_class:
  accepted_by:
```

## Superseded State

```yaml
superseded_state:
  statement:
  reason_superseded:
  preservation_required:
```

## Boundary Effect

```yaml
boundary_effect:
  doctrine_changed:
  authority_changed:
  production_scope_changed:
  commercial_position_changed:
```

## Required Action

```yaml
required_action:
  update_console:
  update_chronology:
  update_repo:
  Architect_decision_required:
```

## Final Rule

Reconciliation identifies current truth.

It does not rewrite history.
