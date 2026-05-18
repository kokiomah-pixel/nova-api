from pathlib import Path

from scripts.doctrine_lint import scan_text


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
