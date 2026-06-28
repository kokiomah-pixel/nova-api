from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nova.harnesses.agent_prepared_financial_action_review import (  # noqa: E402
    build_chronology_ingestion_package,
)


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: python examples/pre_execution_review/"
            "run_agent_prepared_financial_action_chronology_package.py "
            "<v0.3-export-directory> <chronology-package-output-directory>",
            file=sys.stderr,
        )
        return 2

    export_dir = Path(sys.argv[1])
    package_dir = Path(sys.argv[2])

    if not export_dir.exists():
        print(f"Export directory not found: {export_dir}", file=sys.stderr)
        return 2

    if not export_dir.is_dir():
        print(f"Export path is not a directory: {export_dir}", file=sys.stderr)
        return 2

    manifest = build_chronology_ingestion_package(export_dir, package_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
