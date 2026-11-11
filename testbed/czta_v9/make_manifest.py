#!/usr/bin/env python3
"""Hash every shipped source/document file, excluding generated keys and results."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIXES = {".py", ".sh", ".md", ".txt"}
EXCLUDED_NAMES = {"MANIFEST.sha256"}
EXCLUDED_PARTS = {"results", "__pycache__", ".venv"}


def main():
    lines = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name in EXCLUDED_NAMES:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix not in SUFFIXES:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT)}")
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} manifest entries")


if __name__ == "__main__":
    main()
