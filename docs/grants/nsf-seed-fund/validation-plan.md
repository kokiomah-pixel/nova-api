# Validation Plan

Sharpe Nova OS validation should measure whether governed pre-action context improves pre-execution review before local authority acts. It should not measure market-return or portfolio outcome claims.

## Candidate Metrics

- classification consistency rate
- reconstruction speed
- source-context clarity
- authority-scope recognition
- reviewer decision quality
- retry/escalation clarity
- replayable governance evidence reproducibility
- doctrine lint pass rate
- non-authority boundary violations
- source segmentation coverage
- continuity test coverage
- deterministic replay success
- offline decision intake completion
- governance epoch documentation coverage

## Excluded Metrics

Nova validation should avoid metrics such as:

- return improvement
- market-edge claims
- trade win rate
- portfolio performance
- prediction accuracy

Those metrics would misrepresent the system. Nova is evaluated as a non-authority pre-execution governance review layer, not as a trading system.

## Validation Activities

Phase I validation should include:

- comparing baseline workflow review against Nova-conditioned workflow review
- replaying synthetic decision-pressure scenarios as the proof mechanism
- checking reproducible proof hashes for equivalent normalized inputs
- testing ambiguous inputs for classification stability
- confirming emitted responses preserve the non-authority boundary
- simulating model-provider loss with offline governance intake
- reviewing examples for execution-authority drift
- running doctrine lint, decision scenarios, and pytest in CI

In the baseline condition, reviewers evaluate intended financial workflow actions using ordinary logs, source notes, and post-hoc context. In the Nova-conditioned condition, reviewers receive structured pre-action context generated before local authority is exercised.
