# Allocator Entry

Sharpe Nova OS should be integrated as a non-authority pre-execution governance review layer.

## Allocator Role

Allocators use Nova to inspect governed review context before local authority decides whether and how a proposed capital action proceeds elsewhere.

## Operating Rule

- submit the intended action context through the API
- read `decision_status`
- retain `decision_id`
- retrieve `/v1/proof/{decision_id}` when audit evidence is required
- bind downstream behavior to local governance rules after reviewing Nova's context

## Do Not Treat Nova As

- a source of signals
- a ranking engine
- an execution venue
- a bypassable suggestion
- an approval or authority layer

The correct question is not "what should I buy?"

The correct question is "what review context does Nova surface before local authority acts?"
