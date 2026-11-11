"""Offline tests for the registered analysis pipeline; all data are synthetic."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (cluster_bootstrap, failure_class, mcnemar_exact,  # noqa: E402
                     newcombe_paired)


def test_paired_score_interval_and_mcnemar():
    pairs = []
    for i in range(20):
        pairs.append(((f"t{i}", 1), True, True, {}))
    for i in range(20, 25):
        pairs.append(((f"t{i}", 1), True, False, {}))
    for i in range(25, 40):
        pairs.append(((f"t{i}", 1), False, True, {}))
    for i in range(40, 100):
        pairs.append(((f"t{i}", 1), False, False, {}))
    rd, lo, hi, counts, n = newcombe_paired(pairs)
    assert n == 100 and counts == (20, 5, 15, 60)
    assert abs(rd + 0.1) < 1e-12 and lo < rd < hi
    assert abs(mcnemar_exact(15, 5) - 0.04138946533203125) < 1e-12


def test_cluster_bootstrap_is_seeded():
    pairs = [((f"t{i}", rep), i % 3 != 0, i % 2 == 0, {}) for i in range(12) for rep in (1, 2, 3)]
    one = cluster_bootstrap(pairs, reps=200, seed=17)
    two = cluster_bootstrap(pairs, reps=200, seed=17)
    assert one == two and one[2] == 12


def test_failure_taxonomy_priority():
    assert failure_class({"utility": False, "n_blocked": 1, "degenerate": True}) == "defense"
    assert failure_class({"utility": False, "n_blocked": 0, "null_output": True}) == "degenerate"
    assert failure_class({"utility": False, "n_blocked": 0, "n_model_calls": 2}) == "model"
    assert failure_class({"utility": True}) is None


def _run(rows, extra=(), oracle_rows=None):
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "log.jsonl")
        macros = os.path.join(d, "macros.tex")
        with open(log, "w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "analyze.py"), log,
               "--macros", macros, "--bootstrap", "100", *extra]
        if oracle_rows is not None:
            oracle = os.path.join(d, "oracle.jsonl")
            with open(oracle, "w") as f:
                for row in oracle_rows:
                    f.write(json.dumps(row) + "\n")
            cmd.extend(["--oracle-log", oracle])
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
        return out, open(macros).read()


def test_rq3_macros_are_emitted():
    rows = []
    for task in range(4):
        for rep in (1, 2):
            base = {"case_id": f"workspace:util:user_task_{task}", "kind": "utility", "rep": rep,
                    "decisions": [], "n_protected": 0}
            rows.append({**base, "arm": "no-defense", "utility": True, "benign_blocked": False,
                         "n_blocked": 0, "n_quarantined": 0, "n_model_calls": 1})
            failed = task == 0 and rep == 1
            rows.append({**base, "arm": "dei+gate", "utility": not failed, "benign_blocked": failed,
                         "n_blocked": 1 if failed else 0, "n_quarantined": 0, "n_model_calls": 1})
            for arm in ("b1", "b2strict"):
                rows.append({**base, "arm": arm, "utility": True, "benign_blocked": False,
                             "n_blocked": 0, "n_quarantined": 0, "n_model_calls": 1})
    _, macros = _run(rows)
    for name in ("UtilDeiGatePairedN", "UtilDeiGatePairedRD", "UtilDeiGatePairedRDlo",
                 "UtilDeiGateClusterRDlo", "UtilDeiGateMcNemarP", "UtilDeiGateFailDefense",
                 "UtilDeiGateVsB2strictHolmP", "UtilDeiGateVsB1PairedRD", "UtilDeiGateNoProtectedUseN"):
        assert f"\\newcommand{{\\Sp{name}}}" in macros, name
    assert "\\newcommand{\\SpUtilDeiGatePairedN}{8}" in macros


def test_unevaluated_delta_is_not_a_zero_result():
    rows = [{"case_id": "workspace:probe:1", "kind": "security", "arm": "dei+gate", "rep": 1,
             "family": "F1_test", "placement": "separate", "target_hit": True, "utility": False,
             "n_blocked": 0, "n_quarantined": 0, "n_recommits": 1,
             "decisions": [{"protected": True, "gate": {"quarantine": False,
                            "flips": {"delta3": {"flip": False}}}}]}]
    out, macros = _run(rows)
    assert "delta1: not run" in out and "any: quar 0/1" in out
    assert "\\newcommand{\\SpProbeF1TestSeparateDelta1QuarN}{0}" in macros
    assert "\\newcommand{\\SpProbeF1TestSeparateDelta3QuarN}{1}" in macros


def test_pooled_rq2_macros_and_oracle_confusion():
    rows, oracle = [], []
    design = [(True, False, True), (False, True, True), (True, True, False), (False, False, False)]
    for rep, (d3, d2, d1) in enumerate(design, 1):
        base = {"case_id": "workspace:probe:1", "kind": "security", "arm": "dei+gate", "rep": rep,
                "family": "F1_wrong_file", "placement": "separate", "target_hit": True, "utility": False,
                "n_blocked": 0, "n_quarantined": 0, "n_recommits": 1}
        rows.append({**base, "decisions": [{"protected": True, "gate": {"quarantine": d3,
                     "flips": {"delta3": {"flip": d3}, "delta2": {"flip": d2}}}}]})
        oracle.append({**base, "decisions": [{"protected": True, "gate": {"quarantine": d1,
                       "flips": {"delta1": {"flip": d1}}}}]})
    out, macros = _run(rows, oracle_rows=oracle)
    assert "\\newcommand{\\SpRq2SeparableDelta3K}{2}" in macros
    assert "\\newcommand{\\SpRq2SeparableDelta3N}{4}" in macros
    assert "\\newcommand{\\SpRq2SeparableDelta3Probes}{1}" in macros
    for rule in ("Delta2", "Delta3"):
        for suffix, value in (("Tp", 1), ("Fn", 1), ("Fp", 1), ("Tn", 1)):
            assert f"\\newcommand{{\\SpRq2{rule}{suffix}}}{{{value}}}" in macros
    assert "4 matched episodes" in out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)}/{len(tests)} analysis tests passed")
