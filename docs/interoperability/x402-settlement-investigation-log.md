# x402 Settlement Investigation Log

This log tracks Nova's environmental settlement observability work for the Constraint Pressure feed. It does not record secrets, private keys, raw signatures, bearer tokens, or wallet credentials.

## Current Validation State

- Public x402 discovery surface is constrained to `/v1/feeds/constraint_pressure`.
- Sovereign authority routes remain outside x402 discoverability.
- CDP facilitator authentication has moved from 401 rejection to reachable verification.
- The live payment runner uses the official x402 HTTP helper and derives payment metadata from the live `PAYMENT-REQUIRED` challenge.
- Settlement remains under investigation after facilitator rejection with `invalid_payload`.

## Diagnostic Boundary

Nova records settlement telemetry, interoperability diagnostics, facilitator response tracing, and machine-native coordination telemetry.

Nova does not log authorization tokens, CDP secrets, EOA private keys, raw signatures, settlement credentials, Reflex Memory, or sovereign admission logic.

## Next Diagnostic Focus

- Compare facilitator rejection categories across helper-generated payloads.
- Track challenge metadata, helper metadata, and facilitator response metadata in one chronology.
- Confirm whether rejection is caused by challenge freshness, supported asset/network routing, wallet funding state, or protocol-version mismatch.

