# Model Provider Independence Protocol

## Purpose

Sharpe Nova OS preserves governance continuity without depending on any single model provider, chat account, API key, or hosted reasoning interface.

GitHub repository history is the durable archive for Nova doctrine, telemetry schemas, decision-intake scenario logic, Reflex Memory chronology, governance protocols, security protocols, x402 observability, audit artifacts, tests, and offline operator procedures.

OpenAI and other model providers may support live reasoning, drafting, interpretation, and conversational operation. They are optional reasoning interfaces. They are not the sovereign core of Sharpe Nova OS.

The May 25 to June 11, 2026 Business workspace deactivation confirmed why model-provider independence and workspace continuity must be treated as separate but related continuity layers.

Model-provider independence protects reasoning continuity.

Workspace continuity protects operating-environment availability.

## Continuity Principle

The sovereign core remains in repository-controlled artifacts:

- canonical doctrine
- telemetry schemas
- Reflex Memory chronology
- decision-intake scenario suites
- governance protocols
- security linting
- x402 observability records
- audit artifacts
- offline operator procedures
- test infrastructure

If OpenAI access is unavailable, live reasoning may degrade, but Nova's infrastructure layer must remain operational. The Architect can continue using deterministic decision-intake workflows, local doctrine, offline templates, chronology logs, and governance checklists.

## Mode 1 - Full Reasoning Mode

OpenAI or another reasoning provider is available.

Capabilities:

- live analysis
- artifact drafting
- scenario expansion
- strategic interpretation
- conversational Jarvis-Nova interface

Operating posture:

- reasoning output is advisory and must remain inside Nova's governance boundaries
- model-generated material should be reviewed against canonical doctrine
- repository artifacts remain the source of continuity

## Mode 2 - Degraded Governance Mode

OpenAI is unavailable, but repo tooling works.

Capabilities:

- doctrine and security linting
- decision scenario runner
- deterministic risk classification
- chronology logs
- governance protocols
- offline review templates
- test suite validation

Limitations:

- no live model-generated analysis
- no automatic narrative synthesis
- no conversational reasoning layer

Operating posture:

- run local lint, scenario, and test commands before changing doctrine or governance artifacts
- record decisions and environmental pressure in chronology artifacts
- use offline decision-intake templates for operator review
- preserve the boundary that Nova emits environmental governance context and does not move capital

## Mode 3 - Sovereign Continuity Mode

No external model provider is available.

Capabilities:

- manual Architect review
- offline decision-intake templates
- local doctrine documents
- local scenario library
- chronology recording
- governance checklists
- security protocols

Purpose:

Preserve Sharpe Nova OS even without live AI assistance.

Operating posture:

- treat repository history and local files as the continuity substrate
- capture operator decisions in chronology records
- apply governance checklists before changing canonical doctrine
- defer live narrative synthesis until a reasoning interface is available again

## Required Local Validation

Use these commands to validate continuity in Mode 2:

```bash
./.venv/bin/python scripts/doctrine_lint.py
./.venv/bin/python scripts/run_decision_scenario_suite.py
./.venv/bin/python -m pytest
git diff --check
```

Expected continuity result:

- doctrine and security lint pass
- decision scenario suite passes
- full test suite passes
- no core governance path requires OpenAI access
- no core test requires OpenAI access

## Boundary Statement

Sharpe Nova OS may use model providers for live reasoning, but it must never depend on one provider for the preservation of operating doctrine. Nova continuity lives in doctrine, telemetry, chronology, tests, scenario logic, governance protocol, and disciplined repository history.
