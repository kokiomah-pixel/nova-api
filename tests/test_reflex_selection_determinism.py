from core.reflex_memory.registry import build_registry, select_active_entry


def test_reflex_selection_is_deterministic_for_same_regime_and_intent():
    registry = build_registry("Elevated Fragility")

    selected = [
        select_active_entry(registry=list(reversed(registry)), intent="trade", size=10000)
        for _ in range(5)
    ]

    assert [entry.registry_id for entry in selected if entry] == ["elevated_fragility_size_brake"] * 5


def test_reflex_selection_uses_canonical_priority_when_multiple_entries_apply():
    combined_registry = build_registry("Elevated Fragility") + build_registry("Stress")

    selected = select_active_entry(registry=list(reversed(combined_registry)), intent="trade", size=10000)

    assert selected is not None
    assert selected.registry_id == "stress_new_risk_block"
