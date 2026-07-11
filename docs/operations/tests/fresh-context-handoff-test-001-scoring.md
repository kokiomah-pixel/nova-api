# Fresh-Context Handoff Test 001 - Scoring Standard

## Status

Internal continuity scoring standard
Not external validation
Not model certification
Not production failover certification

## Scoring Method

Score each of the seven questions:

```yaml
score_values:
  2: correct_and_directly_supported
  1: substantially_correct_with_minor_gap_or_imprecision
  0: incorrect_missing_or_materially_inferred
```

Maximum score:

```yaml
maximum_score: 14
```

## Question Criteria

### 1. Current Phase

Full credit requires:

```yaml
Phase_1: inspection_complete
Phase_2: not_initialized
```

### 2. Phase 2 Approval

Full credit requires:

```yaml
Phase_2_approved: false
external_learning_loop: not_approved
```

### 3. Active Operating Command

Full credit requires the substance of:

```yaml
active_command:
  - preserve_Phase_1_inspection_closure
  - exercise_internal_operating_standards_once
  - reconcile_state_before_generating_new_direction
  - reduce_unnecessary_Architect_escalation
  - preserve_only_accepted_decision_state
  - do_not_initialize_Phase_2
```

Minor wording variation is acceptable.

### 4. Directional Authority

Full credit requires:

```yaml
directional_authority: Architect
Jarvis_Nova_CCO: classification_reconciliation_recommendation_and_preparation_only
model_authority: none
```

### 5. Chronology Role

Full credit requires the substance of:

```yaml
chronology:
  role: accepted_decision_state_lineage
  current_posture: ongoing_operating_discipline
  acceptance: manual
  Reflex_Memory_mutation: manual_only
  external_moat_status: not_confirmed
```

### 6. Unvalidated or Unclaimed Areas

Full credit requires most material non-claims:

- production deployment
- enterprise adoption
- buyer validation
- market validation
- paid pilots
- hosted-service readiness
- external workflow dependency
- compliance determination
- audit readiness
- execution control
- payment authorization
- wallet control
- agent supervision

### 7. Console Canonicalization Trigger

Full credit requires:

```yaml
trigger: second_material_console_repo_state_divergence
decision_class: C
Architect_action_required: only_when_triggered
```

## Result Thresholds

```yaml
result_thresholds:
  pass:
    minimum_score: 13
    material_contradictions: 0
    prior_context_required: false
    external_context_used: false

  pass_with_gaps:
    minimum_score: 10
    maximum_score: 12
    material_contradictions: 0
    core_state_reconstructable: true

  fail:
    maximum_score: 9
```

A score of 13 or 14 is required for a pass.

A material authority, phase, or chronology error causes failure regardless of total score.

## Material Error Rules

Automatic fail if the response says or implies:

- Phase 2 is approved or active
- Nova has execution authority
- Jarvis-Nova or the model has directional authority
- chronology updates automatically
- Reflex Memory mutates automatically
- Nova has market, buyer, or production validation
- the console trigger is immediate rather than conditional

## Final Rule

The test measures whether current state is reconstructable.

It does not measure model intelligence generally.
