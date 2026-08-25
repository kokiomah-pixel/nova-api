# Sharpe Nova OS

Sharpe Nova OS preserves governed review context for agent-prepared financial
actions before local authority acts.

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## The problem

A transaction system can preserve what ultimately moved while the institution
loses the exact review state that informed the decision.

When a proposal changes, the institution may need to reconstruct:

* which version local authority reviewed;
* which sources were authoritative;
* when each source was observed;
* which assumptions and constraints applied;
* what was missing, stale, conflicting, or unresolved.

Nova is designed to preserve that review context before execution.

## First bounded workflow

The first bounded workflow is an agent-prepared stablecoin treasury action.

Nova structures the review package around the proposed action. Local authority
decides whether and how the institution proceeds. External systems remain
responsible for execution.

Nova does not approve, authorize, sign, settle, or move capital.

## Current state

* Legacy v1 is implemented but is not the canonical future external model.
* New external integrations against Legacy v1 admission semantics are prohibited.
* The target v2 non-authority review-context contract is canonical at design-v2.1.
* The private synthetic target-v2 reference adapter is implemented; it has no
  runtime, public-endpoint, production, or authority effect.
* The target v2 runtime is not implemented and target v2 is not production-active.
* Phase 1 is an offline, repository-validated proof chain.
* Production readiness, institutional use, buyer validation, and adoption are
  not established.

Read the authoritative current-state summary:

* [Current State](CURRENT_STATE.md)

## Start here

1. [Current State](CURRENT_STATE.md)
2. [Start Here](docs/start-here.md)
3. [Target v2](docs/target-v2/README.md)
4. [First Use Case](docs/go-to-market/first-use-case-agent-prepared-treasury-action.md)
5. [Production Readiness](docs/operations/production-readiness-register.md)

## Product generations

* [Legacy v1](docs/legacy-v1/README.md)
* [Target v2](docs/target-v2/README.md)

## What Nova is not

Nova is not a trading system, execution engine, agent framework, payment
processor, wallet, portfolio optimizer, investment recommendation system, or
authority layer. Local institutions remain responsible for every decision and
external action.

## What is not claimed

Repository artifacts and passing tests do not establish:

* current production custody or deployment identity;
* target v2 runtime implementation or production activation;
* institutional use or operator dependency;
* buyer or market validation;
* adoption or product-market fit;
* pricing power or marketplace authority;
* production payment or settlement activity.

Gate-level evidence and limitations are maintained in the
[Production Readiness Register](docs/operations/production-readiness-register.md).

## Architecture and governance

The deeper internal frame is that Sharpe Nova OS is a pre-execution decision
discipline layer that conditions capital through telemetry, Reflex Memory, and
constraint logic before execution. These concepts describe internal
architecture and do not change Nova's non-authority boundary.

Key references:

* [External review-context contract v2](docs/architecture/external-review-context-contract-v2.md)
* [Pre-action context contract](docs/architecture/pre-action-context-contract.md)
* [Governed context flow](docs/architecture/governed-context-flow.md)
* [Review-context state and portability](docs/architecture/review-context-state-and-portability-specification.md)
* [Review completeness standard](docs/governance/review-completeness-standard.md)
* [Source-state taxonomy](docs/governance/source-state-taxonomy.md)
* [Proof determinism and classification stability](docs/governance/proof-determinism-and-classification-stability.md)
* [Institution-owned governance chronology](docs/governance/institution-owned-governance-chronology.md)
* [Reflex Memory specification](docs/governance/reflex-memory-specification.md)
* [Continuity protocols](docs/continuity/)

## Legacy v1 inspection

The implemented Legacy v1 runtime is preserved for dependency inspection,
migration analysis, historical integrity, and existing test coverage. Its
local inspection commands are intentionally separated from the default reader
path:

* [Legacy v1 local inspection](docs/legacy-v1/quickstart.md)
* [Legacy v1 isolation plan](docs/migrations/v1-admission-isolation-plan.md)
* [Historical March 2026 project report](docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md)

Legacy v1 implementation does not establish target v2 implementation or
current production custody.

## Proof and inspection

Phase 1 provides an offline proof chain for pre-action review, replay,
governance-record export, manual acceptance and movement planning, chronology
candidate packaging, lifecycle reporting, and deterministic repository tests.

It does not establish deployed integration, production readiness, market or
buyer validation, operator dependency, institutional adoption, audit or
compliance readiness, or automatic acceptance and memory mutation.

Review:

* [Phase 1 inspection status](docs/inspection/phase-1-inspection-status.md)
* [Phase 1 offline proof chain](docs/phase_1_offline_proof_chain.md)
* [Reviewer paths](docs/reviewer-paths.md)
* [Technical evidence map](docs/validation/technical-evidence-map.md)
* [Pre-action context example](examples/pre_action_context/)
* [Proof replay example](examples/proof_replay/)

## Operator and GTM research

Nova's proposed differentiation is a hypothesis about a residual
review-context gap, not proof that existing financial controls lack comparable
capabilities.

* [System-class comparator](docs/go-to-market/system-class-comparator.md)
* [Where Nova sits](docs/go-to-market/where-nova-sits.md)
* [First use case](docs/go-to-market/first-use-case-agent-prepared-treasury-action.md)
* [Treasury operator discovery template](docs/go-to-market/treasury-operator-discovery-template.md)
* [GTM comprehension test protocol](docs/go-to-market/gtm-comprehension-test-protocol.md)
* [Commercialization sequence](docs/go-to-market/commercialization-sequence.md)

## Research and grants

The NSF Seed Fund materials describe a research and commercialization case.
They are not current production, buyer, adoption, or product-market evidence.

* [NSF Seed Fund materials](docs/grants/nsf-seed-fund/)
* [Project pitch draft](docs/grants/nsf-seed-fund/project-pitch-draft.md)
* [Technical novelty](docs/grants/nsf-seed-fund/technical-novelty.md)
* [Phase I validation matrix](docs/grants/nsf-seed-fund/phase-i-validation-matrix.md)
* [Reviewer risk and response](docs/grants/nsf-seed-fund/reviewer-risk-and-response.md)

## Historical Legacy v1 references

Older environmental telemetry, decision-admission, metering, and epoch
materials describe Legacy v1 behavior. Read them through the generation
boundary in [Legacy v1](docs/legacy-v1/README.md).

* [Legacy integration entry](docs/integration_entry.md)
* [Telemetry reframe](docs/telemetry_reframe.md)
* [Canonical terminology](docs/canonical-terminology.md)
* [Decision-admission contract](specs/decision_admission_contract.json)

## Verification

Create the canonical repository environment and install local development test
dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

Run the canonical repository verification:

```bash
make verify
```

The verification chain includes doctrine, scenarios, tests, chronology,
whitespace, and public-surface coherence checks. The repository `.venv` is the
canonical local validation environment.

## Developer environment and continuity

Contributors should use minimal trusted tooling, keep secrets and environment
files untracked, rotate credentials after suspicious tooling activity, and run
the canonical verification before opening a pull request.

* [Developer environment integrity](docs/security/developer-environment-integrity-protocol.md)
* [Workspace continuity](docs/continuity/)
* [Public-surface coherence standard](docs/operations/public-surface-coherence-standard.md)
* [Public file review checklist](docs/governance/public-file-review-checklist.md)
