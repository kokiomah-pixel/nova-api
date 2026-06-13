# Proof Replay Example

## Purpose

This conceptual example explains how reviewers can inspect proof determinism without adding a new runtime flow.

Identical normalized governance inputs should produce:

- same canonical signature
- same classification path
- same reproducibility hash

## What To Inspect

Use the existing proof determinism materials:

- [docs/governance/proof-determinism-and-classification-stability.md](../../docs/governance/proof-determinism-and-classification-stability.md)
- [docs/architecture/pre-action-context-contract.md](../../docs/architecture/pre-action-context-contract.md)
- `/v1/proof/{decision_id}` after a `/v1/context` response creates a proof-bearing record

## Boundary

Proof replay verifies governance context and reproducibility. It is not a permission grant, execution instruction, or capital-movement record.

Nova conditions the environment before execution; it does not authorize execution.
