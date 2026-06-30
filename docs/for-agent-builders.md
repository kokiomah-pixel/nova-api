# For Agent Builders

If your agents prepare financial actions, Sharpe Nova OS helps structure the pre-execution review context before local authority acts.

Nova is not an agent runtime, wallet policy engine, payment rail, signing layer, or approval system.

Nova sits upstream.

## The Problem

Agent-prepared financial actions can move faster than institutions can review.

As agent workflows expand into treasury, payments, stablecoins, portfolio operations, custody workflows, and settlement-adjacent processes, the key problem is not only whether agents can act.

The key problem is whether the decision context is reviewable before authority is exercised.

## Nova's Role

Nova structures pre-execution review context.

It helps surface:

- source context
- constraint context
- chronology context
- exception context
- replayable evidence
- review posture

Nova does not decide whether an action proceeds.

Local authority decides.

## Correct Integration Mental Model

Do not think of Nova as:

- a plugin that approves payments
- an API that blocks transactions
- a signing policy engine
- an agent supervisor
- a compliance automation layer
- a settlement control system

Think of Nova as:

- a pre-action context layer
- a review-context formation system
- a boundary-safe governance layer before execution
- a way to make agent-prepared financial actions reviewable before local authority acts

## Phase 1

Phase 1 is an offline proof chain.

It is useful for inspection, evaluation, and boundary review.

It is not production deployment guidance.

It is not a live integration guide.

It is not market validation.

It is not buyer validation.

It is not execution infrastructure.

## Safe Next Step

Start by reading:

1. `docs/start-here.md`
2. `docs/phase_1_offline_proof_chain.md`
3. `examples/pre_execution_review/agent_prepared_financial_action_review.md`

Then inspect the harness code as offline proof infrastructure, not production runtime infrastructure.
