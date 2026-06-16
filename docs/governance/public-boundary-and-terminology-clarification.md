# Public Boundary and Terminology Clarification

## Purpose

This note clarifies how to read public Sharpe Nova OS repository language when older, experimental, interoperability-facing, or technical artifacts use terms that may sound adjacent to authority, execution, payment, settlement, routing, or trading systems.

The purpose is interpretation safety. This pass does not change runtime behavior and does not rename runtime files before grant submission.

## Current Canonical Boundary

Sharpe Nova OS is pre-execution environmental governance infrastructure.

Its core mechanism is pre-action context: reviewable environmental state, source-segmented records, reproducibility metadata, proof references, and governance chronology emitted before local systems decide how to act.

## Why This Matters

Public reviewers may encounter filenames, archived examples, or older integration language that mention payment-adjacent, admission-adjacent, or enforcement-adjacent concepts. Without a boundary note, those terms can create category drift and make Nova appear broader than its current doctrine.

Some historical, experimental, or interoperability-facing artifacts may contain payment-adjacent, admission-adjacent, or enforcement-adjacent terminology. These terms should not be interpreted as Nova authorizing execution, moving capital, approving payments, routing transactions, or acting as an execution system.

## Terms That Can Create Confusion

Terms that require careful interpretation include:

- admission
- enforcement
- authorization
- approval
- denial
- execution
- routing
- settlement
- payment
- x402
- trading
- portfolio optimization

These words may appear in historical materials, negative boundary statements, interoperability notes, or tests that preserve a non-authority boundary. Their presence alone should not be read as current product positioning.

## Current Interpretation Rules

In the current canonical doctrine, Nova emits pre-action context and non-authority telemetry before local systems decide how to act.

Execution, approval, denial, routing, settlement, payment, and capital movement remain outside Nova.

Current repository language should be read through these rules:

- Nova may describe environmental state before action.
- Nova may preserve reviewable governance evidence.
- Nova may support reproducible proof replay and classification stability.
- Nova may help local reviewers reconstruct workflow chronology.
- Nova must not be interpreted as the actor that approves, rejects, routes, settles, pays, trades, or executes.

## Historical / Archive Interpretation

Archived files are historical, experimental, deprecated, or non-canonical unless explicitly linked from current doctrine as active guidance.

Archive examples may preserve older terminology for continuity and traceability. They should be interpreted as historical context, not current runtime authority, integration guidance, or grant positioning.

## x402 / Payment-Adjacent Interpretation

References to x402, payment, facilitator behavior, billing, or settlement investigation are interoperability and observability context unless a current document says otherwise.

They should not be interpreted as Nova processing payments, approving payments, routing payment flows, settling transactions, or moving capital. Payment-adjacent records may be used as environmental context for local review, but local systems remain responsible for any payment, settlement, or capital movement.

## Admission / Enforcement-Adjacent Interpretation

References to admission, admissibility, enforcement, binding, or constraint behavior should be read as legacy terminology, historical adapter language, or local-consumer interpretation unless the current document explicitly defines a non-authority meaning.

Nova may emit context that local systems consume. Nova does not become the local approval authority, denial authority, execution authority, or enforcement layer.

## What Nova Does

Nova:

- emits pre-action context
- emits non-authority telemetry
- preserves reproducible governance evidence
- supports proof replay and classification stability
- records source segmentation and governance chronology
- helps reviewers inspect environmental state before local systems act

## What Nova Does Not Do

Nova does not:

- authorize execution
- approve or deny actions
- route transactions
- settle transactions
- process payments
- move capital
- execute trades
- optimize portfolios
- generate alpha
- control agents
- replace local policy, custody, compliance, orchestration, or execution systems

## Naming Watchlist

The following file or artifact names should be reviewed after grant submission for possible renaming, quarantine, or stronger archival labeling because they may create authority or payment-adjacent interpretation risk:

- `core/x402_middleware.py`
- `core/cdp_auth.py`
- `scripts/live_x402_constraint_pressure_payment.py`
- `specs/decision_admission_contract.json`
- `specs/decision_admission_rules.json`
- `archive/hyperliquid_nova_enforcement_adapter.py`

No runtime renaming is performed in this pass.

## Final Boundary

Nova conditions the environment before execution; it does not authorize execution.
