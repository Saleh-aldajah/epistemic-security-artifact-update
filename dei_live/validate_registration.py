#!/usr/bin/env python3
"""Audit deposited case separation, episode counts, and deterministic ordering."""
from __future__ import annotations

import argparse
import json
import pathlib

from run_campaign import ARMS_ALL, episode_plan

EXPECTED_HELD = {
    "workspace": {"sec": 60, "util": 2},
    "slack": {"sec": 30, "util": 20},
    "travel": {"sec": 30, "util": 19},
    "banking": {"sec": 30, "util": 15},
}
EXPECTED_EPISODES = {
    "rq1": (150 + 56) * 7,
    "rq2_main": (20 + 20) * 4 * 4,
    "rq2_oracle_security_only": 20 * 1 * 4,
    "rq3": 97 * 4 * 3,
    "rq4a": (150 + 56) * 4,
    "rq4b": 60 * 2,
    "rq4c": 150 * 3,
}


def read_log(path):
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    value = json.loads(path.read_text())
    if isinstance(value, list):
        return value
    for key in ("episodes", "results", "rows"):
        if isinstance(value.get(key), list):
            return value[key]
    raise ValueError(f"no episode list in {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registration", default="registration")
    ap.add_argument("--log", action="append", default=[], help="development JSON/JSONL to audit against the deposit")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    root = pathlib.Path(args.registration)
    held = json.loads((root / "held_out_cases.json").read_text())
    development = json.loads((root / "development_cases.json").read_text())
    probes = json.loads((root / "probe_cases.json").read_text())
    strata = json.loads((root / "strata.json").read_text())

    counts = {}
    overlaps = {}
    for suite, expected in EXPECTED_HELD.items():
        ids = held[suite]
        counts[suite] = {"sec": sum(":sec:" in x for x in ids), "util": sum(":util:" in x for x in ids)}
        assert counts[suite] == expected, (suite, counts[suite], expected)
        overlap = set(ids) & set(development.get(suite, []))
        overlaps[suite] = sorted(overlap)
        assert not overlap, (suite, sorted(overlap)[:5])
        assert all(":sec:" not in x or x.split(":")[2] != "user_task_0" for x in ids)

    workspace_benign = sorted(x for x in held["workspace"] if ":util:" in x)
    assert workspace_benign == ["workspace:util:user_task_23", "workspace:util:user_task_39"]
    tau = strata["tau_tuning_user_tasks"]["workspace"]
    assert len(tau) == 22 and len(set(tau)) == 22
    dev_workspace_benign = {x.split(":")[2] for x in development["workspace"] if ":util:" in x}
    assert set(tau) <= dev_workspace_benign
    for suite in EXPECTED_HELD:
        assert f"{suite}:util:user_task_0" in development[suite]

    assert sum(":probe:" in x["id"] and ":probe-honest:" not in x["id"] for x in probes) == 20
    assert sum(":probe-honest:" in x["id"] for x in probes) == 20
    assert EXPECTED_EPISODES == {
        "rq1": 1442, "rq2_main": 640, "rq2_oracle_security_only": 80,
        "rq3": 1164, "rq4a": 824, "rq4b": 120, "rq4c": 450,
    }
    rq2_denominators = {"separable_attack": 10 * 4, "actionable_honest": 15 * 4,
                        "nonaction_f2_honest_reported_not_scored": 5 * 4}
    assert rq2_denominators == {"separable_attack": 40, "actionable_honest": 60,
                                "nonaction_f2_honest_reported_not_scored": 20}

    dummy = [{"id": f"workspace:sec:user_task_1:injection_task_{i}"} for i in range(2)]
    jobs1, digest1 = episode_plan(dummy, ["no-defense", "dei"], 3, "workspace", "mock", 0.7, "important_instructions")
    jobs2, digest2 = episode_plan(dummy, ["no-defense", "dei"], 3, "workspace", "mock", 0.7, "important_instructions")
    assert digest1 == digest2 and [(c["id"], a, r) for c, a, r in jobs1] == [(c["id"], a, r) for c, a, r in jobs2]
    assert len(jobs1) == 12 and len({(c["id"], a, r) for c, a, r in jobs1}) == 12

    held_ids = {x for values in held.values() for x in values}
    development_ids = {x for values in development.values() for x in values}
    log_audits = []
    for name in args.log:
        rows = read_log(pathlib.Path(name))
        ids = {r.get("case_id") for r in rows if r.get("case_id")}
        leak = sorted(ids & held_ids)
        unregistered = sorted(ids - development_ids)
        log_audits.append({"path": name, "episodes": len(rows), "case_ids": len(ids),
                           "held_out_overlap": leak, "ids_not_in_development_set": unregistered})
        assert not leak, (name, leak[:5])
        assert not unregistered, (name, unregistered[:5])

    result = {
        "status": "PASS",
        "held_out_counts": counts,
        "held_out_total": {"security": 150, "benign": 56},
        "development_overlap": overlaps,
        "workspace_untouched_benign": workspace_benign,
        "tau_tuning_tasks": len(tau),
        "probe_cases": {"attack": 20, "honest": 20},
        "expected_episodes": EXPECTED_EPISODES,
        "rq2_primary_denominators": rq2_denominators,
        "arms": ARMS_ALL,
        "episode_order": {"algorithm": "episode-order-v1", "test_digest": digest1, "deterministic": True},
        "development_log_audits": log_audits,
        "agentdyn": "not run (pre-deposit decision, 2026-11-01)",
        "rq4a_model": "gpt-4.1-mini",
    }
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n")


if __name__ == "__main__":
    main()
