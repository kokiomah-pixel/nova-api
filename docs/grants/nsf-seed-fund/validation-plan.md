# Validation Plan

Sharpe Nova OS validation should measure governance reliability, boundary preservation, reproducibility, and continuity. It should not measure market-return or portfolio outcome claims.

## Candidate Metrics

- classification consistency rate
- proof reproducibility rate
- scenario suite pass rate
- doctrine lint pass rate
- non-authority boundary violations
- source segmentation coverage
- continuity test coverage
- deterministic replay success
- orchestration pacing example completion
- offline decision intake completion
- governance epoch documentation coverage

## Excluded Metrics

Nova validation should avoid metrics such as:

- return improvement
- market-edge claims
- trade win rate
- portfolio performance
- prediction accuracy

Those metrics would misrepresent the system. Nova is evaluated as pre-execution environmental governance infrastructure, not as a trading system.

## Validation Activities

Phase I validation should include:

- replaying synthetic decision-pressure scenarios
- checking reproducible proof hashes for equivalent normalized inputs
- testing ambiguous inputs for classification stability
- confirming emitted responses preserve the non-authority boundary
- simulating model-provider loss with offline governance intake
- reviewing examples for execution-authority drift
- running doctrine lint, decision scenarios, and pytest in CI
