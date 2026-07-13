# Chronology Reconciliation Runbook

Use this sequence: inventory sources, classify records, identify duplicates, build proposed events, review unresolved fields, obtain approval for exact event IDs, append approved events, validate ledgers, build the master index, generate the cleanliness report, and confirm console consumption.

Run `make chronology-verify PYTHON=.venv/bin/python`, followed by `make verify PYTHON=.venv/bin/python`. Use `reconcile_chronology.py --inspect` for read-only inventory or `--propose --output work/chronology/proposed.yaml` for review material. There is no apply mode.

Imports require a reviewed and authorized manifest, an events JSONL file, `--approved-by Architect`, and `--reviewed-by "Jarvis-Nova CCO"`. Wildcards are prohibited. Reports under `reports/chronology/` are generated and ignored.
