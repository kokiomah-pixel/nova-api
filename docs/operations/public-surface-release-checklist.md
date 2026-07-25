# Public-Surface Release Checklist

## Machine Discovery Surfaces

- [ ] `/openapi.json` reviewed
- [ ] `/docs` reviewed
- [ ] `/redoc` reviewed
- [ ] `/services.json` reviewed
- [ ] `/.well-known/*` routes reviewed
- [ ] MCP surfaces reviewed
- [ ] x402 challenge surfaces reviewed
- [ ] registry entries reviewed
- [ ] SDK and package metadata reviewed
- [ ] repository machine-readable contracts reviewed

## Required Default Posture

```yaml
public_API_documentation: false
public_service_discovery: false
public_x402: false
facilitator_settlement: false
```

## Authority Review

- [ ] No public surface presents Legacy v1 admission outcomes as the canonical
      future Nova contract.
- [ ] No new external integration is directed toward Legacy v1.
- [ ] Any proposed v2 surface is labeled not implemented until runtime approval.
- [ ] Payment purchases service access only and has no authority effect.

## Deployment Attestation

- [ ] Named production owner exists.
- [ ] Backup operator exists.
- [ ] Deployed commit is recorded.
- [ ] Effective environment flags are recorded.
- [ ] Logs and credential ownership are accessible.
- [ ] External route verification is complete.
