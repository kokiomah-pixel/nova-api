from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.x402_config import X402_FACILITATOR_URL
from core.cdp_auth import build_cdp_auth_provider_from_env


def _bool_text(value: bool) -> str:
    return "yes" if value else "no"


def _safe_error(response: httpx.Response) -> str:
    if not response.text:
        return "none"
    try:
        body: Any = response.json()
    except Exception:
        return "non_json_response"

    if isinstance(body, dict):
        detail = body.get("detail") or body.get("error") or body.get("message")
        return str(detail).strip() if detail else "none"
    return "none"


def main() -> int:
    try:
        auth_provider = build_cdp_auth_provider_from_env(
            facilitator_url=X402_FACILITATOR_URL,
        )
        auth_headers = auth_provider.get_auth_headers()
    except Exception as exc:
        print("cdp_auth_probe_attempted: no")
        print("cdp_auth_accepted: no")
        print("auth_failure_still_401: no")
        print("probe_endpoint: none")
        print("probe_http_status: 0")
        print(f"probe_error: {exc}")
        return 2

    attempted = False
    accepted = False
    auth_401 = False
    endpoint = "supported"
    status = 0
    error = "none"

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        attempted = True
        supported_response = client.get(
            f"{X402_FACILITATOR_URL.rstrip('/')}/supported",
            headers=auth_headers.supported,
        )
        status = supported_response.status_code
        error = _safe_error(supported_response)

        if status == 401:
            auth_401 = True
        elif 200 <= status < 300:
            accepted = True
        else:
            endpoint = "verify_invalid_payload"
            verify_response = client.post(
                f"{X402_FACILITATOR_URL.rstrip('/')}/verify",
                headers=auth_headers.verify,
                json={"paymentPayload": {}, "paymentRequirements": {}},
            )
            status = verify_response.status_code
            error = _safe_error(verify_response)
            if status == 401:
                auth_401 = True
            elif status in {400, 404, 405, 415, 422} or 200 <= status < 300:
                accepted = True

    print(f"cdp_auth_probe_attempted: {_bool_text(attempted)}")
    print(f"cdp_auth_accepted: {_bool_text(accepted)}")
    print(f"auth_failure_still_401: {_bool_text(auth_401)}")
    print(f"probe_endpoint: {endpoint}")
    print(f"probe_http_status: {status}")
    print(f"probe_error: {error}")

    return 0 if accepted and not auth_401 else 1


if __name__ == "__main__":
    raise SystemExit(main())
