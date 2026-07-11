# Reviewer Paths

## Purpose

This file gives different readers a short path through the Sharpe Nova OS public repo.

The repo is a controlled public proof surface.

It is not the full operating archive of the Sharpe Nova OS living system.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Nova does not approve, deny, authorize, block, route, settle, sign, trade, optimize, manage wallets, supervise agents, perform compliance review, perform audit reporting, or replace local authority.

---

## Phase 1 Inspection Status

- `docs/inspection/phase-1-inspection-status.md`

Use this document to understand what Phase 1 proves, what it does not prove, and what reviewers should inspect before moving into deeper architecture, governance, or strategy artifacts.

---

## Ten-Minute Path

Use this path if you are reviewing Sharpe Nova OS for the first time.

1. `docs/start-here.md`
2. `docs/phase_1_offline_proof_chain.md`
3. `docs/architecture/pre-action-context-contract.md`
4. `examples/pre_action_context/`
5. `docs/governance/reflex-memory-specification.md`
6. `docs/governance/reflex-memory-v0-1-fixture.md`
7. `docs/validation/technical-evidence-map.md`

You should leave this path understanding:

- where Nova sits
- what Nova emits
- what Nova does not do
- how Phase 1 is bounded
- how Reflex Memory appears as review context only

---

## NSF Reviewer Path

Use this path to evaluate technical novelty, R&D risk, and Phase I readiness.

1. `docs/grants/nsf-seed-fund/project-pitch-portal-version.md`
2. `docs/grants/nsf-seed-fund/technical-novelty.md`
3. `docs/grants/nsf-seed-fund/reflex-memory-rd-plan.md`
4. `docs/grants/nsf-seed-fund/phase-i-validation-matrix.md`
5. `docs/grants/nsf-seed-fund/reviewer-risk-and-response.md`
6. `docs/validation/phase-i-outcome-validation-plan.md`

What this path shows:

- Sharpe Nova OS is framed as R&D, not production deployment.
- The technical risk is explicit.
- Reflex Memory is bounded, fixture-tested, and still research-worthy.
- Phase I validation focuses on risk reduction.
- Nova preserves local authority and does not execute.

What this path does not claim:

- market validation
- buyer validation
- production readiness
- institutional adoption
- compliance approval
- audit readiness
- trading performance

---

## Developer Path

Use this path to inspect implementation behavior.

1. `README.md`
2. `docs/architecture/pre-action-context-contract.md`
3. `docs/architecture/governed-context-flow.md`
4. `docs/governance/review-completeness-standard.md`
5. `docs/governance/source-state-taxonomy.md`
6. `docs/architecture/agent-framework-adapter-contract.md`
7. `examples/pre_action_context/`
8. `docs/architecture/review-context-loop.md`
9. `examples/agent_prepared_action/`
10. `core/reflex_memory/context.py`
11. `core/reflex_memory/replay.py`
12. `fixtures/reflex_memory/`
13. `schemas/reflex_memory/`
14. `tests/test_agent_prepared_action_example.py`
15. `tests/test_reflex_memory_v0_1.py`
16. `tests/test_reflex_memory_loader.py`
17. `tests/test_reflex_memory_context_endpoint.py`
18. `tests/test_reflex_memory_legacy_semantics_cleanup.py`
19. `tests/test_reflex_memory_multi_scenario.py`
20. `tests/test_reflex_memory_schema_validation.py`
21. `tests/test_reflex_memory_replay.py`
22. `docs/validation/technical-evidence-map.md`

Suggested local checks:

```bash
python3 scripts/doctrine_lint.py
python3 -m pytest
```

What this path shows:

- `/v1/context` emits governed review context
- Reflex Memory appears as context with `authority_effect: none`
- Reflex Memory fixture state is validated
- legacy decision-effect semantics are removed from active Reflex Memory paths
- tests preserve non-authority behavior

---

## Strategic Reader Path

Use this path to understand category, positioning, and institutional logic.

1. `docs/start-here.md`
2. `docs/go-to-market/where-nova-sits.md`
3. `docs/go-to-market/first-use-case-agent-prepared-treasury-action.md`
4. `docs/architecture/review-context-loop.md`
5. `docs/architecture/governed-context-flow.md`
6. `docs/architecture/attribution-vs-governance-context.md`
7. `docs/governance/institution-owned-governance-chronology.md`
8. `docs/governance/governance-context-rot.md`
9. `docs/go-to-market/gtm-comprehension-test-protocol.md`
10. `docs/strategy/non-authority-commercial-boundary.md`
11. `docs/strategy/open-source-commercial-boundary.md`

What this path shows:

- Nova operates before local authority acts.
- Nova structures governed review context.
- Institution-owned chronology matters before capital moves.
- The memory around a capital action should not belong to the system that moves the capital.
- Nova is infrastructure, not optional tooling, only if review context becomes required before action.

---

## Reflex Memory Path

Use this path to inspect Reflex Memory specifically.

1. `docs/governance/reflex-memory-specification.md`
2. `docs/architecture/reflex-memory-api-context.md`
3. `docs/architecture/reflex-memory-vs-agent-memory.md`
4. `docs/governance/source-state-taxonomy.md`
5. `docs/governance/reflex-memory-temporal-state-standard.md`
6. `docs/governance/reflex-memory-v0-1-fixture.md`
7. `docs/grants/nsf-seed-fund/reflex-memory-rd-plan.md`
8. `fixtures/reflex_memory/`
9. `schemas/reflex_memory/`
10. `core/reflex_memory/context.py`
11. `core/reflex_memory/replay.py`
12. `tests/test_reflex_memory_v0_1.py`
13. `tests/test_reflex_memory_loader.py`
14. `tests/test_reflex_memory_context_endpoint.py`
15. `tests/test_reflex_memory_legacy_semantics_cleanup.py`
16. `tests/test_reflex_memory_multi_scenario.py`
17. `tests/test_reflex_memory_schema_validation.py`
18. `tests/test_reflex_memory_replay.py`

Reflex Memory should be interpreted as:

```text
accepted governance memory that may condition future review posture
```

It should not be interpreted as:

- autonomous learning
- automatic memory mutation
- approval
- denial
- authorization
- blocking
- routing
- settlement
- signing
- execution
- compliance review
- audit reporting
- wallet control
- agent supervision
- local authority replacement

---

## Internal Operating Integrity Path

Use this path to inspect how Sharpe Nova OS preserves coherence without depending on one chat window, one model session, or continuous Architect attention:

1. `docs/operations/current-authority-and-escalation-map.md`
2. `docs/operations/architect-decision-triage-standard.md`
3. `docs/operations/chronology-capture-and-reconciliation-standard.md`
4. `docs/operations/internal-falsification-standard.md`
5. `docs/operations/language-behavior-integrity-standard.md`
6. `docs/operations/model-independence-and-context-continuity-standard.md`
7. `docs/operations/templates/decision-state-handoff.md`
8. `docs/operations/templates/state-reconciliation-record.md`
9. `docs/operations/templates/adversarial-review-record.md`

These artifacts define internal operating discipline.

They do not claim production deployment, external validation, autonomous governance, execution authority, compliance determination, or audit readiness.

### Current State and First Integrity Exercise

- `docs/operations/current-system-state.md`
- `docs/operations/internal-integrity-exercise-001.md`

The current-state record identifies the accepted operating posture.

The integrity exercise tests whether decision triage, reconciliation, falsification, language-behavior discipline, and model-independent handoff work in practice.

These artifacts do not initialize Phase 2 or create external, commercial, production, compliance, audit, or authority claims.

### Fresh-Context Continuity Test

- `docs/operations/tests/fresh-context-handoff-test-001-prompt.md`
- `docs/operations/tests/fresh-context-handoff-test-001-execution.md`
- `docs/operations/tests/fresh-context-handoff-test-001-scoring.md`
- `docs/operations/tests/results/fresh-context-handoff-test-001-raw.md`
- `docs/operations/tests/results/fresh-context-handoff-test-001-evaluation.md`

This test evaluates whether a fresh model context can reconstruct Nova's accepted operating state from canonical repository artifacts without prior conversational memory.

It does not create external, commercial, production, compliance, audit, authority, or execution validation.

## Deep Scenario Validation

Use this path to review whether Nova preserves coherence across changing institutional decision environments:

1. `docs/validation/deep-scenario-validation-standard.md`
2. `docs/validation/deep-scenario-matrix.md`
3. `fixtures/deep_scenarios/`
4. `scripts/run_deep_scenario_suite.py`
5. `tests/test_deep_scenario_suite.py`
6. `tests/test_deep_scenario_state_transitions.py`
7. `tests/test_deep_scenario_authority_boundary.py`
8. `tests/test_deep_scenario_recovery.py`
9. `docs/validation/deep-scenario-validation-report.json`

This validation layer tests:

- multi-stage review posture
- cross-layer conflict visibility
- temporal relevance
- Reflex Memory relevance and irrelevance
- recovery and de-escalation
- institutional role pressure
- non-authority preservation

It does not establish production readiness, external validation, institutional adoption, compliance readiness, audit readiness, or execution safety.

---

## Public Repo Visibility Path

Use this path to understand what belongs in the public repo and what does not.

1. `docs/governance/public-repo-visibility-standard.md`
2. `docs/governance/public-file-review-checklist.md`
3. `.github/pull_request_template.md`

The public repo should show:

- bounded proof surface
- non-authority architecture
- review-context contracts
- deterministic fixtures
- tests
- controlled R&D planning

The public repo should not expose:

- private operating memory
- unaccepted Reflex Memory candidates
- raw internal chronology
- buyer-specific notes
- pricing pressure signals
- unresolved GTM objections
- confidential allocator conversations
- security-sensitive implementation details

---

## Final Rule

This repo should make Sharpe Nova OS easier to inspect, not bigger to explain.

Public repo shows the proof surface.
Private OS preserves the operating memory.
