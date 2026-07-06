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
6. `examples/pre_action_context/`
7. `docs/architecture/review-context-loop.md`
8. `examples/agent_prepared_action/`
9. `core/reflex_memory/context.py`
10. `core/reflex_memory/replay.py`
11. `fixtures/reflex_memory/`
12. `schemas/reflex_memory/`
13. `tests/test_agent_prepared_action_example.py`
14. `tests/test_reflex_memory_v0_1.py`
15. `tests/test_reflex_memory_loader.py`
16. `tests/test_reflex_memory_context_endpoint.py`
17. `tests/test_reflex_memory_legacy_semantics_cleanup.py`
18. `tests/test_reflex_memory_multi_scenario.py`
19. `tests/test_reflex_memory_schema_validation.py`
20. `tests/test_reflex_memory_replay.py`
21. `docs/validation/technical-evidence-map.md`

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
3. `docs/governance/source-state-taxonomy.md`
4. `docs/governance/reflex-memory-v0-1-fixture.md`
5. `docs/grants/nsf-seed-fund/reflex-memory-rd-plan.md`
6. `fixtures/reflex_memory/`
7. `schemas/reflex_memory/`
8. `core/reflex_memory/context.py`
9. `core/reflex_memory/replay.py`
10. `tests/test_reflex_memory_v0_1.py`
11. `tests/test_reflex_memory_loader.py`
12. `tests/test_reflex_memory_context_endpoint.py`
13. `tests/test_reflex_memory_legacy_semantics_cleanup.py`
14. `tests/test_reflex_memory_multi_scenario.py`
15. `tests/test_reflex_memory_schema_validation.py`
16. `tests/test_reflex_memory_replay.py`

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
