"""Small command-line surface for the bounded NSF demo."""
from __future__ import annotations

import json

from review_state_compiler import compile_review_state


def main() -> None:
    print(json.dumps(compile_review_state(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
