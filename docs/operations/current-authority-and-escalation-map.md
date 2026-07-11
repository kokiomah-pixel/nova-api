# Current Authority and Escalation Map

## Status

Internal operating map
Not delegation of institutional authority
Not runtime authority map
Not execution authorization

## Authority Map

```yaml
Architect:
  may:
    - accept_directional_changes
    - approve_doctrine
    - approve_phase_changes
    - approve_commercial_commitments
    - approve_material_architecture
    - accept_material_governance_memory
  remains_final_authority: true

Jarvis_Nova_CCO:
  may:
    - classify_issues
    - identify_drift
    - prepare_implementation_packets
    - reconcile_state
    - recommend_acceptance_or_rejection
    - maintain_quiet_watch_items
  may_not:
    - change_direction_without_approval
    - create_execution_authority
    - accept_material_commercial_commitments
    - autonomously_mutate_Reflex_Memory

Repository:
  role:
    - preserve_inspectable_architecture
    - preserve_validation_artifacts
    - preserve_current_documented_boundaries
  authority: none

Internal_Monitoring_Console:
  role:
    - report_current_operating_state
    - identify_pressure_and_drift
  authority: none

Model:
  role:
    - reasoning_and_synthesis_engine
  authority: none
```

## Escalation Matrix

```yaml
escalation_matrix:
  routine_classification:
    decision_class: A
    Architect_required: false

  bounded_maintenance:
    decision_class: B
    Architect_required: implementation_approval

  directional_change:
    decision_class: C
    Architect_required: true

  sovereign_boundary_change:
    decision_class: D
    Architect_required: true
    CCO_review_required: true
    chronology_required: true
```

## Final Rule

Authority must be explicit.

Reasoning capability is not authority.
