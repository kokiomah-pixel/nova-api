from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.reflex_memory.replay import build_reflex_memory_replay


def main() -> None:
    replay = build_reflex_memory_replay()
    print(json.dumps(replay, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
