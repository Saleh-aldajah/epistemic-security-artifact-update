#!/usr/bin/env python3
"""
run_campaign.py — registered live-model campaign runner (S&P version).

Arms:  no-defense | dei | dei+gate | b1 | b2 | b2strict | b3
Cases: per suite, security = user_task x injection_task; utility = user_task alone.
Every episode is written as one JSON line with AgentDojo's own verdicts and the
full decision ledger (every protected call: enforced verdict + shadow verdicts
of every other arm + support / score / binding labels, so tau and ell_beta
sweeps can be recomputed offline from the first decision).

Keys come from the environment, never from a file:
  FRONTIER_API_KEY, FRONTIER_BASE_URL, FRONTIER_MODEL      (hosted endpoint)
  OW_BASE_URL, OW_MODEL, OW_API_KEY                         (Ollama / vLLM)
Usage:
  python3 run_campaign.py --suite workspace --arms no-defense,dei,dei+gate,b1,b2,b3 \
      --sec 40 --util 24 --reps 1 --temperature 0.7 --model-kind frontier --out out/campaign.jsonl
  python3 run_campaign.py --mock --suite workspace --sec 3 --util 2     # offline dry run
  python3 run_campaign.py --cases held_out_cases.json ...               # the deposited case list
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import random
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MASTER_SEED = 20260814
ARMS_ALL = ("no-defense", "dei", "dei+gate", "b1", "b2", "b2strict", "b3")


def derive_seed(master_seed, suite, model, temp, arm, rep):
    """Exactly the sealed PROTOCOL_EVAL_V2 derivation: first 8 hex chars of
    SHA-256(f"{master}|{suite}|{model}|{temp}|{arm}|{rep}")."""
    msg = f"{master_seed}|{suite}|{model}|{temp}|{arm}|{rep}".encode("utf-8")
    d = hashlib.sha256(msg).hexdigest()
    return int(d[:8], 16), d


def episode_plan(cases, arms, reps, suite, model, temperature, attack):
    """Deterministically shuffled jobs, bound to the complete registered design.

    The order digest covers case ids, arms, replicates, model, temperature, and
    attack. Resume therefore reproduces exactly the same order without relying
    on wall-clock randomness or on which episodes already completed.
    """
    if not arms or any(arm not in ARMS_ALL for arm in arms):
        raise ValueError(f"unknown or empty arm set: {arms}")
    case_ids = [case["id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("duplicate case id in episode plan")
    material = json.dumps({"version": "episode-order-v1", "master": MASTER_SEED,
                           "suite": suite, "model": model, "temperature": str(temperature),
                           "attack": attack, "cases": sorted(case_ids), "arms": arms, "reps": reps},
                          sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    jobs = [(case, arm, rep) for case in cases for arm in arms for rep in range(1, reps + 1)]
    random.Random(digest).shuffle(jobs)
    return jobs, digest


def make_client(kind: str):
    import openai
    if kind == "mock":
        from dei_live.mock_model import MockClient
        from test_dei_live import compliant_model
        return MockClient(compliant_model), "mock"
    if kind == "frontier":
        key = os.environ.get("FRONTIER_API_KEY")
        if not key:
            raise SystemExit("FRONTIER_API_KEY is unset (export it; never paste it in chat or files)")
        base = os.environ.get("FRONTIER_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        model = os.environ.get("FRONTIER_MODEL", "gemini-2.5-flash")
        return openai.OpenAI(api_key=key, base_url=base), model
    base = os.environ.get("OW_BASE_URL", "http://localhost:11434/v1")
    model = os.environ.get("OW_MODEL", "qwen3-coder:30b")
    return openai.OpenAI(api_key=os.environ.get("OW_API_KEY", "ollama"), base_url=base), model


def load_cases(suite_name: str, sec: int, util: int, case_file: str | None):
    from agentdojo.task_suite.load_suites import get_suites
    S = get_suites(os.environ.get("AD_BENCHMARK_VERSION", "v1.2"))
    suite = S[suite_name]
    cases = []
    for ut in suite.user_tasks.values():
        cases.append({"id": f"{suite_name}:util:{ut.ID}", "suite": suite_name, "kind": "utility",
                      "user_task": ut, "injection_task": None})
    for ut in suite.user_tasks.values():
        for it in suite.injection_tasks.values():
            cases.append({"id": f"{suite_name}:sec:{ut.ID}:{it.ID}", "suite": suite_name, "kind": "security",
                          "user_task": ut, "injection_task": it})
    if case_file:
        wanted = json.load(open(case_file))
        ids = set(wanted.get(suite_name, wanted) if isinstance(wanted, dict) else wanted)
        cases = [c for c in cases if c["id"] in ids]
        missing = ids - {c["id"] for c in cases}
        assert not missing, f"deposited case ids not found in the suite: {sorted(missing)[:5]}"
        return suite, cases
    secs = [c for c in cases if c["kind"] == "security"][:sec]
    utils = [c for c in cases if c["kind"] == "utility"][:util]
    return suite, secs + utils


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", default="workspace")
    ap.add_argument("--arms", default=",".join(ARMS_ALL))
    ap.add_argument("--sec", type=int, default=40)
    ap.add_argument("--util", type=int, default=24)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--model-kind", choices=["frontier", "ow", "mock"], default="frontier")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cases", default=None, help="JSON list/dict of deposited case ids")
    ap.add_argument("--out", default="out/campaign.jsonl")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--max-consecutive-voids", type=int, default=5)
    ap.add_argument("--attack", default=os.environ.get("AD_ATTACK", "important_instructions"))
    ap.add_argument("--oracle-delta1", action="store_true", help="development only: supply payloads for delta1")
    ap.add_argument("--probes", action="store_true", help="run the registered choice-laundering probe families (+ honest controls)")
    ap.add_argument("--kind", choices=["security", "utility", "all"], default="all",
                    help="restrict the case set (also when --cases is given); RQ4(b) uses --kind security")
    ap.add_argument("--tau", type=float, default=None)
    ap.add_argument("--ell-req", default=None)
    args = ap.parse_args()
    if args.mock:
        args.model_kind = "mock"

    from dei_live import policy as P
    from dei_live.admission import PolicyConfig
    from dei_live.pipeline import run_one_case

    out = pathlib.Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            try:
                e = json.loads(line)
                if not e.get("voided"):
                    done.add((e["case_id"], e["arm"], e["rep"]))
            except Exception:
                pass
    client, model = make_client(args.model_kind)
    if args.probes:
        from probes import choice_laundering as cl
        suite, cases = cl.WS, cl.probe_cases()
        args.attack = "choice_laundering"; args.suite = "workspace"
    else:
        suite, cases = load_cases(args.suite, args.sec, args.util, args.cases)
    if args.kind != "all":
        cases = [c for c in cases if c["kind"] == args.kind]
    arms = args.arms.split(",")
    cfg = PolicyConfig(tau=args.tau, ell_req=args.ell_req)

    def _timeout(signum, frame):
        raise TimeoutError(f"episode exceeded {args.timeout}s")
    signal.signal(signal.SIGALRM, _timeout)

    jobs, order_digest = episode_plan(cases, arms, args.reps, args.suite, model, args.temperature, args.attack)
    header = {"campaign": "sp2028", "suite": args.suite, "model": model, "temperature": args.temperature,
              "attack": args.attack, "policy_hash": P.policy_hash(), "arms": arms, "n_cases": len(cases),
              "episode_order": "sha256-seeded shuffle (episode-order-v1)", "episode_order_sha256": order_digest,
              "agentdojo": __import__("agentdojo").__version__ if hasattr(__import__("agentdojo"), "__version__") else "0.1.35",
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(json.dumps(header), flush=True)
    total = len(jobs)
    consec_void = 0
    for n, (case, arm, rep) in enumerate(jobs, 1):
                if (case["id"], arm, rep) in done:
                    continue
                seed, digest = derive_seed(MASTER_SEED, args.suite, model, f"{args.temperature}", arm, rep)
                signal.alarm(args.timeout)
                try:
                    rec = run_one_case(suite, case, client, model, arm, args.temperature, seed, cfg=cfg,
                                       attack=args.attack, oracle=args.oracle_delta1)
                    consec_void = 0
                except Exception as ex:
                    rec = {"case_id": case["id"], "arm": arm, "rep": rep, "suite": args.suite, "model": model,
                           "voided": True, "fault": f"{type(ex).__name__}: {str(ex)[:200]}"}
                    consec_void += 1
                finally:
                    signal.alarm(0)
                rec.update(rep=rep, seed_digest=digest, suite=args.suite, attack=args.attack,
                           family=case.get("family"), placement=case.get("placement"),
                           order_index=n, episode_order_sha256=order_digest)
                with open(out, "a") as f:
                    f.write(json.dumps(rec, default=str) + "\n")
                print(f"[{n}/{total}] {arm:10s} {case['id']:48s} r{rep} hit={rec.get('target_hit')} "
                      f"util={rec.get('utility')} blocked={rec.get('n_blocked')} q={rec.get('n_quarantined')} "
                      f"{'VOID ' + rec['fault'] if rec.get('voided') else ''}", flush=True)
                if consec_void >= args.max_consecutive_voids:
                    sys.exit(f"ABORT: {consec_void} consecutive voided episodes; last fault: {rec.get('fault')}")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
