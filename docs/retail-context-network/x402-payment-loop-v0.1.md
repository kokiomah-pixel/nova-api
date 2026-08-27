# Nova Context Network — Retail x402 Payment Loop v0.1

**Gate:** RP6
**Scope:** isolated, in-process retail payment/access contract only

## Contract

RP6 establishes this deterministic sequence for the two launch resources:

```text
context resource requested
-> payment requirement constructed
-> x402 v2 payment presented
-> payment verified
-> payment settled
-> bounded settlement receipt reconciled
-> process-local resource access permitted
```

The stages are deliberately separate:

```text
payment requirement
!= payment verification
!= settlement
!= resource access
!= decision authority
```

Verification does not imply settlement. Settlement does not imply access until
the transaction reference, Base network, exact atomic amount, original
requirement identity, resource type, and resource URI reconcile. Access has
`authority_effect: none` and grants only `context_resource_access_only`.

The retail x402 layer meters access to decision-context resources. It does not
alter the epistemic content of those resources. In particular, payment cannot
verify evidence, resolve context, change confidence or contradictions, approve
an action, authorize execution, or purchase a favorable answer.

## Fixed protocol and prices

RP6 uses upstream `x402==2.9.0` v2 models directly with the `exact` scheme,
network `eip155:8453`, and Base USDC asset
`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (6 decimals).

The authoritative closed catalog is integer atomic USDC:

| Resource | Display USDC | Atomic USDC |
| --- | ---: | ---: |
| `state_ping` | `0.002` | `2000` |
| `context_delta` | `0.02` | `20000` |

The pricing model is `pay_per_context_resource`. There are no subscriptions,
tiers, cadence prices, overages, or caller-provided price overrides.

## Configuration and facilitator boundary

The settlement destination is required and has no default. Only
`NOVA_RETAIL_X402_SETTLEMENT_WALLET` is read; legacy x402 variables and CDP
credentials are not fallbacks.

The loop accepts an injected facilitator exposing `verify` and `settle`. RP6
does not construct a live facilitator, make a network request, sign a wallet
payload, create an HTTP endpoint, configure settlement, or activate production.
The v2 `PAYMENT-SIGNATURE` contract is exposed; legacy `X-PAYMENT` is not part
of the retail contract.

## Outcome, receipt, and later replay control

The successful verify -> settle -> reconcile function returns a process-local
`RetailPaymentOutcome`. That outcome carries the schema-valid receipt together
with a private in-process access capability that is never serialized.

The serialized `payment_receipt` is an audit and reconciliation artifact only.
Its stable identity derives from the requirement ID, transaction reference,
payer when present, network, and exact amount—not raw facilitator payloads.
Those deterministic IDs establish identity consistency; they do not establish
receipt authenticity and are not bearer credentials.

Consequently:

```text
successful in-process settlement outcome
-> may permit resource access

serialized or reconstructed payment receipt
-> audit / reconciliation evidence
!= independent resource-access proof
```

Copying, serializing, or deserializing a receipt does not reproduce the
process-local access capability. A future HTTP/runtime layer must consume the
successful in-process outcome or introduce a separately authorized durable
access-proof mechanism; it must not treat a reconstructed RP6 receipt as proof
that payment occurred.

RP6 establishes receipt identity and reconciliation fields. Durable
consumed-payment/replay state is a production-control concern for a later gate;
RP6 does not claim replay protection, receipt signing, or durable bearer-token
authentication.

## Effects

```yaml
retail_runtime_effect: x402_payment_contract_and_injectable_loop_only
data_source_effect: none
payment_effect: retail_pay_per_context_challenge_verify_settle_access_logic
public_endpoint_effect: none
deployment_effect: none
facilitator_connection_effect: none
settlement_configuration_effect: none
institutional_Gate_5_effect: none
institutional_data_effect: none
chronology_effect: none
institutional_Reflex_Memory_effect: none
```
