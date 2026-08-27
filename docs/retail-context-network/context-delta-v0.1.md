# Context Delta v0.1

Context Delta is a deterministic, authority-neutral comparison of two already
valid retail context objects. It answers what structurally changed across
bounded evidence-state fields. It does not reacquire evidence, assign economic
meaning, forecast future state, recommend action, or trigger execution.

The dedicated Draft 2020-12 contract is
`specs/retail_context_delta_v0_1.schema.json`. The pure Python entry point is:

```python
build_context_delta(previous_context, current_context, generated_at=...)
```

The function performs no clock read, network call, persistence, provider
access, payment handling, or institutional access.

## Compatibility and validation

Both inputs are validated under RP2 before comparison and must have identical
subjects, schema versions, and resource types. Their authority effect is
therefore necessarily `none`. Duplicate bounded identities fail closed because
they would make ID-keyed comparison ambiguous.

RP5 normally compares State Ping resources. Its fixtures construct those inputs
through the remediated RP4 signature with explicit RP3 source entries that are
configuration-eligible; no source-eligibility boundary is bypassed.

## Structural comparison

The following are material structural changes:

- context-status change
- evidence addition, removal, status change, or bounded content change
- contradiction addition, removal, status change, or bounded content change
- unresolved-evidence addition, removal, status change, or bounded content
  change
- explicit freshness-field or confidence-field change
- provenance source addition/removal or source status, reconciliation status,
  scope, type, or observation-time change
- limitation addition/removal or impact/content change

Each change is recorded in a typed collection and summarized in
`material_changes`. Prior and current evidence states remain distinct. A removed
contradiction, unresolved-evidence item, or limitation is labeled only as
`removed_from_current_bounded_context`; removal never establishes resolution.

No fuzzy matching or semantic interpretation occurs. Evidence,
contradictions, unresolved evidence, provenance, and limitations are compared
only by their stable RP2 identifiers. A content change accompanied by a new ID
therefore appears as removal plus addition.

## Status and determinism

`changed` means at least one bounded material change exists. `unchanged` means
no material field changed and both inputs have a sufficient comparison basis.
`indeterminate` means no structural material change was detected but at least
one input has `insufficient_evidence`. If structural changes exist alongside an
insufficient input, the result remains `changed` and carries an indeterminate
comparison limitation.

Ordering of dictionaries and ID-keyed arrays is non-semantic. Contribution and
evidence-reference scopes are normalized before comparison. Every output array
is sorted by deterministic SHA-256-derived change identity. The resource ID is
derived from directional context identifiers, generated time, and canonical
change content. Swapping inputs therefore reverses additions/removals and
changes the resource identity.

Context Delta always emits `resource_type: context_delta` and
`authority_effect: none`. It introduces no endpoint, payment, price, wallet,
marketplace, live source, or institutional state surface.
