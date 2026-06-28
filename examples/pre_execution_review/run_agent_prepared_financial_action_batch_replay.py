from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    run_batch_replay_for_directory,
)


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_batch_replay.py "
            "<path-to-directory-containing-json-records>",
            file=sys.stderr,
        )
        return 2

    input_dir = Path(sys.argv[1])

    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        return 2

    if not input_dir.is_dir():
        print(f"Input path is not a directory: {input_dir}", file=sys.stderr)
        return 2

    output = run_batch_replay_for_directory(input_dir)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

