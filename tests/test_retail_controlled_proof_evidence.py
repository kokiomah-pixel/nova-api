from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError

from retail_context.control_store import SQLiteRetailProductionControlStore
from retail_context.proof_evidence import (
    load_retail_controlled_proof_schema,
    validate_retail_controlled_proof_evidence,
)
from scripts.retail_control_operator import main as operator_main


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = (
    REPO_ROOT
    / "fixtures"
    / "retail_context"
    / "controlled_proof"
    / "evidence_template.json"
)
DEPLOYMENT_PATH = REPO_ROOT / "deployment" / "render-retail-controlled-proof.yaml"


def evidence_template() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def operator_env(db_path: Path) -> dict[str, str]:
    return {
        "NOVA_RETAIL_CONTROL_DB_PATH": str(db_path),
        "NOVA_RETAIL_RATE_LIMIT_WINDOW_SECONDS": "60",
        "NOVA_RETAIL_STATE_PING_MAX_REQUESTS": "2",
        "NOVA_RETAIL_CONTEXT_DELTA_MAX_REQUESTS": "2",
    }


def test_evidence_schema_is_draft_2020_12_and_template_is_valid() -> None:
    schema = load_retail_controlled_proof_schema()
    assert schema["$schema"].endswith("draft/2020-12/schema")
    template = evidence_template()
    validate_retail_controlled_proof_evidence(template)
    assert template["evidence_state"] == "proof_not_started"
    assert template["evidence_origin"] == "repository_template"


def test_repository_template_cannot_be_changed_to_proof_complete() -> None:
    evidence = evidence_template()
    evidence["evidence_state"] = "proof_complete"
    with pytest.raises(ValidationError):
        validate_retail_controlled_proof_evidence(evidence)


def test_repository_template_cannot_claim_deployment() -> None:
    evidence = evidence_template()
    evidence["deployment_commit"] = "a" * 40
    evidence["service_identifier"] = "unit-test-service"
    with pytest.raises(ValidationError):
        validate_retail_controlled_proof_evidence(evidence)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("buyer_demand_effect", "observed"),
        ("public_activation_effect", "active"),
        ("authority_effect", "approval"),
    ),
)
def test_evidence_cannot_infer_authority_activation_or_demand(
    field: str, value: str
) -> None:
    evidence = evidence_template()
    evidence[field] = value
    with pytest.raises(ValidationError):
        validate_retail_controlled_proof_evidence(evidence)


def test_payment_events_cannot_add_commercial_claim_fields() -> None:
    evidence = evidence_template()
    evidence.update({"adoption": True, "pricing_power": True, "product_market_fit": True})
    with pytest.raises(ValidationError):
        validate_retail_controlled_proof_evidence(evidence)


def test_operator_cli_mode_is_disabled_by_default_and_persists(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db_path = tmp_path / "retail" / "controls.sqlite3"
    env = operator_env(db_path)
    assert operator_main(["show-mode"], environ=env) == 0
    assert json.loads(capsys.readouterr().out)["operating_mode"] == "disabled"
    assert operator_main(["set-mode", "controlled_proof"], environ=env) == 0
    assert json.loads(capsys.readouterr().out)["operating_mode"] == "controlled_proof"
    reopened = SQLiteRetailProductionControlStore(db_path)
    reopened.initialize()
    assert reopened.get_service_mode() == "controlled_proof"
    assert operator_main(["set-mode", "disabled"], environ=env) == 0
    assert json.loads(capsys.readouterr().out)["authority_effect"] == "none"
    assert SQLiteRetailProductionControlStore(db_path).get_service_mode() == "disabled"


def test_operator_readiness_is_bounded(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env = operator_env(tmp_path / "controls.sqlite3")
    assert operator_main(["read-readiness"], environ=env) == 0
    disabled = json.loads(capsys.readouterr().out)
    assert disabled["readiness_status"] == "not_ready"
    assert operator_main(["set-mode", "controlled_proof"], environ=env) == 0
    capsys.readouterr()
    assert operator_main(["read-readiness"], environ=env) == 0
    ready = json.loads(capsys.readouterr().out)
    assert ready["readiness_status"] == "ready_for_controlled_proof"
    assert "production_ready" not in json.dumps(ready)
    assert ready["authority_effect"] == "none"


@pytest.mark.parametrize("mode", ("public", "live", "production_active"))
def test_operator_rejects_unbounded_service_modes(mode: str) -> None:
    with pytest.raises(SystemExit):
        operator_main(["set-mode", mode], environ={})


def test_operator_has_no_http_administration_surface() -> None:
    source = (REPO_ROOT / "scripts" / "retail_control_operator.py").read_text(
        encoding="utf-8"
    )
    assert "FastAPI" not in source
    assert "APIRouter" not in source
    assert "@app" not in source


def test_retail_app_is_factory_only_and_not_mounted_in_legacy_app() -> None:
    source = (REPO_ROOT / "retail_context" / "service.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    top_level_assignments = {
        target.id
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
    }
    assert "app" not in top_level_assignments
    legacy = (REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "retail_context.service" not in legacy


def test_deployment_blueprint_is_isolated_controlled_proof_only() -> None:
    blueprint = yaml.safe_load(DEPLOYMENT_PATH.read_text(encoding="utf-8"))
    assert len(blueprint["services"]) == 1
    service = blueprint["services"][0]
    assert service["autoDeploy"] is False
    assert service["healthCheckPath"] == "/health"
    assert "retail_context.service:create_retail_app_from_env" in service["startCommand"]
    assert "--factory" in service["startCommand"]
    assert service["disk"]["mountPath"] == "/var/data/nova-retail"
    keys = {item["key"] for item in service["envVars"]}
    assert keys
    assert all(key.startswith("NOVA_RETAIL_") for key in keys)
    rendered = json.dumps(blueprint)
    assert "NOVA_API_KEY" not in rendered
    assert "CDP_" not in rendered
    assert "marketplace" not in rendered.lower()


def test_ci_runtime_code_has_no_proof_complete_emitter() -> None:
    runtime_sources = list((REPO_ROOT / "retail_context").glob("*.py")) + [
        REPO_ROOT / "scripts" / "retail_control_operator.py"
    ]
    assert all(
        '"proof_complete"' not in path.read_text(encoding="utf-8")
        and "'proof_complete'" not in path.read_text(encoding="utf-8")
        for path in runtime_sources
    )


def test_schema_rejects_unrecognized_gate_states() -> None:
    evidence = copy.deepcopy(evidence_template())
    evidence["evidence_state"] = "production_active"
    with pytest.raises(ValidationError):
        validate_retail_controlled_proof_evidence(evidence)
