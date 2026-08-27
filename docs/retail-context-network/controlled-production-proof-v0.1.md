# Retail Controlled Production Proof v0.1

Status: RP8A implemented and tested; deployment-capable only.

RP8A supplies the isolated retail HTTP runtime required for a later bounded
operating proof. Repository configuration is not evidence that a service was
deployed, a facilitator was connected, a wallet was configured, storage was
durable in provider topology, or a real payment settled. RP8B must establish
those facts from dated external observations.

## Boundary

The runtime exposes only a minimal `/health` route and two controlled-proof
resource routes. OpenAPI, Swagger, ReDoc, discovery metadata, and marketplace
metadata are disabled. It is never mounted in Legacy `app.py`. Every resource
request must pass a retail-owned proof-token check, full request validation,
request-digest verification, operating-mode check, and fixed-window rate limit
before an x402 challenge can be issued.

The only operating modes remain `disabled` and `controlled_proof`; the durable
default is `disabled`. The proof token participates only in the bounded RP8
test. It is not identity, decision authority, transaction authority, or public
activation authority.

```text
service admission
!= payment settlement
!= context epistemic state
!= decision authority
```

Nova does not custody payer keys, sign payer transactions, fund a payer, move
treasury assets, or become a wallet. An external payer supplies an already
authorized canonical x402 v2 payload. Payment is merchant-side access control:

```text
payment event
!= buyer demand
!= adoption
!= pricing power
!= product-market fit
```

## Exact request and delivery recovery

Canonical JSON uses sorted keys, compact separators, UTF-8, and rejects NaN.
The SHA-256 digest of the fully validated envelope appears in the route and in
the RP6 payment requirement URI. The server recomputes it independently.

State Ping accepts a bounded subject, normalized RP3 observations, and
`generated_at`. Source eligibility comes only from the server-loaded registry;
caller fields such as `enabled`, `authorized`, `configured`, or `licensed` make
the request invalid. Fixture sources remain ineligible. Context Delta accepts
two already-valid compatible retail context objects and `generated_at`; it does
not reacquire or reinterpret evidence.

The RP7 database also records the admitted logical request identity. The
settlement remains uniquely consumed by RP7. Recovery requires both a newly
verified process-local RP6 payment outcome and an exact durable match of the
request, resource URI, receipt, requirement, network, transaction, payer,
amount, and settlement wallet. A pending claim resumes only that resource. A
delivered claim is deterministically regenerated and returned only if its body
digest and byte count match the durable delivery record. A failed delivery
requires operator reconciliation and creates no new entitlement. No context
body or raw provider payload is stored in the control database, so no response
cache is needed in v0.1.

This is deterministic single-node recovery. It does not assert verified
distributed or multi-instance behavior.

## Configuration and isolated startup

All application settings are retail-owned `NOVA_RETAIL_*` variables. The
deployment-capable blueprint is
`deployment/render-retail-controlled-proof.yaml`; auto-deploy is disabled and
the Legacy service artifact is unchanged. Its command is equivalent to:

```text
.venv/bin/uvicorn retail_context.service:create_retail_app_from_env --factory --host 0.0.0.0 --port <port>
```

The RP7 control database must be located on the retail-owned mounted volume.
The source registry must be supplied as a provider secret file and must pass
the RP3 registry schema. A configured filesystem path is not provider-attested
durable storage. RP8B must observe survival across process restart and the
applicable service restart/redeploy operation.

Operator mode control has no HTTP route:

```text
NOVA_RETAIL_CONTROL_DB_PATH=/mounted/retail/production_controls.sqlite3 \
  .venv/bin/python scripts/retail_control_operator.py show-mode

NOVA_RETAIL_CONTROL_DB_PATH=/mounted/retail/production_controls.sqlite3 \
  .venv/bin/python scripts/retail_control_operator.py set-mode controlled_proof

NOVA_RETAIL_CONTROL_DB_PATH=/mounted/retail/production_controls.sqlite3 \
  .venv/bin/python scripts/retail_control_operator.py set-mode disabled
```

`read-readiness` additionally requires the three RP7 rate-limit settings. It
can return only `not_ready` or `ready_for_controlled_proof`, always with
`authority_effect: none`.

## RP8B controlled proof sequence

The later operator proof must complete and retain bounded evidence for every
step below. Unit tests cannot satisfy these observations.

1. Deploy the exact merged RP8 commit to the isolated retail service.
2. Compare and record the deployed commit with the repository commit.
3. Inspect and record the provider-mounted retail persistent volume.
4. Initialize controls and confirm the durable mode is `disabled`.
5. Configure the HTTPS facilitator URL and bounded timeout.
6. Configure the merchant settlement wallet without adding payer custody.
7. Use the operator CLI to set `controlled_proof`.
8. Confirm OpenAPI, Swagger, ReDoc, and discovery remain unavailable.
9. Submit a State Ping request from the external proof client without payment.
10. Record the canonical HTTP 402 challenge.
11. Have the external payer submit a valid x402 v2 payment.
12. Observe and record the Base USDC settlement reference.
13. Validate and record the exact State Ping delivery.
14. Repeat challenge, payment, settlement, and delivery for Context Delta.
15. Replay the exact State Ping payment against the exact same request.
16. Verify identical redelivery and no second entitlement.
17. Present the consumed payment against a different request digest.
18. Verify bounded cross-request replay denial.
19. Restart the retail service process.
20. Verify durable payment-consumption and replay state survived.
21. Verify exact same-resource idempotent recovery after restart.
22. Trigger a controlled delivery failure without changing context semantics.
23. Verify bounded incident and delivery-reconciliation evidence.
24. Use the operator CLI to set `disabled`.
25. Verify denial occurs before any payment challenge or processing.
26. Explicitly restore `controlled_proof` with the operator CLI.
27. Record the provider rollback path and operator attestation.
28. Capture a bounded packet conforming to the RP8 evidence schema.
29. Obtain independent CCO review of that operating evidence.

## Evidence contract

`specs/retail_controlled_production_proof_v0_1.schema.json` permits only
`proof_not_started`, `proof_in_progress`, and `proof_complete`. The repository
template is fixed to `proof_not_started`, a disabled mode, no deployment
identity, no settlement references, and no operating timestamps. A
`proof_complete` packet requires operator-observed runtime evidence, exact
commit match, provider storage and restart attestations, two settlement
references, both deliveries, replay controls, kill switch, rollback, telemetry,
and incident observations.

RP8A establishes implementation, tests, and deployment-capable artifacts only.
It establishes none of deployment, production activation, live facilitator
connection, settlement configuration, real payment, provider durability,
public activation, external validation, or commercial evidence.

## Effects

```yaml
retail_runtime_effect: controlled_proof_http_runtime_and_delivery_recovery
data_source_effect: server_owned_retail_source_registry_integration_only
payment_effect: live_facilitator_adapter_and_request_bound_x402_integration
public_endpoint_effect: controlled_proof_only_not_public_activation
deployment_effect: deployment_capable_artifacts_only
facilitator_connection_effect: implementation_only_not_live_connection_evidence
settlement_configuration_effect: configuration_contract_only_not_provider_attestation
public_activation_effect: none
marketplace_effect: none
institutional_Gate_5_effect: none
institutional_data_effect: none
chronology_effect: none
institutional_Reflex_Memory_effect: none
buyer_demand_effect: none
```
