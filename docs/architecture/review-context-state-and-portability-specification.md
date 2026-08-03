# Review-Context State and Portability Specification

## Status

```yaml
specification:
  status: proposed_for_architectural_review
  decision_reference: CCO-MARKET-2026-08-02-001
  runtime_implementation: not_authorized
  production_effect: none
```

## Purpose

Define the institution-owned review-context objects that must remain interpretable across model, harness, gateway, wallet, risk-provider, custodian, and execution-provider changes.

## State ownership

```yaml
state_ownership:
  transport_state:
    owner: protocol_or_gateway

  working_context:
    owner: agent_or_harness

  workflow_state:
    owner: application_or_orchestrator

  governance_state:
    owner: institution
    Nova_role: structure_and_preserve_review_context
```

Nova is not a generic stateful agent service. Governance state must survive replaceable transport and workflow components.

## Stable action identity

```yaml
action_identity:
  action_id:
  action_class:
  proposal_version:
  originating_system:
  created_at:
  current_review_reference:
```

A technical retry, materially revised proposal, and authority reconsideration are distinct institutional events even when their transport requests look similar.

## Versioned review snapshots

```yaml
review_snapshot:
  review_state_id:
  review_state_version:
  action_reference:
  evidence_snapshot_reference:
  constraint_set_reference:
  external_result_references: []
  chronology_reference:
  created_at:
  supersedes:
```

A snapshot records review context at a specific time. It is not approval, authorization, or execution entitlement.

## External-system result

```yaml
external_system_result:
  provider:
  system_type:
  result:
  evidence_supplied: []
  assumptions_disclosed: []
  observed_at:
  institutionally_authoritative: false
  authority_effect: none
  execution_effect: none
```

Nova preserves what specialized systems concluded without inheriting their authority.

## Authority override and disagreement history

Preserve cases where local authority:

- rejects an external approval;
- requests additional evidence;
- narrows an agent proposal;
- interprets a policy differently;
- refuses to treat a verified source as institutionally authoritative; or
- defers because absence or contradiction remains material.

## Absence as a first-class state

```yaml
absence_state:
  current_source_available:
  independent_corroboration_available:
  active_delegation_available:
  comparable_precedent_available:
  contradiction_resolved:
  temporal_state_certain:
```

Absence must be explicit rather than silently replaced by inference.

## Material contribution filter

Retain by default:

- material claims;
- source provenance;
- constraint application;
- unresolved conflicts;
- authority interpretation;
- decisions or overrides; and
- outcomes relevant to later review.

Exclude by default:

- agent scratch work;
- redundant tool calls;
- intermediate plans;
- low-level transport logs; and
- unbounded reasoning traces.

## Portability requirements

```yaml
portability_requirements:
  institution_controlled_export: required
  stable_action_identity: required
  versioned_review_snapshots: required
  contribution_provenance: required
  bounded_persistence: required
  chain_of_material_transformation: required
  semantic_interpretability_after_migration: required
```

## Promotion gates

This specification may move toward implementation only after bounded operator evidence identifies:

- a recurring action class;
- the review owner and local authority;
- required source and constraint relationships;
- portability or reconstruction friction;
- a measurable benefit from prior chronology; and
- approved information-governance controls.

No endpoint, database migration, MCP server, graph database, or production integration is authorized by this document.
