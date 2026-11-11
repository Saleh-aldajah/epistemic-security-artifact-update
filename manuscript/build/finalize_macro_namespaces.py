#!/usr/bin/env python3
"""Namespace RQ3/RQ4 macros and make every identifier LaTeX-safe."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMESPACES = {
    "results_macros_rq3.tex": "RqThree",
    "results_macros_rq4a.tex": "RqFourA",
    "results_macros_rq4c.tex": "RqFourC",
}
REPLACEMENTS = [
    ("B2strict", "BTwoStrict"),
    ("Delta2", "DeltaTwo"),
    ("Delta3", "DeltaThree"),
    ("Delta1", "DeltaOne"),
    ("B1", "BOne"),
    ("B2", "BTwo"),
    ("B3", "BThree"),
    ("Tau030", "TauThirty"),
    ("Tau045", "TauFortyFive"),
    ("Tau050", "TauFifty"),
    ("Tau060", "TauSixty"),
    ("Tau067", "TauSixtySeven"),
    ("F1", "FOne"),
    ("F2", "FTwo"),
    ("F3", "FThree"),
]
for filename, prefix in NAMESPACES.items():
    path = ROOT / filename
    text = path.read_text().replace("\\Sp", "\\" + prefix)
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    path.write_text(text)
    print("namespaced", filename, "as", prefix)
