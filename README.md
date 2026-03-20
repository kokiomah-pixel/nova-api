# nova-api

A small FastAPI service that provides a “Nova” decision context API with signed payloads and API-key gating.

---

## ✅ Quick start

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

## 🔐 Auth (API key)

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

---

## 🧪 Endpoints

### Billable (counts toward monthly quota)
- `GET /v1/regime` – protected; returns current regime + signature
- `GET /v1/epoch` – protected; returns epoch hash + signature
- `GET /v1/context` – protected; returns guardrail/memory context + signature

### Non-billable (does NOT count toward quota)
- `GET /health` – public healthcheck
- `GET /v1/key-info` – protected; returns info for the authenticated key
- `GET /v1/usage` – protected; returns accumulated usage stats for the key

### Admin-only (non-billable)
- `POST /v1/usage/reset` – protected; clears usage stats for the key (admin tier only)

---

## 🧩 Notes

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

## ✅ Quick verification

```bash
curl -i http://127.0.0.1:8000/health
```

```bash
export NOVA_API_KEY="mytestkey"
curl -i -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/regime

curl -i -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/usage

curl -i -X POST -H "Authorization: Bearer mytestkey" http://127.0.0.1:8000/v1/usage/reset
```

---

## 🔑 Getting an API Key

To use the Nova API, you need a valid API key.

### Request Access

Contact the Nova operations team to request an API key. Provide:

- Your organization name
- Intended use case
- Expected monthly request volume

### Tier Selection

API keys are provisioned at one of three tiers:

- **Free** – up to 1,000 billable calls/month; good for evaluation
- **Pro** – up to 100,000 billable calls/month; for production use  
- **Admin** – unlimited; for internal operations and testing

Each tier allows unlimited calls to non-billable endpoints (`/health`, `/v1/key-info`, `/v1/usage`).

### Using Your Key

Once provisioned, include your key in the `Authorization` header as a Bearer token:

```bash
curl -H "Authorization: Bearer your-api-key-here" \
  https://your-api-domain.com/v1/regime
```

---

## 🧪 Running tests

```bash
./.venv/bin/pytest -q
```
