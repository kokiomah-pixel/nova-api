# Allocator Entry

Sharpe Nova OS should be integrated as a capital conditioning layer ahead of execution.

## Allocator Role

Allocators use Nova to determine whether a proposed capital action is admissible before capital moves.

## Operating Rule

- submit the decision through the API
- read `decision_status`
- retain `decision_id`
- retrieve `/v1/proof/{decision_id}` when audit evidence is required
- bind downstream behavior to the returned state

## Do Not Treat Nova As

- a source of signals
- a ranking engine
- an execution venue

The correct question is not "what should I buy?"

The correct question is "may this decision proceed under current constraints?"
