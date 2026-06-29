from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    summarize_chronology_acceptance_ledger,
)


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_chronology_lifecycle_report.py "
            "<chronology-acceptance-ledger-directory> <report-output-directory> "
            "[reviewer]",
            file=sys.stderr,
        )
        return 2

    ledger_dir = Path(sys.argv[1])
    report_output_dir = Path(sys.argv[2])
    reviewer = sys.argv[3] if len(sys.argv) == 4 else None

    try:
        report = summarize_chronology_acceptance_ledger(
            ledger_dir=ledger_dir,
            report_output_dir=report_output_dir,
            reviewer=reviewer,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
