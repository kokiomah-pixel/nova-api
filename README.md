# Sharpe Nova OS

Sharpe Nova OS is a pre-execution environmental governance layer that emits derivative environmental context to condition upstream execution environments before capital moves.

This repository is the canonical Sharpe Nova OS system repo. It contains the Nova API, proof layer, governance runtime, canonical specs, tests, and runnable examples. The project has been reframed to emphasize environmental coordination, pacing normalization, and sovereignty-preserving boundaries.

## Start Here (Required)

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

## What Nova Is Not

Nova is not an execution engine, strategy system, signal engine, or order execution middleware. It does not move capital or prescribe execution steps. Instead, Nova emits admissibility environments, pacing conditions, and coordination-state telemetry for integrators to use within their orchestration systems.

## Proof Determinism and Infrastructure Credibility

Sharpe Nova OS treats proof determinism and classification stability as infrastructure credibility requirements.

The proof layer is designed so identical normalized governance inputs produce the same canonical signature, classification path, and reproducibility hash unless a documented governance epoch, registry version, classification version, or proof schema version intentionally changes the result.

This is not a market-outcome feature.

It protects Reflex Memory chronology, institutional inspectability, governance record integrity, and environmental state reliability.

Nova does not authorize execution, move capital, provide trading signals, or optimize portfolios. It conditions the environment in which autonomous systems and operators make execution decisions locally.

## Builder Entry Points

- Pre-Action Context Contract: [docs/architecture/pre-action-context-contract.md](docs/architecture/pre-action-context-contract.md)
- Pre-Action Context Example: [examples/pre_action_context/](examples/pre_action_context/)
- Proof Replay Example: [examples/proof_replay/](examples/proof_replay/)
- NSF Fundability Materials: [docs/grants/nsf-seed-fund/](docs/grants/nsf-seed-fund/)
- Proof Determinism Note: [docs/governance/proof-determinism-and-classification-stability.md](docs/governance/proof-determinism-and-classification-stability.md)
- Continuity Protocols: [docs/continuity/](docs/continuity/)

## NSF Seed Fund Readiness

Sharpe Nova OS is preparing an NSF Seed Fund research and commercialization packet focused on pre-execution environmental governance for autonomous capital systems.

The grant-readiness materials describe the system's technical novelty, research risk, validation plan, commercialization pathway, and societal impact.

See [docs/grants/nsf-seed-fund/](docs/grants/nsf-seed-fund/).

## NSF Fundability Materials

Sharpe Nova OS maintains reviewer-facing NSF Seed Fund materials that explain the system's technical novelty, research risk, Phase I validation plan, commercialization pathway, societal impact, and non-trading boundary.

Key materials:

- [Project Pitch Draft](docs/grants/nsf-seed-fund/project-pitch-draft.md)
- [Non-Trading Positioning Memo](docs/grants/nsf-seed-fund/non-trading-positioning-memo.md)
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

## Doctrine Consistency Check

Run the doctrine lint before changing canonical docs or examples:

```bash
./.venv/bin/python scripts/doctrine_lint.py
```

The check blocks prohibited execution-authority wording, code-like ALLOW enforcement examples, and hidden Unicode controls. Deprecated positioning terms are surfaced as warnings for review.

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
