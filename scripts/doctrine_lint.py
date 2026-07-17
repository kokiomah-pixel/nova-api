from __future__ import annotations

import argparse
import re
import subprocess
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

TEXT_FILENAMES = {
    ".env.example",
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
    Path("tests/test_developer_environment_integrity.py"),
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

NSF_PROHIBITED_ESTABLISHED_FORMULATIONS = (
    "Nova is production ready",
    "Nova is deployed across institutional workflows",
    "Nova has demonstrated buyer demand",
    "Nova improves financial decisions",
    "Nova guarantees compliant execution",
    "Nova authorizes transactions",
    "Nova blocks unauthorized transactions",
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
    "has not ",
    "will test ",
    "research will ",
    "future research",
    "not established",
    "prohibited",
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
    "\u00a0": "NO-BREAK SPACE",
}

SENSITIVE_ENV_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
}

SENSITIVE_SUFFIXES = {
    ".key",
    ".pem",
}

SECRET_ASSIGNMENT_NAMES = (
    "PRIVATE_KEY",
    "SECRET_KEY",
    "GITHUB_TOKEN",
    "CDP_API_KEY",
    "CDP_API_KEY_ID",
    "CDP_API_SECRET",
    "CDP_API_KEY_SECRET",
    "WALLET_PRIVATE_KEY",
    "EVM_PRIVATE_KEY",
    "SEED_PHRASE",
    "MNEMONIC",
    "X-API-KEY",
    "api_key",
)

SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b("
    + "|".join(re.escape(name) for name in SECRET_ASSIGNMENT_NAMES)
    + r")\b\s*[:=]\s*[\"']?([^\"'\s,#]+)"
)

AUTHORIZATION_PATTERN = re.compile(
    r"(?i)\bAuthorization\b\s*:\s*[\"']?Bearer\s+([A-Za-z0-9._~+/=-]{16,})"
)

BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+([A-Za-z0-9._~+/=-]{24,})")
GITHUB_TOKEN_PATTERN = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")

PLACEHOLDER_MARKERS = (
    "your_",
    "placeholder",
    "replace",
    "example",
    "sample",
    "dummy",
    "mock",
    "fake",
    "test",
    "redacted",
    "paste_secret_locally_only",
    "server-secret",
    "secret-token-value",
    "mytestkey",
)

SAFE_ENV_EXAMPLE_NAMES = {
    "CDP_API_KEY_ID",
    "CDP_API_KEY_SECRET",
    "EVM_PRIVATE_KEY",
    "NOVA_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
}

UNSAFE_EXTENSION_PATTERNS = (
    re.compile(r"\bcode\s+--install-extension\b", re.IGNORECASE),
    re.compile(r"\b(?:random|unknown|unreviewed)\b.*\b(?:vs code\s+)?extension\b", re.IGNORECASE),
    re.compile(r"\b(?:auto[- ]install|auto[- ]recommended)\b.*\bextension\b", re.IGNORECASE),
)


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
    if root == REPO_ROOT and (root / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            pass
        else:
            for raw_path in sorted(result.stdout.splitlines()):
                path = root / raw_path
                rel = Path(raw_path)
                if rel in EXEMPT_FILES:
                    continue
                if any(part in SKIP_PARTS for part in rel.parts):
                    continue
                if not path.is_file():
                    continue
                if _is_text_candidate(path):
                    yield path
            return

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel in EXEMPT_FILES:
            continue
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if not _is_text_candidate(path):
            continue
        yield path


def _is_text_candidate(path: Path) -> bool:
    if path.name in TEXT_FILENAMES or path.name.startswith(".env"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def _is_boundary_line(line: str, term: str) -> bool:
    lowered = line.lower()
    index = lowered.find(term)
    if index < 0:
        return False
    prefix = lowered[max(0, index - 100) : index]
    return any(qualifier in prefix for qualifier in BOUNDARY_QUALIFIERS)


def _is_nsf_allowed_context(line: str, term: str) -> bool:
    lowered = line.lower()
    index = lowered.find(term.lower())
    if index < 0:
        return False
    window = lowered[max(0, index - 120) : index + len(term) + 120]
    return any(qualifier in window for qualifier in BOUNDARY_QUALIFIERS)


def _should_scan_code_like_examples(path: Path) -> bool:
    suffix = path.suffix.lower()
    return suffix in {".md", ".txt"} or "examples" in path.parts


def _is_placeholder_value(value: str) -> bool:
    normalized = value.strip().strip("\"'").lower()
    if not normalized:
        return True
    if normalized.startswith("<") and normalized.endswith(">"):
        return True
    if normalized.startswith("${") and normalized.endswith("}"):
        return True
    if normalized.endswith("-key") or normalized.endswith("_key"):
        return True
    return any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def _is_sanitized_env_example(rel: Path, name: str, value: str) -> bool:
    return rel.name == ".env.example" and name.upper() in SAFE_ENV_EXAMPLE_NAMES and _is_placeholder_value(value)


def _looks_like_secret_value(value: str) -> bool:
    normalized = value.strip().strip("\"'")
    if _is_placeholder_value(normalized):
        return False
    if "(" in normalized or ")" in normalized:
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_./-]*", normalized) and not GITHUB_TOKEN_PATTERN.search(normalized):
        return False
    if normalized.startswith("-----BEGIN"):
        return True
    if GITHUB_TOKEN_PATTERN.search(normalized):
        return True
    if len(normalized) >= 24:
        return True
    if re.fullmatch(r"[A-Fa-f0-9]{32,}", normalized):
        return True
    return False


def scan_path_metadata(path: Path, root: Path = REPO_ROOT) -> list[Finding]:
    rel = path.relative_to(root) if path.is_relative_to(root) else path
    findings: list[Finding] = []
    name = rel.name
    lowered_name = name.lower()

    if lowered_name in SENSITIVE_ENV_FILENAMES or (
        lowered_name.startswith(".env.") and lowered_name != ".env.example"
    ):
        findings.append(
            Finding(
                rel,
                1,
                "error",
                "env-file-committed",
                "do not commit local environment files; keep only sanitized .env.example templates",
            )
        )

    if rel.suffix.lower() in SENSITIVE_SUFFIXES:
        findings.append(
            Finding(
                rel,
                1,
                "error",
                "credential-file-committed",
                "review committed key or certificate material; secrets must remain outside the repository",
            )
        )

    if ".vscode" in rel.parts and lowered_name == "extensions.json":
        findings.append(
            Finding(
                rel,
                1,
                "error",
                "unsafe-extension-reference",
                "avoid repository-level VS Code extension recommendations without security review",
            )
        )

    return findings


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

        for phrase in NSF_PROHIBITED_ESTABLISHED_FORMULATIONS:
            if phrase.lower() in lowered and not _is_nsf_allowed_context(line, phrase):
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "nsf-prohibited-established-claim",
                        f"classify as future research or unsupported, not established fact: {phrase!r}",
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

        for match in SECRET_ASSIGNMENT_PATTERN.finditer(line):
            name, value = match.groups()
            if _is_sanitized_env_example(rel, name, value):
                continue
            if _looks_like_secret_value(value):
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "secret-pattern",
                        f"possible credential material assigned to {name}; use placeholders only",
                    )
                )

        if GITHUB_TOKEN_PATTERN.search(line):
            findings.append(
                Finding(
                    rel,
                    line_number,
                    "error",
                    "github-token-pattern",
                    "possible GitHub token detected; revoke and rotate before committing",
                )
            )

        for pattern in (AUTHORIZATION_PATTERN, BEARER_PATTERN):
            for match in pattern.finditer(line):
                value = match.group(1)
                if _is_placeholder_value(value):
                    continue
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "bearer-token-pattern",
                        "possible bearer credential detected; never commit authorization headers",
                    )
                )

        for pattern in UNSAFE_EXTENSION_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        rel,
                        line_number,
                        "error",
                        "unsafe-extension-reference",
                        "review VS Code extension references as supply-chain dependencies",
                    )
                )

    return findings


def scan_files(paths: Iterable[Path], root: Path = REPO_ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        findings.extend(scan_path_metadata(path, root=root))
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
