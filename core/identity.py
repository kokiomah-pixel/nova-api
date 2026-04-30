import hashlib
from typing import Optional


ANONYMOUS_ACTOR_ID = "anonymous"


def api_key_from_authorization(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None

    scheme, _, token = authorization.strip().partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def actor_id_from_api_key(api_key: Optional[str]) -> str:
    normalized = (api_key or "").strip()
    if not normalized:
        return ANONYMOUS_ACTOR_ID

    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"actor_{digest}"


def actor_id_from_authorization(authorization: Optional[str]) -> str:
    return actor_id_from_api_key(api_key_from_authorization(authorization))
