# Proof Layer Integration

`/v1/context` returns a pre-action context record.

`/v1/proof/{decision_id}` verifies the emitted context state with proof-backed governance fields.

## Required Fields

- decision_id
- decision_status
- constraint_effect
- intervention_type
- failure_class
- reproducibility_hash

## Usage

- audit verification
- governance tracking
- proof-backed review of the emitted context state

Execution authority remains outside Nova.

Proof may inform audit and downstream review, but it does not authorize action.
