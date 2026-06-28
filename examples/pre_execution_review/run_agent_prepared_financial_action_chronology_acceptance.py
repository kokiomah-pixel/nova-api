from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    create_manual_chronology_acceptance_decision,
)


def main() -> int:
    if len(sys.argv) not in {5, 6}:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_chronology_acceptance.py "
            "<chronology-package-directory> <decision-output-directory> "
            "<accepted|rejected|deferred|review_only> <decision-rationale> [reviewer]",
            file=sys.stderr,
        )
        return 2

    chronology_package_dir = Path(sys.argv[1])
    decision_output_dir = Path(sys.argv[2])
    decision_outcome = sys.argv[3]
    decision_rationale = sys.argv[4]
    reviewer = sys.argv[5] if len(sys.argv) == 6 else None

    try:
        decision = create_manual_chronology_acceptance_decision(
            chronology_package_dir=chronology_package_dir,
            decision_output_dir=decision_output_dir,
            decision_outcome=decision_outcome,
            decision_rationale=decision_rationale,
            reviewer=reviewer,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
