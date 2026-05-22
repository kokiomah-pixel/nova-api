from pathlib import Path

from scripts.doctrine_lint import scan_files, scan_text


def _scan(content: str):
    path = Path("sample.md")
    return scan_text(path, content, root=Path("."))


def test_doctrine_lint_blocks_prohibited_execution_authority_phrases():
    findings = _scan("Nova authorizes execution when the context says execute if admitted.")

    assert {finding.rule for finding in findings} == {"prohibited-phrase"}
    assert all(finding.severity == "error" for finding in findings)


def test_doctrine_lint_flags_code_like_allow_enforcement():
    findings = _scan("if decision_status == ALLOW:\n    downstream_route()")

    assert any(finding.rule == "code-like-enforcement" for finding in findings)
    assert any(finding.severity == "error" for finding in findings)


def test_doctrine_lint_allows_negated_boundary_language():
    findings = _scan("Nova is not a signal engine and does not grant execution authority.")

    assert findings == []


def test_doctrine_lint_flags_hidden_unicode_controls():
    findings = _scan("chronology\u202erecord")

    assert len(findings) == 1
    assert findings[0].rule == "hidden-unicode"
    assert findings[0].severity == "error"


def test_doctrine_lint_flags_no_break_space():
    findings = _scan("chronology\u00a0record")

    assert len(findings) == 1
    assert findings[0].rule == "hidden-unicode"
    assert findings[0].severity == "error"


def test_doctrine_lint_flags_private_key_assignment():
    findings = _scan("WALLET_PRIVATE_KEY=0123456789abcdef0123456789abcdef0123456789abcdef")

    assert any(finding.rule == "secret-pattern" for finding in findings)
    assert any(finding.severity == "error" for finding in findings)


def test_doctrine_lint_flags_bearer_token_pattern():
    findings = _scan("Authorization: Bearer liveCredentialValue0123456789abcdef")

    assert any(finding.rule == "bearer-token-pattern" for finding in findings)
    assert any(finding.severity == "error" for finding in findings)


def test_doctrine_lint_flags_github_token_pattern():
    findings = _scan("GITHUB_TOKEN=ghp_0123456789abcdef0123456789abcdef0123")

    assert {finding.rule for finding in findings} >= {"secret-pattern", "github-token-pattern"}
    assert all(finding.severity == "error" for finding in findings)


def test_doctrine_lint_flags_committed_env_files(tmp_path):
    env_file = tmp_path / ".env.production"
    env_file.write_text("NOVA_API_KEY=liveCredentialValue0123456789abcdef\n", encoding="utf-8")

    findings = scan_files([env_file], root=tmp_path)

    assert any(finding.rule == "env-file-committed" for finding in findings)


def test_doctrine_lint_allows_sanitized_env_example(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text(
        "CDP_API_KEY_SECRET=your_cdp_api_key_secret\n"
        "EVM_PRIVATE_KEY=your_base_wallet_private_key\n",
        encoding="utf-8",
    )

    findings = scan_files([env_file], root=tmp_path)

    assert findings == []


def test_doctrine_lint_flags_unsafe_extension_recommendation_text():
    findings = _scan("Install this random VS Code extension before changing Nova docs.")

    assert any(finding.rule == "unsafe-extension-reference" for finding in findings)
