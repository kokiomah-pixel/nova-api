# OpenAI Workspace Agent Integration

OpenAI workspace agents may propose actions.

Nova emits pre-action context before any local system decides whether capital-moving execution should occur.

Nova remains external, model-agnostic, and non-authority.

## Required Flow

Agent -> Decision Proposal -> Nova -> Pre-Action Context -> Local Decision

## Rules

- Agent should call `/v1/context` before local execution decisions
- `decision_status` is context for local governance review
- Agent may not treat its own reasoning as permission
- Agent may retrieve `/v1/proof/{decision_id}` when proof-backed verification is required
- Refusal states should be escalated through local governance rules

## Outcome Handling

ALLOW -> inspect and decide locally
CONSTRAIN -> inspect conditioned context before acting
DENY / DELAY / HALT / VETO -> delay, escalate, cancel, or apply local governance rules
