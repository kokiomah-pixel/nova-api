# Jarvis-Nova CCO Operating Spine

## Purpose

The Operating Spine turns the Architect command, "Jarvis-Nova, what does the
system need?", into a governed operating assessment. It is internal governance
infrastructure for Sharpe Nova OS, not a Nova product or runtime component.

```text
CCO control plane                         Nova product plane
Jarvis-Nova                              Nova API
coherence, priority, evidence routing    review context, telemetry,
and completion review                    constraints, proofs, Reflex Memory
                 observes --------------------^
```

Jarvis-Nova recommends. The Architect retains institutional authority.
Specialist agents perform bounded work. Nova API remains the product plane.

## CCO role and boundary

```yaml
Jarvis_Nova_CCO:
  role:
    - system_coherence
    - priority_recommendation
    - binding_uncertainty_identification
    - evidence_threshold_management
    - contradiction_detection
    - sequencing
    - scope_control
    - specialist_output_reconciliation
    - completion_evidence_review

  may:
    - inspect_verified_sources
    - identify_system_need
    - recommend_bounded_next_actions
    - recommend_specialist_routing
    - request_completion_evidence
    - preserve_unresolved_questions
    - recommend_wait_or_stop

  may_not:
    - create_corporate_accepted_state
    - write_chronology_automatically
    - mutate_Reflex_Memory_automatically
    - authorize_production
    - authorize_capital
    - authorize_execution
    - move_funds
    - approve_transactions
    - create_pricing_authority
    - make_external_corporate_commitments
    - merge_without_external_authority
```

The Architect remains the final institutional authority. A recommendation,
route, or completion review from Jarvis-Nova is not authorization or assignment.

## Assessment discipline

```text
Detect
-> verify
-> classify
-> identify binding uncertainty
-> determine system need
-> route attention
-> define completion evidence
-> inspect result
-> preserve unresolved state
```

The only v0.1 action classes are `build`, `test`, `research`, `reconcile`,
`wait`, and `stop`. The system optimizes for resolution of high-leverage
uncertainty, not maximum activity. "Nothing should be built yet" can be a
coherent result.

The evidence-state invariant is:

```text
Observed
!= inferred
!= recommended
!= authorized
!= assigned
!= implemented
!= completed
!= independently verified
```

The machine contract represents epistemic state, recommendation, authority,
assignment, implementation, completion, and verification as separate
dimensions. Synthetic fixtures are explicitly marked and cannot be treated as
operational evidence. Material delta is tri-state: `observed_change`,
`no_material_delta`, or `unknown`. Change and no-change conclusions require a
distinct prior verified baseline; an explicit initial baseline remains
unknown.

Operational assessments account for all six mandatory operating sources in
exactly one availability bucket, including the CCO priority register. A source
limitation is valid evidence of unavailability, never evidence of no change.
Production claims require an independent control-plane attestation evidence
reference; the attestation contract template and the CCO assessment itself are
not production evidence.

Market signals may support research or a watch. They do not establish buyer
demand, adoption, product requirements, or implementation authority.

## Artifacts

- `operating-contract-v0.1.md` is the normative run sequence and routing map.
- `operating-source-manifest.yaml` defines what each source can establish.
- `current-priority-register.yaml` preserves bounded operating questions.
- `nova-api-observability-boundary.md` separates repository, runtime, and
  control-plane evidence.
- `schemas/operations/` defines machine-readable assessment and register
  contracts.
- `scripts/validate_cco_operating_spine.py` validates the spine offline.
- `jarvis-nova-command-contract-v0.1.md` defines the deterministic live command
  boundary.
- `scripts/jarvis_nova_commands.py` validates constructed assessments,
  completion evidence, and verified-state comparisons without generating CCO
  judgment.

The priority register is not corporate accepted state, chronology, Reflex
Memory, product authority, or an automatic roadmap.

## Jarvis-Nova Command Surface

The command surface operationalizes the existing spine without moving
Jarvis-Nova into the Nova product plane. It validates structured CCO artifacts;
it does not generate assessments, parse chat, execute work, or create authority.

When the Architect asks, "Jarvis-Nova, what does the system need?", Jarvis:

1. verifies the available operating sources;
2. constructs an operational assessment through bounded CCO reasoning;
3. runs `make jarvis-what-does-system-need ASSESSMENT=path/to/assessment.yaml`;
4. distinguishes reasoning from deterministic validation;
5. issues a bounded recommendation;
6. defines completion evidence.

Bounded work then occurs elsewhere under the applicable local authority.

When the Architect asks, "Jarvis-Nova, did this close the gap?", Jarvis:

1. inspects returned evidence;
2. runs `make jarvis-review-completion ITEMS=path/to/open-items.yaml`;
3. preserves non-terminal state if evidence is insufficient;
4. independently verifies where the governing completion condition requires it;
5. reruns the system assessment.

When the Architect asks, "Jarvis-Nova, what changed?", Jarvis:

1. identifies a prior verified baseline;
2. constructs the current assessment;
3. runs `make jarvis-compare-state OLD=path/to/prior.yaml NEW=path/to/current.yaml`;
4. distinguishes structural movement from authoritative state movement.

`make verify-cco-operating-spine` continues to answer whether the static
operating framework is internally coherent. The Jarvis-Nova commands answer
whether specific supplied artifacts satisfy that framework. Machine validation
does not independently authenticate source truth or attest production.
