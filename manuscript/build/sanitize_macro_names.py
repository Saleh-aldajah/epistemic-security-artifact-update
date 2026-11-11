#!/usr/bin/env python3
"""Make analyzer-generated LaTeX macro names legal (no digits)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = [
    ("B2strict", "BTwoStrict"),
    ("Delta2", "DeltaTwo"),
    ("Delta3", "DeltaThree"),
    ("Delta1", "DeltaOne"),
    ("B1", "BOne"),
    ("B2", "BTwo"),
    ("B3", "BThree"),
]
for name in ("results_macros_rq1.tex", "results_macros_rq2.tex"):
    path = ROOT / name
    text = path.read_text()
    for old, new in MAPPING:
        text = text.replace(old, new)
    path.write_text(text)
    print("sanitized", name)
