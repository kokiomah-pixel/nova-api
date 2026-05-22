from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_developer_environment_integrity_protocol_exists():
    protocol = REPO_ROOT / "docs/security/developer-environment-integrity-protocol.md"

    assert protocol.is_file()
    text = protocol.read_text(encoding="utf-8")

    assert "Developer Tooling Risk" in text
    assert "Approved Extension Posture" in text
    assert "Credential Hygiene" in text
    assert "Secret Exposure Response" in text
    assert "Extension Incident Response" in text
    assert "Local Environment Rebuild Guidance" in text
    assert "without exposing sovereign internals" in text


def test_security_chronology_logs_exist_and_exclude_secret_material():
    chronology_files = [
        REPO_ROOT / "docs/security/chronology/developer-environment-security-log.md",
        REPO_ROOT / "docs/security/chronology/credential-rotation-log.md",
        REPO_ROOT / "docs/security/chronology/security-response-timeline.md",
    ]

    for path in chronology_files:
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "| Date | Event Type | Affected Surface | Action Taken | Remaining Risk | Follow-Up Owner / Status |" in text
        assert "Do not record raw tokens" in text or "must not include raw tokens" in text
        assert "policy weights" in text


def test_pull_request_template_contains_security_integrity_checklist():
    template = REPO_ROOT / ".github/pull_request_template.md"

    assert template.is_file()
    text = template.read_text(encoding="utf-8")

    assert "No secrets, keys, tokens, or credentials committed" in text
    assert "No `.env` files committed" in text
    assert "No hidden Unicode / bidi control characters introduced" in text
    assert "Doctrine/security lint passes" in text
    assert "No private x402, CDP, wallet, or facilitator credentials exposed" in text
