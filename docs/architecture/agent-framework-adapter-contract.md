# Agent Framework Adapter Contract

## Status

Future integration boundary note
Architecture hardening artifact
Not runtime adapter
Not framework integration
Not production claim
Not adoption evidence
Not market validation
Not buyer validation

## Purpose

This document defines how an external agent framework could pass prepared-action context to Sharpe Nova OS without adopting Nova doctrine and without receiving approval, denial, authorization, execution, compliance, audit, or wallet-control outputs.

This is a contract note.

It is not an implemented adapter.

## Canonical Boundary

Agent prepares action.
Nova structures review context.
Local authority decides.
Nova does not execute.

Execution happens elsewhere.

## Integration Principle

Agent frameworks do not need to adopt Nova doctrine.

They need to provide enough prepared-action context for Nova to structure governed review context before local authority decides.

Nova doctrine governs Nova's boundary and output.

It does not govern the entire agent runtime.

## Adapter Position

The adapter sits after action preparation and before local authority review.

```text
agent framework
-> prepared-action package
-> Nova review-context endpoint
-> governed review context
-> local authority
-> execution elsewhere
```

The adapter does not convert Nova into an agent supervisor.

The adapter does not give Nova authority.

The adapter does not execute.

## What an Agent Framework May Send

A framework may send:

```yaml
framework_sends:
  prepared_action_package:
    required: true
    examples:
      - action intent
      - asset or instrument
      - amount or size
      - proposed rail or workflow path
      - destination or counterparty if available

  source_context:
    required: true
    examples:
      - tool outputs
      - system outputs
      - user-provided inputs
      - policy references
      - market or operational context if relevant

  evidence_refs:
    required: true
    examples:
      - file references
      - system references
      - tool result IDs
      - chronology IDs if available

  authority_context:
    required: if_available
    examples:
      - required reviewer
      - approval chain outside Nova
      - escalation path
      - local authority owner

  execution_status:
    required: true
    required_value: not_executed

  framework_metadata:
    required: optional
    examples:
      - framework name
      - agent ID
      - run ID
      - task ID
      - timestamp
```

## What Nova May Return

Nova may return:

```yaml
nova_returns:
  governed_review_context:
    purpose: structured context for local authority review

  review_readiness_state:
    purpose: describes whether the prepared action has sufficient governed context for review

  source_state_context:
    purpose: classifies confirmed, incomplete, conflicting, stale, unavailable, or reconciled source context

  chronology_references:
    purpose: surfaces relevant accepted decision-state lineage if available

  reflex_memory_context:
    purpose: surfaces accepted governance memory if present and review-relevant

  temporal_state_context:
    purpose: qualifies whether Reflex Memory remains review-relevant

  proof_metadata:
    purpose: preserves reconstructability of review context

  exception_visibility:
    purpose: surfaces gaps, contradictions, missing proof, or review limitations

  authority_effect:
    required_value: none
```

## What Nova Must Not Return

Nova must not return:

```yaml
nova_must_not_return:
  - approval
  - denial
  - authorization
  - execution_instruction
  - payment_permission
  - routing_instruction
  - settlement_instruction
  - signing_instruction
  - wallet_control_instruction
  - compliance_determination
  - audit_opinion
  - trading_signal
  - portfolio_recommendation
  - agent_supervision_command
```

## Minimal Adapter Contract

A minimal adapter contract should preserve:

```yaml
minimal_adapter_contract:
  input:
    prepared_action_package: required
    source_context: required
    evidence_refs: required
    execution_status: not_executed

  output:
    governed_review_context: required
    review_readiness_state: required
    authority_effect: none
    non_authority_statement: required
```

## Framework-Neutral Memory Boundary

Reflex Memory may appear in Nova output as review context.

It does not become framework memory automatically.

The framework may receive Reflex Memory context, but that does not mean the framework owns, mutates, accepts, rejects, or updates Reflex Memory.

Safe rule:

```text
The framework prepares action context.
Nova structures governed review context.
Local authority decides.
Accepted governance memory remains governed by Nova's Reflex Memory lifecycle.
```

## Doctrine Independence

External frameworks do not need to adopt Nova doctrine internally.

They only need to respect the Nova integration boundary:

```yaml
nova_boundary_requirements:
  prepared_action_before_nova: required
  execution_status_not_executed: required
  local_authority_after_nova: required
  no_nova_execution: required
  no_nova_authority: required
```

If a framework expects Nova to approve, deny, authorize, block, route, settle, sign, supervise, or execute, the integration is out of scope.

## Example Flow

```text
LangGraph, CrewAI, OpenAI Agents, AutoGen, or another framework prepares an action.
v
Adapter packages prepared action, source context, evidence references, and execution_status: not_executed.
v
Nova receives package.
v
Nova structures governed review context.
v
Nova may surface source-state limitations, chronology, Reflex Memory, temporal-state context, proof metadata, and exception visibility.
v
Local authority decides.
v
Execution happens outside Nova.
```

This example is illustrative.

It is not a claim that any framework integration is implemented.

## Current Implementation Status

```yaml
implementation_status:
  adapter_standard: described
  runtime_adapter: not_implemented
  framework_tests: not_implemented
  production_integration: not_claimed
  external_validation: not_claimed
```

## Safe Language

Use:

```text
Agent frameworks can prepare action context for Nova review.
```

Use:

```text
Nova returns governed review context, not authority.
```

Use:

```text
Framework adapters should preserve execution_status: not_executed.
```

Use:

```text
External frameworks do not need to adopt Nova doctrine; they need to respect Nova's boundary.
```

## Unsafe Language

Do not say:

```text
Nova supervises agent frameworks.
```

Do not say:

```text
Nova manages agent authority.
```

Do not say:

```text
Nova approves agent actions.
```

Do not say:

```text
Nova blocks unsafe agent actions.
```

Do not say:

```text
Nova controls framework execution.
```

Do not say:

```text
Nova is an agent orchestration layer.
```

Do not say:

```text
Nova memory becomes the framework memory.
```

## Final Rule

The adapter boundary is simple:

Agent prepares action.

Nova structures governed review context.

Local authority decides.

Execution happens elsewhere.
