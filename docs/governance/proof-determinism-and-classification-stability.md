# Proof Determinism and Classification Stability
## Sharpe Nova OS Governance Hardening Note

---

## Purpose

This note records why Sharpe Nova OS hardens proof determinism, classification stability, canonical signatures, source segmentation, and reflex selection before market-specific or rail-specific expansion.

This pass is governance hardening. It is not execution optimization, trading optimization, payment expansion, or rail-specific product work.

Canonical invariant:

```text
same normalized input -> same canonical signature -> same classification path -> same reproducibility hash
```

Nova's proof layer must be boringly deterministic before external systems can depend on it.

---

## Why Determinism Matters

Proof records are institutional evidence. If identical normalized inputs produce different classifications, proof hashes, or governance record signatures, the proof layer becomes difficult to inspect and weakens trust in Reflex Memory chronology.

Deterministic proof behavior allows operators and downstream reviewers to distinguish between:

- real governance changes
- intentional epoch or schema updates
- registry changes
- accidental runtime drift
- nondeterministic serialization defects

The objective is not to make every decision outcome identical forever. The objective is to ensure that any change in output is caused by a visible input, version, registry, or governance rule change.

---

## Classification Stability

Classification stability means the same normalized request and proof inputs produce the same classification path.

Classification must not depend on:

- dictionary key order
- local runtime timestamps
- generated decision IDs
- mutable iteration ordering
- empty fallback behavior
- environment-specific state
- account naming unless source segmentation is the intended field

When a proof cannot be classified into a stronger closed category, Nova uses an explicit fallback:

```text
unclassified_governance_event
```

An explicit fallback is preferable to an empty classification because it keeps alerting, Reflex Memory, and chronology systems inspectable.

---

## Reproducibility Hash Discipline

Reproducibility hashes must be generated from canonical material only.

Canonical serialization uses stable JSON properties:

```text
sort_keys=True
separators=(",", ":")
ensure_ascii=True where public canonical signatures are computed
```

Runtime-only metadata is excluded from reproducibility hash inputs unless it is explicitly part of the normalized proof input by design.

Excluded runtime metadata includes:

- current timestamp
- generated decision ID
- local storage location
- object memory address
- retrieval audit fields
- proof retrieval timestamp
- runtime-only diagnostics

---

## Reflex Memory Chronology Impact

Reflex Memory depends on stable record grouping. If canonical signatures drift for the same normalized input, Reflex Memory can incorrectly report classification inconsistency, reproducibility failure, or pattern compression.

Stable signatures allow Reflex Memory to answer a simpler question:

```text
Did the governance interpretation change, or did the runtime merely serialize the same event differently?
```

This distinction protects chronology legitimacy.

---

## Allowed Sources of Change

Outputs may intentionally change when a visible governance input changes.

Allowed sources include:

- governance epoch
- registry version
- classification version
- proof schema version
- documented rule version
- explicit normalized input changes

Any intentional change should be visible in the proof input, governance record, registry entry, or chronology record.

---

## Non-Authority Boundary

Proof determinism does not turn Nova into an execution authority.

Nova remains pre-execution environmental governance infrastructure. It emits governance context, proof records, classifications, and telemetry for upstream systems to inspect. It does not move capital, authorize execution, optimize trades, or control agents.

Reflex calibration improves discipline accuracy.

Reflex calibration does not improve trade performance.

---

## Non-Goals

This hardening pass does not implement:

- Arc-specific reflex entries
- Circle-specific metadata
- Arc-specific domain traces
- chain-specific regime labels
- new x402 settlement behavior
- payment processing logic
- do not add trading optimization logic
- portfolio optimization
- execution authorization
- agent control behavior
- prediction language
- outcome-performance tuning

Market-specific rails such as Arc should wait until the proof and classification substrate is hardened. Future machine-native settlement work should be framed as settlement pressure or machine-native settlement pressure, not as Nova identity.

---

## Follow-Up Work

Future hardening may add:

- explicit proof schema version migration records
- registry version identifiers in governance records
- classification version identifiers
- expanded record source provenance
- reproducibility reports across persisted proof archives
- alert calibration around synthetic versus production-like records
