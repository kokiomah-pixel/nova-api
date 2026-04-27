# Nova Comparison Agent Demo

This demo compares two agent behaviors on the same scenarios:

- WITHOUT Nova: always executes requested action.
- WITH Nova: calls `/v1/context`, binds to authoritative `decision_status`, and applies returned constraints before any execution step.

These examples demonstrate how Nova defines the admissible state of a proposed decision.
They do not represent trading signals, advisory outputs, or execution instructions.

## Run

From the repository root:

```bash
./.venv/bin/python examples/nova_comparison_agent.py
```

Optional environment overrides:

```bash
export NOVA_API_URL="https://nova-api-ipz6.onrender.com"
export NOVA_API_KEY="your_api_key_here"
./.venv/bin/python examples/nova_comparison_agent.py
```
