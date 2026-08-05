# Public-Surface Coherence Standard

## Public state precedence

```yaml
public_state_precedence:
  1: CURRENT_STATE.md
  2: docs/operations/production-readiness-register.md
  3: docs/target-v2/README.md
  4: README.md
  5: docs/start-here.md
  6: specialized_current_documents
  7: historical_or_Legacy_documents
```

## Current-state claim rules

1. “Ready” must name the exact gate or layer.
2. “Implemented” must name the product generation and component.
3. “Live” requires a dated deployment and control-plane evidence reference.
4. “Production” requires a dated production-attestation reference.
5. “Customer,” “adoption,” “buyer pull,” and “pricing power” require admissible external evidence.
6. Historical claims must remain inside clearly labeled historical documents.
7. Legacy implementation must not be presented as target v2 implementation.
8. Repository validation must not be presented as production validation.
9. Offline proof must not be presented as deployed integration.
10. Metering code must not be presented as current commercial validation.

## Prohibited unqualified current claims

Current public entry surfaces must not use these phrases without the evidence
and layer qualification required above:

```text
GTM-Ready
operationally live
production-ready
institutionally production-ready
monetization implemented
technically operational
deployed and operational
customer validated
market validated
```

Historical archives may preserve those phrases only when an explicit
supersession banner appears, the evidence period is identified, the current
state source is linked, and the claim cannot be mistaken for current status.
