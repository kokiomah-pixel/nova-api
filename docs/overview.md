# Overview

Sharpe Nova OS is the canonical control-plane interface for pre-execution decision admissibility.

It exists to define whether a proposed capital action is admissible before execution by returning an authoritative decision state over a machine-readable API.

The interaction surface is two-step:

- `/v1/context` returns a Decision Admission Record and `decision_id`
- `/v1/proof/{decision_id}` verifies the governed decision state

## What the System Does

- receives a proposed decision
- evaluates admissibility under current constraints
- returns a binding decision state for downstream systems
- provides verifiable proof of the governed state

## What the System Does Not Do

- generate trades
- optimize strategy
- execute orders
- produce bypassable risk signals
- act as a generic toolkit

## Core Model

Sharpe Nova OS is denial-first.

The system is designed so that:

- refusal states are explicit
- governance layers are visible
- downstream systems inherit discipline through the API contract
- execution proceeds only after decision admission

## Authority Model

- `decision_status` is authoritative.
- Supporting fields explain the state.
- Proof verifies the governed state.
- No derived field overrides decision authority.
