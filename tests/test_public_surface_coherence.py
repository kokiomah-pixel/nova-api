from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.validate_public_surface_coherence import REPO_ROOT, validate_repository


FIXTURE_FILES = (
    "README.md",
    "CURRENT_STATE.md",
    "PROJECT_REPORT.md",
    "docs/start-here.md",
    "docs/reviewer-paths.md",
    "docs/inspection/phase-1-inspection-status.md",
    "docs/legacy-v1/README.md",
    "docs/legacy-v1/quickstart.md",
    "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md",
    "docs/target-v2/README.md",
    "docs/go-to-market/system-class-comparator.md",
    "docs/go-to-market/commercialization-sequence.md",
    "docs/operations/public-surface-coherence-standard.md",
    "docs/operations/production-readiness-register.md",
    "docs/governance/public-private-repository-boundary-v0.1.md",
    "docs/governance/public-exposure-inventory-v0.1.md",
)


@pytest.fixture
def coherent_repo(tmp_path: Path) -> Path:
    for relative in FIXTURE_FILES:
        source = REPO_ROOT / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return tmp_path


def _fields(root: Path) -> set[str]:
    return {error.field for error in validate_repository(root)}


def _replace(root: Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_current_repository_passes() -> None:
    assert [error.format() for error in validate_repository(REPO_ROOT)] == []


def test_missing_current_state_fails(coherent_repo: Path) -> None:
    (coherent_repo / "CURRENT_STATE.md").unlink()
    assert "canonical_files.CURRENT_STATE.md" in _fields(coherent_repo)


def test_root_readme_legacy_quickstart_fails(coherent_repo: Path) -> None:
    path = coherent_repo / "README.md"
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\nNOVA_API_KEY=mytestkey ./.venv/bin/uvicorn app:app\n",
        encoding="utf-8",
    )
    assert "root_README.Legacy_v1_quickstart_absent" in _fields(coherent_repo)


def test_root_readme_deep_jargon_in_first_screen_fails(coherent_repo: Path) -> None:
    path = coherent_repo / "README.md"
    path.write_text("constraint_pressure\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert "root_README.first_screen_terminology.constraint_pressure" in _fields(coherent_repo)


def test_root_project_report_gtm_ready_claim_fails(coherent_repo: Path) -> None:
    path = coherent_repo / "PROJECT_REPORT.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n**Status:** GTM-Ready\n",
        encoding="utf-8",
    )
    assert "root_PROJECT_REPORT.current_GTM_ready_claim_absent" in _fields(coherent_repo)


def test_root_project_report_operationally_live_claim_fails(coherent_repo: Path) -> None:
    path = coherent_repo / "PROJECT_REPORT.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nThe API is **operationally live**.\n",
        encoding="utf-8",
    )
    assert "root_PROJECT_REPORT.current_operationally_live_claim_absent" in _fields(coherent_repo)


def test_historical_report_without_banner_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md",
        "Superseded current-state notice",
        "Historical note",
    )
    assert "historical_report.supersession_banner_in_first_40_lines" in _fields(coherent_repo)


def test_historical_report_with_preserved_claim_and_banner_passes(coherent_repo: Path) -> None:
    historical = coherent_repo / "docs/legacy-v1/reports/PROJECT_REPORT-2026-03-20.md"
    assert "GTM-Ready" in historical.read_text(encoding="utf-8")
    assert not {field for field in _fields(coherent_repo) if field.startswith("historical_report.")}


def test_legacy_v1_marked_canonical_future_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/legacy-v1/README.md",
        "canonical_future_external_model: false",
        "canonical_future_external_model: true",
    )
    assert "product_generation.Legacy_v1_canonical_future_false" in _fields(coherent_repo)


def test_target_v2_marked_implemented_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/target-v2/README.md",
        "runtime_implemented: false",
        "runtime_implemented: true",
    )
    assert "product_generation.target_v2_runtime_implemented_false" in _fields(coherent_repo)


def test_target_v2_marked_production_active_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/target-v2/README.md",
        "production_active: false",
        "production_active: true",
    )
    assert "product_generation.target_v2_production_active_false" in _fields(coherent_repo)


def test_system_wide_production_ready_claim_fails(coherent_repo: Path) -> None:
    path = coherent_repo / "CURRENT_STATE.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nSharpe Nova OS is production-ready.\n",
        encoding="utf-8",
    )
    assert "production_claims.unqualified_system_wide_production_ready_claim_absent" in _fields(coherent_repo)


def test_repository_governance_ready_claim_passes(coherent_repo: Path) -> None:
    readiness = coherent_repo / "docs/operations/production-readiness-register.md"
    assert "repository_governance: ready" in readiness.read_text(encoding="utf-8")
    assert not {field for field in _fields(coherent_repo) if field.startswith("production_claims.")}


def test_institutional_marketplace_activation_authorized_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/go-to-market/commercialization-sequence.md",
        "    marketplace_activation: false",
        "    marketplace_activation: true",
    )
    assert "commercialization.institutional_restrictions_preserved" in _fields(coherent_repo)


def test_institutional_x402_activation_authorized_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/go-to-market/commercialization-sequence.md",
        "    x402_activation: false",
        "    x402_activation: true",
    )
    assert "commercialization.institutional_restrictions_preserved" in _fields(coherent_repo)


def test_missing_retail_x402_authority_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/go-to-market/commercialization-sequence.md",
        "    x402_payment_authorized: true",
        "    x402_payment_authorized: false",
    )
    assert "commercialization.retail_authority.x402_payment_authorized" in _fields(coherent_repo)


def test_missing_retail_marketplace_submission_authority_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/go-to-market/commercialization-sequence.md",
        "    marketplace_submission_authorized: true",
        "    marketplace_submission_authorized: false",
    )
    assert "commercialization.retail_authority.marketplace_submission_authorized" in _fields(coherent_repo)


def test_missing_repository_exposure_boundary_fails(coherent_repo: Path) -> None:
    (coherent_repo / "docs/governance/public-private-repository-boundary-v0.1.md").unlink()
    assert "canonical_files.docs/governance/public-private-repository-boundary-v0.1.md" in _fields(coherent_repo)


def test_comparator_without_hypothesis_boundary_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/go-to-market/system-class-comparator.md",
        "Nova’s differentiation is a hypothesis",
        "Nova’s differentiation is established",
    )
    assert "comparator.differentiation_labeled_hypothesis" in _fields(coherent_repo)


def test_comparator_with_existing_system_classes_passes(coherent_repo: Path) -> None:
    assert not {field for field in _fields(coherent_repo) if field.startswith("comparator.")}


def test_current_state_links_resolve(coherent_repo: Path) -> None:
    assert not {field for field in _fields(coherent_repo) if field.startswith("links.CURRENT_STATE.md")}


def test_default_reviewer_path_starts_with_current_state(coherent_repo: Path) -> None:
    assert "reviewer_paths.default_path_starts_with_CURRENT_STATE" not in _fields(coherent_repo)


def test_default_reviewer_path_wrong_order_fails(coherent_repo: Path) -> None:
    _replace(
        coherent_repo,
        "docs/reviewer-paths.md",
        "1. `README.md`\n2. `CURRENT_STATE.md`",
        "1. `CURRENT_STATE.md`\n2. `README.md`",
    )
    assert "reviewer_paths.default_path_starts_with_CURRENT_STATE" in _fields(coherent_repo)
