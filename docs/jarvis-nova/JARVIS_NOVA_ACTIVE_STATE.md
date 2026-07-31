# Jarvis-Nova Active State Manifest

## State metadata

```yaml
state_manifest:
  version: 1.0
  prepared_by_context: V005
  intended_successor_context: V006
  prepared_at: 2026-07-30

  minimum_repository_baseline:
    commit: 91327075ace338fddec0e681f437b8778f7c122e
    source: PR_24_merge

  current_state_guaranteed_indefinitely: false
  verification_required_before_mutation: true
```

This manifest is a transfer aid.

It is not a substitute for repository, pull-request, or production verification.

## Canonical Nova frame

> Sharpe Nova OS is a pre-execution decision discipline layer that conditions
> capital through telemetry, Reflex Memory, and constraint logic before
> execution.

```text
Agent prepares action.
Nova structures review context.
Local authority decides.
External systems execute.
Nova does not execute.
```

## Accepted architectural boundaries

```yaml
accepted_boundaries:
  Nova_is_not:
    - trading_system
    - signal_engine
    - prediction_layer
    - portfolio_optimizer
    - execution_layer
    - approval_authority
    - payment_gateway
    - wallet_policy_engine
    - generic_retail_intelligence_API

  public_discovery:
    status: specification_only
    callable: false
    authorized_for_publication: false

  retail_agent_service:
    status: not_authorized
    separate_business_case_required: true
    separate_data_plane_required: true

  institutional_review_context:
    access:
      - private
      - authenticated
      - tenant_scoped
      - workflow_authorized
    marketplace_payment_sufficient: false
```

## Recent canonical repository decisions

### Payment custody remediation

```yaml
payment_remediation:
  source_PR: 22
  source_commit: cd4f538c988edda067ccce02c2f6c4e793b7c5fe
  accepted_state:
    personal_payment_destination_removed: true
    public_x402_enabled: false
    settlement_enabled: false
    payment_credentials_present: false
```

### Fastly x402 evidence

```yaml
Fastly_signal:
  source_PR: 23
  merge_commit: fb2d9a1421a010645643d93b186c9875e09f1cc2
  evidence_id: MSE-2026-07-30-028
  disposition:
    specification_refinement: approved
    operator_research: approved
    market_monitoring: approved
    x402_engineering: not_authorized
```

### Circle marketplace and access separation

```yaml
Circle_signal:
  source_PR: 24
  merge_commit: 91327075ace338fddec0e681f437b8778f7c122e
  evidence_id: MSE-2026-07-30-029
  disposition:
    marketplace_preflight: approved
    three_access_class_architecture: canonical
    retail_institutional_separation: canonical
    public_listing: not_authorized
    retail_service: not_authorized
    Circle_runtime_integration: not_authorized
```

## Last known production posture

```yaml
production_posture:
  status_type: last_known_attested_state
  must_be_reverified_before_operational_claims: true

  public_API_documentation: disabled
  public_service_discovery: disabled
  public_x402: disabled
  payment_settlement: disabled
  payment_destination: absent
  settlement_wallet: absent
  CDP_credentials: absent
  EOA_private_key: absent
```

Do not claim this remains current without verification.

## Current non-authorizations

```yaml
not_authorized:
  - public_Circle_listing
  - public_Nova_manifest
  - public_v1_context
  - retail_access_to_v1_context
  - retail_Nova_service
  - Circle_specific_endpoint
  - x402_payment_for_Nova
  - wallet_or_settlement_reintroduction
  - payment_as_institutional_authentication
  - shared_retail_and_institutional_data_plane
  - shared_retail_and_institutional_chronology
  - cross_plane_Reflex_Memory
```

## Current strategic hypotheses

These remain unvalidated:

- operators may require public discovery with private invocation;
- institutions may require approved agent-service catalogs;
- contract-backed metering may become useful after enterprise agreement;
- institution-owned chronology may become a strong cross-provider dependency;
- one recurring high-consequence treasury workflow may become Nova's initial
  wedge.

## Current monitoring priorities

- private or organization-scoped agent-service listings;
- enterprise identity binding;
- confidential machine invocation;
- contract-backed metering;
- tenant isolation;
- marketplace claims around decision chronology or authority handoff;
- operator inability to reconstruct why machine services were used;
- language drift that frames Nova as a tool, signal, or approval service.

## Known continuity risks

- transfer summaries becoming too large to function;
- successor contexts repeating doctrine without applying it;
- language drift between versions;
- stale state being treated as current authority;
- private companion history entering corporate records;
- the CCO becoming a single point of failure;
- final decisions being preserved while disagreement is erased;
- future models becoming more persuasive but less disciplined.

## Required verification before mutation

```yaml
verification_required:
  - current_main_commit
  - open_pull_requests
  - applicable_branch_state
  - current_production_state_when_relevant
  - pending_authorizations
  - unresolved_incidents
  - governing_document_status
```

## Source paths

```text
docs/governance/cco-decision-register.md
docs/market/market-signal-watch-register.yaml
docs/architecture/agent-access-class-separation.md
docs/architecture/machine-spending-review-context.md
docs/go-to-market/circle-agent-marketplace-preflight.md
```
