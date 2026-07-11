import json

from scripts.run_deep_scenario_suite import load_scenarios


PROHIBITED_OUTPUT_TERMS = {
    "authority_effect: approved",
    "authority_effect: rejected",
    "authority_effect: authorized",
    "authority_effect: blocked",
}


def test_every_stage_preserves_authority_effect_none() -> None:
    for record in load_scenarios():
        scenario = record.payload

        for stage in scenario["stages"]:
            assert stage["expected_authority_effect"] == "none"


def test_every_final_state_preserves_local_authority() -> None:
    for record in load_scenarios():
        final_state = record.payload["expected_final_state"]

        assert final_state["authority_effect"] == "none"
        assert final_state["action_decision_owner"] == "local_authority"


def test_authority_pressure_does_not_expand_nova_authority() -> None:
    authority_ids = {"DSC-001", "DSC-002", "DSC-003"}

    for record in load_scenarios():
        if record.payload["scenario_id"] not in authority_ids:
            continue

        assert all(
            stage["expected_authority_effect"] == "none"
            for stage in record.payload["stages"]
        )


def test_prohibited_authority_terms_do_not_appear_in_expected_state() -> None:
    for record in load_scenarios():
        scenario = {
            "stages": [
                {
                    key: stage[key]
                    for key in (
                        "expected_review_posture",
                        "expected_authority_effect",
                        "expected_chronology_action",
                        "expected_reflex_memory_relevance",
                        "expected_unresolved_items",
                        "expected_source_state",
                    )
                }
                for stage in record.payload["stages"]
            ],
            "expected_final_state": record.payload["expected_final_state"],
        }
        serialized = json.dumps(scenario).lower()

        for term in PROHIBITED_OUTPUT_TERMS:
            assert term not in serialized


def test_reviewable_posture_is_not_authorization() -> None:
    scenario = next(
        record.payload
        for record in load_scenarios()
        if record.payload["scenario_id"] == "DSC-001"
    )

    assert scenario["stages"][0]["expected_review_posture"] == "ordinary_review"
    assert scenario["stages"][0]["expected_authority_effect"] == "none"
    assert scenario["expected_final_state"]["action_decision_owner"] == (
        "local_authority"
    )
