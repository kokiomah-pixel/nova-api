#!/usr/bin/env python3
import re
from pathlib import Path

# Exact replacements (only public-facing / docs / examples)
REPLACEMENTS = [
    (r"", "governance substrate"),
    (r"", "pre-execution governance layer"),
    (r"\bexecute\b", "admit"),
    (r"\bexecution\b", "admit"),
    (r"control the decision", "condition the intent"),
    (r"\bdictate\b", "condition"),
    (r"\bprescribe\b", "condition"),
    (r"run a decision", "evaluate an intent"),
    (r"safety layer", "retained discipline layer"),
    (r"guardrails", "retained discipline layer"),
    (r"decision admission", "intent admissibility"),
]

# Target files and folders
TARGETS = [
    "README.md",
    "START_HERE.md",
    "bazaar_metadata.py",
    "app.py",                    # only comments/docstrings will be touched
    Path("examples"),
    Path("docs"),
    Path("specs"),
]

def replace_in_file(file_path: Path):
    if not file_path.is_file():
        return
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        for old, new in REPLACEMENTS:
            content = re.sub(old, new, content, flags=re.IGNORECASE)
        if content != original:
            file_path.write_text(content, encoding="utf-8")
            print(f"✓ Updated: {file_path}")
        else:
            print(f"  No change: {file_path}")
    except Exception as e:
        print(f"✗ Error in {file_path}: {e}")

def main():
    print("Starting terminology alignment...\n")
    for target in TARGETS:
        if isinstance(target, str):
            replace_in_file(Path(target))
        else:
            # It's a folder
            for file in target.rglob("**/*"):
                if file.suffix in [".md", ".py", ".json"]:
                    replace_in_file(file)
    print("\nTerminology alignment complete.")

if __name__ == "__main__":
    main()