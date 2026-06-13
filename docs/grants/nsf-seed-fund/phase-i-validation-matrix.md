# Phase I Validation Matrix

This matrix translates the Phase I research plan into measurable validation work without relying on market-outcome or portfolio metrics.

| Research Question | Validation Method | Metric | Target | Evidence Source |
|---|---|---:|---:|---|
| Can normalized governance inputs produce stable identity? | Deterministic replay suite | Canonical signature consistency | >=99% | governance identity tests |
| Can governance proofs remain reproducible? | Repeated proof generation under identical inputs | Reproducibility hash match rate | >=99% | proof reproducibility tests |
| Can classification remain stable under ambiguous inputs? | Adversarial classification scenarios | Classification consistency rate | >=95% | classification determinism tests |
| Can non-authority boundaries be preserved? | Doctrine lint and scenario review | Boundary violation count | 0 | doctrine lint + decision scenario suite |
| Can autonomous systems consume pre-action context? | Builder integration examples | Working example completion | 3 examples | examples/pre_action_context/ |
| Can builders inspect the pre-action interface? | Contract review and endpoint documentation | Contract-to-endpoint traceability | documented | docs/architecture/pre-action-context-contract.md |
| Can provider-loss continuity be preserved? | Offline decision-intake workflow | Documented continuity completion | successful run | continuity docs/tests |
| Can synthetic and production-like records be separated? | Source segmentation validation | Source segmentation coverage | documented/tested | source segmentation tests |
| Can Reflex selection remain deterministic? | Repeated registry selection tests | Selection stability | 100% deterministic | reflex selection tests |

## Excluded Measures

Phase I should not use market-return, trade-win, portfolio-performance, or prediction-accuracy metrics. Those measures would misclassify Nova as speculative financial tooling rather than pre-execution environmental governance infrastructure.
