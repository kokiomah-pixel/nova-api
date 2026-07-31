# Machine-Spending Review Context

## Status

```yaml
status:
  classification: approved_specification_level_concept
  evidence_reference: MSE-2026-07-30-028
  product_requirement_validated: false
  operator_need_validated: false
  runtime_implementation_authorized: false
  public_interface_authorized: false
```

This specification extracts a provider-independent architectural question from
the Fastly market-signal
[`MSE-2026-07-30-028`](../market/signals/2026/MSE-2026-07-30-028-fastly-x402-edge-payment.md).
Fastly is one evidence source, not a Nova dependency. Evidence shows that
machine payment and resource delivery can be compressed; the institutional
need described here remains an unvalidated hypothesis.

## Required architectural boundary

```text
Agent discovers or requests a paid resource.
Nova structures applicable institutional review context.
Local authority or a standing institution-defined mandate determines permission.
An external wallet exercises economic authority.
External payment infrastructure verifies payment and serves the resource.
Nova does not sign, pay, verify, settle, approve, or release the resource.
```

Agent prepares action. Nova structures review context. Local authority decides.
External systems execute. Nova does not execute.

## Separation model

```text
Discoverable
≠ callable
≠ institutionally permitted
≠ economically authorized
≠ paid
≠ authoritative
≠ review complete
≠ capital-action approval
```

```text
Payment verified
≠ institutionally permitted
≠ provider approved
≠ source authoritative
≠ review context complete
≠ capital action approved
```

## Three-event lifecycle

```yaml
machine_resource_lifecycle:
  resource_discovery_or_quotation:
    description: >
      An agent identifies a paid resource and receives commercial,
      contractual, access, or payment terms.
    chronology_default: do_not_retain

  resource_acquisition:
    description: >
      Applicable institutional authority or a standing mandate permits or
      declines the expenditure, and external systems process any payment.
    chronology_default: retain_only_when_governance_material

  evidentiary_reliance:
    description: >
      The resulting information, service, capability, or output materially
      influences review of a consequential institutional action.
    chronology_default: candidate_for_governed_retention
```

Discovery identifies an opportunity. Acquisition concerns permission and
external economic action. Evidentiary reliance concerns how the resulting
resource affects later review. Implementations must not collapse these events.

## Spending governance and information governance

These are separate proposed review dimensions:

```yaml
spending_governance:
  requesting_agent:
  intended_task:
  payer_wallet_owner:
  delegated_spending_reference:
  provider_permission_status:
  resource_class:
  quoted_amount:
  payment_asset:
  one_time_or_recurring:
  standing_mandate_reference:
  local_review_required:
  unresolved_spending_conditions:

information_governance:
  provider:
  resource_reference:
  output_reference:
  data_classification:
  source_authority_status:
  claim_supported:
  evidence_freshness:
  conflicting_evidence:
  permitted_evidentiary_use:
  considered_by_local_authority:
  material_to_review:
```

> An institution may permit the purchase while refusing to treat the resulting
> output as authoritative evidence.

The reverse distinction also matters: a source may be authoritative for a
claim while a particular purchase path, disclosure, or recurring commitment
was not permitted.

## Nonfinancial consequences

```yaml
resource_consequence:
  contractual_terms_created:
  confidential_context_disclosed:
  provider_jurisdiction:
  restricted_data_acquired:
  recurring_commitment_created:
  capability_acquired:
  external_dependency_created:
  downstream_access_expanded:
```

> The price of a machine purchase may be economically trivial while its
> contractual, informational, jurisdictional, confidentiality, or capability
> consequences are institutionally material.

These proposed fields surface consequences for local interpretation. They do
not make Nova a contract, privacy, compliance, or authorization authority.

## Edge-payment results as external observations

At specification level, `edge_payment_enforcement` is an external-system type:

```yaml
external_system_taxonomy:
  edge_payment_enforcement:
    description: >
      External edge or gateway infrastructure that presents payment
      requirements, verifies externally supplied payment evidence, and
      releases or blocks access to a protected resource.
    possible_outputs:
      - payment_challenge_issued
      - payment_verified
      - payment_rejected
      - request_released
      - request_blocked
      - verification_failed
      - route_policy_applied
    institutional_authority_effect: none
    evidentiary_authority_effect: none
    capital_action_authority_effect: none
    execution_effect: resource_access_only
    Nova_treatment:
      - preserve_as_external_system_result
      - preserve_provider_and_timestamp
      - preserve_supporting_reference_when_material
      - do_not_treat_as_institutional_permission
      - do_not_treat_as_source_authority
      - do_not_treat_as_review_completeness
```

A material observation may use this proposed representation:

```yaml
external_system_result:
  provider:
  system_type: edge_payment_enforcement
  result:
  result_reference:
  observed_at:
  supporting_artifacts:

  institutionally_authoritative: false
  evidentiary_authority_effect: none
  capital_action_authority_effect: none
  execution_effect: resource_access_only
```

Fastly, Cloudflare, Akamai, an API gateway, an MCP gateway, a wallet provider,
or an x402 facilitator could supply observations. Provider attribution does
not create dependency or institutional authority.

## Selective chronology rule

> Preserve decision significance, not every machine transaction.

The relationship Nova may eventually preserve, subject to separate
authorization, is:

```text
Resource requested
→ applicable mandate or review applied
→ resource acquired or declined
→ output received
→ output supported a claim
→ claim entered review
→ local authority accepted, questioned, or rejected it
→ later outcome informed future review
```

The reference-first default is:

```yaml
retention_default:
  preserve_when_material:
    - provider_reference
    - resource_reference
    - payment_reference
    - output_hash_or_artifact_reference
    - relevant_claim
    - provenance
    - materiality_determination
    - authority_treatment
    - related_action_reference

  do_not_preserve_by_default:
    - full_paid_resource_content
    - wallet_private_material
    - signing_credentials
    - payment_secrets
    - unrestricted_agent_transcripts
    - proprietary_provider_content
```

This specification creates no chronology event, candidate, ledger entry, or
automatic ingestion behavior.

## Reflex Memory boundary

Subject to future evidence and separate authorization, Reflex Memory may
eventually identify:

- repeated usefulness of a paid source;
- repeated rejection of provider outputs;
- duplication of approved internal sources;
- recurring lateness;
- repeated conflicts;
- usefulness limited to one action class.

Reflex Memory must never automatically:

- approve a provider;
- make a source authoritative;
- increase spending limits;
- alter a mandate;
- create future purchase authority;
- authorize a wallet signature;
- alter governance without formal institutional acceptance.

This specification creates no learning object and changes no Reflex Memory
state.

## Related access-class boundary

Machine-spending context does not authorize a shared retail and institutional
service surface.

Public discovery, retail agent usage, and private institutional review context
are separate access classes.

Circle is one example channel, not a Nova dependency. Any distribution model
must remain nonexclusive.

See
[`agent-access-class-separation.md`](agent-access-class-separation.md).

A marketplace payment, wallet identity, API-key tier, subscription upgrade, or
retail invocation must not create access to institution-owned evidence,
constraints, authority maps, source registries, chronology, Reflex Memory, or
tenant configuration.

`/v1/context` must not become a combined retail and institutional marketplace
endpoint. It remains a private authenticated Legacy v1 surface and is not
represented here as the approved future external contract. Retail or
marketplace access is not authorized.

```text
Marketplace discovery may identify the capability.

Retail usage, if separately authorized, remains non-institutional.

Institutional Nova remains private, tenant-scoped decision-context
infrastructure before local authority acts.
```

## Category protection

Nova is not a payment gateway, x402 facilitator, wallet-policy engine,
spending-control product, edge-enforcement service, signing service, settlement
service, transaction-authorization system, resource-access authority, or
paid-data marketplace.

> x402 and edge infrastructure determine whether a payment requirement was
> satisfied and whether a resource may be served. Sharpe Nova OS structures the
> institution-defined review context surrounding why a machine expenditure was
> proposed and how the resulting resource should be treated if it later
> influences a consequential capital review.

```text
Nova structures.
Institutional authority interprets.
External wallets and payment systems act.
```

## Commercial boundary

```text
Weak commercial unit:
one paid HTTP request

Stronger commercial unit:
one recurring institutionally governed machine-action class with review
continuity, source provenance, and durable chronology
```

Possible future commercial units include governed action classes,
institutional review environments, machine-spending context configuration,
provider and source governance, evidentiary provenance, selective chronology,
cross-provider continuity, and recurring workflow coverage. Each remains a
hypothesis. No buyer demand, product requirement, GTM category, pricing model,
or implementation authority has been established.

## Authorization boundary

This document is specification only. It does not authorize runtime behavior,
public discovery, x402 activation, payment gating, a wallet, signing, payment
verification, settlement, resource release, automatic spending approval,
chronology mutation, or Reflex Memory mutation.
