#!/usr/bin/env python3
"""Merge three independently restarted repetitions of one arm without altering raw files."""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=["A0", "A1", "A2"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args()
    documents = []
    for name in args.inputs:
        match = re.search(r"_rep([123])(?:\.json)?$", name)
        if not match:
            raise SystemExit(f"Cannot infer repetition from filename: {name}")
        rep = int(match.group(1))
        doc = json.loads(Path(name).read_text())
        if doc.get("arm") != args.arm or doc.get("status") != "PASS" or doc.get("errors"):
            raise SystemExit(f"Invalid or failed input: {name}")
        documents.append((rep, doc))
    if sorted(rep for rep, _ in documents) != [1, 2, 3]:
        raise SystemExit("Need exactly rep1, rep2, rep3")
    hashes = {doc["implementation"]["code_manifest_sha256"] for _, doc in documents}
    if len(hashes) != 1:
        raise SystemExit("Code hash changed between repetitions")
    base = copy.deepcopy(documents[0][1])
    runs = []
    for rep, doc in sorted(documents):
        if doc.get("reps") != 1:
            raise SystemExit(f"Input was not a single-repetition run: {doc}")
        for run in doc["runs"]:
            if run.get("errors"):
                raise SystemExit(f"Measured errors in rep {rep}")
            run["rep"] = rep
            runs.append(run)
    base["reps"] = 3
    base["runs"] = sorted(runs, key=lambda r: (r["rate_req_s"], r["rep"]))
    base["status"] = "PASS"
    base["errors"] = []
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(base, indent=2) + "\n")
    print(f"WROTE {out}: PASS (three independently restarted repetitions)")


if __name__ == "__main__":
    main()
