# NSF Phase I Proposal Control Matrix

## Control status and use

```yaml
artifact_status: controlling_internal_map_pending_Architect_and_CCO_review
artifact_type: internal_grant_planning_and_proposal_coherence_artifact
claim_state: proposed_Phase_I_research
purpose: >
  Connect Nova's repository-observed technical preparation to a testable,
  reviewer-legible NSF Phase I research program without presenting proposed
  research as completed work.
derivative_drafting_gate: >
  Do not draft or revise the final Project Summary or Project Description from
  this matrix until Architect and CCO review is complete.
```

This matrix is not the final Project Summary or Project Description. It is not evidence that Phase I research has been completed, that customers or partners are committed, that product-market fit exists, or that any institution depends on Nova. It does not authorize a change to Nova's canonical boundary.

## Canonical boundary

**Claim state: `repository_observed`**

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

For the proposed research:

```text
An agent-prepared financial action is formed.
Nova structures pre-execution review context.
A reviewer evaluates that context.
Local authority remains responsible for any decision.
No live capital execution is required for Phase I.
```

Nova does not authorize, approve, deny, block, execute, route, sign, or settle actions or transactions. It does not recommend trades, generate trading signals, optimize portfolios, determine compliance, produce audit opinions, or replace institutional authority.

## Claim-state legend

| Label | Meaning |
|---|---|
| `repository_observed` | Directly supported by a verified current repository artifact. |
| `internally_validated` | Tested within the current Nova environment; not external or commercial validation. |
| `proposed_Phase_I_research` | Work or evaluation to be conducted under the proposed award. |
| `hypothesis` | Plausible and testable, but not yet validated. |
| `external_evidence_required` | Requires buyer, reviewer, partner, market, or other external evidence. |
| `prohibited_claim` | Outside Nova's boundary or unsupported and unavailable for proposal use. |

An important statement without a state label must be treated as a drafting defect. Repository tests may support feasibility and experimental readiness; they do not by themselves establish external reviewer utility, institutional adoption, production readiness, or commercial demand.

## Controlling research logic

| Technical uncertainty | Research question | Experimental method | Baseline comparison | Measurement | Failure condition | Phase I deliverable | Commercial implication | Claim state |
|---|---|---|---|---|---|---|---|---|
| Equivalent actions may not yield equivalent context identities across heterogeneous scenarios. | RQ1 | Normalize paired fixtures, generate context and proofs repeatedly, and replay across scenario classes. | Same scenario represented by ordinary logs/post-hoc records and by a Nova-conditioned packet. | Signature match, proof match, replay consistency, unexplained variance. | Material unexplained output differences remain for equivalent normalized inputs. | Versioned context contract, equivalence suite, deterministic-context report. | Reproducibility may support an integration wedge, but demand remains unvalidated. | `proposed_Phase_I_research`; commercial implication `hypothesis` |
| Ambiguity, schema variation, or governance-epoch change may destabilize classification and source interpretation. | RQ2 | Introduce controlled missing, conflicting, stale, schema-varied, and epoch-varied context. | Same underlying scenario and disclosed variation, without versus with structured segmentation and epoch context. | Expected stability, justified change, unexplained drift, source recognition. | Changes cannot be reconstructed or tied to a visible input, schema, or authorized epoch change. | Stability suite, source-validation report, epoch-transition report, failure catalog. | Inspectable change may matter to governance and risk users; buyer ownership remains a hypothesis. | `proposed_Phase_I_research`; commercial implication `hypothesis` |
| Structured context may not improve human reconstruction or authority-scope recognition enough to justify added burden. | RQ3 | Controlled paired-packet reviewer evaluation after protocol and human-subjects determination. | Ordinary logs/post-hoc packet versus Nova-conditioned packet for the same scenario. | Accuracy, time, source recognition, authority recognition, burden. | No interpretable benefit, material confusion, or burden without compensating accuracy/comprehension. | Protocol, rubric, anonymized results, comparative and burden analyses. | Measurable reviewer value would support, but not prove, a commercial wedge. | `proposed_Phase_I_research`; commercial implication `hypothesis` |

## Core Phase I thesis and technical uncertainty

**Claim state: `proposed_Phase_I_research`**

> Phase I will determine whether a non-authority pre-execution context layer can produce deterministic, reproducible, source-segmented review context and measurably improve institutional reconstruction and authority-boundary recognition for agent-prepared financial actions compared with ordinary logs and post-hoc records.

The central uncertainty is:

> Can governed pre-execution review context remain deterministic, reproducible, inspectable, and useful under heterogeneous agent-prepared financial-action conditions without transferring decision authority into Nova?

**Claim state: `repository_observed` / `internally_validated`.** The repository contains an offline harness, tests, deterministic proof components, doctrine linting, chronology controls, source segmentation, fixtures, and reviewer-facing examples. These provide an experimental foundation.

**Claim state: `prohibited_claim`.** Those artifacts do not establish that the comparative Phase I research is complete, that external reviewers benefit, that institutions use Nova, or that buyers will pay.

## Research questions

### RQ1 — Deterministic context formation

**Claim state: `proposed_Phase_I_research`**

Can equivalent normalized inputs produce reproducible pre-action review context across heterogeneous agent-prepared financial-action scenarios?

Investigation areas: input normalization, canonical signatures, equivalent-action detection, deterministic proof generation, replay consistency, and variation across scenario classes.

### RQ2 — Stability under ambiguity and change

**Claim state: `proposed_Phase_I_research`**

Can classification, source segmentation, and authority-boundary recognition remain stable under ambiguous inputs, schema variation, and governance-epoch change?

Investigation areas: incomplete and conflicting context, source-class changes, telemetry-schema variation, governance-epoch transitions, model-provider interruption, and workspace or continuity interruption.

### RQ3 — Comparative reviewer utility

**Claim state: `proposed_Phase_I_research`**

Does structured pre-action review context improve reconstruction, source-context comprehension, and authority-scope recognition compared with ordinary logs and post-hoc records?

Investigation areas: reconstruction accuracy and time, source recognition, authority-boundary recognition, classification comprehension, retry/escalation comprehension, and reviewer burden.

## Controlled comparison

### Baseline condition

**Claim state: `proposed_Phase_I_research`**

```yaml
baseline_condition:
  input:
    - agent_prepared_financial_action
    - ordinary_event_logs
    - available_post_hoc_records
  absent_or_unstructured:
    - governed_pre_action_context_contract
    - canonical_review_identity
    - explicit_source_segmentation
    - constraint_posture
    - Reflex_Memory_references
    - structured_governance_epoch_context
```

### Nova-conditioned condition

**Claim state: `proposed_Phase_I_research`**

```yaml
Nova_condition:
  input:
    - equivalent_agent_prepared_financial_action
  review_context:
    - Pre_Action_Context_Contract
    - deterministic_environmental_state
    - canonical_signatures
    - source_segmentation
    - classification_context
    - constraint_posture
    - reproducibility_metadata
    - Reflex_Memory_references
    - governance_epoch_context
    - replayable_proof_artifacts
  authority_effect: none
```

The same underlying scenario must be evaluated in both conditions whenever methodologically appropriate. Materially different scenarios cannot be presented as evidence of a Nova effect. Packet length, information availability, order, and task instructions must be controlled or disclosed.

## Scenario classes

**Claim state: `proposed_Phase_I_research`.** These eight classes are research scenarios, not production deployments or institutional usage evidence.

| Scenario ID | Controlled purpose | Primary RQ(s) | Required paired comparison |
|---|---|---|---|
| `stablecoin_transfer_proposal` | Agent prepares a stablecoin transfer for local institutional review. | RQ1, RQ3 | Equivalent action represented in baseline and Nova packets. |
| `liquidity_movement_request` | Agent prepares a request to move liquidity between approved financial environments. | RQ1, RQ3 | Same action facts and source availability. |
| `treasury_reserve_reallocation` | Agent prepares a reserve reallocation proposal without executing it. | RQ1, RQ3 | Same proposal, facts, and reviewer task. |
| `incomplete_source_context` | Required source context is missing, incomplete, or insufficiently segmented. | RQ2, RQ3 | Same missing information disclosed through each packet form. |
| `conflicting_context` | Available sources contain decision-relevant conflict. | RQ2, RQ3 | Same conflict; packet structure is the experimental difference. |
| `governance_epoch_change` | Equivalent action is reviewed under a changed epoch or constraint configuration. | RQ1, RQ2 | Within-epoch replay plus disclosed cross-epoch variation. |
| `model_provider_or_workspace_interruption` | Workflow experiences provider, workspace, or continuity interruption. | RQ2 | Same preserved scenario before and after controlled interruption. |
| `retry_or_escalation_condition` | Action is retried, escalated, deferred, or returned for context. | RQ2, RQ3 | Same retry history and authority posture. |

Scenario fixtures must identify whether they are synthetic, production-like, inferred, or unavailable. No scenario may be labeled live without verified live provenance and separate approval.

## Evaluation design control

**Claim state: `proposed_Phase_I_research` unless marked otherwise.** No final numeric targets may be selected until the corresponding method is justified.

```yaml
evaluation_design:
  total_scenario_count:
    value: TBD
    justification_required: true
  scenario_instances_per_class:
    value: TBD
    justification_required: true
  reviewer_population:
    reviewer_types: []
    total_reviewers: TBD
    recruitment_status: unconfirmed
    claim_state: external_evidence_required
  reviewer_assignment:
    randomization_method: TBD
    blinding_method: TBD
    repeated_measure_design: TBD
  baseline_packet_definition:
    status: required
  Nova_packet_definition:
    status: required
  scoring_rubric:
    status: required
  statistical_or_decision_method:
    status: required
  human_subjects_review:
    determination_status: required_before_external_reviewer_study
```

Reviewer recruitment, institutional participation, and external study access are `external_evidence_required`; none are committed in this matrix.

## Measurement framework

All targets remain `TBD_after_method_design` or `TBD_after_pilot_measurement`. The internal artifacts establish candidate measures, not achieved Phase I outcomes.

| Metric | RQ | Operational definition and method | Candidate measures | Target | Failure condition | Claim state |
|---|---|---|---|---|---|---|
| Deterministic reproducibility | RQ1 | Re-run equivalent normalized inputs within a declared version/epoch and compare canonical identities and proof outputs. | Signature match rate; artifact match rate; replay consistency; unexplained variance. | TBD after scenario design | Equivalent inputs produce unexplained material differences in context or proof identity. | `proposed_Phase_I_research` |
| Classification stability | RQ2 | Apply controlled ambiguity, schema, and epoch changes; score unchanged outputs where stability is expected and traceable changes where change is expected. | Expected consistency; justified-change rate; unexplained drift; comprehension of change reason. | TBD after rubric design | A change cannot be reconstructed or tied to visible context, schema, version, or epoch. | `proposed_Phase_I_research` |
| Source-segmentation recognition | RQ2 | Ask blinded reviewers to classify source state and lineage from each packet. | Correct source classification; lineage comprehension; unsupported-live-inference rate. | TBD after rubric design | Reviewers materially confuse synthetic or production-like evidence with live institutional evidence. | `proposed_Phase_I_research` |
| Reconstruction accuracy | RQ3 | Score preregistered facts required to reconstruct the context available before local authority received the action. | Required-fact recall; sequence; constraint, source, and epoch identification. | TBD after rubric design | Nova packets do not improve accuracy or introduce material confusion relative to baseline. | `proposed_Phase_I_research` |
| Reconstruction time | RQ3 | Measure time from packet opening to completion of the reconstruction task using identical stop rules. | Median completion time; time to missing context, boundary, or conflict identification. | TBD after pilot measurement | Nova packets materially increase time without compensating accuracy or comprehension. | `proposed_Phase_I_research` |
| Authority-boundary recognition | RQ3 | Score explicit questions about Nova's role, local decision ownership, and external execution ownership. | Correct local-authority identification; correct non-execution identification; false approval/blocking/authorization inference rate. | TBD after rubric design | Reviewers repeatedly infer that Nova approves, blocks, authorizes, or executes. | `proposed_Phase_I_research` |
| Reviewer burden | RQ3 | Collect a bounded effort scale and count irrelevant or missing information after the objective task. | Perceived complexity; irrelevant and missing information; confidence; effort. | TBD after pilot measurement | Added context increases cognitive burden without measurable review benefit. | `proposed_Phase_I_research` |

The analysis method must define unit of analysis, missing-data handling, learning/carryover controls, uncertainty reporting, and the rule for interpreting a null or mixed result. Statistical significance cannot be promised before sample design.

## Work packages

### WP1 — Pre-Action Context Contract Stabilization

```yaml
claim_state: proposed_Phase_I_research
primary_research_question: [RQ1]
objective: stabilize_the_minimum_context_contract_before_local_authority_acts
activities:
  - define_required_and_optional_context_fields
  - define_normalization_and_canonical_identity_rules
  - define_equivalence_conditions
  - build_scenario_fixtures
  - test_deterministic_output_behavior
milestone: versioned_contract_and_fixture_suite_support_reproducible_context_formation
target_date: TBD
deliverables:
  - versioned_pre_action_context_contract
  - normalization_specification
  - equivalence_test_suite
  - deterministic_context_report
risks:
  - semantic_equivalence_is_difficult_to_define
  - normalization_removes_material_context
  - canonical_identity_is_unstable
failure_conditions:
  - equivalent_inputs_cannot_be_reliably_normalized
  - material_context_is_lost_during_normalization
  - canonical_outputs_remain_unexplainedly_variable
```

### WP2 — Classification and Source Stability

```yaml
claim_state: proposed_Phase_I_research
primary_research_question: [RQ2]
objective: test_classification_and_source_identity_under_controlled_change
activities:
  - construct_ambiguity_and_conflicting_source_scenarios
  - vary_source_classes_and_governance_epochs
  - test_expected_and_unexpected_classification_changes
  - measure_source_recognition
milestone: classification_changes_and_source_distinctions_are_reconstructable_and_explainable
target_date: TBD
deliverables:
  - classification_stability_suite
  - source_segmentation_validation_report
  - governance_epoch_transition_report
  - classification_failure_catalog
risks: [classification_drift, source_confusion, schema_variation, governance_epoch_incompatibility]
failure_conditions:
  - unexplained_classification_drift
  - synthetic_or_production_like_sources_are_misrepresented_as_live
  - governance_epoch_changes_break_reconstruction
```

### WP3 — Chronology and Replay Validation

```yaml
claim_state: proposed_Phase_I_research
primary_research_question: [RQ1, RQ2]
objective: test_replay_and_reconstruction_across_versions_and_interruptions
activities:
  - preserve_context_and_proof_artifacts
  - replay_equivalent_scenarios
  - test_versioned_governance_epochs
  - test_workspace_or_provider_interruption
  - validate_source_and_provenance_continuity
  - document_reconstruction_failures
milestone: approved_scenarios_replay_with_traceable_identity_provenance_and_epoch_interpretation
target_date: TBD
deliverables:
  - replay_validation_suite
  - chronology_reconstruction_report
  - continuity_interruption_report
  - provenance_integrity_report
risks: [chronology_rot, provenance_loss, replay_non_equivalence, version_interpretation_failure]
failure_conditions:
  - preserved_context_cannot_be_reconstructed
  - replay_results_cannot_be_explained
  - provenance_is_lost_or_ambiguous
```

### WP4 — Comparative Reviewer Evaluation

```yaml
claim_state: proposed_Phase_I_research
primary_research_question: [RQ3]
objective: compare_ordinary_records_with_Nova_conditioned_review_packets
activities:
  - define_baseline_and_Nova_packets
  - create_scoring_rubric
  - conduct_internal_pilot
  - obtain_human_subjects_determination_if_required
  - conduct_bounded_reviewer_evaluation
  - analyze_accuracy_time_comprehension_and_burden
milestone: comparative_evaluation_yields_interpretable_evidence_of_benefit_or_failure
target_date: TBD
deliverables:
  - reviewer_evaluation_protocol
  - scoring_rubric
  - anonymized_evaluation_results
  - comparative_analysis
  - reviewer_burden_analysis
risks: [insufficient_sample, learning_effects, scenario_bias, packet_length_bias, no_measurable_improvement]
failure_conditions:
  - no_detectable_review_benefit
  - increased_burden_without_compensating_accuracy
  - authority_boundary_confusion_persists
  - evaluation_design_cannot_support_interpretation
```

### WP5 — Commercial and Integration Discovery

```yaml
claim_state: hypothesis
primary_research_question: commercial_hypothesis_validation
objective: identify_or_reject_a_credible_workflow_pain_owner_buyer_and_integration_wedge
scope_control: supporting_commercial_de_risking_does_not_dominate_technical_R_and_D
activities:
  - conduct_structured_customer_discovery
  - capture_category_placement_and_boundary_comprehension
  - identify_pain_owner_and_budget_owner
  - document_manual_workarounds
  - test_review_context_value_and_integration_questions
  - test_vendor_neutrality_and_chronology_language
milestone: discovery_identifies_or_rejects_a_credible_initial_commercial_hypothesis
target_date: TBD
deliverables:
  - discovery_interview_protocol
  - anonymized_signal_register
  - buyer_and_pain_hypothesis_report
  - integration_path_requirements
  - commercialization_decision_memo
risks: [unbudgeted_problem, pain_and_budget_owner_diverge, low_purchase_priority, integration_burden, category_confusion]
failure_conditions:
  - no_repeatable_pain_pattern
  - no_identifiable_budget_owner
  - no_credible_integration_path
  - no_evidence_of_value_beyond_internal_coherence
```

## Technical risk matrix

| Risk | Research consequence | Phase I treatment | Evidence of resolution | Claim state |
|---|---|---|---|---|
| Context equivalence failure | Equivalent actions yield inconsistent context. | Normalization rules, signatures, controlled equivalence tests. | Reproducibility results. | `proposed_Phase_I_research` |
| Classification instability | Ambiguity creates unexplained drift. | Controlled ambiguity and epoch tests. | Stability and drift report. | `proposed_Phase_I_research` |
| Source confusion | Synthetic evidence is mistaken for live evidence. | Explicit segmentation and recognition tasks. | Source-recognition results. | `proposed_Phase_I_research` |
| Authority-boundary confusion | Nova is interpreted as an authority or executor. | Boundary rubric and reviewer testing. | Authority-scope accuracy. | `proposed_Phase_I_research` |
| Chronology degradation | Preserved context becomes unreconstructable. | Versioned replay and continuity tests. | Replay and reconstruction report. | `proposed_Phase_I_research` |
| Reviewer burden | Added structure creates complexity without benefit. | Paired time, accuracy, and effort comparison. | Comparative reviewer analysis. | `proposed_Phase_I_research` |
| Provider/workspace dependency | Context does not survive interruption. | Degraded-mode and continuity scenarios. | Interruption recovery report. | `proposed_Phase_I_research` |
| Commercial category compression | Prospective users misclassify Nova. | Structured discovery and misunderstanding tracking. | Category-placement evidence. | `hypothesis` / `external_evidence_required` |

## Verified repository evidence map

All paths below were verified in the repository during matrix construction. `repository_observed` means the artifact exists and says or implements the described thing; `internally_validated` means a current test exercises it. Neither state implies completion of the proposed comparative study.

```yaml
repository_evidence_map:
  - research_question: RQ1
    work_package: WP1
    evidence_path: docs/architecture/pre-action-context-contract.md
    evidence_type: architecture_contract
    current_status: repository_observed
    what_it_supports: [existing_context_surface, candidate_fields, non_authority_contract]
    what_it_does_not_prove: [cross_scenario_equivalence, external_reviewer_utility, production_readiness]

  - research_question: RQ1
    work_package: WP1
    evidence_path: core/governance_identity.py
    evidence_type: implementation
    current_status: repository_observed
    what_it_supports: [canonical_signature_implementation, input_normalization_foundation]
    what_it_does_not_prove: [semantic_equivalence_across_all_scenarios, Phase_I_target_attainment]

  - research_question: RQ1
    work_package: WP1
    evidence_path: tests/test_classification_determinism.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [stable_signature_for_tested_normalizations, deterministic_test_classification, explicit_fallback]
    what_it_does_not_prove: [heterogeneous_scenario_generalization, external_validity, commercial_value]

  - research_question: RQ1
    work_package: WP1
    evidence_path: tests/test_proof_reproducibility.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [proof_hash_reproducibility_for_tested_inputs, runtime_metadata_exclusion]
    what_it_does_not_prove: [all_version_replay, all_schema_variation, production_reproducibility]

  - research_question: RQ1
    work_package: WP1
    evidence_path: nova/harnesses/agent_prepared_financial_action_review/reviewer.py
    evidence_type: offline_harness_implementation
    current_status: repository_observed
    what_it_supports: [bounded_review_context_generation, explicit_boundary_log, deterministic_rule_surface]
    what_it_does_not_prove: [live_operation, reviewer_benefit, institutional_adoption, execution_prevention]

  - research_question: RQ1
    work_package: WP1
    evidence_path: tests/test_agent_prepared_financial_action_review_harness.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [offline_harness_behavior, tested_retry_stale_and_conflict_cases, non_authority_assertions]
    what_it_does_not_prove: [production_readiness, external_reviewer_utility, buyer_demand]

  - research_question: RQ1
    work_package: WP1
    evidence_path: examples/pre_execution_review/batch_inputs/agent_prepared_action_batch_001/normal_context.json
    evidence_type: scenario_fixture
    current_status: repository_observed
    what_it_supports: [controlled_normal_context_fixture, Phase_I_fixture_design_starting_point]
    what_it_does_not_prove: [representative_population, live_institutional_context, external_validity]

  - research_question: RQ2
    work_package: WP2
    evidence_path: docs/governance/proof-determinism-and-classification-stability.md
    evidence_type: governance_hardening_specification
    current_status: repository_observed
    what_it_supports: [candidate_stability_invariant, allowed_change_sources, failure_interpretation]
    what_it_does_not_prove: [stability_under_all_ambiguity, Phase_I_success, reviewer_comprehension]

  - research_question: RQ2
    work_package: WP2
    evidence_path: docs/governance/source-state-taxonomy.md
    evidence_type: source_taxonomy
    current_status: repository_observed
    what_it_supports: [source_state_classes, non_authority_source_interpretation]
    what_it_does_not_prove: [human_recognition_accuracy, live_source_quality, compliance_or_audit_status]

  - research_question: RQ2
    work_package: WP2
    evidence_path: tests/test_synthetic_record_segmentation.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [tested_source_type_segmentation_for_named_fixture_owners]
    what_it_does_not_prove: [reviewer_source_recognition, source_truth, live_provenance, institutional_use]

  - research_question: RQ2
    work_package: WP2
    evidence_path: examples/pre_execution_review/batch_inputs/agent_prepared_action_batch_001/source_conflict.json
    evidence_type: scenario_fixture
    current_status: repository_observed
    what_it_supports: [controlled_conflict_input, repeatable_ambiguity_test_basis]
    what_it_does_not_prove: [coverage_of_real_conflicts, conflict_resolution, reviewer_benefit]

  - research_question: RQ2
    work_package: WP2
    evidence_path: docs/governance-epochs/README.md
    evidence_type: governance_epoch_definition
    current_status: repository_observed
    what_it_supports: [epoch_record_fields, versioned_governance_concept]
    what_it_does_not_prove: [automated_epoch_transition, cross_epoch_replay_success, production_regime_management]

  - research_question: RQ1_RQ2
    work_package: WP3
    evidence_path: docs/governance/chronology-preservation-standard.md
    evidence_type: chronology_standard
    current_status: repository_observed
    what_it_supports: [decision_state_lineage_rules, manual_acceptance_discipline, source_classification]
    what_it_does_not_prove: [long_term_reconstruction_performance, external_audit_readiness, institutional_dependency]

  - research_question: RQ1_RQ2
    work_package: WP3
    evidence_path: tests/chronology/test_chronology_provenance.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [tested_commit_provenance_fields, malformed_commit_rejection]
    what_it_does_not_prove: [all_artifact_provenance, long_term_chronology_durability, external_acceptance]

  - research_question: RQ1_RQ2
    work_package: WP3
    evidence_path: docs/governance/reflex-memory-specification.md
    evidence_type: R_and_D_specification
    current_status: repository_observed
    what_it_supports: [bounded_memory_definition, manual_acceptance, authority_effect_none, replay_requirement]
    what_it_does_not_prove: [dynamic_persistence, autonomous_detection, production_use, reviewer_benefit]

  - research_question: RQ1_RQ2
    work_package: WP3
    evidence_path: tests/test_reflex_memory_replay.py
    evidence_type: fixture_backed_automated_test
    current_status: internally_validated
    what_it_supports: [fixture_replay_to_accepted_entry, source_chronology_trace, non_authority_preservation]
    what_it_does_not_prove: [production_replay, arbitrary_scenario_replay, commercial_or_external_value]

  - research_question: RQ2
    work_package: WP3
    evidence_path: docs/continuity/model-provider-independence-protocol.md
    evidence_type: continuity_protocol
    current_status: repository_observed
    what_it_supports: [degraded_mode_definition, local_validation_path, provider_independence_design]
    what_it_does_not_prove: [production_failover, equivalent_model_outputs, interruption_recovery_targets]

  - research_question: RQ2
    work_package: WP3
    evidence_path: tests/test_model_provider_independence.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [selected_governance_tools_run_without_OpenAI_key]
    what_it_does_not_prove: [complete_provider_independence, workspace_recovery, operational_continuity]

  - research_question: RQ2
    work_package: WP3
    evidence_path: docs/continuity/business-workspace-continuity-protocol.md
    evidence_type: continuity_protocol
    current_status: repository_observed
    what_it_supports: [workspace_risk_controls, incident_and_recovery_questions]
    what_it_does_not_prove: [tested_recovery_time, zero_data_loss, production_resilience]

  - research_question: RQ1_RQ2_RQ3
    work_package: WP1_WP2_WP4
    evidence_path: fixtures/deep_scenarios/authority_boundary.yaml
    evidence_type: multi_stage_scenario_fixture
    current_status: repository_observed
    what_it_supports: [authority_pressure_scenarios, multi_stage_internal_test_basis]
    what_it_does_not_prove: [external_reviewer_behavior, production_behavior, scenario_representativeness]

  - research_question: RQ1_RQ2_RQ3
    work_package: WP1_WP2_WP4
    evidence_path: tests/test_deep_scenario_authority_boundary.py
    evidence_type: automated_test
    current_status: internally_validated
    what_it_supports: [fixture_authority_effect_none, local_authority_ownership]
    what_it_does_not_prove: [human_boundary_recognition, live_workflow_safety, commercial_value]

  - research_question: RQ1_RQ2
    work_package: WP1_WP2_WP3
    evidence_path: scripts/doctrine_lint.py
    evidence_type: verification_script
    current_status: repository_observed
    what_it_supports: [automated_boundary_phrase_checks, terminology_and_integrity_checks]
    what_it_does_not_prove: [semantic_correctness_of_all_prose, runtime_behavior, reviewer_utility]

  - research_question: RQ3
    work_package: WP4
    evidence_path: docs/reviewer-paths.md
    evidence_type: reviewer_facing_documentation
    current_status: repository_observed
    what_it_supports: [structured_repo_inspection_paths, explicit_claim_boundaries]
    what_it_does_not_prove: [reviewer_comprehension, lower_reconstruction_time, external_validation]

  - research_question: RQ1_RQ2_RQ3
    work_package: WP1_WP2_WP3_WP4
    evidence_path: docs/validation/technical-evidence-map.md
    evidence_type: reviewer_facing_evidence_index
    current_status: repository_observed
    what_it_supports: [implemented_vs_R_and_D_distinction, distributed_evidence_orientation]
    what_it_does_not_prove: [accuracy_of_unverified_external_claims, Phase_I_outcomes, buyer_or_market_validation]
```

## Commercial hypotheses and questions

**Claim state: `hypothesis`; validation state: `external_evidence_required`.** The groups below are not confirmed users, buyers, customers, partners, or design partners.

```yaml
commercial_hypotheses:
  primary_user_groups:
    - institutional_treasury_operations
    - digital_asset_operations
    - financial_workflow_governance_or_risk_leads
  secondary_user_groups:
    - custody_workflow_owners
    - agentic_finance_platform_operators
  pain_hypotheses:
    - fragmented_pre_action_context
    - inability_to_reconstruct_why_an_action_was_reviewable
    - unclear_source_lineage
    - unstable_or_unexplained_classification
    - loss_of_review_context_across_models_or_workflows
    - confusion_between_agent_preparation_and_local_authority
  benefit_hypotheses:
    - improved_pre_action_reconstruction
    - clearer_source_lineage
    - greater_authority_boundary_recognition
    - more_consistent_classification
    - reduced_review_ambiguity
    - durable_context_across_workflow_changes
```

Commercial discovery must ask which workflow has the strongest problem; who feels the pain and controls budget; what workaround exists; what triggers a purchase or pilot; which integration point and review artifact are acceptable; whether vendor-neutral chronology and non-action review value are understood; and which business model is credible.

Candidate models—enterprise software license, infrastructure subscription, usage-based context generation, deployment and support, and governed private environment—remain hypotheses. Nova must not be described as outsourced governance or authority. Unsupported claims about systemic-risk reduction, guaranteed compliance, harmful-transaction prevention, audit-cost reduction, investment performance, or financial-loss reduction are `prohibited_claim`.

## Broader impacts

**Claim state: `hypothesis`, contingent on successful Phase I research.**

> As autonomous and semi-autonomous workflows approach financial authority, institutions need ways to preserve inspectable context without delegating decision authority to an automated system. Successful Phase I research could improve the reproducibility, reviewability, and institutional ownership of the context surrounding machine-prepared financial actions while preserving local human or institutional authority.

Potential impacts include more inspectable machine-prepared financial workflows, stronger preservation of local institutional authority, improved reproducibility of pre-action context, improved source and provenance clarity, reduced dependence on a single model or workflow vendor, and a research foundation for vendor-neutral governance context. These outcomes have not yet occurred and cannot be presented as current impact.

## Contingent Phase II bridge

```yaml
Phase_II_bridge:
  status: contingent
  claim_state: proposed_Phase_I_research
  justified_only_if_Phase_I_demonstrates:
    - reproducible_context_formation
    - stable_and_explainable_classification
    - reliable_source_segmentation
    - replayable_chronology
    - measurable_reviewer_benefit
    - credible_buyer_problem
    - credible_integration_path
  possible_Phase_II_work:
    - controlled_external_workflow_integrations
    - expanded_institutional_scenario_evaluation
    - design_partner_or_pilot_work_only_with_real_commitments
    - deployment_and_security_hardening
    - expanded_governance_epoch_and_schema_testing
    - commercial_model_validation
```

No Phase II partner, pilot, deployment, or commitment is claimed.

## Proposal section control matrix

| Proposal section | Reviewer question | Required Nova answer | Research evidence | Commercial evidence | Boundary risk | Status |
|---|---|---|---|---|---|---|
| Project Summary — Overview | What is the innovation and problem? | A non-authority layer structures deterministic, source-segmented context before local authority decides; Phase I tests whether it works and helps reviewers. | Repository foundation plus RQ1–RQ3 plan. | Buyer and pain hypotheses only. | Execution or product-feature framing. | Draft after control-matrix review; `proposed_Phase_I_research` |
| Project Summary — Intellectual Merit | What technical hurdle will Phase I resolve? | Whether context remains reproducible, stable, inspectable, and useful under heterogeneous, ambiguous, and changing conditions. | WP1–WP4 methods and failure conditions. | N/A | Presenting completed engineering as unresolved R&D or vice versa. | Research logic defined; methods unresolved |
| Project Summary — Broader Impacts | Who benefits if research succeeds? | Institutions retaining local authority may benefit from more inspectable and reproducible context. | RQ3 and continuity results, if achieved. | Discovery evidence, if obtained. | Unsupported present-tense societal claims. | Contingent hypothesis |
| Technical problem | Why is existing practice insufficient? | Ordinary logs and post-hoc records may omit structured pre-action identity, segmentation, constraints, epochs, and memory references; the comparative effect remains untested. | Baseline packet specification and paired scenarios. | Workflow interviews required. | Generic AI-governance framing or universal institutional claims. | Baseline defined; external problem evidence required |
| Proposed innovation | What is technically novel? | Deterministic governed context identity, source segmentation, versioned chronology, and bounded memory references with no authority effect. | Verified implementation, tests, and proposed stability research. | N/A | Overstating Reflex Memory, chronology, or production maturity. | Repository foundation mapped |
| Research plan | What experiments will be conducted? | Paired scenario generation, controlled ambiguity/version tests, replay/continuity tests, and reviewer evaluation. | WP1–WP4. | N/A | Engineering task list without hypotheses. | Experiments framed; design decisions open |
| Evaluation | How will success and failure be measured? | Seven metrics with paired comparisons and explicit failure conditions; targets follow design/pilot justification. | Measurement framework. | N/A | Arbitrary targets or promised significance. | Metrics defined; targets and analysis TBD |
| Commercial opportunity | Who pays and why? | Candidate users, pain owners, budget owners, workarounds, and integration points will be tested rather than asserted. | N/A | WP5 discovery register and decision memo. | Claiming buyer validation or adoption. | `hypothesis`; external evidence required |
| Team | Why can this team execute? | Use only verified founder/team roles, relevant experience, and repository execution evidence approved for application use. | Repository development evidence may support technical preparation. | Verified discovery or domain experience only. | Unsupported biography, staffing, or commitment claims. | Architect input and source evidence required |
| Phase II bridge | What follows if Phase I succeeds? | Controlled integration, expanded evaluation, hardening, and commercial validation only if Phase I gates are met. | Phase I deliverables and gate results. | Credible pain and integration evidence. | Treating contingent work as commitment. | Explicitly contingent |

## Current draft claim-removal and recast register

The following current NSF draft language should be removed or recast before submission. This matrix does not modify those drafts during this implementation pass.

| Current path and line | Current claim risk | Required treatment | Claim state |
|---|---|---|---|
| `docs/grants/nsf-seed-fund/project-pitch-submission-draft.md:5` | “Institutions lack reliable infrastructure” is a broad market fact without cited external evidence. | Recast as a problem hypothesis to be tested or add credible external evidence. | `external_evidence_required` |
| `docs/grants/nsf-seed-fund/project-pitch-submission-draft.md:46` | “Initial buyers are...” presents hypothesized groups as established buyers and states their need as fact. | Use “candidate user and buyer groups include...” and “Phase I discovery will test whether...” | `hypothesis` |
| `docs/grants/nsf-seed-fund/project-pitch-submission-draft.md:56` | “Nova supports... by improving” reads as achieved broader impact. | Use “successful research could support... by testing whether it improves...” | `hypothesis` |
| `docs/grants/nsf-seed-fund/project-pitch-portal-version.md:15` | “can improve reviewability” is not yet supported by comparative reviewer results. | Use “is designed to structure context; Phase I will test whether this improves...” | `proposed_Phase_I_research` |
| `docs/grants/nsf-seed-fund/project-pitch-portal-version.md:33` | “Initial buyers are...” overstates unvalidated commercial identity. | Recast as candidate groups and explicitly attach discovery questions. | `hypothesis` |
| `docs/grants/nsf-seed-fund/project-pitch-portal-version.md:35` | “These buyers need...” states unverified pain and buyer status. | Use “the discovery hypothesis is that these groups may need...” | `hypothesis` |
| `docs/grants/nsf-seed-fund/commercialization-pathway.md:14` | “Expected early adopters” implies an adoption forecast without external evidence. | Use “candidate early-user groups for discovery.” | `hypothesis` |
| `docs/grants/nsf-seed-fund/economic-value-hardening-notes.md:87` | “Likely early adopters” may be carried into the proposal as validated market language. | Keep internal only or recast as candidate interview segments. | `hypothesis` |
| `docs/grants/nsf-seed-fund/reviewer-risk-and-response.md:26` | “The customer pathway begins...” and “customer” language may imply established commercial validation. | Use “commercial discovery will test candidate user groups...” | `external_evidence_required` |
| `docs/grants/nsf-seed-fund/societal-impact.md:12` | “Improved auditability” can compress Nova into an audit product and reads as a realized benefit. | Prefer “potentially improved inspectability and reconstruction of pre-action context.” | `hypothesis` |

No verified evidence was found supporting confirmed customers, partners,
design partners, institutional adoption, or product-market fit.

Several existing draft passages present candidate buyers, institutional need,
reviewer benefit, or broader impact more strongly than current evidence
supports. Those passages remain controlled by the claim-removal and recast
register above.

Negative disclaimers in existing drafts do not validate the corresponding
positive claims.

## Unresolved Architect decisions

1. Define operational equivalence: which fields may vary while two agent-prepared actions remain equivalent, and which differences are material.
2. Approve the minimum and optional fields, versioning rule, and canonical identity boundary for the Phase I Pre-Action Context Contract.
3. Select total scenario count and instances per class with a power, precision, saturation, or decision-theoretic justification.
4. Define baseline and Nova packet contents, including parity rules for information volume, ordering, source availability, and visual presentation.
5. Select reviewer roles, eligibility criteria, recruitment channel, compensation, and whether internal pilot participants may enter the external evaluation.
6. Choose randomization, blinding, counterbalancing, repeated-measures, washout, and learning-effect controls.
7. Approve the scoring rubric, primary endpoint, secondary endpoints, analysis population, missing-data rules, uncertainty reporting, and success/failure decision rule.
8. Obtain and document the applicable human-subjects/IRB determination before any external reviewer study.
9. Define approved schema-variation and governance-epoch transition sets, including which changes should and should not alter outputs.
10. Define interruption scope, preservation checkpoints, recovery criteria, and the maximum claims supported by a successful continuity test.
11. Approve the source-class vocabulary used in reviewer packets and the provenance threshold required before any evidence can be called live.
12. Confirm verified team biographies, roles, facilities, budget, award period, subcontractors/consultants, and letters or commitments available for proposal use.
13. Decide which commercial interview segments and hypotheses WP5 may prioritize without displacing the technical R&D scope.
14. Approve any external citations supporting the market problem, broader impacts, and commercial opportunity.

## Implementation and review gate

```yaml
NSF_control_matrix_implementation:
  artifact_path: docs/grants/nsf-seed-fund/nsf-phase-1-proposal-control-matrix.md
  branch: grant/nsf-phase-1-control-matrix
  commit_sha: 37554fcbfee12085e302483db6bd31484f0c1804
  core_research_thesis_present: true
  research_question_count: 3
  baseline_defined: true
  Nova_condition_defined: true
  scenario_class_count: 8
  work_package_count: 5
  metric_count: 7
  failure_conditions_present: true
  verified_repository_paths_mapped: 24
  unverified_paths_included: 0
  claim_state_labels_applied: true
  commercial_hypotheses_bounded: true
  broader_impacts_bounded: true
  Phase_II_bridge_contingent: true
  unsupported_customer_claims_detected: true_in_existing_drafts_and_registered_for_recast
  unsupported_partner_claims_detected: false_positive_partner_claims_verified
  execution_authority_drift_detected: false_in_this_matrix
  trading_or_prediction_drift_detected: false_in_this_matrix
  audit_or_compliance_product_drift_detected: false_in_this_matrix
  unresolved_design_fields: 14_Architect_decision_groups
  contradictions_detected: >
    Existing draft language sometimes presents candidate buyers, institutional
    need, reviewer benefit, or broader impact more strongly than current
    evidence supports; the recast register controls those contradictions.
  overall_status: ready_for_Architect_and_CCO_review_not_ready_for_derivative_drafting
```

Review must confirm verified paths, unresolved method fields, claim-state discipline, and the canonical boundary before this matrix governs derivative proposal drafting. Do not merge until Architect and CCO review is complete.

## Final operating principle

```text
The repository demonstrates technical preparation.

The Phase I proposal must define what remains technically uncertain.

The control matrix connects the two without presenting preparation as completed
research.
```
