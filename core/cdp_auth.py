from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

from cdp.auth.utils.jwt import JwtOptions, generate_jwt
from x402.http.facilitator_client_base import AuthHeaders, AuthProvider


CDP_API_KEY_ID_ENV = "CDP_API_KEY_ID"
CDP_API_KEY_SECRET_ENV = "CDP_API_KEY_SECRET"
PLACEHOLDER_PREFIX = "PASTE_"


@dataclass(frozen=True)
class CDPCredentials:
    api_key_id: str
    api_key_secret: str


def load_cdp_credentials_from_env() -> CDPCredentials:
    api_key_id = os.getenv(CDP_API_KEY_ID_ENV, "").strip()
    api_key_secret = os.getenv(CDP_API_KEY_SECRET_ENV, "").strip()
    missing = [
        name
        for name, value in (
            (CDP_API_KEY_ID_ENV, api_key_id),
            (CDP_API_KEY_SECRET_ENV, api_key_secret),
        )
        if not value or PLACEHOLDER_PREFIX in value
    ]
    if missing:
        raise RuntimeError(
            f"Missing or placeholder env vars: {', '.join(missing)}"
        )
    return CDPCredentials(api_key_id=api_key_id, api_key_secret=api_key_secret)


class CDPFacilitatorAuthProvider(AuthProvider):
    def __init__(self, *, api_key_id: str, api_key_secret: str, facilitator_url: str) -> None:
        parsed = urlparse(facilitator_url)
        self._api_key_id = api_key_id
        self._api_key_secret = api_key_secret
        self._request_host = parsed.netloc
        self._base_path = parsed.path.rstrip("/")

    def _headers_for(self, *, method: str, suffix: str) -> Dict[str, str]:
        request_path = f"{self._base_path}/{suffix.lstrip('/')}"
        token = generate_jwt(
            JwtOptions(
                api_key_id=self._api_key_id,
                api_key_secret=self._api_key_secret,
                request_method=method,
                request_host=self._request_host,
                request_path=request_path,
                expires_in=120,
            )
        )
        return {"Authorization": f"Bearer {token}"}

    def get_auth_headers(self) -> AuthHeaders:
        return AuthHeaders(
            verify=self._headers_for(method="POST", suffix="verify"),
            settle=self._headers_for(method="POST", suffix="settle"),
            supported=self._headers_for(method="GET", suffix="supported"),
        )


def build_cdp_auth_provider_from_env(*, facilitator_url: str) -> CDPFacilitatorAuthProvider:
    credentials = load_cdp_credentials_from_env()
    return CDPFacilitatorAuthProvider(
        api_key_id=credentials.api_key_id,
        api_key_secret=credentials.api_key_secret,
        facilitator_url=facilitator_url,
    )
