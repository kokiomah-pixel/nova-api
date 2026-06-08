import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any previous broken insertions of _apply_key_aliases
content = re.sub(r'# Soft schema migration:.*?(?=\n\s*def )', '', content, flags=re.DOTALL)
content = re.sub(r'def _apply_key_aliases\(payload: dict\) -> dict:.*?(?=\n\s*def )', '', content, flags=re.DOTALL)
content = re.sub(r'payload = _apply_key_aliases\(payload\)', '', content)

# Insert the helper function at a safe, reliable location (right before _temporal_response)
content = re.sub(
    r'(def _build_structured_response\(.*?\n\n)',
    r'''\1    # Soft schema migration: support old keys for backward compatibility
    def _apply_key_aliases(payload: dict) -> dict:
        """Backward-compatible aliases for old key names."""
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

''',
    content,
    flags=re.DOTALL
)

# Add the call at the correct place (after human intervention taxonomy)
content = re.sub(
    r'(payload = _apply_human_intervention_taxonomy\(payload\))',
    r'''\1
    payload = _apply_key_aliases(payload)''',
    content
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Clean key aliases fix applied")
