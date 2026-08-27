from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .context_delta import build_context_delta, validate_context_delta
from .schema import validate_retail_context_object
from .sources import (
    validate_source_observation,
    validate_source_registry,
)
from .state_ping import build_state_ping


STATE_PING_REQUEST_FIELDS = frozenset({"subject", "observations", "generated_at"})
CONTEXT_DELTA_REQUEST_FIELDS = frozenset(
    {"previous_context", "current_context", "generated_at"}
)


def canonical_json_bytes(value: object) -> bytes:
    try:
        rendered = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_request") from exc
    return rendered.encode("utf-8")


def retail_request_digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_server_source_registry(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as registry_file:
        registry = json.load(registry_file)
    validate_source_registry(registry)
    return registry


@dataclass(frozen=True)
class PreparedRetailRequest:
    resource_type: str
    request_envelope: Mapping[str, Any]
    request_digest: str
    subject_key: str
    source_entries: tuple[Mapping[str, Any], ...] = ()

    @property
    def resource_uri(self) -> str:
        slug = "state-ping" if self.resource_type == "state_ping" else "context-delta"
        return f"/retail/v1/context/{slug}/{self.request_digest}"

    @property
    def request_id(self) -> str:
        return f"retail-request-{self.request_digest[:24]}"

    def build_resource(self) -> dict[str, Any]:
        envelope = copy.deepcopy(dict(self.request_envelope))
        if self.resource_type == "state_ping":
            resource = build_state_ping(
                envelope["subject"],
                envelope["observations"],
                list(self.source_entries),
                generated_at=envelope["generated_at"],
            )
            validate_retail_context_object(resource)
            return resource
        resource = build_context_delta(
            envelope["previous_context"],
            envelope["current_context"],
            generated_at=envelope["generated_at"],
        )
        validate_context_delta(resource)
        return resource


def prepare_state_ping_request(
    envelope: Mapping[str, Any],
    *,
    source_registry: Mapping[str, Any],
) -> PreparedRetailRequest:
    request = copy.deepcopy(dict(envelope))
    if set(request) != STATE_PING_REQUEST_FIELDS:
        raise ValueError("invalid_state_ping_request")
    if not isinstance(request["subject"], Mapping):
        raise ValueError("invalid_state_ping_request")
    if not isinstance(request["observations"], list) or not request["observations"]:
        raise ValueError("invalid_state_ping_request")
    if not isinstance(request["generated_at"], str):
        raise ValueError("invalid_state_ping_request")
    validate_source_registry(source_registry)
    for observation in request["observations"]:
        if not isinstance(observation, Mapping):
            raise ValueError("invalid_state_ping_request")
        validate_source_observation(observation)
    source_ids = {item["source_id"] for item in request["observations"]}
    selected = tuple(
        copy.deepcopy(item)
        for item in source_registry["sources"]
        if item["source_id"] in source_ids
    )
    prepared = PreparedRetailRequest(
        resource_type="state_ping",
        request_envelope=request,
        request_digest=retail_request_digest(request),
        subject_key=canonical_json_bytes(request["subject"]).decode("utf-8"),
        source_entries=selected,
    )
    prepared.build_resource()
    return prepared


def prepare_context_delta_request(
    envelope: Mapping[str, Any],
) -> PreparedRetailRequest:
    request = copy.deepcopy(dict(envelope))
    if set(request) != CONTEXT_DELTA_REQUEST_FIELDS:
        raise ValueError("invalid_context_delta_request")
    if not isinstance(request["previous_context"], Mapping) or not isinstance(
        request["current_context"], Mapping
    ):
        raise ValueError("invalid_context_delta_request")
    if not isinstance(request["generated_at"], str):
        raise ValueError("invalid_context_delta_request")
    validate_retail_context_object(request["previous_context"])
    validate_retail_context_object(request["current_context"])
    prepared = PreparedRetailRequest(
        resource_type="context_delta",
        request_envelope=request,
        request_digest=retail_request_digest(request),
        subject_key=canonical_json_bytes(request["current_context"]["subject"]).decode(
            "utf-8"
        ),
    )
    prepared.build_resource()
    return prepared
