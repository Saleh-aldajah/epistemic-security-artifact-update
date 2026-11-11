#!/usr/bin/env python3
"""Combine A0/A1/A2 protocol outputs and compute relative A2-A0 overhead."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--out", default="results/testbed.json")
    args = parser.parse_args()
    documents = [json.loads(Path(p).read_text()) for p in args.inputs]
    if sorted(d["arm"] for d in documents) != ["A0", "A1", "A2"]:
        raise SystemExit("Need exactly one result document for each arm A0, A1, A2")
    if any(d["status"] != "PASS" for d in documents):
        raise SystemExit("All arms must PASS with zero errors before combination")
    runs = [run for d in documents for run in d["runs"]]
    summary = []
    for rate in sorted({r["rate_req_s"] for r in runs}):
        by_arm = {arm: [r for r in runs if r["arm"] == arm and r["rate_req_s"] == rate] for arm in ("A0", "A1", "A2")}
        if any(len(by_arm[arm]) != 3 for arm in by_arm):
            raise SystemExit(f"Rate {rate} does not have three repetitions for every arm")
        row = {"rate_req_s": rate}
        for arm, group in by_arm.items():
            row[arm] = {
                "p50_ms": [r["p50_ms"] for r in group],
                "p95_ms": [r["p95_ms"] for r in group],
                "measured_requests": sum(r["measured_requests"] for r in group),
            }
        a0_p50 = sum(r["p50_ms"] for r in by_arm["A0"]) / 3
        a2_p50 = sum(r["p50_ms"] for r in by_arm["A2"]) / 3
        row["a2_minus_a0_p50_ms"] = a2_p50 - a0_p50
        row["a2_minus_a0_p50_percent"] = 100.0 * (a2_p50 - a0_p50) / a0_p50 if a0_p50 else None
        summary.append(row)
    result = {
        "protocol": "czta-v9-replacement-open-loop-v2",
        "status": "PASS",
        "documents": [d for d in documents],
        "summary": summary,
        "note": "Relative overhead is implementation- and deployment-specific. With a stub upstream it is an upper-bound testbed measurement, not a production-latency claim.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"WROTE {out}: PASS")


if __name__ == "__main__":
    main()
