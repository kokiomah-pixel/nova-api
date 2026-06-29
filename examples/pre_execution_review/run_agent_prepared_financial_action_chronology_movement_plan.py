from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    create_accepted_records_manual_movement_plan,
)


def main() -> int:
    if len(sys.argv) not in {5, 6}:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_chronology_movement_plan.py "
            "<chronology-package-directory> <manual-acceptance-decision-directory> "
            "<movement-plan-output-directory> <proposed-chronology-root-path> "
            "[reviewer]",
            file=sys.stderr,
        )
        return 2

    chronology_package_dir = Path(sys.argv[1])
    acceptance_decision_dir = Path(sys.argv[2])
    movement_plan_output_dir = Path(sys.argv[3])
    proposed_chronology_root_path = Path(sys.argv[4])
    reviewer = sys.argv[5] if len(sys.argv) == 6 else None

    try:
        plan = create_accepted_records_manual_movement_plan(
            chronology_package_dir=chronology_package_dir,
            acceptance_decision_dir=acceptance_decision_dir,
            movement_plan_output_dir=movement_plan_output_dir,
            proposed_chronology_root_path=proposed_chronology_root_path,
            reviewer=reviewer,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
