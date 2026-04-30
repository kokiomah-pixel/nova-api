# Sharpe Nova OS

Sharpe Nova OS is a pre-execution decision admissibility layer that defines the governed state of a proposed capital decision before execution.

This repository is the canonical Sharpe Nova OS system repo. It contains the Nova API, proof layer, governance runtime, canonical specs, tests, and runnable examples.

## Start Here (Required)

Before reading further, run one decision through Nova.
Nova is not understood through explanation.
Nova is understood when a proposed decision receives an authoritative decision state before execution.

### 1. Start Nova Locally

```bash
NOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

### 2. Submit One Decision

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=allocate&asset=ETH&size=10000"
```

### 3. Read the Authority Field

Bind execution behavior to:

```text
decision_status
```

Execution rules:

```text
ALLOW -> proceed
CONSTRAIN -> apply governed adjustment before execution
DENY / DELAY / HALT / VETO -> do not execute
```

Supporting fields may explain the outcome.

They do not define permission.

### 4. Retrieve Proof

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/proof/<decision_id>"
```

Proof verifies the governed outcome.

Proof does not grant permission.

### Required Interpretation

Nova is not a callable helper module.

Nova is a pre-execution decision admission layer.

If a decision is not admitted by Nova, execution must not proceed.

Continue only after running the decision and observing `decision_status`.

## What Lives Here

- API implementation and runtime behavior
- proof generation and retrieval
- governance specifications and system contracts
- tests for decision admission and proof integrity
- examples showing one-decision flows and integration behavior

## What Nova Is Not

Nova is not an execution engine, strategy system, signal engine, or generic toolkit. It does not move capital on its own. It determines whether a proposed capital action is admitted, constrained, delayed, denied, halted, or vetoed before execution can occur.

## End-to-End Decision Flow

See a complete example of decision admission, decision-state binding, and proof:

[examples/nova_end_to_end_decision_flow.md](examples/nova_end_to_end_decision_flow.md)

For a controlled enforcement example, see [examples/README_controlled_execution_loop.md](examples/README_controlled_execution_loop.md).

## Read Next

1. [START_HERE.md](START_HERE.md)
2. [docs/overview.md](docs/overview.md)
3. [docs/integration_entry.md](docs/integration_entry.md)
4. [docs/telemetry_reframe.md](docs/telemetry_reframe.md)
5. [specs/decision_admission_contract.json](specs/decision_admission_contract.json)

For developer integration doctrine, see:
https://github.com/kokiomah-pixel/nova-developer-docs
