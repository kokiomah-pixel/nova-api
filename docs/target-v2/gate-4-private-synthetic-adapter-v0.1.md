# Gate 4 Private Synthetic Adapter v0.1

## Scope

```yaml
Gate_4: authorized_for_bounded_branch_implementation
artifact: isolated_private_synthetic_reference_adapter
canonical_contract: design-v2.1
semantic_authorities:
  - docs/architecture/external-review-context-contract-v2.md
  - specs/review_context_contract_v2.json
  - docs/target-v2/gate-3-field-derivation-ledger-v0.1.md
  - specs/review_context_field_derivation_v0_1.json
  - docs/target-v2/context-proof-canonicalization-v0.1.md
Legacy_v1_derivation_dependency: none
Gate_3_reference_semantics_role: test_oracle_only
authority_effect: none
execution_effect: none
```

The adapter is an offline harness package at
`nova/harnesses/target_v2_private_synthetic_adapter`. It has no application
startup import, public route, service process, network input/output, production
configuration, provider SDK, credential, or production-data dependency.

The adapter independently normalizes exact financial values, timestamps,
declared sets, and JCS structural serialization. It constructs descriptive
target-v2 review context from explicit synthetic facts and profile rules. It
does not consume Legacy v1 decisions or admissions, select a winning source,
interpret chronology or accepted-memory references, or produce an approval,
authorization, settlement, or execution result.

## Reference and proof boundary

Chronology and accepted-memory values are opaque identities sorted only by the
incorporated G3-R11 chronology-reference tuple. No precedent, treatment,
applicability, abstraction, acceptance, or mutation behavior is implemented.

The result exposes canonical semantic bytes and deterministic proof-envelope
inputs. The proof input explicitly records that digest and signature algorithm
selection is `not_selected`. A deliberately non-cryptographic fixture checksum
may identify synthetic proposal material in tests; its qualification begins
with `fixture-only-` and it is not a production default or security claim.

## Resulting state

```yaml
private_synthetic_adapter_branch_implemented: true
canonical_private_adapter_implemented: false
target_v2_runtime_implemented: false
target_v2_production_active: false
system_wide_production_readiness: not_established
merge_requested: false
deployment_authority: false
```
