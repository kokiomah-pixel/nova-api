from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    create_or_append_chronology_acceptance_ledger_entry,
)


def main() -> int:
    if len(sys.argv) not in {5, 7}:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_chronology_acceptance_ledger.py "
            "<chronology-package-directory> <manual-acceptance-decision-directory> "
            "<manual-movement-plan-directory> <ledger-output-directory> "
            "[reviewer lifecycle_status]",
            file=sys.stderr,
        )
        return 2

    chronology_package_dir = Path(sys.argv[1])
    acceptance_decision_dir = Path(sys.argv[2])
    movement_plan_dir = Path(sys.argv[3])
    ledger_output_dir = Path(sys.argv[4])

    reviewer = None
    lifecycle_status = "planned_for_manual_movement"
    if len(sys.argv) == 7:
        reviewer = sys.argv[5]
        lifecycle_status = sys.argv[6]

    try:
        ledger = create_or_append_chronology_acceptance_ledger_entry(
            chronology_package_dir=chronology_package_dir,
            acceptance_decision_dir=acceptance_decision_dir,
            movement_plan_dir=movement_plan_dir,
            ledger_output_dir=ledger_output_dir,
            reviewer=reviewer,
            lifecycle_status=lifecycle_status,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(ledger, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
