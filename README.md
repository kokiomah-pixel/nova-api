# Sharpe Nova OS

## Stop. Run This First.

If your system moves capital, run this before reading anything else:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
"https://YOUR_API_DOMAIN/v1/context?intent=trade&asset=ETH&size=10000"
```

## Your System Is Increasing Size Into Volatility

Most execution systems do this:

signal → confidence ↑ → size ↑ → execute

That works in stable conditions.

It fails in fragile ones.

Because rising volatility is not strength.

It is instability.

---

## What Happens Without a Control Check

Your system:
- increases exposure as conditions deteriorate
- continues deploying risk during regime shifts
- executes at full size because nothing tells it not to

This is not a model problem.

It is an execution control failure.

---

## The Missing Step

Every system has:

intent → size → execute

What's missing is:

intent → size → [CHECK: is this permitted right now?] → execute or halt

## What Nova Does

Nova inserts that check.

Before execution, your system calls:

```
GET /v1/context
```

And receives:
- current regime
- execution constraints
- allowed actions

Your system reads `action_policy` and decides:
- proceed
- reduce
- or stop

---

## Why This Matters (Real Output)

Without Nova:
- 4/4 scenarios executed at full size
- Total executed: 80,500

With Nova:
- 4/4 scenarios constrained
- Total executed: 40,250

Same strategies.
Same signals.

Different execution.

### Example (Live Behavior)

WITHOUT NOVA
- Executed size: 80,500

WITH NOVA (Elevated Fragility)
- Decision: CONSTRAIN
- Executed size: 40,250
- Reason: position increase blocked

Nova reduced deployed risk by **50%** under the same conditions.

If your system would have executed 80,500 instead of 40,250:

It is increasing size into volatility.

---

## The One Line That Matters

Most systems increase size into volatility. Nova prevents that.

---

## What This Is

Nova is not a signal.
Nova is not a model.

Nova determines whether execution is permitted under current conditions.

---

## Why This Should Not Live Inside Strategy

You can build constraint logic internally.

But once it lives inside your strategy stack, it begins to adapt to that strategy.

Thresholds change.
Overrides appear.
Constraints bend under performance pressure.

Nova stays outside strategy logic.

That is the point.

It acts as a consistent execution check that does not adapt to your own bias.

---

## What This Means

If your system executes without checking Nova:

it is executing unconditionally

---

## Next Step

Run the comparison:

```bash
python examples/nova_comparison_agent.py
```

If the output changes what your system would have done:

You have a control gap.

Close it.

---

## Nova Decision State (Live)

Nova provides a pre-execution decision checkpoint for capital systems.

Before executing, agents call:

`GET /v1/context`

### Current State

```json
{
  "epoch": 2461,
  "regime": "Elevated Fragility",
  "action_policy": {
    "allow_new_risk": true,
    "allow_risk_reduction": true,
    "allow_position_increase": false,
    "allow_position_decrease": true
  }
}
```

This response is machine-readable. Agent logic reads `action_policy` directly and gates execution accordingly.

---

## Behavior Model

Nova produces one of three outcomes per decision call:

| Outcome | Condition | Agent behavior |
|---------|-----------|----------------|
| **ALLOW** | `allow_new_risk=true`, `allow_position_increase=true` | Proceed under normal controls |
| **CONSTRAIN** | `allow_new_risk=true`, `allow_position_increase=false` | Proceed with reduced size; no position increases |
| **VETO** | `allow_new_risk=false` | Do not initiate new risk; reduce or exit only |

### Regime to outcome mapping

| Regime | Severity | Outcome |
|--------|----------|---------|
| Stable | low | ALLOW |
| Elevated Fragility | medium | CONSTRAIN |
| Stress | high | VETO |

The current regime (`Elevated Fragility`) maps to **CONSTRAIN**: new risk is allowed, but position increases are blocked.

---

## Why This Exists

Most systems today:
- generate signals
- run strategies
- execute trades

But they do not standardize **decision context before execution**.

Nova provides:
- regime awareness
- guardrails
- memory context

This allows systems to:
- adapt behavior
- reduce uncoordinated risk
- operate with shared decision context

Nova is designed to become a required checkpoint before capital moves.

---

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run the server:

```bash
./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

### Run via Docker

```bash
docker build -t nova-api .
docker run --rm -p 8000:8000 -e NOVA_API_KEY=mytestkey nova-api
```

---

## Auth / API keys

The service protects `/v1/*` endpoints with a bearer token.

### Legacy single-key mode

Set one key via `NOVA_API_KEY`:

```bash
export NOVA_API_KEY="mytestkey"
```

Then call an endpoint:

```bash
curl -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/regime
```

### New registry mode

You may instead supply a JSON key registry via `NOVA_KEYS_JSON`. It must be a JSON object mapping keys to metadata, for example:

```bash
export NOVA_KEYS_JSON='{"mykey":{"owner":"dev","tier":"admin","status":"active","monthly_quota":1000000,"allowed_endpoints":["/v1/regime","/v1/epoch","/v1/context","/v1/key-info","/v1/usage","/v1/usage/reset","/health"]}}'
```

### Getting an API Key

Contact the Nova operations team to request an API key. Provide your organization name, intended use case, and expected monthly request volume.

API keys are provisioned at one of three tiers:

- **Free** - up to 1,000 billable calls/month; good for evaluation
- **Pro** - up to 100,000 billable calls/month; for production use
- **Admin** - unlimited; for internal operations and testing

Each tier allows unlimited calls to non-billable endpoints (`/health`, `/v1/key-info`, `/v1/usage`).

---

## Endpoints

### Billable (counts toward monthly quota)
- `GET /v1/regime` - protected; returns current regime + signature
- `GET /v1/epoch` - protected; returns epoch hash + signature
- `GET /v1/context` - protected; returns guardrail/memory context + signature

### Non-billable (does NOT count toward quota)
- `GET /health` - public healthcheck
- `GET /v1/key-info` - protected; returns info for the authenticated key
- `GET /v1/usage` - protected; returns accumulated usage stats for the key

### Admin-only (non-billable)
- `POST /v1/usage/reset` - protected; clears usage stats for the key (admin tier only)

---

## Policy B - Billing Model

Nova meters **decision value**, not introspection or system management.

### Billable Endpoints
These endpoints represent decision checkpoints and count toward monthly quota:
- `/v1/context` - guardrails and memory context for deployments
- `/v1/regime` - current regime assessment
- `/v1/epoch` - epoch hash and constitution snapshot

### Non-Billable Endpoints
These endpoints are operational and do **not** consume quota:
- `/health` - public healthcheck (no auth required)
- `/v1/key-info` - key metadata and entitlements (auth required)
- `/v1/usage` - accumulated usage statistics (auth required)

### Admin-Only Endpoint
This endpoint requires admin tier and does **not** consume quota:
- `/v1/usage/reset` - clears usage counters for an API key

---

## 60-Second Integration

Call `/v1/context` before any capital action. Read `action_policy` and gate execution.

### Python

```python
import requests

NOVA_API_URL = "https://your-api-domain.com"
NOVA_API_KEY = "your-api-key"

def get_nova_context(intent: str, asset: str, size: float) -> dict:
    response = requests.get(
        f"{NOVA_API_URL}/v1/context",
        headers={"Authorization": f"Bearer {NOVA_API_KEY}"},
        params={"intent": intent, "asset": asset, "size": size}
    )
    response.raise_for_status()
    return response.json()

def can_execute(context: dict, intent: str) -> bool:
    policy = context["guardrail"]["action_policy"]
    if not policy.get("allow_new_risk", False):
        return False  # VETO
    if intent == "increase" and not policy.get("allow_position_increase", False):
        return False  # CONSTRAIN - position increase blocked
    return True       # ALLOW

# Before executing:
context = get_nova_context(intent="trade", asset="ETH", size=10000)
if can_execute(context, intent="increase"):
    pass  # proceed
else:
    pass  # halt or reduce
```

### curl

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://YOUR_API_DOMAIN/v1/context?intent=trade&asset=ETH&size=10000"
```

---

## Fastest Adoption Path

If you want the simplest way to integrate Nova, use the client wrapper:

`examples/nova_client.py`

```python
from examples.nova_client import get_nova_decision

decision = get_nova_decision("trade", "ETH", 10000)

if decision["decision"] == "VETO":
    # stop execution
    pass

elif decision["decision"] == "CONSTRAIN":
    # reduce size or adjust behavior
    pass

else:
    # proceed normally
    pass
```

This wrapper:
- calls `/v1/context`
- reads `action_policy`
- returns a top-level decision: ALLOW, CONSTRAIN, or VETO

Use this if you want to integrate Nova in under 60 seconds.

---

## Execution Visibility

Nova should not only be called before execution.

Its decision should remain visible after execution.

A Nova-gated system should be able to show:

- what action was requested
- what Nova state was active
- whether execution was allowed, constrained, or blocked
- how execution changed as a result

### Example

```json
{
  "intent": "trade",
  "asset": "ETH",
  "size_requested": 10000,
  "size_executed": 5000,
  "nova_regime": "Elevated Fragility",
  "nova_decision": "CONSTRAIN",
  "reason": "position increase blocked"
}
```

### Comparison Demo

See:

`examples/nova_comparison_agent.py`

This runs the same scenarios twice:

- once without Nova
- once with Nova

It shows exactly how execution changes when Nova is in the loop.

---

## Same System. Different Execution.

Nova does not change your strategy.

It changes how your system executes based on regime.

The same agent, the same inputs, produces different outcomes depending on system conditions.

### Example — Same Trade, Different Regimes

| Regime | Decision | Execution |
|--------|----------|-----------|
| **Stress** | VETO | No execution (0%) |
| **Elevated Fragility** | CONSTRAIN | Reduced size (50%) |
| **Stable** | ALLOW | Full execution (100%) |

### What This Means

Without Nova:
- execution is constant
- systems apply the same behavior regardless of conditions

With Nova:
- execution becomes state-dependent
- systems automatically adapt to environment conditions
- capital deployment becomes conditional, not fixed

Nova is not a throttle.

It is a regime-aware execution layer.

---

### Reference

Run:

```bash
python examples/nova_comparison_agent.py
```

See:

`examples/nova_comparison_agent.py`

Run the same scenarios under different regimes to observe:

- full execution (Stable)
- reduced execution (Elevated Fragility)
- blocked execution (Stress)

---

## Live vs Fixed Mode

Nova operates in two modes depending on environment configuration.

### Live Mode (default)

- `timestamp_utc` updates on every request
- `epoch` updates automatically (hourly bucket)
- reflects current system conditions in real time

This is the default production behavior.

### Fixed Mode (for testing and evidence)

You can override time using environment variables:

```bash
export NOVA_TIMESTAMP_UTC="2026-03-16T16:00:00Z"
export NOVA_EPOCH=2461
```

## Evidence

Controlled behavior evidence is documented in [`NOVA_EVIDENCE_PACK_V1.md`](NOVA_EVIDENCE_PACK_V1.md).

This includes verified output captures for all three behavior outcomes across regimes:

| Outcome | Regime | Verified |
|---------|--------|---------|
| VETO | Stress | yes |
| CONSTRAIN | Elevated Fragility | yes |
| ALLOW | Stable | yes |

Evidence was captured under controlled conditions with locked epoch, regime, and action policy values. All outputs are machine-verifiable via HMAC-SHA256 payload signatures.

---

## Notes

- Payload signatures are HMAC-SHA256 using `NOVA_SIGNING_SECRET` (default: `replace_me`).
- Usage is persisted between restarts in a JSON file (default `.usage.json`). You can override via `NOVA_USAGE_FILE`.
- For scalable shared deployment, you can use Redis (set `NOVA_REDIS_URL`) instead of file persistence; this makes usage/quota/rate-limit state shared across instances.
- The service enforces a per-key `monthly_quota` (from the key metadata). If usage exceeds the quota, protected endpoints return `429`.
- Optionally, a key can set a `rate_limit` object in its metadata to enforce short-term rate limits (e.g. `{"window_seconds": 60, "max_calls": 30}`).
- Default regime/epoch values are set via:
  - `NOVA_EPOCH`
  - `NOVA_TIMESTAMP_UTC`
  - `NOVA_CONSTITUTION_VERSION`
  - `NOVA_REGIME`

---

## Verification / Tests

### Health check (no auth required)
```bash
curl -i http://127.0.0.1:8000/health
```

### Live decision call
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://YOUR_API_DOMAIN/v1/context?intent=trade&asset=ETH&size=10000"
```

### Usage and reset
```bash
export NOVA_API_KEY="mytestkey"
curl -i -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/regime

curl -i -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/usage

curl -i -X POST -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/usage/reset
```

### Run tests
```bash
./.venv/bin/pytest -q
```
