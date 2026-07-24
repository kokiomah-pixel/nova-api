# Agent-Prepared Stablecoin Treasury Integration Path

## Status

Architecture and integration-path artifact
Bounded design specification
Discovery and operator-onboarding support
Not runtime implementation
Not production integration
Not adoption evidence
Not authorization logic
Not execution logic

## Purpose

This artifact makes one specific workflow concrete:

```text
agent-prepared stablecoin treasury action
→ Nova-structured review context
→ local authority decision
→ external execution
```

It is a bounded profile of the existing [Pre-Action Context Contract](pre-action-context-contract.md). The envelopes below are conceptual design vocabulary, not a second canonical contract, a new endpoint, or current runtime behavior.

## Canonical Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

Adjacent systems determine how agents operate, who may act, and how value can move.

Nova structures and evaluates the institution-defined review context presented to local authority before it decides.

Nova does not determine whether capital should move.

## Workflow

```text
Agent or managed runtime
prepares a proposed treasury action
        |
        v
Identity / authorization / wallet-policy systems
provide actor, delegated-scope, and policy state
        |
        v
Sharpe Nova OS
structures evidence, source state, constraints,
contradictions, chronology, and temporal context
        |
        v
Local institutional authority
reviews and decides
        |
        v
External wallet / custodian / payment rail
signs, routes, settles, or executes
        |
        v
Accepted governance record may enter chronology
under separate acceptance discipline
```

Nova does not control any downstream execution system.
Nova does not convert review readiness into authorization.
Nova does not automatically write the review event into chronology.

## Integration Questions

### 1. What prepares the action?

An agent or managed runtime prepares a proposed stablecoin treasury action. The preparing system owns its sessions, tools, memory, scheduling, and action-generation behavior. Nova does not control the agent or runtime.

### 2. What systems establish identity and permissions?

Institution-controlled identity, credential, delegation, authorization, and wallet-policy systems establish who may act and within what limits. Nova does not originate identities, manage credentials, grant delegated scope, or enforce wallet policy.

### 3. What information is provided to Nova?

The supplied package may include the proposed action, preparation context, evidence sources, source-authority rules, pending activity, contradictions, operational references, external policy results, institutional constraints, required evidence, and prior related decisions.

### 4. What does Nova structure?

Nova structures evidence visibility, source state, constraints, unresolved contradictions, relevant chronology, proof and replay references, review completeness, temporal context, and the local-authority handoff.

### 5. What does Nova emit?

Nova emits a review-context packet. The packet makes missing, stale, conflicting, unavailable, or superseded context visible. It is not a recommendation, approval, denial, authorization, execution instruction, or certification of review sufficiency.

### 6. Who receives the output?

Local institutional authority or an institution-controlled review workflow receives the packet. Authorized reviewers may inspect it before local authority decides.

### 7. What does local authority decide?

Local authority decides whether the institution should proceed, refuse, escalate, narrow the action, or request updated context under its own rules. Nova does not make that decision.

### 8. Which systems execute outside Nova?

External wallets, custodians, signing systems, treasury systems, payment rails, routing systems, settlement systems, and other institution-controlled infrastructure perform any downstream action. Nova does not operate those systems.

### 9. What may later enter chronology?

An accepted governance record may later enter chronology under separate acceptance discipline. The prepared action, Nova packet, review event, or external execution record does not enter chronology automatically.

### 10. What does Nova never do?

Nova does not approve, deny, authorize, block, route, sign, settle, execute, control agents, manage credentials, manage wallets, make compliance determinations, certify review sufficiency, replace local authority, or determine whether capital should move.

## Conceptual Input Envelope

The following is a non-runtime conceptual example. It does not describe a JSON request body or change `/v1/context`.

```yaml
proposed_action_package:
  action:
    action_id:
    action_type: stablecoin_treasury_movement
    action_description:
    asset:
    amount:
    source_account_reference:
    destination_reference:
    intended_execution_window:

  preparation_context:
    preparing_system:
    preparing_agent_reference:
    runtime_reference:
    session_reference:
    prepared_at:
    assumptions: []
    unresolved_questions: []

  evidence_context:
    sources: []
    source_authority_rules: []
    known_pending_activity: []
    known_contradictions: []
    missing_evidence: []

  operational_context:
    actor_identity_reference:
    delegated_scope_reference:
    wallet_or_account_reference:
    external_policy_results: []
    transaction_limit_context:
    external_authorization_state:

  institutional_context:
    applicable_constraints: []
    required_review_evidence: []
    prior_related_decisions: []
    local_authority_role:
```

Identity, delegated scope, wallet-policy results, and external authorization state are review inputs.

Nova does not originate or enforce them.

## Conceptual Output Envelope

The following packet is a conceptual interface illustration, not an implemented runtime schema.

```yaml
review_context_packet:
  review_context_id:
  action_reference:

  review_completeness:
    state:
      - complete_for_review
      - incomplete_but_visible
      - blocked_for_review_context
    missing_context: []
    unresolved_questions: []

  source_state:
    authoritative_sources: []
    non_authoritative_sources: []
    stale_sources: []
    unavailable_sources: []
    conflicting_sources: []

  constraint_context:
    applicable_constraints: []
    unresolved_constraint_questions: []
    exception_visibility: []

  contradiction_context:
    unresolved_contradictions: []
    Nova_selected_winning_source: false

  chronology_context:
    prior_related_records: []
    chronology_gaps: []
    automatic_chronology_write: false

  temporal_context:
    status:
      - current
      - uncertain
      - stale
      - superseded
    reasons: []
    institution_defined_conditions: []
    revalidation_context_required:

  authority_handoff:
    local_authority_required: true
    decision_owner:
    Nova_recommendation: false
    Nova_approval: false
    Nova_denial: false
    Nova_authorization: false
    Nova_execution: false

  proof_and_replay:
    source_references: []
    schema_reference:
    reproducibility_reference:

  explicit_non_outputs:
    transaction_authorization: prohibited
    approval_or_rejection_decision: prohibited
    execution_instruction: prohibited
    wallet_signature: prohibited
    routing_instruction: prohibited
    settlement_instruction: prohibited
```

## Temporal Context

Nova may report that the previously structured review context no longer satisfies institution-defined temporal conditions for the prepared action.

This means Nova can surface observed times, pending state, temporal conflicts, evidence-age conditions, and newer material evidence as review context. It does not mean Nova expired an approval, blocked a transaction, revoked authorization, prevented execution, or continuously monitored external state.

Temporal context remains a bounded discovery concept. This artifact does not add an expiration service, scheduler, market-surveillance process, transaction monitor, automatic authorization-revocation mechanism, execution blocker, API implementation, or production schema.

## Synthetic Scenario

At `2026-07-23T14:00:00Z`, an agent prepares a proposed movement of `250,000` synthetic USDC units from a treasury account reference to a synthetic custody account reference.

A wallet-policy snapshot is observed at `13:42:00Z`. A custody ledger is observed later at `13:51:00Z`. The custody ledger reports known pending outbound activity that changes the available position, while the earlier wallet snapshot reports a different available balance. The intended execution window begins at `14:30:00Z`, after both observations.

The institution has supplied a condition that evidence used for this action class should be no more than 20 minutes old at the start of the intended execution window, and that known pending activity must be represented. Nova surfaces:

- different observation times;
- the pending activity;
- the unresolved available-position conflict;
- temporal uncertainty at the intended execution window; and
- the institution-defined evidence-age condition.

Nova does not select the authoritative source and does not decide whether the movement should occur. Local authority decides whether updated context is needed before it makes its institutional decision.

This scenario uses invented identifiers only. It contains no client data, wallet addresses, transfer instructions, transaction-signing material, or production claims. A structured version appears in [the synthetic stablecoin treasury example](../../examples/pre_action_context/agent_prepared_stablecoin_treasury_action.yaml).

## Final Boundary

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```
