import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the alias helper function after the _build_structured_response definition
# (We insert it right before the first major function that comes after it)
content = re.sub(
    r'(def _build_structured_response.*?)(def _temporal_response)',
    r'''\1
    # Soft schema migration: support old keys for backward compatibility
    def _apply_key_aliases(payload: dict) -> dict:
        aliases = {
            "decision_engine": "governance_substrate",
            "decision_layer": "pre-execution_governance_layer",
            "safety_layer": "retained_discipline_layer",
            "guardrails": "retained_discipline_layer",
            "decision_admission": "intent_admissibility",
            "run_a_decision": "evaluate_an_intent",
        }
        for old, new in aliases.items():
            if old in payload:
                payload[new] = payload.pop(old)
        return payload

\2''',
    content,
    flags=re.DOTALL
)

# Call the helper at the end of _build_structured_response
content = re.sub(
    r'(payload = _apply_system_state\(payload, api_key\)\s*'
    r'payload = _apply_human_intervention_taxonomy\(payload\))',
    r'''\1
    payload = _apply_key_aliases(payload)''',
    content
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Key aliases added successfully to app.py")
