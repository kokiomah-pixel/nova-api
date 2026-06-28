from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    AgentPreparedFinancialAction,
    build_governance_record,
    review_agent_prepared_action,
)


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_review.py "
            "<path-to-agent-prepared-action-json>",
            file=sys.stderr,
        )
        return 2

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2

    data = json.loads(input_path.read_text(encoding="utf-8"))
    action = AgentPreparedFinancialAction.from_dict(data)
    review = review_agent_prepared_action(action)
    governance_record = build_governance_record(action, review)

    output = {
        "review": review.to_dict(),
        "governance_record": governance_record,
    }

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

