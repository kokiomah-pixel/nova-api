# Integration Patterns

Examples in this repository are controlled integration patterns for Sharpe Nova OS.

## Required Example Behavior

- submit decisions to the Nova API
- read authoritative `decision_status`
- retain `decision_id`
- retrieve `/v1/proof/{decision_id}` when audit evidence is required
- bind behavior to non-admissible states
- preserve the authoritative decision-state surface

## Prohibited Example Behavior

- execute trades
- optimize strategies
- bypass governance
- treat refusal states as non-binding
- derive alternate permission from supporting fields

## Current Example Set

- `hyperliquid_nova_enforcement_adapter.py`: demonstrates downstream binding to non-admissible decision states
- `governance_key_profiles.json`: demonstrates governed environment profiles

Other examples should be read only if they preserve the same contract discipline.
