from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/chronology-event.schema.json"
LANE_PATHS = {
    "reflex": ROOT / "chronology/reflex/reflex-events.jsonl",
    "archive": ROOT / "chronology/archive/archive-events.jsonl",
    "operations": ROOT / "chronology/operations/operational-events.jsonl",
    "governance": ROOT / "chronology/governance/governance-events.jsonl",
}
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ChronologyError(ValueError):
    """Raised when chronology evidence is malformed or unsafe."""


class ChronologyProvenanceError(RuntimeError):
    """Raised when chronology evidence provenance is invalid."""


def git_commit(root: Path, revision: str = "HEAD") -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", revision],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ChronologyProvenanceError(
            completed.stderr.strip() or f"Unable to resolve Git revision: {revision}"
        )
    commit = completed.stdout.strip().lower()
    if not FULL_SHA_PATTERN.fullmatch(commit):
        raise ChronologyProvenanceError(
            f"Invalid Git commit resolved for {revision}: {commit!r}"
        )
    return commit


def validate_full_commit(value: str, *, field_name: str) -> str:
    commit = value.strip().lower()
    if not FULL_SHA_PATTERN.fullmatch(commit):
        raise ChronologyProvenanceError(
            f"{field_name} must be a 40-character lowercase Git SHA"
        )
    return commit


def resolve_reviewed_source_commit(root: Path) -> str:
    explicit = os.environ.get("NOVA_REVIEWED_SOURCE_COMMIT", "").strip()
    if explicit:
        return validate_full_commit(
            explicit, field_name="NOVA_REVIEWED_SOURCE_COMMIT"
        )
    return git_commit(root, "HEAD")


def resolve_ci_checkout_commit(root: Path) -> str:
    explicit = os.environ.get("NOVA_CI_CHECKOUT_COMMIT", "").strip()
    if explicit:
        return validate_full_commit(explicit, field_name="NOVA_CI_CHECKOUT_COMMIT")
    return git_commit(root, "HEAD")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not path.exists():
        raise ChronologyError(f"Missing chronology ledger: {path.relative_to(ROOT)}")
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ChronologyError(f"Malformed JSONL at {path.name}:{number}") from exc
        if not isinstance(value, dict):
            raise ChronologyError(f"Chronology event must be an object at {path.name}:{number}")
        events.append(value)
    return events


def ordered(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(events, key=lambda event: (event["occurred_at"], event["event_id"]))


def write_jsonl_new(path: Path, events: Iterable[dict[str, Any]]) -> None:
    if path.exists():
        raise ChronologyError(f"Refusing to overwrite chronology ledger: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in ordered(events)), encoding="utf-8")


def append_jsonl(path: Path, events: Iterable[dict[str, Any]]) -> None:
    existing = read_jsonl(path)
    additions = list(events)
    ids = {event["event_id"] for event in existing}
    if ids.intersection(event["event_id"] for event in additions):
        raise ChronologyError("Duplicate chronology event ID")
    with path.open("a", encoding="utf-8") as handle:
        for event in ordered(additions):
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ChronologyError(f"Invalid timestamp: {value}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
