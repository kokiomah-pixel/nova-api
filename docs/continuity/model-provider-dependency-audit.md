# Model Provider Dependency Audit

## Scope

This audit validates that Sharpe Nova OS can continue operating as a governance, telemetry, chronology, and decision-intake infrastructure layer if OpenAI access is unavailable.

Search terms used:

- `OPENAI_API_KEY`
- `openai`
- `OpenAI`
- `ChatGPT`
- `GPT`
- `LLM`
- `model provider`
- `assistant`
- `Jarvis-Nova`

Search command:

```bash
rg -n -i --hidden -g '!/.git/**' -g '!/.venv/**' -g '!__pycache__/**' "OPENAI_API_KEY|openai|ChatGPT|GPT|LLM|model provider|assistant|Jarvis-Nova" .
```

## Reference Classification

| File | Reference | Classification | Notes |
| --- | --- | --- | --- |
| `docs/openai_workspace_agents.md` | OpenAI workspace agents | optional reasoning interface | Documents how workspace agents may propose actions while Nova remains model-agnostic and binding for intent admissibility. |
| `docs/openai_workspace_agents.md` | OpenAI in title | documentation reference | Documentation label only; no runtime import or required API key. |
| `doctrine-alignment-report.md` | Jarvis-Nova Chief Coherence Officer | documentation reference | Review/audit role language only. |
| `unresolved-risks-and-actions.md` | Jarvis-Nova Chief Coherence Officer | documentation reference | Follow-up ownership language only. |
| `scripts/doctrine_lint.py` | `GITHUB_TOKEN_PATTERN.search` | safe/no action needed | Contains the uppercase substring `GPT` inside `GITHUB`; this is a false-positive match from the search pattern. |
| `scripts/doctrine_lint.py` | hex regex `fullmatch` | safe/no action needed | Contains the lowercase substring `llm` inside `fullmatch`; this is a false-positive match from the search pattern. |
| `core/billing_state.py` | wallet regex `fullmatch` | safe/no action needed | Contains the lowercase substring `llm` inside `fullmatch`; this is a false-positive match from the search pattern. |
| `README.md` | Model Provider Independence section | documentation reference | Continuity note added by this audit. |
| `docs/continuity/model-provider-independence-protocol.md` | OpenAI/model provider/Jarvis-Nova references | documentation reference | Defines provider independence operating modes and continuity boundaries. |
| `docs/continuity/model-provider-dependency-audit.md` | search terms and classifications | documentation reference | This audit artifact. |
| `tests/test_model_provider_independence.py` | `OPENAI_API_KEY` unset behavior | test-only reference | Confirms core governance utilities remain usable with the provider key absent. |

## Continuity Artifacts Added

- `docs/continuity/model-provider-independence-protocol.md`
- `docs/continuity/offline-decision-intake-template.md`
- `docs/continuity/model-provider-dependency-audit.md`
- `tests/test_model_provider_independence.py`

## Workspace Continuity Reference

The May 25 to June 11, 2026 Business workspace deactivation confirmed why model-provider independence and workspace continuity must be treated as separate but related continuity layers.

Model-provider independence protects reasoning continuity.

Workspace continuity protects operating-environment availability.

## Runtime Dependency Finding

No required runtime dependency on OpenAI was found in the core Nova API, governance runtime, telemetry engine, decision-intake scenario suite, x402 observability helpers, billing state, proof layer, or doctrine lint tooling.

The existing OpenAI-specific documentation describes an optional reasoning interface. It does not introduce a required account, API key, model provider SDK, import, endpoint dependency, or execution path for core governance behavior.

## Test Dependency Finding

No required test dependency on OpenAI was found.

The added model-provider independence test clears `OPENAI_API_KEY` and validates that deterministic governance utilities remain usable:

- doctrine lint text scanning
- decision scenario library loading and processing
- x402 observability event creation

## Remediation

No code remediation is required.

OpenAI support and OpenAI-facing documentation should remain available as optional reasoning-interface guidance. The current boundary is documentation-only and does not block degraded governance operation.

Recommended ongoing practice:

- keep provider-specific integrations isolated from deterministic governance paths
- avoid adding required model-provider imports to core governance modules
- keep API keys out of tests, docs, and repository state
- preserve offline templates and chronology procedures for provider outage periods

## Final Continuity Conclusion

Sharpe Nova OS can preserve operating doctrine without OpenAI access.

GitHub is the durable archive. OpenAI is an optional reasoning interface. Nova's sovereign continuity lives in doctrine, telemetry, chronology, tests, scenario logic, x402 observability, security protocol, and governance discipline.
