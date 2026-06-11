from pathlib import Path

from scripts.doctrine_lint import scan_files


REPO_ROOT = Path(__file__).resolve().parents[1]
INCIDENT_RECORD = REPO_ROOT / "docs/continuity/incidents/2026-05-25-business-workspace-deactivation-gap.md"
PROTOCOL = REPO_ROOT / "docs/continuity/business-workspace-continuity-protocol.md"
LOG = REPO_ROOT / "docs/continuity/workspace-continuity-log.md"
CHRONOLOGY = REPO_ROOT / "docs/chronology/2026-05-25-workspace-deactivation-gap.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workspace_continuity_artifacts_exist():
    assert INCIDENT_RECORD.exists()
    assert PROTOCOL.exists()
    assert LOG.exists()
    assert CHRONOLOGY.exists()


def test_workspace_deactivation_incident_window_is_recorded():
    incident = _read(INCIDENT_RECORD)
    log = _read(LOG)
    chronology = _read(CHRONOLOGY)

    assert "May 25, 2026 to June 11, 2026" in incident
    assert "Start: 2026-05-25" in log
    assert "End: 2026-06-11" in log
    assert "May 25, 2026 to June 11, 2026" in chronology


def test_workspace_continuity_canonical_phrases_are_recorded():
    protocol = _read(PROTOCOL)
    incident = _read(INCIDENT_RECORD)

    assert "Workspace tools are operating interfaces" in protocol
    assert "GitHub remains the durable archive" in protocol
    assert "Nova can survive interruption if it remembers interruption correctly." in incident


def test_workspace_continuity_docs_do_not_contain_secret_patterns():
    findings = scan_files(
        [INCIDENT_RECORD, PROTOCOL, LOG, CHRONOLOGY],
        root=REPO_ROOT,
    )

    assert [finding.format() for finding in findings if finding.severity == "error"] == []
