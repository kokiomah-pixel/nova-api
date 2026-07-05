from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.reflex_memory.context import build_reflex_memory_context

PACKAGE_PATH = ROOT / "examples" / "agent_prepared_action" / "agent_prepared_treasury_action.json"


def load_agent_package() -> dict[str, Any]:
    with PACKAGE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_review_context_from_agent_package(package: dict[str, Any]) -> dict[str, Any]:
    """Build a bounded review-context example from an agent-prepared action package.

    This is not an execution instruction.
    This is not an approval, denial, authorization, routing, settlement, signing,
    compliance review, audit report, wallet action, or agent supervision layer.
    """
    return {
        "context_id": "CTX-AGENT-PREPARED-0001",
        "context_type": "pre_action_review_context",
        "source_package_id": package["package_id"],
        "canonical_boundary": [
            "Agent prepares action.",
            "Nova structures review context.",
            "Local authority decides.",
            "Nova does not execute.",
        ],
        "prepared_action": package["prepared_action"],
        "source_context": package["source_context"],
        "authority_context": package["authority_context"],
        "review_requirements": package["review_requirements"],
        "reflex_memory_context": build_reflex_memory_context(),
        "local_authority": {
            "decision_responsibility": "local_authority",
            "nova_authority": "none",
            "agent_authority": package["authority_context"]["agent_authority"],
            "execution_layer": "external",
        },
        "review_readiness": {
            "prepared_action_present": True,
            "source_context_present": bool(package.get("source_context")),
            "authority_context_present": bool(package.get("authority_context")),
            "reflex_memory_context_present": True,
            "execution_status": "not_executed",
        },
        "non_authority_statement": (
            "This output is governed review context only. It is not approval, denial, "
            "authorization, blocking, routing, settlement, signing, execution, compliance "
            "review, audit reporting, wallet control, agent supervision, or local authority replacement."
        ),
    }


def main() -> None:
    package = load_agent_package()
    context = build_review_context_from_agent_package(package)
    print(json.dumps(context, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
