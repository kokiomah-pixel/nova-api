#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "agent_files/state/accepted-state-registry.yaml"
SCHEMA_PATH = ROOT / "schemas/accepted-state-registry.schema.json"


class AcceptedStateRegistryError(ValueError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AcceptedStateRegistryError(f"Registry must be a YAML object: {path}")
    return payload


def _git_resolves(commit: str) -> bool:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "-t", commit],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0 and completed.stdout.strip() == "commit"


def validate_registry(
    path: Path = REGISTRY_PATH,
    *,
    require_resolvable_commits: bool = True,
) -> dict[str, Any]:
    registry = _load_yaml(path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(registry), key=lambda error: list(error.path))
    if errors:
        joined = "; ".join(error.message for error in errors)
        raise AcceptedStateRegistryError(joined)

    ids = [entry["accepted_state_id"] for entry in registry["entries"]]
    if len(ids) != len(set(ids)):
        raise AcceptedStateRegistryError("Duplicate accepted_state_id")

    for entry in registry["entries"]:
        review = entry["review_authority"]
        if entry["classification"]["status"] == "accepted" and not (
            review["Architect_reviewed"] or review["CCO_reviewed"]
        ):
            raise AcceptedStateRegistryError(
                f"{entry['accepted_state_id']} lacks explicit review authority"
            )
        excluded = set(entry["excluded_claims"])
        for required in {
            "production readiness",
            "external comprehension",
            "buyer adoption",
            "Stage_B_activation",
        }:
            if required not in excluded:
                raise AcceptedStateRegistryError(
                    f"{entry['accepted_state_id']} does not preserve excluded claim: {required}"
                )
        if require_resolvable_commits:
            for label, commit in entry["source"]["merge_commits"].items():
                if not _git_resolves(commit):
                    raise AcceptedStateRegistryError(
                        f"{entry['accepted_state_id']} source commit does not resolve: {label}"
                    )
    return {
        "status": "passed",
        "registry_path": str(path.relative_to(ROOT)),
        "accepted_state_ids": ids,
        "entry_count": len(ids),
    }


def main() -> None:
    print(json.dumps(validate_registry(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
