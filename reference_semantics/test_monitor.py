"""
test_monitor.py — property tests for the DEI reference monitor.
Run: python3 -m pytest test_monitor.py -q   (or: python3 test_monitor.py)
Stdlib-only fallback runner included so it works without pytest.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dei_monitor import (  # noqa: E402
    Belief, DEIMonitor, Label, Policy, Verdict, meet,
    make_attested, make_expired, make_unattested,
)

NOW = 1_700_000_000.0


def _policy():
    return Policy(
        ell_min=Label.MEDIUM,
        protected_classes={"act", "hibar"},
        ell_req={"act": Label.MEDIUM, "hibar": Label.HIGH},
        tau={"act": 0.3, "hibar": 0.5},
        authorized_endorsements={"k_corroboration"},
    )


def _m():
    return DEIMonitor(_policy(), now_fn=lambda: NOW)


# --- lattice -----------------------------------------------------------------
def test_meet_is_min():
    assert meet([Label.HIGH, Label.LOW, Label.MEDIUM]) == Label.LOW
    assert meet([]) == Label.TRUSTED  # empty meet = top


# --- I1: provenance-completeness --------------------------------------------
def test_i1_blocks_orphan():
    m = _m()
    m.update_belief(Belief("b", Label.HIGH, deps={"ghost"}))
    r = m.admit_action("act", ["b"])
    assert r.verdict == Verdict.BLOCK and r.invariant == "I1"


def test_i1_blocks_unattested_root():
    m = _m()
    m.ingest_evidence(make_unattested("e", "x", Label.HIGH, NOW))
    m.update_belief(Belief("b", Label.MEDIUM, deps={"e"}))
    r = m.admit_action("act", ["b"])
    assert r.verdict == Verdict.BLOCK and r.invariant == "I1"


def test_i1_blocks_expired_root():
    m = _m()
    m.ingest_evidence(make_expired("e", "x", Label.HIGH, NOW))
    m.update_belief(Belief("b", Label.MEDIUM, deps={"e"}))
    r = m.admit_action("act", ["b"])
    assert r.verdict == Verdict.BLOCK and r.invariant == "I1"


def test_i1_admits_attested_root():
    m = _m()
    m.ingest_evidence(make_attested("e", "x", Label.HIGH, now=NOW))
    m.update_belief(Belief("b", Label.MEDIUM, deps={"e"}))
    r = m.admit_action("act", ["b"], evidence_weights={"e": 1.0})
    assert r.verdict == Verdict.ADMIT


# --- I2: integrity non-degradation ------------------------------------------
def test_i2_blocks_unendorsed_upgrade():
    m = _m()
    m.ingest_evidence(make_unattested("e", "x", Label.UNTRUSTED, NOW))
    r = m.update_belief(Belief("b", Label.HIGH, deps={"e"}))
    assert r.verdict == Verdict.BLOCK and r.invariant == "I2"


def test_i2_allows_authorized_endorsement():
    m = _m()
    m.ingest_evidence(make_attested("c1", "s", Label.MEDIUM, now=NOW))
    m.ingest_evidence(make_attested("c2", "s", Label.MEDIUM, now=NOW))
    r = m.update_belief(Belief("b", Label.HIGH, deps={"c1", "c2"},
                               endorsed_by=["k_corroboration"]))
    assert r.verdict == Verdict.ADMIT


def test_i2_enforces_derivation_meet():
    # Strict I2: an unendorsed declaration above the meet is BLOCKED (not stored).
    m = _m()
    m.ingest_evidence(make_attested("hi", "s", Label.HIGH, now=NOW))
    m.ingest_evidence(make_attested("lo", "s", Label.MEDIUM, now=NOW))
    r = m.update_belief(Belief("b", Label.HIGH, deps={"hi", "lo"}))  # over-declared
    assert r.verdict == Verdict.BLOCK and r.invariant == "I2"
    assert "b" not in m.beliefs
    # Declared AT the meet: admitted and stored at the meet.
    m2 = _m()
    m2.ingest_evidence(make_attested("hi", "s", Label.HIGH, now=NOW))
    m2.ingest_evidence(make_attested("lo", "s", Label.MEDIUM, now=NOW))
    assert m2.update_belief(Belief("b2", Label.MEDIUM, deps={"hi", "lo"})).verdict == Verdict.ADMIT
    assert m2.beliefs["b2"].label == Label.MEDIUM
    # Endorsed upgrade: raised label stands.
    m3 = _m()
    m3.ingest_evidence(make_attested("c1", "s", Label.MEDIUM, now=NOW))
    m3.ingest_evidence(make_attested("c2", "s", Label.MEDIUM, now=NOW))
    m3.update_belief(Belief("b3", Label.HIGH, deps={"c1", "c2"},
                            endorsed_by=["k_corroboration"]))
    assert m3.beliefs["b3"].label == Label.HIGH


# --- I3: evidential-support sufficiency -------------------------------------
def test_i3_blocks_below_threshold():
    m = _m()
    m.ingest_evidence(make_attested("e", "x", Label.HIGH, now=NOW))
    m.update_belief(Belief("b", Label.HIGH, deps={"e"}))
    r = m.admit_action("hibar", ["b"], evidence_weights={"e": 0.2})  # weak
    assert r.verdict == Verdict.BLOCK and r.invariant == "I3"


def test_i3_admits_sufficient():
    m = _m()
    m.ingest_evidence(make_attested("e1", "x", Label.HIGH, now=NOW))
    m.ingest_evidence(make_attested("e2", "x", Label.HIGH, now=NOW))
    m.update_belief(Belief("b", Label.HIGH, deps={"e1", "e2"}))
    r = m.admit_action("hibar", ["b"], evidence_weights={"e1": 1.5, "e2": 1.5})
    assert r.verdict == Verdict.ADMIT


# --- Proposition 1: blocking preserves trace legality (truncation automaton) -
def test_blocking_yields_legal_continuation():
    """After a BLOCK, the same monitor still admits a subsequent legal action:
    truncation removes the bad event, it does not wedge the system."""
    m = _m()
    # bad update blocked
    m.ingest_evidence(make_unattested("bad", "x", Label.UNTRUSTED, NOW))
    assert m.update_belief(Belief("bb", Label.HIGH, deps={"bad"})).verdict == Verdict.BLOCK
    # a legal path still goes through
    m.ingest_evidence(make_attested("good", "x", Label.HIGH, now=NOW))
    m.update_belief(Belief("gb", Label.MEDIUM, deps={"good"}))
    assert m.admit_action("act", ["gb"], evidence_weights={"good": 1.0}).verdict == Verdict.ADMIT


# --- determinism -------------------------------------------------------------
def test_determinism():
    def scenario():
        m = _m()
        m.ingest_evidence(make_attested("e", "x", Label.HIGH, now=NOW))
        m.update_belief(Belief("b", Label.MEDIUM, deps={"e"}))
        return m.admit_action("act", ["b"], evidence_weights={"e": 1.0}).verdict
    assert scenario() == scenario() == Verdict.ADMIT


# --- anti-triviality: unprotected classes are not gated ----------------------
def test_unprotected_class_admitted():
    m = _m()
    r = m.admit_action("noop_unprotected", ["nonexistent"])
    assert r.verdict == Verdict.ADMIT


def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n  {passed}/{len(fns)} tests passed")
    return passed == len(fns)


if __name__ == "__main__":
    print("=== DEI monitor property tests ===")
    sys.exit(0 if _run_all() else 1)
