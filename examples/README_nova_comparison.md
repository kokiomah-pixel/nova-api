# Nova Comparison Agent Demo

This demo compares two agent behaviors on the same scenarios:

- WITHOUT Nova: always executes requested action.
- WITH Nova: calls `/v1/context`, reads `guardrail.action_policy`, then decides `ALLOW`, `CONSTRAIN`, or `VETO`.

These examples demonstrate how Nova conditions decision context.
They do not represent trading signals or execution instructions.

## Run

From the repository root:

```bash
python examples/nova_comparison_agent.py
```

Optional environment overrides:

```bash
export NOVA_API_URL="https://nova-api-ipz6.onrender.com"
export NOVA_API_KEY="your_api_key_here"
python examples/nova_comparison_agent.py
```
