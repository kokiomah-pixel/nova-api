# Target v2 — Non-Authority Review Context

## Status

```yaml
target_v2:
  canonical_future_external_model: true
  contract_approved: true
  canonicality_source: authoritative_repository_main
  field_derivation_complete: true
  runtime_implemented: false
  private_adapter_implemented: false
  Gate_4_status: not_authorized
  production_active: false
  institutional_pilot_started: false
```

Target v2 is the canonical future Sharpe Nova OS external contract.

It is designed to structure governed review context around an agent-prepared
financial action before local authority acts.

```text
Agent prepares an action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Target output responsibility

Target v2 should make the following review state inspectable:

* action identity;
* proposal-version identity;
* source identity and authority;
* observation time;
* constraint context;
* missing information;
* stale information;
* conflicting information;
* unavailable information;
* local-authority boundary;
* context-integrity and reconstruction information.

## Prohibited authority behavior

Target v2 must not return or imply:

* approval;
* authorization;
* permission;
* admission;
* execution instruction;
* signing authority;
* settlement authority;
* wallet control;
* capital movement authority.

## First bounded workflow

The first bounded workflow is an agent-prepared stablecoin treasury action
before local authority review.

The workflow exists as a bounded specification and offline demonstration
surface.

A deployed target v2 workflow has not yet been established.

## Progression gates

1. Production custody attestation.
2. Legacy v1 dependency inventory.
3. Target v2 field-derivation rules.
4. Private synthetic adapter.
5. Bounded operator rehearsal.
6. Controlled private production candidate.
7. Bounded institutional pilot.
8. Commercial and distribution validation.

No later gate becomes active merely because an earlier artifact exists.

Gate 3 design completion does not activate Gate 4. The `design-v2.1` contract
revision creates no runtime, private-adapter, endpoint, deployment,
payment, settlement, or execution authority.

## References

* [External review-context contract v2](../architecture/external-review-context-contract-v2.md)
* [Pre-action context contract](../architecture/pre-action-context-contract.md)
* [Legacy v1 admission isolation plan](../migrations/v1-admission-isolation-plan.md)
* [First bounded workflow](../go-to-market/first-use-case-agent-prepared-treasury-action.md)
* [Production readiness register](../operations/production-readiness-register.md)
