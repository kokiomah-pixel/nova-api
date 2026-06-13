# Contributing

Thank you for contributing to Sharpe Nova OS. Contributions should preserve the system's role as pre-execution environmental governance infrastructure.

## Doctrine Boundaries

Contributions must preserve these boundaries:

- Nova does not authorize execution.
- Nova does not move capital.
- Nova does not provide trading signals.
- Nova does not optimize portfolios.
- Nova emits environmental state for local operators, agents, and orchestration systems to consume before making their own decisions.

Avoid adding examples, field names, docs, or tests that imply Nova grants permission, approves decisions, executes orders, or recommends trades.

## Required Checks

Before opening a pull request, run:

```bash
./.venv/bin/python scripts/doctrine_lint.py
./.venv/bin/python scripts/run_decision_scenario_suite.py
./.venv/bin/python -m pytest
git diff --check
```

Keep changes narrowly scoped and document governance-boundary changes in the relevant docs.

