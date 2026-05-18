# x402 Interoperability Timeline

## Phase 1: Public Environmental Surface

- `/services.json` declares Nova Constraint Pressure as machine-readable environmental conditioning telemetry.
- `/v1/feeds/constraint_pressure` is the only public x402-protected feed surface.
- `/v1/context` and `/v1/proof` remain sovereign/private routes.

## Phase 2: Auth and Plane Separation

- CDP facilitator auth was centralized through a shared auth builder.
- Telemetry admin inspection was split from sovereign authority.
- Telemetry admin access is limited to feed usage and billing summary inspection.

## Phase 3: Canonical Helper Construction

- Manual x402 payment header construction was removed from the live runner.
- The live runner uses the official x402 HTTP helper against the live `PAYMENT-REQUIRED` challenge.
- Helper-generated metadata is validated against Base, USDC, settlement wallet, and amount expectations.

## Phase 4: Settlement Observability

- Structured diagnostics now frame the remaining work as machine-native settlement interoperability observability.
- Events include challenge intake, helper invocation, payload generation, facilitator rejection, and interoperability failure.
- Redaction protects secrets before diagnostic output.

