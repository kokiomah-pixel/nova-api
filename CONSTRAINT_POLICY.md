# Constraint Policy

Sharpe Nova OS defines denial-first decision states at the pre-execution boundary.

## Policy Intent

- make incorrect usage harder
- make correct usage obvious
- preserve a stable interface for humans and machines

## Policy Rules

- Decisions must be submitted through the Nova API.
- API output is authoritative for admission state.
- Refusal states are non-admissible decision states.
- Downstream integrations must bind execution behavior to those states.
- Governance layers must not be bypassed through examples or helper scripts.
- Interpretations that reclassify Nova as a trading or execution system are out of policy.

## Refusal Semantics

- `ALLOW`: decision may proceed downstream
- `CONSTRAIN`: decision may proceed only under the returned constraints
- `DELAY`: decision is held pending admissibility conditions
- `DENY`: decision is not admissible
- `HALT`: admission is suspended pending restored integrity

## Repository Policy

- `docs/` explains behavior and boundary
- `specs/` defines stable machine-readable contracts
- `examples/` must submit decisions and bind to non-admissible states
- `tests/` verify the contract surface
