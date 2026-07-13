# Chronology Reconciliation Runbook

Use this sequence: inventory sources, classify records, identify duplicates, build proposed events, review unresolved fields, obtain approval for exact event IDs, append approved events, validate ledgers, build the master index, generate the cleanliness report, and confirm console consumption.

Run `make chronology-verify`, followed by `make verify`. Both commands use the repository `.venv` by default and fail visibly if it is missing. Host Python is not the canonical chronology validation environment. Use `reconcile_chronology.py --inspect` for read-only inventory or `--propose --output work/chronology/proposed.yaml` for review material. There is no apply mode.

The generated report distinguishes the reviewed source branch commit (`source_commit`) from the actual checked-out commit (`ci_checkout_commit`). Pull-request CI records the PR head as the reviewed source and may record GitHub's synthetic merge commit as the checkout. Push-to-main CI records the pushed commit as the reviewed source; its checkout normally matches.

Imports require a reviewed and authorized manifest, an events JSONL file, `--approved-by Architect`, and `--reviewed-by "Jarvis-Nova CCO"`. Wildcards are prohibited. Reports under `reports/chronology/` are generated and ignored.
