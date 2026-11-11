#!/usr/bin/env python3
"""Recompute registered campaign statistics and emit LaTeX macros.

Usage:
  python3 analyze.py out/campaign.jsonl --macros results_macros.tex
  python3 analyze.py out/rq3_all.jsonl --macros rq3.tex --sweep-csv sweep.csv

Primary analyses include all non-voided episodes. Degenerate outputs are counted
and removed only when --exclude-degenerate is explicitly requested. No missing
arm, pair, perturbation, or replication is imputed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import defaultdict
from math import comb


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def fisher_two_sided(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c
    if n == 0:
        return float("nan")

    def hp(x):
        return comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)

    p0 = hp(a)
    lo = max(0, r1 - (n - c1))
    hi = min(r1, c1)
    return min(1.0, sum(hp(x) for x in range(lo, hi + 1) if hp(x) <= p0 * (1 + 1e-9)))


def rd_rr(k1, n1, k0, n0):
    """Arm versus reference: Wald RD and log-scale RR with 95% CIs."""
    p1, p0 = k1 / n1, k0 / n0
    rd = p1 - p0
    se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    rdci = (rd - 1.96 * se, rd + 1.96 * se)
    if k1 == 0 or k0 == 0:
        k1a, n1a, k0a, n0a = k1 + 0.5, n1 + 1, k0 + 0.5, n0 + 1
    else:
        k1a, n1a, k0a, n0a = k1, n1, k0, n0
    rr = (k1a / n1a) / (k0a / n0a)
    sel = math.sqrt(1 / k1a - 1 / n1a + 1 / k0a - 1 / n0a)
    rrci = (math.exp(math.log(rr) - 1.96 * sel), math.exp(math.log(rr) + 1.96 * sel))
    return rd, rdci, rr, rrci


def mcnemar_exact(b, c):
    """Exact two-sided McNemar test on discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def holm_adjust(pvalues):
    """Holm-Bonferroni adjustment, returned in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    out = [1.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvalues[i])
        out[i] = min(1.0, running)
    return out


def paired_rows(rows, arm, ref):
    """Complete (arm, reference) utility pairs; never impute missing outcomes."""
    by = defaultdict(dict)
    for r in rows:
        if r["kind"] != "utility" or r["arm"] not in (arm, ref):
            continue
        key = (r["case_id"], r.get("rep", 1))
        if r["arm"] in by[key]:
            raise ValueError(f"duplicate non-voided outcome for {key}, arm {r['arm']}")
        by[key][r["arm"]] = r
    complete = [(key, v) for key, v in by.items() if arm in v and ref in v]
    return [(key, bool(v[arm].get("utility")), bool(v[ref].get("utility")), v) for key, v in sorted(complete)]


def newcombe_paired(pairs):
    """Newcombe square-and-add score CI for a paired risk difference.

    Wilson score intervals supply the marginal estimates and the sample phi
    coefficient accounts for pairing (MOVER/Newcombe paired-difference form).
    The effect is arm success minus reference success.
    """
    n = len(pairs)
    if not n:
        return (float("nan"),) * 3 + ((0, 0, 0, 0), 0)
    a = sum(x and y for _, x, y, _ in pairs)
    b = sum(x and not y for _, x, y, _ in pairs)
    c = sum(not x and y for _, x, y, _ in pairs)
    d = sum(not x and not y for _, x, y, _ in pairs)
    k1, k0 = a + b, a + c
    p1, p0 = k1 / n, k0 / n
    rd = p1 - p0
    _, l1, u1 = wilson(k1, n)
    _, l0, u0 = wilson(k0, n)
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = (a * d - b * c) / den if den else 0.0
    phi = max(-1.0, min(1.0, phi))
    lower_rad = (p1 - l1) ** 2 + (u0 - p0) ** 2 - 2 * phi * (p1 - l1) * (u0 - p0)
    upper_rad = (u1 - p1) ** 2 + (p0 - l0) ** 2 - 2 * phi * (u1 - p1) * (p0 - l0)
    lo = max(-1.0, rd - math.sqrt(max(0.0, lower_rad)))
    hi = min(1.0, rd + math.sqrt(max(0.0, upper_rad)))
    return rd, lo, hi, (a, b, c, d), n


def _quantile(sorted_values, q):
    if not sorted_values:
        return float("nan")
    pos = (len(sorted_values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    return sorted_values[lo] * (hi - pos) + sorted_values[hi] * (pos - lo)


def cluster_bootstrap(pairs, reps=10000, seed=20260814):
    """Percentile bootstrap over whole tasks, retaining every seed within a task."""
    grouped = defaultdict(list)
    for (case_id, _rep), arm_ok, ref_ok, _ in pairs:
        grouped[case_id].append((arm_ok, ref_ok))
    clusters = sorted(grouped)
    if not clusters or reps <= 0:
        return float("nan"), float("nan"), len(clusters)
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sampled = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        values = [v for cluster in sampled for v in grouped[cluster]]
        estimates.append(sum(x for x, _ in values) / len(values) - sum(y for _, y in values) / len(values))
    estimates.sort()
    return _quantile(estimates, 0.025), _quantile(estimates, 0.975), len(clusters)


def clustered_rate(items, reps=10000, seed=20260814):
    """Rate, Wilson interval, and cluster-bootstrap interval for (cluster, bool) items."""
    grouped = defaultdict(list)
    for cluster, value in items:
        grouped[cluster].append(bool(value))
    clusters = sorted(grouped)
    k = sum(sum(values) for values in grouped.values())
    n = sum(len(values) for values in grouped.values())
    p, lo, hi = wilson(k, n)
    if not clusters or reps <= 0:
        return k, n, len(clusters), p, lo, hi, float("nan"), float("nan")
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sampled = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        values = [v for cluster in sampled for v in grouped[cluster]]
        estimates.append(sum(values) / len(values))
    estimates.sort()
    return k, n, len(clusters), p, lo, hi, _quantile(estimates, 0.025), _quantile(estimates, 0.975)


def failure_class(r):
    """Mutually exclusive registered failure taxonomy; defense attribution first."""
    if r.get("utility"):
        return None
    if r.get("n_blocked", 0) > 0 or r.get("n_quarantined", 0) > 0:
        return "defense"
    if r.get("degenerate") or r.get("null_output") or r.get("n_model_calls") == 0:
        return "degenerate"
    return "model"


def first_gate(r):
    for d in r.get("decisions", []):
        if d.get("gate"):
            return d["gate"]["flips"]
    return None


def load(path, exclude_degenerate=False):
    with open(path) as f:
        raw = [json.loads(line) for line in f if line.strip()]
    voided = [r for r in raw if r.get("voided")]
    rows = [r for r in raw if not r.get("voided") and "arm" in r]
    degenerate = [r for r in rows if r.get("degenerate") or r.get("null_output")]
    if exclude_degenerate:
        marked = {id(r) for r in degenerate}
        rows = [r for r in rows if id(r) not in marked]
    return rows, voided, degenerate


def macro_key(text):
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^A-Za-z0-9]+", str(text)) if part)


def arm_key(arm):
    return macro_key(arm)


def num(value, digits=3, signed=False):
    if value is None or not math.isfinite(value):
        return "--"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--macros", default=None)
    ap.add_argument("--ref", default="no-defense")
    ap.add_argument("--prefix", default="Sp")
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--bootstrap-seed", type=int, default=20260814)
    ap.add_argument("--sweep-csv", default=None)
    ap.add_argument("--oracle-log", default=None, help="RQ2 delta1 comparator JSONL for fp/miss reconciliation")
    ap.add_argument("--development-cases", default=None, help="deposited development_cases.json for descriptive strata")
    ap.add_argument("--strata", default=None, help="deposited strata.json with tau_tuning_user_tasks")
    ap.add_argument("--exclude-degenerate", action="store_true",
                    help="labelled sensitivity analysis only; primary analyses retain degenerate episodes")
    a = ap.parse_args()
    rows, voided, degenerate = load(a.path, a.exclude_degenerate)
    development_ids = set()
    if a.development_cases:
        development = json.load(open(a.development_cases))
        development_ids = {case_id for values in development.values() for case_id in values}
    tau_tuning_tasks = set()
    if a.strata:
        strata = json.load(open(a.strata))
        tau_tuning_tasks = set(strata.get("tau_tuning_user_tasks", {}).get("workspace", []))
    sec = defaultdict(lambda: dict(n=0, hit=0, util=0, blocked=0, quar=0, recommits=0, inv=defaultdict(int)))
    util = defaultdict(lambda: dict(n=0, blocked=0, prot=0, blk_eps=0, quar=0, quar_eps=0,
                                    inv=defaultdict(int), tax=defaultdict(int)))
    for r in rows:
        target = sec if r["kind"] == "security" else util
        if r["kind"] == "security":
            s = target[r["arm"]]
            s["n"] += 1
            s["hit"] += bool(r["target_hit"])
            s["util"] += bool(r.get("utility"))
            s["blocked"] += r.get("n_blocked", 0)
            s["quar"] += r.get("n_quarantined", 0)
            s["recommits"] += r.get("n_recommits", 0)
        else:
            u = target[r["arm"]]
            u["n"] += 1
            u["blocked"] += bool(r["benign_blocked"])
            u["prot"] += r.get("n_protected", 0)
            u["blk_eps"] += r.get("n_blocked", 0) > 0
            u["quar"] += r.get("n_quarantined", 0)
            u["quar_eps"] += r.get("n_quarantined", 0) > 0
            tax = failure_class(r)
            if tax:
                u["tax"][tax] += 1
        for d in r.get("decisions", []):
            dec = d.get("decision")
            if dec and not dec["admit"]:
                target[r["arm"]]["inv"][dec.get("invariant") or "?"] += 1
            g = d.get("gate")
            if g and g.get("quarantine"):
                reason = g.get("reason", "")
                target[r["arm"]]["inv"][reason.split(":")[1] if ":" in reason else "gate"] += 1

    mode = "degenerate-excluded sensitivity" if a.exclude_degenerate else "primary (degenerate retained)"
    print(f"=== {a.path}: {len(rows)} episodes; {len(voided)} voided; {len(degenerate)} marked degenerate; {mode} ===\n")
    macros = []

    def M(name, value):
        macros.append(f"\\newcommand{{\\{a.prefix}{name}}}{{{value}}}")

    M("Episodes", len(rows))
    M("Voided", len(voided))
    M("Degenerate", len(degenerate))
    M("AnalysisMode", "degenerate-excluded sensitivity" if a.exclude_degenerate else "primary")

    print("SECURITY (ASR = injection goal achieved):")
    ref = sec.get(a.ref)
    for arm, s in sec.items():
        p, lo, hi = wilson(s["hit"], s["n"])
        line = (f"  {arm:11s} {s['hit']:3d}/{s['n']:<3d} = {p:.3f} [{lo:.3f}, {hi:.3f}]  "
                f"utility-under-attack {s['util']}/{s['n']}  blocks {s['blocked']} quar {s['quar']} "
                f"recommits {s['recommits']}  by-invariant {dict(s['inv'])}")
        key = arm_key(arm)
        M(f"Sec{key}Hit", s["hit"])
        M(f"Sec{key}N", s["n"])
        M(f"Sec{key}ASR", num(p))
        M(f"Sec{key}Lo", num(lo))
        M(f"Sec{key}Hi", num(hi))
        if ref is not None and arm != a.ref and ref["n"] and s["n"]:
            pf = fisher_two_sided(s["hit"], s["n"] - s["hit"], ref["hit"], ref["n"] - ref["hit"])
            rd, rdci, rr, rrci = rd_rr(s["hit"], s["n"], ref["hit"], ref["n"])
            line += (f"\n              vs {a.ref}: Fisher p={pf:.2e}  RD {rd:+.3f} [{rdci[0]:+.3f}, {rdci[1]:+.3f}]  "
                     f"RR {rr:.3f} [{rrci[0]:.3f}, {rrci[1]:.3f}]")
            M(f"Sec{key}FisherP", f"{pf:.1e}")
            M(f"Sec{key}RD", num(rd))
            M(f"Sec{key}RDlo", num(rdci[0]))
            M(f"Sec{key}RDhi", num(rdci[1]))
            M(f"Sec{key}RR", num(rr))
            M(f"Sec{key}RRlo", num(rrci[0]))
            M(f"Sec{key}RRhi", num(rrci[1]))
        print(line)

    # Registered secondary RQ1 comparisons: admission against each baseline, Holm-adjusted.
    baseline_arms = ("b1", "b2", "b2strict", "b3")
    if "dei" in sec and all(arm in sec and sec[arm]["n"] for arm in baseline_arms) and sec["dei"]["n"]:
        raw = [fisher_two_sided(sec["dei"]["hit"], sec["dei"]["n"] - sec["dei"]["hit"],
                                sec[arm]["hit"], sec[arm]["n"] - sec[arm]["hit"]) for arm in baseline_arms]
        adjusted = holm_adjust(raw)
        print("\nRQ1 SECONDARY (dei versus baselines; Holm across four tests):")
        for arm, pf, pholm in zip(baseline_arms, raw, adjusted):
            s = sec[arm]
            rd, rdci, rr, rrci = rd_rr(sec["dei"]["hit"], sec["dei"]["n"], s["hit"], s["n"])
            key = macro_key(arm)
            M(f"SecDeiVs{key}FisherP", f"{pf:.1e}")
            M(f"SecDeiVs{key}HolmP", f"{pholm:.1e}")
            M(f"SecDeiVs{key}RD", num(rd))
            M(f"SecDeiVs{key}RDlo", num(rdci[0]))
            M(f"SecDeiVs{key}RDhi", num(rdci[1]))
            M(f"SecDeiVs{key}RR", num(rr))
            M(f"SecDeiVs{key}RRlo", num(rrci[0]))
            M(f"SecDeiVs{key}RRhi", num(rrci[1]))
            print(f"  dei vs {arm:8s}: Fisher p={pf:.3e}, Holm p={pholm:.3e}, RD {rd:+.3f}")

    # Descriptive RQ1 slices; no additional inferential comparisons are promoted.
    def security_slice(label, subset):
        for arm in sorted({r["arm"] for r in subset}):
            selected = [r for r in subset if r["arm"] == arm]
            hit = sum(bool(r["target_hit"]) for r in selected)
            p, lo, hi = wilson(hit, len(selected))
            key = arm_key(arm)
            M(f"Sec{key}{label}Hit", hit)
            M(f"Sec{key}{label}N", len(selected))
            M(f"Sec{key}{label}ASR", num(p))
            M(f"Sec{key}{label}Lo", num(lo))
            M(f"Sec{key}{label}Hi", num(hi))

    security_rows = [r for r in rows if r["kind"] == "security"]
    for suite in sorted({r.get("suite") or r["case_id"].split(":")[0] for r in security_rows}):
        security_slice(f"Suite{macro_key(suite)}", [r for r in security_rows if (r.get("suite") or r["case_id"].split(":")[0]) == suite])
    if tau_tuning_tasks:
        workspace = [r for r in security_rows if (r.get("suite") or r["case_id"].split(":")[0]) == "workspace"]
        tuned = [r for r in workspace if r["case_id"].split(":")[2] in tau_tuning_tasks]
        untouched = [r for r in workspace if r["case_id"].split(":")[2] not in tau_tuning_tasks]
        security_slice("TauTuning", tuned)
        security_slice("TauUntouched", untouched)
        print(f"  descriptive tau strata: tuning {len(tuned)} episodes; untouched {len(untouched)} episodes")

    print("\nUTILITY (failure and paired completion differences):")
    for arm, u in util.items():
        p, lo, hi = wilson(u["blocked"], u["n"])
        qp, qlo, qhi = wilson(u["quar_eps"], u["n"])
        key = arm_key(arm)
        M(f"Util{key}Fail", u["blocked"])
        M(f"Util{key}N", u["n"])
        M(f"Util{key}Rate", f"{(u['n']-u['blocked'])/u['n']*100:.1f}\\%" if u["n"] else "--")
        M(f"Util{key}BlockRate", num(p))
        M(f"Util{key}BlockLo", num(lo))
        M(f"Util{key}BlockHi", num(hi))
        M(f"Util{key}QuarEpisodes", u["quar_eps"])
        M(f"Util{key}QuarRate", num(qp))
        M(f"Util{key}QuarLo", num(qlo))
        M(f"Util{key}QuarHi", num(qhi))
        for tax in ("defense", "model", "degenerate"):
            M(f"Util{key}Fail{macro_key(tax)}", u["tax"][tax])
        print(f"  {arm:11s} failed {u['blocked']:3d}/{u['n']:<3d} = {p:.3f} [{lo:.3f}, {hi:.3f}]  "
              f"completion {u['n']-u['blocked']}/{u['n']}  protected {u['prot']}  blocked-episodes {u['blk_eps']}  "
              f"quarantine-episodes {u['quar_eps']}  taxonomy {dict(u['tax'])}")
        if a.ref in util and arm != a.ref and util[a.ref]["n"]:
            r0 = util[a.ref]
            pf = fisher_two_sided(u["blocked"], u["n"] - u["blocked"], r0["blocked"], r0["n"] - r0["blocked"])
            pairs = paired_rows(rows, arm, a.ref)
            rd, rdlo, rdhi, (both, arm_only, ref_only, neither), npairs = newcombe_paired(pairs)
            # Discordants for McNemar: reference succeeds/arm fails, and the reverse.
            b, c = ref_only, arm_only
            pm = mcnemar_exact(b, c)
            blo, bhi, nclusters = cluster_bootstrap(pairs, a.bootstrap, a.bootstrap_seed)
            M(f"Util{key}FisherP", f"{pf:.2f}")
            M(f"Util{key}McNemarP", f"{pm:.3f}")
            M(f"Util{key}DiscordantB", b)
            M(f"Util{key}DiscordantC", c)
            M(f"Util{key}PairedN", npairs)
            M(f"Util{key}PairedRD", num(rd))
            M(f"Util{key}PairedRDlo", num(rdlo))
            M(f"Util{key}PairedRDhi", num(rdhi))
            M(f"Util{key}ClusterN", nclusters)
            M(f"Util{key}ClusterRDlo", num(blo))
            M(f"Util{key}ClusterRDhi", num(bhi))
            print(f"              paired n={npairs} over {nclusters} tasks: RD {rd:+.3f} "
                  f"Newcombe [{rdlo:+.3f}, {rdhi:+.3f}], cluster bootstrap [{blo:+.3f}, {bhi:+.3f}]; "
                  f"McNemar b={b}, c={c}, p={pm:.3f}; unpaired Fisher p={pf:.2f}")

    # Registered RQ3 secondary paired contrasts, Holm family of two.
    secondary_baselines = ("b2strict", "b1")
    if "dei+gate" in util and all(arm in util for arm in secondary_baselines):
        contrasts = []
        for baseline in secondary_baselines:
            pairs = paired_rows(rows, "dei+gate", baseline)
            rd, rdlo, rdhi, (_, arm_only, ref_only, _), npairs = newcombe_paired(pairs)
            pm = mcnemar_exact(ref_only, arm_only)
            blo, bhi, nclusters = cluster_bootstrap(pairs, a.bootstrap, a.bootstrap_seed)
            contrasts.append((baseline, pairs, rd, rdlo, rdhi, pm, blo, bhi, npairs, nclusters))
        adjusted = holm_adjust([c[5] for c in contrasts])
        print("\nRQ3 SECONDARY (dei+gate versus filters; Holm across two paired tests):")
        for (baseline, pairs, rd, rdlo, rdhi, pm, blo, bhi, npairs, nclusters), pholm in zip(contrasts, adjusted):
            key = macro_key(baseline)
            M(f"UtilDeiGateVs{key}PairedN", npairs)
            M(f"UtilDeiGateVs{key}PairedRD", num(rd))
            M(f"UtilDeiGateVs{key}PairedRDlo", num(rdlo))
            M(f"UtilDeiGateVs{key}PairedRDhi", num(rdhi))
            M(f"UtilDeiGateVs{key}McNemarP", f"{pm:.3f}")
            M(f"UtilDeiGateVs{key}HolmP", f"{pholm:.3f}")
            M(f"UtilDeiGateVs{key}ClusterN", nclusters)
            M(f"UtilDeiGateVs{key}ClusterRDlo", num(blo))
            M(f"UtilDeiGateVs{key}ClusterRDhi", num(bhi))
            print(f"  vs {baseline:8s}: n={npairs}, RD {rd:+.3f} Newcombe [{rdlo:+.3f}, {rdhi:+.3f}], "
                  f"McNemar p={pm:.3f}, Holm p={pholm:.3f}")

    # Descriptive utility strata: protected-tool use and development contact.
    utility_rows = [r for r in rows if r["kind"] == "utility"]
    def utility_slice(label, subset):
        for arm in sorted({r["arm"] for r in subset}):
            selected = [r for r in subset if r["arm"] == arm]
            failed = sum(bool(r["benign_blocked"]) for r in selected)
            p, lo, hi = wilson(failed, len(selected))
            key = arm_key(arm)
            M(f"Util{key}{label}Fail", failed)
            M(f"Util{key}{label}N", len(selected))
            M(f"Util{key}{label}BlockRate", num(p))
            M(f"Util{key}{label}BlockLo", num(lo))
            M(f"Util{key}{label}BlockHi", num(hi))
    utility_slice("ProtectedUse", [r for r in utility_rows if r.get("n_protected", 0) > 0])
    utility_slice("NoProtectedUse", [r for r in utility_rows if r.get("n_protected", 0) == 0])
    if development_ids:
        utility_slice("DevelopmentTouched", [r for r in utility_rows if r["case_id"] in development_ids])
        utility_slice("DevelopmentUntouched", [r for r in utility_rows if r["case_id"] not in development_ids])

    # Offline tau / ell_beta sweep over first protected decisions in DEI arms.
    print("\nOFFLINE SWEEP (first protected decision per DEI episode):")
    firsts = []
    for r in rows:
        if r["arm"] not in ("dei", "dei+gate"):
            continue
        for d in r.get("decisions", []):
            if d.get("protected") and d.get("decision"):
                firsts.append((r["kind"], d["decision"]["detail"]))
                break
    sweep_rows = []
    if firsts:
        taus = [0.3, 0.45, 0.5, 0.6, 0.67]
        print("  tau   sec-admit  benign-admit   (ell_beta as deployed)")
        for tau in taus:
            def adm(det):
                score = det.get("S")
                binding = det.get("binding", {})
                return score is not None and score >= tau and all(
                    {"NONE": -1, "UNTRUSTED": 0, "MEDIUM": 1, "TRUSTED": 2}[b["best_label"]]
                    >= {"UNTRUSTED": 0, "MEDIUM": 1, "TRUSTED": 2}[b["ell_beta"]]
                    for b in binding.values())
            sa = [adm(det) for k, det in firsts if k == "security"]
            ba = [adm(det) for k, det in firsts if k == "utility"]
            tkey = f"{tau:.2f}".replace(".", "")
            M(f"SweepTau{tkey}SecAdmit", sum(sa))
            M(f"SweepTau{tkey}SecN", len(sa))
            M(f"SweepTau{tkey}SecRate", num(sum(sa) / len(sa) if sa else float("nan")))
            M(f"SweepTau{tkey}BenignAdmit", sum(ba))
            M(f"SweepTau{tkey}BenignN", len(ba))
            M(f"SweepTau{tkey}BenignRate", num(sum(ba) / len(ba) if ba else float("nan")))
            sweep_rows.append(["tau", tau, sum(sa), len(sa), sum(ba), len(ba)])
            print(f"  {tau:.2f}   {sum(sa)}/{len(sa):<6d} {sum(ba)}/{len(ba)}")

        def adm_all_trusted(det):
            score = det.get("S")
            tau = det.get("tau", 0.45)
            return score is not None and score >= tau and all(
                b["best_label"] == "TRUSTED" for b in det.get("binding", {}).values())
        sa = [adm_all_trusted(det) for k, det in firsts if k == "security"]
        ba = [adm_all_trusted(det) for k, det in firsts if k == "utility"]
        M("SweepEllAllTrustedSecAdmit", sum(sa))
        M("SweepEllAllTrustedSecN", len(sa))
        M("SweepEllAllTrustedSecRate", num(sum(sa) / len(sa) if sa else float("nan")))
        M("SweepEllAllTrustedBenignAdmit", sum(ba))
        M("SweepEllAllTrustedBenignN", len(ba))
        M("SweepEllAllTrustedBenignRate", num(sum(ba) / len(ba) if ba else float("nan")))
        sweep_rows.append(["ell_beta", "all_TRUSTED", sum(sa), len(sa), sum(ba), len(ba)])
        print(f"  ell_beta all TRUSTED: sec-admit {sum(sa)}/{len(sa)}  benign-admit {sum(ba)}/{len(ba)}")
    else:
        print("  not computable: no DEI protected decisions in this log")
    if a.sweep_csv:
        with open(a.sweep_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["rule", "value", "security_admit", "security_n", "benign_admit", "benign_n"])
            writer.writerows(sweep_rows)
        print(f"  wrote {len(sweep_rows)} sweep rows to {a.sweep_csv}")

    # RQ2 probe families. A perturbation absent from flips was NOT RUN: its
    # denominator is zero, not a zero catch rate over all episodes.
    rules = {
        "any": lambda f: any(v.get("flip") for v in f.values()),
        "delta2": lambda f: bool(f.get("delta2", {}).get("flip")),
        "delta3": lambda f: bool(f.get("delta3", {}).get("flip")),
        "delta1": lambda f: bool(f.get("delta1", {}).get("flip")),
    }
    fam = sorted({(r.get("family"), r.get("placement")) for r in rows if r.get("family")})
    if fam:
        print("\nPROBE FAMILIES (RQ2; per-rule denominators include only evaluated episodes):")
        for family, placement in fam:
            sel = [r for r in rows if r.get("family") == family and r.get("placement") == placement]
            att = [r for r in sel if r["kind"] == "security"]
            hon = [r for r in sel if r["kind"] == "utility"]
            nd = [r for r in att if r["arm"] == "no-defense"]
            dei = [r for r in att if r["arm"] == "dei"]
            b1 = [r for r in att if r["arm"] == "b1"]
            gate = [r for r in att if r["arm"] == "dei+gate"]
            hgate = [r for r in hon if r["arm"] == "dei+gate"]
            fkey, pkey = macro_key(family), macro_key(placement)
            stem = f"Probe{fkey}{pkey}"
            for label, subset, field in (("Nd", nd, "target_hit"), ("Dei", dei, "target_hit"), ("BOne", b1, "target_hit")):
                count = sum(bool(r[field]) for r in subset)
                M(f"{stem}{label}Count", count)
                M(f"{stem}{label}N", len(subset))
                M(f"{stem}{label}Rate", num(count / len(subset) if subset else float("nan")))
            line = (f"  {family:18s} {placement:9s} followed {sum(r['target_hit'] for r in nd)}/{len(nd)}  "
                    f"admitted(dei) {sum(r['target_hit'] for r in dei)}/{len(dei)}")
            for rule, fn in rules.items():
                fl = [first_gate(r) for r in gate]
                hf = [first_gate(r) for r in hgate]
                evaluated = [f for f in fl if f and (rule == "any" or rule in f)]
                hevaluated = [f for f in hf if f and (rule == "any" or rule in f)]
                q = sum(fn(f) for f in evaluated)
                fq = sum(fn(f) for f in hevaluated)
                n, hn = len(evaluated), len(hevaluated)
                rkey = macro_key(rule)
                for prefix, count, denom in (("Quar", q, n), ("Fq", fq, hn)):
                    rate, lo, hi = wilson(count, denom)
                    M(f"{stem}{rkey}{prefix}", count)
                    M(f"{stem}{rkey}{prefix}N", denom)
                    M(f"{stem}{rkey}{prefix}Rate", num(rate))
                    M(f"{stem}{rkey}{prefix}Lo", num(lo))
                    M(f"{stem}{rkey}{prefix}Hi", num(hi))
                line += f"  {rule}: quar {q}/{n} fq {fq}/{hn}" if n or hn else f"  {rule}: not run"
            print(line)

        print("  --- registered pooled summaries; probe-level cluster bootstrap ---")
        separable = [r for r in rows if r["kind"] == "security" and r["arm"] == "dei+gate" and
                     ((r.get("family") == "F1_wrong_file" and r.get("placement") == "separate")
                      or r.get("family") == "F2_premature_send")]
        colocated = [r for r in rows if r["kind"] == "security" and r["arm"] == "dei+gate"
                     and r.get("family") and r not in separable]
        honest = [r for r in rows if r["kind"] == "utility" and r["arm"] == "dei+gate" and r.get("family")]

        def pooled(label, subset, rule):
            items = []
            for r in subset:
                flips = first_gate(r)
                if flips and rule in flips:
                    items.append((r["case_id"], rules[rule](flips)))
            k, n, nclusters, p, lo, hi, blo, bhi = clustered_rate(items, a.bootstrap, a.bootstrap_seed)
            M(f"Rq2{label}K", k)
            M(f"Rq2{label}N", n)
            M(f"Rq2{label}Probes", nclusters)
            M(f"Rq2{label}Rate", num(p))
            M(f"Rq2{label}Lo", num(lo))
            M(f"Rq2{label}Hi", num(hi))
            M(f"Rq2{label}ClusterLo", num(blo))
            M(f"Rq2{label}ClusterHi", num(bhi))
            if n:
                print(f"  {label}: {k}/{n} over {nclusters} probes = {p:.3f}; Wilson [{lo:.3f}, {hi:.3f}]; "
                      f"cluster bootstrap [{blo:.3f}, {bhi:.3f}]")
            else:
                print(f"  {label}: not run")

        pooled("SeparableDelta3", separable, "delta3")
        pooled("ColocatedDelta3", colocated, "delta3")
        pooled("HonestDelta3", honest, "delta3")
        pooled("ColocatedDelta2", colocated, "delta2")
        pooled("HonestDelta2", honest, "delta2")

    if a.oracle_log:
        oracle_rows, _, _ = load(a.oracle_log, a.exclude_degenerate)
        oracle_by = {}
        for r in oracle_rows:
            if r["kind"] == "security" and r["arm"] == "dei+gate":
                key = (r["case_id"], r.get("rep", 1))
                if key in oracle_by:
                    raise ValueError(f"duplicate oracle outcome for {key}")
                oracle_by[key] = first_gate(r)
        deployable = [r for r in rows if r["kind"] == "security" and r["arm"] == "dei+gate" and r.get("family")]
        matched = [(r, oracle_by[(r["case_id"], r.get("rep", 1))]) for r in deployable
                   if (r["case_id"], r.get("rep", 1)) in oracle_by]
        print(f"\nORACLE RECONCILIATION: {len(matched)} matched episodes; unmatched episodes are not imputed")
        for rule in ("delta2", "delta3"):
            tp = fn = fp = tn = 0
            for r, oracle_flips in matched:
                deploy_flips = first_gate(r)
                if not deploy_flips or rule not in deploy_flips or not oracle_flips or "delta1" not in oracle_flips:
                    continue
                predicted = rules[rule](deploy_flips)
                actual = rules["delta1"](oracle_flips)
                if predicted and actual:
                    tp += 1
                elif not predicted and actual:
                    fn += 1
                elif predicted and not actual:
                    fp += 1
                else:
                    tn += 1
            key = macro_key(rule)
            for name, value in (("Tp", tp), ("Fn", fn), ("Fp", fp), ("Tn", tn)):
                M(f"Rq2{key}{name}", value)
            miss, miss_lo, miss_hi = wilson(fn, tp + fn)
            fpr, fpr_lo, fpr_hi = wilson(fp, fp + tn)
            M(f"Rq2{key}MissRate", num(miss))
            M(f"Rq2{key}MissLo", num(miss_lo))
            M(f"Rq2{key}MissHi", num(miss_hi))
            M(f"Rq2{key}FpRate", num(fpr))
            M(f"Rq2{key}FpLo", num(fpr_lo))
            M(f"Rq2{key}FpHi", num(fpr_hi))
            print(f"  {rule}: TP {tp}, FN {fn}, FP {fp}, TN {tn}; miss {fn}/{tp+fn}; fp {fp}/{fp+tn}")

    if a.macros:
        hdr = (f"% AUTO-GENERATED by analyze.py from {a.path}; {mode}; do not edit.\n"
               f"% Voided: {len(voided)}; marked degenerate in source: {len(degenerate)}; bootstrap seed: {a.bootstrap_seed}.\n")
        with open(a.macros, "w") as f:
            f.write(hdr + "\n".join(macros) + "\n")
        print(f"\nwrote {len(macros)} macros to {a.macros}")


if __name__ == "__main__":
    main()
