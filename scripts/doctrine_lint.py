from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".py",
    ".yaml",
    ".yml",
}

SKIP_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "archive",
}

EXEMPT_FILES = {
    Path("docs/canonical-terminology.md"),
    Path("scripts/doctrine_lint.py"),
    Path("tests/test_doctrine_lint.py"),
}

PROHIBITED_PHRASES = (
    "must execute",
    "binding authorization",
    "decision approval",
    "execute if admitted",
    "execute only if admitted",
    "nova authorizes",
    "retry until allow",
    "block execution",
)

CODE_LIKE_PATTERNS = (
    re.compile(r"\bif\s+decision_status\s*==\s*['\"]?ALLOW['\"]?", re.IGNORECASE),
)

DEPRECATED_TERMS = (
    "authorization layer",
    "execution permission",
    "signal engine",
    "prediction system",
    "optimization engine",
    "execution middleware",
    "ai signal infrastructure",
    "alpha generation",
    "trading optimization",
    "recommendation engine",
    "dashboard tooling",
)

BOUNDARY_QUALIFIERS = (
    "not ",
    "not an ",
    "not a ",
    "does not ",
    "do not ",
    "avoid ",
    "avoids ",
    "prohibited",
    "deprecated",
    "is not ",
    "should not ",
)

HIDDEN_UNICODE_NAMES = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\ufeff": "BYTE ORDER MARK",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING",
    "\u202c": "POP DIRECTIONAL FORMATTING",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE",
    "\u2066": "LEFT-TO-RIGHT ISOLATE",
    "\u2067": "RIGHT-TO-LEFT ISOLATE",
    "\u2068": "FIRST STRONG ISOLATE",
    "\u2069": "POP DIRECTIONAL ISOLATE",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    severity: str
    rule: str
    message: str

    def format(self) -> str:
        return f"{self.severity.upper()} {self.path}:{self.line} [{self.rule}] {self.message}"


def iter_default_files(root: Path = REPO_ROOT) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel in EXEMPT_FILES:
            continue
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def _is_boundary_line(line: str, term: str) -> bool:
    lowered = line.lower()
    index = lowered.find(term)
    if index < 0:
        return False
    prefix = lowered[max(0, index - 100) : index]
    return any(qualifier in prefix for qualifier in BOUNDARY_QUALIFIERS)


def _should_scan_code_like_examples(path: Path) -> bool:
    suffix = path.suffix.lower()
    return suffix in {".md", ".txt"} or "examples" in path.parts


def scan_text(path: Path, text: str, root: Path = REPO_ROOT) -> list[Finding]:
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    findings: list[Finding] = []
    scan_code_like = _should_scan_code_like_examples(rel)

    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()

        for phrase in PROHIBITED_PHRASES:
            if phrase in lowered:
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "prohibited-phrase",
                        f"replace prohibited execution-authority wording: {phrase!r}",
                    )
                )

        if scan_code_like:
            for pattern in CODE_LIKE_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            rel,
                            line_number,
                            "error",
                            "code-like-enforcement",
                            "review code-like ALLOW enforcement example for category drift",
                        )
                    )

        for term in DEPRECATED_TERMS:
            if term in lowered and not _is_boundary_line(line, term):
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "warning",
                        "deprecated-term",
                        f"prefer canonical environmental-governance wording over {term!r}",
                    )
                )

        for character, name in HIDDEN_UNICODE_NAMES.items():
            if character in line:
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "hidden-unicode",
                        f"remove hidden Unicode control character: {name}",
                    )
                )

    return findings


def scan_files(paths: Iterable[Path], root: Path = REPO_ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            findings.append(
                Finding(
                    rel,
                    1,
                    "error",
                    "utf8-decode",
                    f"file must be valid UTF-8 text: {exc}",
                )
            )
            continue
        findings.extend(scan_text(path, text, root=root))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan repository language for Nova doctrine drift.")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional files or directories to scan.")
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Exit non-zero for deprecated terminology warnings as well as hard errors.",
    )
    args = parser.parse_args(argv)

    if args.paths:
        files: list[Path] = []
        for raw_path in args.paths:
            path = raw_path if raw_path.is_absolute() else REPO_ROOT / raw_path
            if path.is_dir():
                files.extend(iter_default_files(path))
            elif path.is_file():
                files.append(path)
            else:
                print(f"missing path: {raw_path}", file=sys.stderr)
                return 2
    else:
        files = list(iter_default_files(REPO_ROOT))

    findings = scan_files(files, root=REPO_ROOT)
    for finding in findings:
        print(finding.format())

    has_error = any(finding.severity == "error" for finding in findings)
    has_warning = any(finding.severity == "warning" for finding in findings)
    if has_error or (args.warnings_as_errors and has_warning):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
