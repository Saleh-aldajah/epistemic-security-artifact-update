"""
dei_monitor.py — executable reference semantics for decision-level epistemic
integrity (Definitions 1-6, Section 4).

This is the artifact backing Proposition 1: I1-I3 are enforced ONLINE by a
reference monitor that truncates a trace at the first bad event (blocking the
offending action or update). The monitor is deliberately deterministic and
model-free: it inspects only the logged decision trace, never the model.

Scope: this is a *semantics check*, not the CZTA deployment. It validates that
the definitions decide the cases the crosswalk (Table: attack->invariant)
predicts. Live-deployment latency lives in Section 5 (CZTA testbed).

No third-party dependencies (stdlib only) so the artifact runs anywhere.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Definition 1: integrity lattice. A total order suffices for the evaluation
# (UNTRUSTED < LOW < MEDIUM < HIGH < TRUSTED); the monitor uses meet = min.
# ---------------------------------------------------------------------------
class Label(IntEnum):
    UNTRUSTED = 0   # bottom: model output, external/tool content by default
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    TRUSTED = 4     # top: attested first-party evidence


def meet(labels: List["Label"]) -> "Label":
    """Lattice meet (greatest lower bound) = min on a total order (Def. 3)."""
    return Label(min(labels)) if labels else Label.TRUSTED


# ---------------------------------------------------------------------------
# Definition 2: evidence atoms and attestation with validity windows.
# att(e) holds iff the signature verifies AND now in [not_before, not_after].
# The freshness clause makes long-horizon drift an I1 violation (Def. 2 note).
# ---------------------------------------------------------------------------
_TRUSTED_ROOT_KEY = b"trusted-root-key-DEMO-ONLY"  # stands in for a real PKI root


def sign(evidence_id: str, payload: str, not_before: float, not_after: float) -> str:
    msg = f"{evidence_id}|{payload}|{not_before}|{not_after}".encode()
    return hmac.new(_TRUSTED_ROOT_KEY, msg, hashlib.sha256).hexdigest()


@dataclass
class Evidence:
    eid: str
    payload: str
    label: Label
    not_before: float
    not_after: float
    signature: Optional[str] = None  # None => unattested

    def attested(self, now: float) -> bool:
        if self.signature is None:
            return False
        expected = sign(self.eid, self.payload, self.not_before, self.not_after)
        if not hmac.compare_digest(self.signature, expected):
            return False
        return self.not_before <= now <= self.not_after


# ---------------------------------------------------------------------------
# Definition 3: beliefs, provenance (dep sets), updates, endorsements.
# ---------------------------------------------------------------------------
@dataclass
class Belief:
    bid: str
    label: Label
    deps: Set[str]          # ids of Evidence or other Beliefs (provenance DAG)
    endorsed_by: List[str] = field(default_factory=list)  # policy-rule ids


# ---------------------------------------------------------------------------
# Aggregator S for I3 (Def. 5). Instantiated as a normalized sum of qualifying
# evidence weights (evidence at or above the required label). This stands in
# for a Dempster-Shafer Bel(.) or an argumentation acceptance criterion; the
# definition requires only that S be fixed, audited, and in the TCB.
# ---------------------------------------------------------------------------
def support_score(qualifying_weights: List[float]) -> float:
    # Bounded, monotone in evidence; simple and auditable.
    total = sum(qualifying_weights)
    return total / (1.0 + total)  # in [0,1), increasing


# ---------------------------------------------------------------------------
# Policy Pi (Def. 6): floor, per-class required label and threshold, authorized
# endorsement rules, protected classes.
# ---------------------------------------------------------------------------
@dataclass
class Policy:
    ell_min: Label
    protected_classes: Set[str]
    ell_req: Dict[str, Label]           # class -> required evidence label for I3
    tau: Dict[str, float]               # class -> support threshold for I3
    authorized_endorsements: Set[str]   # rule ids permitted to raise labels


class Verdict(IntEnum):
    ADMIT = 0
    BLOCK = 1


@dataclass
class MonitorResult:
    verdict: Verdict
    invariant: Optional[str]   # which invariant tripped, if BLOCK
    reason: str
    event_index: int


# ---------------------------------------------------------------------------
# The reference monitor. Parametric over runtime objects (Def./Prop. 1): the
# object universe at any prefix is the finite set observed so far, so each
# instantiated check is finite-state. Enforcement = truncation: on the first
# bad event we return BLOCK and the caller does not execute it.
# ---------------------------------------------------------------------------
class DEIMonitor:
    def __init__(self, policy: Policy, now_fn=time.time):
        self.pi = policy
        self.now_fn = now_fn
        self.evidence: Dict[str, Evidence] = {}
        self.beliefs: Dict[str, Belief] = {}
        self._root_cert: Dict[str, bool] = {}   # memoized I1 root certificates
        self.log: List[Tuple[str, MonitorResult]] = []

    # --- ingress -----------------------------------------------------------
    def ingest_evidence(self, e: Evidence) -> None:
        self.evidence[e.eid] = e

    # --- I2 enforcement point: updates and endorsements --------------------
    def update_belief(self, b: Belief) -> MonitorResult:
        """upd(b, deps): default label is the meet of input labels (Def. 3).
        I2 (Def. 4): reject any update whose declared label EXCEEDS the meet
        of its inputs unless justified by an authorized endorsement rule."""
        idx = len(self.log)
        input_labels: List[Label] = []
        for d in b.deps:
            if d in self.evidence:
                input_labels.append(self.evidence[d].label)
            elif d in self.beliefs:
                input_labels.append(self.beliefs[d].label)
            else:
                res = MonitorResult(Verdict.BLOCK, "I1",
                                    f"dangling dependency {d} (no evidential root)", idx)
                self.log.append((b.bid, res))
                return res
        derived = meet(input_labels)
        if b.label > derived:
            # Declared above the derivation meet == an attempted integrity
            # upgrade (Def. 4). Lawful iff justified by an authorized
            # endorsement rule; otherwise it is a silent, unjustified upgrade
            # and an I2 violation -- exactly the laundering move an injection
            # uses to turn untrusted content into trusted-enough belief.
            authorized = [r for r in b.endorsed_by
                          if r in self.pi.authorized_endorsements]
            if not authorized:
                res = MonitorResult(Verdict.BLOCK, "I2",
                                    f"unendorsed/ unauthorized upgrade "
                                    f"{derived.name}->{b.label.name}"
                                    + (f" (rules {b.endorsed_by})" if b.endorsed_by else ""),
                                    idx)
                self.log.append((b.bid, res))
                return res
            # authorized endorsement: the raised label stands
        else:
            b.label = derived  # enforce derivation rule (clamp to meet)
        self.beliefs[b.bid] = b
        self._root_cert.pop(b.bid, None)  # invalidate memo
        res = MonitorResult(Verdict.ADMIT, None, "update admitted", idx)
        self.log.append((b.bid, res))
        return res

    # --- I1 root certificate: memoized, O(1) at action time (Remark 1) -----
    def _has_attested_root(self, bid: str, now: float, seen: Optional[Set[str]] = None) -> bool:
        if bid in self._root_cert:
            return self._root_cert[bid]
        seen = seen or set()
        if bid in seen:
            return False  # cycle => not well-founded
        seen.add(bid)
        b = self.beliefs.get(bid)
        if b is None:
            return False
        ok = False
        # every maximal derivation path must terminate in attested, >=floor evidence
        all_paths_ok = True
        touched_evidence = False
        for d in b.deps:
            if d in self.evidence:
                touched_evidence = True
                e = self.evidence[d]
                if not (e.attested(now) and e.label >= self.pi.ell_min):
                    all_paths_ok = False
            elif d in self.beliefs:
                if not self._has_attested_root(d, now, seen):
                    all_paths_ok = False
            else:
                all_paths_ok = False
        ok = all_paths_ok and (touched_evidence or any(d in self.beliefs for d in b.deps))
        self._root_cert[bid] = ok
        return ok

    def _window_valid(self, bid: str, now: float, seen: Optional[Set[str]] = None) -> bool:
        """Action-time freshness re-check (Algorithm 1's WindowValid(b)):
        every terminal evidence root of b's closure is inside its
        attestation validity window at the action time. Complements the
        memoized creation-time certificate (_has_attested_root): a root
        can pass at creation and lapse before use (drift row, Def. 2)."""
        seen = seen or set()
        if bid in seen:
            return True  # cycles are the certificate's concern, not freshness
        seen.add(bid)
        b = self.beliefs.get(bid)
        if b is None:
            return True
        for d in b.deps:
            if d in self.evidence:
                if not self.evidence[d].attested(now):
                    return False
            elif d in self.beliefs:
                if not self._window_valid(d, now, seen):
                    return False
        return True

    # --- action admission: I1 & I3 enforcement point -----------------------
    def admit_action(self, action_class: str, support: List[str],
                     evidence_weights: Optional[Dict[str, float]] = None) -> MonitorResult:
        idx = len(self.log)
        now = self.now_fn()
        if action_class not in self.pi.protected_classes:
            res = MonitorResult(Verdict.ADMIT, None, "unprotected class", idx)
            self.log.append((action_class, res))
            return res

        # I1: provenance-completeness over the support set, in both disjuncts
        # of the paper's Algorithm 1: the memoized creation-time certificate
        # AND the action-time freshness re-check (WindowValid).
        for bid in support:
            if bid not in self.beliefs:
                res = MonitorResult(Verdict.BLOCK, "I1",
                                    f"support belief {bid} has no provenance record", idx)
                self.log.append((action_class, res))
                return res
            if not self._has_attested_root(bid, now):
                res = MonitorResult(Verdict.BLOCK, "I1",
                                    f"support belief {bid} lacks attested/in-window root >= floor", idx)
                self.log.append((action_class, res))
                return res
            if not self._window_valid(bid, now):
                res = MonitorResult(Verdict.BLOCK, "I1",
                                    f"support belief {bid} has a root whose validity window lapsed", idx)
                self.log.append((action_class, res))
                return res

        # I3: evidential-support sufficiency at required label
        req = self.pi.ell_req.get(action_class, Label.UNTRUSTED)
        weights = evidence_weights or {}
        qualifying = []
        for bid in support:
            for d in self.beliefs[bid].deps:
                e = self.evidence.get(d)
                if e is not None and e.label >= req and e.attested(now):
                    qualifying.append(weights.get(d, 1.0))
        score = support_score(qualifying)
        tau = self.pi.tau.get(action_class, 0.0)
        if score < tau:
            res = MonitorResult(Verdict.BLOCK, "I3",
                                f"support score {score:.3f} < tau {tau:.3f} at label {req.name}", idx)
            self.log.append((action_class, res))
            return res

        res = MonitorResult(Verdict.ADMIT, None, f"admitted (score {score:.3f} >= {tau:.3f})", idx)
        self.log.append((action_class, res))
        return res


# --- convenience: an attested evidence factory for tests --------------------
def make_attested(eid: str, payload: str, label: Label,
                  ttl: float = 3600.0, now: float = None) -> Evidence:
    now = now if now is not None else time.time()
    nb, na = now - 1.0, now + ttl
    return Evidence(eid, payload, label, nb, na, sign(eid, payload, nb, na))


def make_expired(eid: str, payload: str, label: Label, now: float = None) -> Evidence:
    now = now if now is not None else time.time()
    nb, na = now - 7200.0, now - 3600.0  # window already closed
    return Evidence(eid, payload, label, nb, na, sign(eid, payload, nb, na))


def make_forged(eid: str, payload: str, label: Label, now: float = None) -> Evidence:
    """Attestation PRESENT but INVALID: the signature does not verify against
    the trusted root (spoofed signer identity, or payload tampered after
    signing). att(e) is False, so this is an I1 root failure -- distinct from
    make_unattested (no signature at all) and make_expired (valid signature,
    lapsed window)."""
    now = now if now is not None else time.time()
    nb, na = now - 1.0, now + 3600.0
    return Evidence(eid, payload, label, nb, na, signature="00" * 32)


def make_unattested(eid: str, payload: str, label: Label, now: float = None) -> Evidence:
    now = now if now is not None else time.time()
    return Evidence(eid, payload, label, now - 1.0, now + 3600.0, signature=None)
