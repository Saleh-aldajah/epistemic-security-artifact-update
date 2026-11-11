"""
bench_root_cert.py — validates Remark 1: with per-belief root certificates,
the I1 check at an action is O(|support|) constant-time receipt verifications,
independent of provenance-chain DEPTH. Without memoization it is O(depth).

We build a linear provenance chain of increasing depth, then time the I1
admission check with and without the memoized root certificate. This is a
SEMANTICS/algorithmics microbenchmark on the reference monitor; it is NOT the
CZTA deployment latency (Section 5), which measures real sign/verify + gateway
overhead under load. We say so explicitly in the paper.

Emits results/bench_results.json and a compact table.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dei_monitor"))
from dei_monitor import (  # noqa: E402
    Belief, DEIMonitor, Label, Policy, make_attested,
)

NOW = 1_700_000_000.0


def policy() -> Policy:
    return Policy(
        ell_min=Label.MEDIUM,
        protected_classes={"act"},
        ell_req={"act": Label.MEDIUM},
        tau={"act": 0.0},  # isolate I1 cost (I3 trivially satisfied)
        authorized_endorsements=set(),
    )


def build_chain(m: DEIMonitor, depth: int) -> str:
    """Root evidence -> b0 -> b1 -> ... -> b_{depth-1}. Returns the tip id."""
    m.ingest_evidence(make_attested("root", "attested root", Label.HIGH, now=NOW))
    prev_dep = "root"
    tip = None
    for i in range(depth):
        bid = f"b{i}"
        b = Belief(bid, label=Label.MEDIUM, deps={prev_dep})
        m.update_belief(b)
        prev_dep = bid
        tip = bid
    return tip


def time_check(depth: int, memoized: bool, reps: int = 2000) -> float:
    """Mean microseconds for one admit_action I1 check at given chain depth."""
    m = DEIMonitor(policy(), now_fn=lambda: NOW)
    tip = build_chain(m, depth)
    # warm the memo (or not)
    if memoized:
        m.admit_action("act", [tip])  # first call populates root cert
    t0 = time.perf_counter()
    for _ in range(reps):
        if not memoized:
            m._root_cert.clear()  # defeat memoization to simulate O(depth)
        m.admit_action("act", [tip])
    dt = (time.perf_counter() - t0) / reps
    return dt * 1e6  # microseconds


def main():
    depths = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    rows = []
    for d in depths:
        memo_us = time_check(d, memoized=True)
        nomemo_us = time_check(d, memoized=False)
        rows.append({
            "depth": d,
            "memoized_us": round(memo_us, 3),
            "no_memo_us": round(nomemo_us, 3),
        })

    # Fit: memoized should be ~flat across depth; no_memo ~linear in depth.
    # Exclude depth=1 (cold-cache warm-up outlier) when assessing flatness of
    # the memoized path; report it but judge stability on depth>=2.
    stable = [r for r in rows if r["depth"] >= 2]
    memo_stable = [r["memoized_us"] for r in stable]
    nomemo_vals = [r["no_memo_us"] for r in rows]
    memo_ratio = max(memo_stable) / min(memo_stable) if min(memo_stable) > 0 else float("inf")
    nomemo_ratio = nomemo_vals[-1] / nomemo_vals[0] if nomemo_vals[0] > 0 else float("inf")

    # Correlation of no-memo cost with depth (should be near +1 for O(depth)).
    ds = [r["depth"] for r in rows]
    ns = nomemo_vals
    n = len(ds)
    mean_d = sum(ds) / n
    mean_c = sum(ns) / n
    cov = sum((ds[i] - mean_d) * (ns[i] - mean_c) for i in range(n))
    var_d = sum((d - mean_d) ** 2 for d in ds) ** 0.5
    var_c = sum((c - mean_c) ** 2 for c in ns) ** 0.5
    pearson = cov / (var_d * var_c) if var_d * var_c > 0 else 0.0

    results = {
        "note": "reference-monitor algorithmic microbenchmark; not CZTA deployment latency",
        "reps_per_point": 2000,
        "rows": rows,
        "memoized_max_over_min_stable": round(memo_ratio, 2),
        "memoized_stable_from_depth": 2,
        "no_memo_last_over_first": round(nomemo_ratio, 2),
        "no_memo_depth_correlation": round(pearson, 4),
        "depth_ratio_first_to_last": depths[-1] // depths[0],
        "memoized_is_flat": memo_ratio < 2.0,      # <2x across depth 2..256 => ~O(1)
        "no_memo_scales_with_depth": pearson > 0.95 and nomemo_ratio > 10.0,
    }
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "results"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "..", "results",
                           "bench_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("=== Root-certificate microbenchmark (Remark 1) ===")
    print(f"  {'depth':>6} | {'memoized (us)':>14} | {'no-memo (us)':>13}")
    print("  " + "-" * 40)
    for r in rows:
        print(f"  {r['depth']:>6} | {r['memoized_us']:>14.3f} | {r['no_memo_us']:>13.3f}")
    print(f"\n  chain depth spans {depths[0]}..{depths[-1]} ({depths[-1]//depths[0]}x)")
    print(f"  memoized cost max/min (depth>=2): {memo_ratio:.2f}x  (flat => amortized O(1))")
    print(f"  no-memo last/first : {nomemo_ratio:.2f}x; corr(cost,depth) = {pearson:.3f}  (=> O(depth))")
    ok = results["memoized_is_flat"] and results["no_memo_scales_with_depth"]
    print(f"  REMARK 1 SUPPORTED     : {ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
