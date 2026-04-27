# Sharpe Nova OS

Sharpe Nova OS is a pre-execution decision admissibility layer that defines the governed state of a proposed capital decision before execution.

This repository is the canonical Sharpe Nova OS system repo. It contains the Nova API, proof layer, governance runtime, canonical specs, tests, and runnable examples.

## Canonical Decision Contract

- `/v1/context` returns a Decision Admission Record and authoritative `decision_status`
- `/v1/proof/{decision_id}` verifies the governed decision state with proof-backed governance fields

Nova is authoritative and auditable. Downstream systems must bind execution behavior to the decision state returned by `/v1/context`.

```text
Decision Proposed -> Nova -> Decision Admitted -> Execution
```

If the decision is not admitted, execution does not occur.

## What Lives Here

- API implementation and runtime behavior
- proof generation and retrieval
- governance specifications and system contracts
- tests for decision admission and proof integrity
- examples showing one-decision flows and integration behavior

## What Nova Is Not

Nova is not an execution engine, strategy system, signal engine, or generic toolkit. It does not move capital on its own. It determines whether a proposed capital action is admitted, constrained, delayed, denied, halted, or vetoed before execution can occur.

## Start Here (Required)

Start the API from the repository root:

```bash
NOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

Before reading further, run one decision through Nova:

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/context?intent=allocate&asset=ETH&size=10000"
```

Then retrieve proof using the returned `decision_id`:

```bash
curl -s -H "Authorization: Bearer mytestkey" \
"http://127.0.0.1:8000/v1/proof/<decision_id>"
```

Read `decision_status` first. It is the decision authority. Supporting fields explain the state; they do not override it.

If the response returns `CONSTRAIN`, apply the governed adjustment before any execution step. If the response returns `DENY`, `DELAY`, `HALT`, or `VETO`, the decision is not admissible and execution must not proceed.

### Why this is required

If you do not run this:

- you will not see `decision_status`
- you will not observe constraint vs admission
- you will not understand how proof verifies outcomes

Nova is not understood through description.

Nova is understood when it defines:

> **what the system is allowed to do before execution.**

### Instruction

Run the command. Observe the result.

Only then continue reading.

## End-to-End Decision Flow

See a complete example of decision admission, decision-state binding, and proof:

[examples/nova_end_to_end_decision_flow.md](examples/nova_end_to_end_decision_flow.md)

## Read Next

1. [START_HERE.md](START_HERE.md)
2. [docs/overview.md](docs/overview.md)
3. [docs/integration_entry.md](docs/integration_entry.md)
4. [docs/telemetry_reframe.md](docs/telemetry_reframe.md)
5. [specs/decision_admission_contract.json](specs/decision_admission_contract.json)

For developer integration doctrine, see:
https://github.com/kokiomah-pixel/nova-developer-docs
