# Public Exposure Inventory v0.1

**Status:** transition inventory  
**Baseline:** public `sharpe-nova-os` repository at RP8A  
**Purpose:** identify which material should remain public, be sanitized, migrate private, or remain provider-only.

## Classification legend

```text
PUBLIC
  suitable for ongoing public repository use

PUBLIC_SANITIZED
  public contract or proof is useful, but implementation detail should be reduced

PRIVATE
  future canonical implementation or operating state should live in a private repository

PROVIDER_ONLY
  secret values or provider control-plane state; never commit
```

## Current high-level classification

| Area | Current exposure | Target classification | Treatment |
| --- | --- | --- | --- |
| README / category doctrine | public | PUBLIC | retain |
| public architecture contracts | public | PUBLIC | retain, keep non-authority framing |
| public response schemas | public | PUBLIC | retain |
| synthetic examples / public test vectors | public | PUBLIC | retain after exposure review |
| public pricing and payment semantics | mixed | PUBLIC | expose only approved retail contract |
| marketplace manifests / discovery metadata | mixed | PUBLIC | publish when approved and live-ready |
| `retail_context/` production implementation | public | PRIVATE | migrate future canonical server implementation private |
| deployment blueprints | public | PRIVATE | migrate future provider topology private |
| production control store / recovery logic | public | PRIVATE | migrate future canonical implementation private |
| facilitator / settlement internals | public | PRIVATE | retain only public x402 contract externally |
| source registry implementation | public/mixed | PRIVATE | keep public source classes only if useful |
| materiality and reconciliation internals | public/mixed | PRIVATE | expose behavior contract, not derivation mechanics |
| retail telemetry implementation | public | PRIVATE | publish aggregate service metrics only when useful |
| institutional constraints / authority maps | public/mixed design material | PRIVATE | keep high-level doctrine public; implementation private |
| institutional chronology / accepted Reflex Memory mechanics | public/mixed | PRIVATE | public boundary only; stores and promotion mechanics private |
| internal governance / accepted-state records | public | PRIVATE | migrate corporate source of truth after authority-transfer gate |
| security principles | public | PUBLIC | retain |
| incident runbooks / kill-switch implementation | public/mixed | PRIVATE | publish contact/policy, not internal procedures |
| secrets / credentials / keys / live env values | untracked/provider | PROVIDER_ONLY | keep outside Git |

## Immediate public exposure requiring migration review

### Retail runtime

The public repository currently contains a substantial `retail_context/` implementation, including context construction, production configuration, production controls, telemetry, delivery recovery, facilitator integration, request binding, and control-store logic.

Target treatment:

```yaml
retail_runtime:
  external_contract: PUBLIC
  synthetic_reference_or_test_vectors: PUBLIC_or_PUBLIC_SANITIZED
  canonical_production_server: PRIVATE
  provider_configuration_values: PROVIDER_ONLY
```

### Deployment topology

The public repository currently contains deployment-capable provider configuration for the controlled retail proof.

Target treatment:

```yaml
deployment:
  existence_and_high_level_provider_posture: PUBLIC_SANITIZED
  service_names_and_topology: PRIVATE
  environment_variable_inventory: PRIVATE
  secret_values: PROVIDER_ONLY
  rollback_and_incident_runbooks: PRIVATE
```

### Payment and x402

Target treatment:

```yaml
x402:
  resource_prices: PUBLIC
  payment_network_and_asset: PUBLIC
  public_payment_protocol_contract: PUBLIC
  merchant_verification_internals: PRIVATE
  settlement_reconciliation: PRIVATE
  wallet_or_key_material: PROVIDER_ONLY
```

### Source and context derivation

Target treatment:

```yaml
context_derivation:
  provenance_fields: PUBLIC
  freshness_semantics: PUBLIC
  context_status_values: PUBLIC
  source_classes: PUBLIC_or_PUBLIC_SANITIZED
  exact_source_registry: PRIVATE
  source_priority_and_fallback: PRIVATE
  materiality_thresholds: PRIVATE
  weighting_and_reconciliation_logic: PRIVATE
```

### Reflex Memory

Target treatment:

```yaml
Reflex_Memory:
  non_authority_doctrine: PUBLIC
  external_read_only_contract_when_approved: PUBLIC
  synthetic examples: PUBLIC_SANITIZED
  institutional_corpus: PRIVATE
  accepted_entry_store: PRIVATE
  promotion_and_retrieval_mechanics: PRIVATE
  institution_specific_similarity_or_exception_logic: PRIVATE
```

## Open PR exposure review

Any open PR that would add implementation, internal governance, Reflex Memory mechanics, deployment topology, production controls, source derivation, or provider internals must be reviewed against the new boundary before merge.

At creation of this inventory, PR #33 is specifically subject to that review because it contains Reflex Memory candidate schemas, lineage, and validation machinery. This inventory does not decide whether PR #33 should merge; it changes the required review lens.

## Historical disclosure rule

Files already published under public Git history are presumed disclosed. Future removal or migration must not be described as restoring secrecy to previously public contents.

## Completion condition

This inventory is complete only as a classification artifact. The repository split is not complete until:

- a private corporate repository exists;
- private-target paths have a verified destination;
- canonical production implementation is migrated;
- public contracts remain usable;
- accepted-state authority is explicitly transferred by the Architect;
- the public repository no longer needs private implementation to function as the external trust and integration surface.
