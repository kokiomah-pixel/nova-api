# Nova API Project Report

## Overview
This repo contains a FastAPI service providing a “Nova decision context” API with:

- API key gating (legacy single-key + JSON key registry)
- Signed payloads (HMAC-SHA256)
- Usage tracking (per-key), with reset
- Monthly quota enforcement
- Optional rate limiting
- Optional Redis-backed shared usage state (for multi-instance scaling)
- Test suite and Docker support


## Key Files

- `app.py` – Main FastAPI app, auth + endpoint logic, usage/quota/rate-limit management
- `requirements.txt` – Dependencies for runtime and tests
- `tests/test_app.py` – Automated test suite (pytest)
- `README.md` – Documentation and run instructions
- `Dockerfile` / `.dockerignore` – Container support
- `.usage.json` – Local usage persistence file (ignored by git)


## How to Run

### Local (file-backed usage)
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

### With Redis (shared state across instances)
```bash
export NOVA_REDIS_URL="redis://localhost:6379/0"
./.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```

### Run tests
```bash
./.venv/bin/pytest -q
```


## Configurable Environment Variables

- `NOVA_API_KEY` – legacy single-key mode
- `NOVA_KEYS_JSON` – JSON key registry
- `NOVA_SIGNING_SECRET` – HMAC secret (default: `replace_me`)
- `NOVA_USAGE_FILE` – usage persistence file (default `.usage.json`)
- `NOVA_REDIS_URL` – switch to Redis-backed shared state (recommended for scaling)


## Endpoints

- `GET /health` – health check
- `GET /v1/regime` – regime response (protected)
- `GET /v1/epoch` – epoch hash (protected)
- `GET /v1/context` – guardrail & context (protected)
- `GET /v1/key-info` – authenticated key info (protected)
- `GET /v1/usage` – usage stats (protected)
- `POST /v1/usage/reset` – reset usage (protected)


## Notes

- Usage tracking is persisted (file by default, Redis if `NOVA_REDIS_URL` is set).
- Monthly quota enforcement uses persisted counters.
- Rate limiting uses Redis for shared enforcement when enabled.


## Git Status
All changes are committed locally in the repository.

---

*Generated automatically by the Copilot assistant.*
