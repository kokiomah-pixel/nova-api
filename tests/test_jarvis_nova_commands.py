from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import yaml

from scripts.jarvis_nova_commands import main
from scripts.validate_cco_operating_spine import PRIORITY_REGISTER_PATH, REPO_ROOT


ASSESSMENT_FIXTURE = (
    REPO_ROOT / "tests/fixtures/cco/valid-minimal-system-need-assessment.yaml"
)


def _assessment() -> dict:
    return yaml.safe_load(ASSESSMENT_FIXTURE.read_text(encoding="utf-8"))


def _operational_assessment() -> dict:
    document = _assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["record_source_type"] = "operational_assessment"
    assessment["operational_evidence_eligible"] = True
    return document


def _register_with_one_item() -> dict:
    register = yaml.safe_load(
        (REPO_ROOT / PRIORITY_REGISTER_PATH).read_text(encoding="utf-8")
    )
    register["items"] = [register["items"][0]]
    return register


def _complete_evidence(*, independently_verified: bool) -> dict:
    return {
        "artifact_or_registry_path": "docs/operations/example-attestation.md",
        "resulting_commit_or_record_id": "record-001",
        "completed_at": "2026-08-10T16:00:00Z",
        "writer_authority": "Architect",
        "historical_entries_preserved": True,
        "provenance_preserved": True,
        "silent_overwrite_detected": False,
        "independently_verified_at": (
            "2026-08-10T16:05:00Z" if independently_verified else None
        ),
    }


def _write_yaml(tmp_path: Path, name: str, document: dict) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def _run_assessment(tmp_path: Path, document: dict) -> int:
    path = _write_yaml(tmp_path, "assessment.yaml", document)
    return main(["what-does-system-need", "--assessment", str(path)])


def test_valid_operational_assessment_passes(tmp_path, capsys):
    assert _run_assessment(tmp_path, _operational_assessment()) == 0
    result = yaml.safe_load(capsys.readouterr().out)["jarvis_nova_command"]
    assert result["validation"]["machine_validated"] is True
    assert (
        result["validation"]["source_truth_independently_verified_by_this_command"]
        is False
    )
    assert result["effects"]["creates_production_authority"] is False


def test_valid_operational_assessment_json_passes(tmp_path, capsys):
    path = tmp_path / "assessment.json"
    path.write_text(json.dumps(_operational_assessment()), encoding="utf-8")
    assert main(["what-does-system-need", "--assessment", str(path)]) == 0
    assert "status: passed" in capsys.readouterr().out


def test_synthetic_fixture_submitted_as_live_assessment_fails(tmp_path, capsys):
    assert _run_assessment(tmp_path, _assessment()) == 1
    stderr = capsys.readouterr().err
    assert "record_source_type" in stderr
    assert "machine_validation_failed: true" in stderr


def test_operational_evidence_ineligible_assessment_fails(tmp_path, capsys):
    document = _operational_assessment()
    document["cco_system_need_assessment"]["operational_evidence_eligible"] = False
    assert _run_assessment(tmp_path, document) == 1
    assert "operational_evidence_eligible" in capsys.readouterr().err


def test_missing_mandatory_source_fails(tmp_path, capsys):
    document = _operational_assessment()
    document["cco_system_need_assessment"]["source_scope"]["available"].remove(
        "cco_priority_register"
    )
    assert _run_assessment(tmp_path, document) == 1
    assert "cco_priority_register" in capsys.readouterr().err


def test_mandatory_source_in_two_availability_buckets_fails(tmp_path, capsys):
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_scope"]["unavailable"].append("production_readiness")
    assessment["source_limitations"].append(
        {
            "source_id": "production_readiness",
            "limitation": "Synthetic duplicate used to prove command rejection.",
        }
    )
    assert _run_assessment(tmp_path, document) == 1
    assert "exactly one availability bucket" in capsys.readouterr().err


def test_explicit_initial_baseline_with_no_material_delta_fails(tmp_path, capsys):
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["source_conclusions"][0]["conclusion"] = "no_material_delta"
    assessment["material_delta"]["status"] = "no_material_delta"
    assert _run_assessment(tmp_path, document) == 1
    assert "explicit initial baseline" in capsys.readouterr().err


def test_explicit_initial_baseline_with_unknown_passes(tmp_path, capsys):
    assert _run_assessment(tmp_path, _operational_assessment()) == 0
    assert "status: passed" in capsys.readouterr().out


def test_all_unknown_evidence_with_no_material_delta_fails(tmp_path, capsys):
    document = _operational_assessment()
    document["cco_system_need_assessment"]["material_delta"][
        "status"
    ] = "no_material_delta"
    assert _run_assessment(tmp_path, document) == 1
    assert "material_delta.status" in capsys.readouterr().err


def test_assessment_claiming_jarvis_authority_fails(tmp_path, capsys):
    document = _operational_assessment()
    routing = document["cco_system_need_assessment"]["attention_routing"]
    routing["authority_status"] = "externally_granted"
    routing["authority_evidence_reference"] = "Jarvis_Nova_CCO"
    routing["authority_evidence_source"] = "external_authority_record"
    assert _run_assessment(tmp_path, document) == 1
    assert "cannot serve as authority evidence" in capsys.readouterr().err


def test_assessment_self_attesting_production_fails(tmp_path, capsys):
    document = _operational_assessment()
    assessment = document["cco_system_need_assessment"]
    assessment["api_observability"]["control_plane_attestation"] = {
        "status": "available",
        "attestation_contract_reference": "docs/operations/production-control-plane-attestation.md",
        "attestation_evidence_reference": assessment["assessment_id"],
        "environment_identifier": "synthetic-production-example",
        "observed_at": "2026-08-10T15:03:00Z",
        "observer_or_system": "synthetic-observer",
        "evidence_method": "synthetic-inspection",
        "control_plane_owner_or_custody": "synthetic-owner-record",
        "deployed_commit": "19cfeb341e8d10d223979f40b88d598da5ae1770",
        "evidence_references": [],
        "limitation": None,
    }
    assert _run_assessment(tmp_path, document) == 1
    assert "independent production evidence" in capsys.readouterr().err


def test_terminal_status_without_completion_evidence_fails(tmp_path, capsys):
    register = _register_with_one_item()
    register["items"][0]["status"] = "verified_complete"
    path = _write_yaml(tmp_path, "items.yaml", register)
    assert main(["review-completion", "--items", str(path)]) == 1
    assert "terminal item lacks valid completion evidence" in capsys.readouterr().err


def test_evidence_submitted_without_independent_verification_remains_nonterminal(
    tmp_path, capsys
):
    register = _register_with_one_item()
    item = register["items"][0]
    item["status"] = "evidence_submitted"
    item["completion_evidence"] = _complete_evidence(independently_verified=False)
    path = _write_yaml(tmp_path, "items.yaml", register)
    assert main(["review-completion", "--items", str(path)]) == 0
    result = yaml.safe_load(capsys.readouterr().out)["jarvis_nova_command"]
    assert result["item"]["resulting_status"] == "evidence_submitted"
    assert result["evidence"]["completion_condition_satisfied"] is True
    assert result["evidence"]["independent_verification_present"] is False


def test_complete_valid_evidence_passes_and_reports_verified_complete(tmp_path, capsys):
    register = _register_with_one_item()
    item = register["items"][0]
    item["status"] = "evidence_submitted"
    item["completion_evidence"] = _complete_evidence(independently_verified=True)
    path = _write_yaml(tmp_path, "items.yaml", register)
    assert main(["review-completion", "--items", str(path)]) == 0
    result = yaml.safe_load(capsys.readouterr().out)["jarvis_nova_command"]
    assert result["item"]["resulting_status"] == "verified_complete"
    assert result["evidence"]["independent_verification_present"] is True
    assert result["authority_effect"] == "none"


def _comparison_documents() -> tuple[dict, dict]:
    old = _operational_assessment()
    old_assessment = old["cco_system_need_assessment"]
    old_assessment["comparison_baseline"] = {
        "baseline_type": "prior_verified_assessment",
        "baseline_reference": "CCO-ASSESSMENT-PRIOR-000",
        "baseline_observed_at": "2026-08-09T15:00:00Z",
    }
    new = deepcopy(old)
    new_assessment = new["cco_system_need_assessment"]
    new_assessment["assessment_id"] = "CCO-ASSESSMENT-2026-08-10-002"
    new_assessment["comparison_baseline"] = {
        "baseline_type": "prior_verified_assessment",
        "baseline_reference": old_assessment["assessment_id"],
        "baseline_observed_at": "2026-08-10T15:04:00Z",
    }
    new_assessment["system_need"]["objective"] = (
        "Reassess the bounded evidence gap after submitted work."
    )
    return old, new


def test_valid_verified_state_comparison_is_deterministic(tmp_path, capsys):
    old, new = _comparison_documents()
    old_path = _write_yaml(tmp_path, "old.yaml", old)
    new_path = _write_yaml(tmp_path, "new.yaml", new)
    args = ["compare-state", "--old", str(old_path), "--new", str(new_path)]
    assert main(args) == 0
    first = capsys.readouterr().out
    assert main(args) == 0
    second = capsys.readouterr().out
    assert first == second
    result = yaml.safe_load(first)["jarvis_nova_command"]
    assert result["comparison"]["structural_difference_detected"] is True
    assert "system_need.objective" in result["comparison"]["changed_paths"]
    assert result["comparison"]["missing_current_evidence"]
    assert result["comparison"]["no_material_delta_established"] is False
    assert (
        result["authoritative_state_movement"][
            "inferred_from_structural_difference"
        ]
        is False
    )


def test_initial_baseline_cannot_be_prior_verified_comparison(tmp_path, capsys):
    old, new = _comparison_documents()
    old["cco_system_need_assessment"]["comparison_baseline"] = {
        "baseline_type": "explicit_initial_baseline",
        "baseline_reference": "synthetic_initial_baseline",
        "baseline_observed_at": "2026-08-09T15:00:00Z",
    }
    old_path = _write_yaml(tmp_path, "old.yaml", old)
    new_path = _write_yaml(tmp_path, "new.yaml", new)
    assert (
        main(
            ["compare-state", "--old", str(old_path), "--new", str(new_path)]
        )
        == 1
    )
    assert "not a prior verified comparison state" in capsys.readouterr().err
