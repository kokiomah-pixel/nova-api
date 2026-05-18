# x402 Facilitator Response Catalog

This catalog normalizes facilitator responses into interoperability categories for Nova settlement observability.

## Categories

| Category | Meaning | Typical Indicators |
| --- | --- | --- |
| `INVALID_CHALLENGE` | Challenge or generated settlement telemetry could not be verified by the facilitator. | `invalid_payload`, malformed payload, missing payload field |
| `STALE_CHALLENGE` | The challenge exceeded its timing window or freshness boundary. | expired, stale, timeout |
| `UNSUPPORTED_NETWORK` | Facilitator does not accept the requested network or chain identifier. | unsupported network, invalid network |
| `UNSUPPORTED_ASSET` | Facilitator does not accept the requested asset. | unsupported asset, invalid asset |
| `ROUTE_REJECTION` | Facilitator endpoint or route rejected the request shape. | 404, 405, retry-after, route |
| `SIGNATURE_REJECTION` | Signature or signer validation failed. | signature rejected, invalid signer |
| `VERSION_MISMATCH` | x402 version metadata is inconsistent. | x402Version, protocol version |
| `UNKNOWN_INTEROPERABILITY_FAILURE` | Rejection does not match a known category. | opaque facilitator failure |

## Safety Rule

Catalog entries must remain diagnostic. They must not include raw signatures, bearer tokens, CDP secrets, private keys, or private settlement metadata.

