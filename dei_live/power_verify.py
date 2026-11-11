#!/usr/bin/env python3
"""Independently reproduce the registered power and resolution calculations.

Standard two-proportion normal approximations are used for independent grids and
asymptotic McNemar power for the registered paired claims. Exact McNemar
enumeration is also printed as a conservative sensitivity analysis. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
from statistics import NormalDist

N = NormalDist()


def two_proportion_power(n, p0, p1, alpha=0.05):
    if not (0 <= p0 <= 1 and 0 <= p1 <= 1):
        return float("nan")
    pbar = (p0 + p1) / 2
    se_null = math.sqrt(2 * pbar * (1 - pbar) / n)
    se_alt = math.sqrt(p0 * (1 - p0) / n + p1 * (1 - p1) / n)
    if se_alt == 0:
        return float(p0 != p1)
    delta = p0 - p1
    z = N.inv_cdf(1 - alpha / 2)
    return N.cdf((-z * se_null - delta) / se_alt) + 1 - N.cdf((z * se_null - delta) / se_alt)


def independent_sample_size(p0, p1, power, alpha=0.05):
    pbar = (p0 + p1) / 2
    z_alpha = N.inv_cdf(1 - alpha / 2)
    z_power = N.inv_cdf(power)
    numerator = (z_alpha * math.sqrt(2 * pbar * (1 - pbar))
                 + z_power * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2
    return numerator / (p0 - p1) ** 2


def mde(p0, n, alpha=0.05, target_power=0.8):
    for i in range(1, 1000):
        d = i / 1000
        if two_proportion_power(n, p0, p0 - d, alpha) >= target_power:
            return d
    return None


def mcnemar_power(n, q, d=0.1, alpha=0.05):
    sd = math.sqrt(q - d * d)
    mean = math.sqrt(n) * d / sd
    critical = N.inv_cdf(1 - alpha / 2) * math.sqrt(q) / sd
    return (1 - N.cdf(critical - mean)) + N.cdf(-critical - mean)


def _pmf(k, n, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def _exact_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def mcnemar_power_exact(n, q, d=0.1, alpha=0.05):
    ratio = (q + d) / (2 * q)
    total = 0.0
    for k in range(n + 1):
        pk = _pmf(k, n, q)
        if pk < 1e-16:
            continue
        reject = 0.0
        for b in range(k + 1):
            if _exact_p(b, k - b) <= alpha:
                reject += _pmf(b, k, ratio)
        total += pk * reject
    return total


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = {
        "method": {
            "independent": "standard two-proportion normal approximation, two-sided alpha=0.05",
            "paired_registered": "asymptotic McNemar power, two-sided alpha=0.05",
            "paired_sensitivity": "exact conditional McNemar enumeration",
        },
        "rq3_independent_floor": {
            "80_percent": math.ceil(independent_sample_size(0.833, 0.733, 0.8)),
            "90_percent": math.ceil(independent_sample_size(0.833, 0.733, 0.9)),
        },
        "rq3_paired_power_291": {},
        "rq3_paired_exact_sensitivity_291": {},
        "rq1_mde_150": {str(p): mde(p, 150) for p in (0.30, 0.45)},
        "rq1_dei_vs_b1_holm_mde": {str(p): mde(p, 150, alpha=0.0125) for p in (0.10, 0.15, 0.20)},
        "rq1_benign_descriptive_mde_56_at_baseline_0_30": mde(0.30, 56),
        "rq4b_mde_60": {str(p): mde(p, 60) for p in (0.30, 0.45)},
        "rq4c_mde_150_baseline_0_25": mde(0.25, 150),
        "pilot_size_effect_power": {
            "rq1_150_0_45_to_0_05": two_proportion_power(150, 0.45, 0.05),
            "rq4b_60_0_45_to_0_05": two_proportion_power(60, 0.45, 0.05),
        },
        "probe_bounds": {
            "5_of_5_wilson": wilson(5, 5),
            "39_of_40_wilson": wilson(39, 40),
            "0_of_60_wilson": wilson(0, 60),
            "0_of_60_rule_of_three": 3 / 60,
        },
    }
    for q in (0.345, 0.30, 0.20):
        result["rq3_paired_power_291"][str(q)] = mcnemar_power(291, q)
        result["rq3_paired_exact_sensitivity_291"][str(q)] = mcnemar_power_exact(291, q)

    assert result["rq3_independent_floor"] == {"80_percent": 266, "90_percent": 355}
    assert abs(result["rq3_paired_power_291"]["0.345"] - 0.831) < 0.002
    assert abs(result["rq3_paired_power_291"]["0.3"] - 0.880) < 0.002
    assert abs(result["rq3_paired_power_291"]["0.2"] - 0.971) < 0.002
    assert result["probe_bounds"]["0_of_60_wilson"][2] < 0.061
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n")


if __name__ == "__main__":
    main()
