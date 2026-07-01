# Sharpe Nova OS

Sharpe Nova OS is a non-authority pre-execution governance review layer for agentic financial workflows. When a workflow forms an intended action but before local execution authority is exercised, Nova emits governed pre-action context that improves reviewability, reconstruction, classification consistency, source-context clarity, and authority-scope recognition without authorizing or executing the action.

This repository is the canonical Sharpe Nova OS system repo. It contains the Nova API, proof layer, governance runtime, canonical specs, tests, and runnable examples. The project has been reframed to emphasize environmental coordination, pacing normalization, and sovereignty-preserving boundaries.

## Phase 1 status

The Agent-Prepared Financial Action Review Harness has completed its Phase 1 public offline proof chain through v0.8.1.

The Phase 1 chain demonstrates offline pre-execution governance context formation for agent-prepared financial actions. It includes pre-action review, batch replay, governance-record export, chronology candidate packaging, manual acceptance, manual movement planning, chronology acceptance ledgering, lifecycle reporting, and a documented pytest verification path.

This harness is offline, boundary-safe, reportable, and test-verifiable.

It is not production readiness, market validation, buyer validation, live integration, execution infrastructure, audit reporting, compliance reporting, production audit infrastructure, automatic chronology ingestion, automatic Reflex Memory mutation, or automatic acceptance.

Canonical boundary:

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.
```

## Start Here

New readers should begin with:

- [docs/start-here.md](docs/start-here.md)
- [docs/phase_1_offline_proof_chain.md](docs/phase_1_offline_proof_chain.md)
- [docs/for-agent-builders.md](docs/for-agent-builders.md)

Sharpe Nova OS is pre-execution governance infrastructure for programmable capital systems.

Nova structures review context before local authority acts.

Nova does not execute.

## Quick Local Check

Before reading further, run one decision through Nova to observe the environmental context it emits. Nova's role is to provide a coordination context — it does not prescribe or perform execution.

### 1. Start Nova Locally

```bash
NOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

### 2. Submit One Context Request

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=allocate&asset=ETH&size=10000"
```

### 3. Read the Coordination Fields

Bind orchestration behavior to the emitted environmental context rather than treating Nova as an execution authority.

Key emitted fields (examples):

```text
coordination_state         # descriptive label of environmental posture
constraint_pressure        # summary of constraint intensity (low/medium/high)
drift_score                # derivative telemetry metric (0.0 - 1.0)
admissibility_metadata     # structured context to inform pacing/adjustment
```

Supporting fields may explain telemetry and constraint analysis. These fields are intended as conditioning inputs for upstream orchestration logic — they do not, by themselves, grant execution authority.

### 4. Retrieve Proof

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/proof/<decision_id>"
```

Proof verifies the emitted coordination context and the integrity of the derived environmental telemetry. Proof is an audit artifact, not a permission grant.

### Required Interpretation

Sharpe Nova OS provides environmental conditioning and coordination telemetry that upstream systems consume to adapt pacing and orchestration. Nova does not issue execution commands or permissions, and it does not generate trade signals.

## What Lives Here

- API implementation and runtime behavior (preserved)
- proof generation and retrieval
- governance specifications and system contracts
- tests for integrity of emitted environmental context and proof
- examples showing integration flows that consume coordination context

## What Nova Is

Sharpe Nova OS is a non-authority pre-execution governance review layer for agentic financial workflows.

It helps local operators, agents, and orchestration systems inspect governed pre-action context after an intended action has formed but before local execution authority is exercised.

## What Nova Is Not

Nova is not any of the following:

- not a trading system
- not a signal engine
- not an execution engine
- not an agent framework
- not a payment processor
- not a portfolio optimizer
- not an investment recommendation system
- not an authority layer that approves or denies execution

Consumers remain responsible for all local governance and execution decisions.

## Ten-Minute Reviewer Path

| Reviewer Question | Where To Look |
|---|---|
| What is Nova? | [docs/overview.md](docs/overview.md) |
| What does Nova emit before action? | [docs/architecture/pre-action-context-contract.md](docs/architecture/pre-action-context-contract.md) |
| How would a builder consume Nova? | [examples/pre_action_context/](examples/pre_action_context/) |
| How does Nova preserve determinism? | [docs/governance/proof-determinism-and-classification-stability.md](docs/governance/proof-determinism-and-classification-stability.md) |
| How does Nova handle continuity failures? | [docs/continuity/](docs/continuity/) |
| Why is this Phase I R&D? | [docs/grants/nsf-seed-fund/project-pitch-submission-draft.md](docs/grants/nsf-seed-fund/project-pitch-submission-draft.md) |
| What is the current direction? | [ROADMAP.md](ROADMAP.md) |

## Proof Determinism and Infrastructure Credibility

Sharpe Nova OS treats proof determinism and classification stability as infrastructure credibility requirements.

The proof layer is designed so identical normalized governance inputs produce the same canonical signature, classification path, and reproducibility hash unless a documented governance epoch, registry version, classification version, or proof schema version intentionally changes the result.

This is not a market-outcome feature.

It protects Reflex Memory chronology, institutional inspectability, governance record integrity, and environmental state reliability.

Nova does not authorize execution, move capital, provide trading signals, or optimize portfolios. It conditions the environment in which autonomous systems and operators make execution decisions locally.

## Trust Surface

Nova's trust posture is based on inspectable governance behavior, not execution performance.

Key trust surfaces include:

- classification stability
- proof reproducibility
- deterministic canonical signatures
- source segmentation
- governance chronology
- doctrine linting
- continuity under model-provider or workspace interruption

These controls support reviewability before local authority acts.

## Builder Entry Points

- Pre-Action Context Contract: [docs/architecture/pre-action-context-contract.md](docs/architecture/pre-action-context-contract.md)
- Pre-Action Context Example: [examples/pre_action_context/](examples/pre_action_context/)
- Proof Replay Example: [examples/proof_replay/](examples/proof_replay/)
- NSF Fundability Materials: [docs/grants/nsf-seed-fund/](docs/grants/nsf-seed-fund/)
- Proof Determinism Note: [docs/governance/proof-determinism-and-classification-stability.md](docs/governance/proof-determinism-and-classification-stability.md)
- Governance-Context Rot: [docs/governance/governance-context-rot.md](docs/governance/governance-context-rot.md) — defines decision-context degradation risk and explains why Nova emphasizes governed pre-action review context, chronology, source segmentation, proof reproducibility, and authority-scope recognition.
- Chronology Preservation Standard: [docs/governance/chronology-preservation-standard.md](docs/governance/chronology-preservation-standard.md)
- Chronology Review Guide: [docs/governance/chronology-review-guide.md](docs/governance/chronology-review-guide.md) — explains how reviewers should interpret chronology, source classifications, continuity gaps, and CCO-reconciled events without treating chronology as execution authority, performance history, or market validation.
- Continuity Protocols: [docs/continuity/](docs/continuity/)

## NSF Seed Fund Readiness

Sharpe Nova OS is preparing an NSF Seed Fund research and commercialization packet focused on non-authority pre-execution governance review for agentic financial workflows.

The grant-readiness materials describe the system's technical novelty, research risk, validation plan, commercialization pathway, societal impact, and non-authority boundary.

See [docs/grants/nsf-seed-fund/](docs/grants/nsf-seed-fund/).

## NSF Fundability Materials

Sharpe Nova OS maintains reviewer-facing NSF Seed Fund materials that explain the system's technical novelty, research risk, Phase I validation plan, commercialization pathway, societal impact, and non-authority boundary.

Key materials:

- [Project Pitch Draft](docs/grants/nsf-seed-fund/project-pitch-draft.md)
- [Non-Trading Positioning Memo](docs/grants/nsf-seed-fund/non-trading-positioning-memo.md)
- [Economic Value and Buyer Wedge](docs/market/economic-value-and-buyer-wedge.md)
- [Phase I Outcome Validation Plan](docs/validation/phase-i-outcome-validation-plan.md)
- [Phase I Validation Matrix](docs/grants/nsf-seed-fund/phase-i-validation-matrix.md)
- [Reviewer Risk and Response Memo](docs/grants/nsf-seed-fund/reviewer-risk-and-response.md)
- [Pre-Action Context Contract](docs/architecture/pre-action-context-contract.md)
- [Pre-Action Context Example](examples/pre_action_context/)

Sharpe Nova OS conditions the environment before execution; it does not authorize execution.

## Read Next

1. [START_HERE.md](START_HERE.md)
2. [docs/overview.md](docs/overview.md)
3. [docs/integration_entry.md](docs/integration_entry.md)
4. [docs/telemetry_reframe.md](docs/telemetry_reframe.md)
5. [docs/canonical-terminology.md](docs/canonical-terminology.md)
6. [docs/governance-epochs/epoch-2026-05-month-two.md](docs/governance-epochs/epoch-2026-05-month-two.md)
7. [specs/decision_admission_contract.json](specs/decision_admission_contract.json)

## Verification

Install local development test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run doctrine lint:

```bash
./.venv/bin/python scripts/doctrine_lint.py
```

Run the decision scenario suite:

```bash
./.venv/bin/python scripts/run_decision_scenario_suite.py
```

Run tests:

```bash
./.venv/bin/python -m pytest
```

Or, after installing the local development test dependencies:

```bash
python3 -m pytest
```

The development test dependency setup is for local verification only. It does not change harness runtime behavior.

The doctrine check blocks prohibited execution-authority wording, code-like ALLOW enforcement examples, and hidden Unicode controls. Deprecated positioning terms are surfaced as warnings for review.

## Developer Environment Integrity

Sharpe Nova OS treats developer environments as part of the infrastructure trust boundary.
Contributors should:

- use minimal, trusted editor extensions
- keep secrets out of repositories and chats
- keep `.env` files untracked
- rotate credentials after suspicious extension or tooling activity
- run doctrine/security lint before opening PRs

See [docs/security/developer-environment-integrity-protocol.md](docs/security/developer-environment-integrity-protocol.md).

## Model Provider Independence

Sharpe Nova OS preserves governance continuity without dependence on a single model provider.
OpenAI or other reasoning systems may support live interpretation, but the sovereign core of Nova lives in repository doctrine, telemetry schemas, scenario suites, chronology records, governance protocols, and tests.
If model-provider access is unavailable, operators can continue in degraded governance mode using local linting, decision-intake scenarios, offline templates, and chronology records.

## Workspace Continuity

Sharpe Nova OS treats workspace availability as part of the operating-environment trust boundary.

The canonical doctrine, chronology, governance protocols, tests, and decision-intake infrastructure are preserved in GitHub.

Workspace tools may support live operations, but they are not the sovereign core of the OS.

Workspace interruptions must be recorded as continuity events, reconciled into chronology, and reviewed for sovereignty, billing, access, and archive-risk implications.

For developer integration doctrine, see:
https://github.com/kokiomah-pixel/nova-developer-docs
