"""
admission.py — the admission decision for one proposed tool call, under the
DEI monitor (I1–I4) and under each registered baseline. Pure functions of
(ledger, tool, args): deterministic, model-free, loggable.

Arms
----
  no-defense  admit everything
  dei         I1 provenance-completeness, I2 (no label raise exists), I3
              evidential-support sufficiency, I4 argument binding
  b1          argument–instruction matching: every short argument value of a
              protected call must appear in the user's instruction
  b2          tool filter (CaMeL lineage): a protected call may not carry a
              value that is tool-sourced (named by a tool result and not by
              the user turn)
  b2strict    block every protected tool regardless of arguments (the
              NDSS-pilot arm, kept for replication)
  b3          I4 alone (ablation)
The gate (Alg. 2) is applied on top of `dei` by the pipeline, not here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import policy as P
from .ledger import LABEL, LNAME, Atom, Ledger, canonical_forms


@dataclass
class Decision:
    admit: bool
    arm: str
    invariant: Optional[str] = None
    reason: str = ""
    detail: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"admit": self.admit, "arm": self.arm, "invariant": self.invariant,
                "reason": self.reason, "detail": self.detail}


@dataclass
class PolicyConfig:
    tau: Optional[float] = None                       # override TAU for all classes
    lbeta: Dict[str, str] = field(default_factory=dict)  # slot -> label override
    ell_req: Optional[str] = None                     # override ELL_REQ for all classes

    def tau_for(self, cls: str) -> float:
        return self.tau if self.tau is not None else P.TAU[cls]

    def ell_req_for(self, cls: str) -> int:
        return LABEL[self.ell_req] if self.ell_req else LABEL[P.ELL_REQ[cls]]

    def beta_for(self, tool: str) -> Dict[str, int]:
        out = {}
        for slot, lab in P.BETA.get(tool, {}).items():
            out[slot] = LABEL[self.lbeta.get(slot, lab)]
        return out


def short_args(args: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Slots whose values can be targets: not free text, not over-long.
    List values are flattened; returns slot -> list of atomic values."""
    out: Dict[str, List[Any]] = {}
    for k, v in (args or {}).items():
        if k in P.FREE_TEXT_SLOTS or v is None:
            continue
        vals = list(v) if isinstance(v, (list, tuple, set)) else [v]
        keep = []
        for x in vals:
            if x is None:
                continue
            if isinstance(x, str) and (len(x.strip()) == 0 or len(x) > P.SUPPORT_MAX_LEN):
                continue
            keep.append(x)
        if keep:
            out[k] = keep
    return out


import re as _re


def directive_supports(atom: Atom, cls: Optional[str]) -> bool:
    """Does this (user) atom express the action class? (directive-root clause)"""
    if cls is None or atom.channel != "user":
        return False
    text = atom.ntext
    return any(_re.search(r"\b" + pat + r"\b", text) for pat in P.DIRECTIVE_LEXICON.get(cls, ()))


def cited_support(ledger: Ledger, args: Dict[str, Any], cls: Optional[str] = None) -> Dict[str, List[str]]:
    """support(a): atom id -> the slots whose values that atom names; user
    atoms that express the action class enter with the pseudo-slot '<directive>'."""
    sup: Dict[str, List[str]] = {}
    for slot, vals in short_args(args).items():
        for v in vals:
            for a in ledger.binders(v):
                sup.setdefault(a.aid, [])
                if slot not in sup[a.aid]:
                    sup[a.aid].append(slot)
    for a in ledger.atoms:
        if directive_supports(a, cls):
            sup.setdefault(a.aid, [])
            if "<directive>" not in sup[a.aid]:
                sup[a.aid].append("<directive>")
    return sup


def _atom(ledger: Ledger, aid: str) -> Atom:
    return next(a for a in ledger.atoms if a.aid == aid)


# ----------------------------------------------------------------------- DEI
def decide_dei(ledger: Ledger, tool: str, args: Dict[str, Any], cfg: PolicyConfig,
               arm: str = "dei") -> Decision:
    cls = P.PROTECTED.get(tool)
    if cls is None:
        return Decision(True, arm, None, "unprotected tool")
    sup = cited_support(ledger, args, cls)
    sup_atoms = [_atom(ledger, aid) for aid in sup]
    detail: Dict[str, Any] = {"class": cls, "support": {aid: {"label": LNAME[_atom(ledger, aid).label],
                                                               "slots": slots, "channel": _atom(ledger, aid).channel}
                                                         for aid, slots in sup.items()}}
    # I1: every cited atom has an attested root at or above the floor
    for a in sup_atoms:
        if not a.attested or a.label < LABEL[P.ELL_MIN]:
            return Decision(False, arm, "I1", f"cited atom {a.aid} unattested or below floor", detail)
    # I2: no endorsement authority exists in this domain; labels are channel-fixed (nothing to check)
    # I3: evidential-support sufficiency at ell_req
    req = cfg.ell_req_for(cls)
    qualifying = [a.aid for a in sup_atoms if a.attested and a.label >= req]
    w = float(len(qualifying))
    S = w / (1.0 + w)
    tau = cfg.tau_for(cls)
    detail.update({"S": S, "tau": tau, "ell_req": LNAME[req], "qualifying": qualifying})
    if S < tau:
        return Decision(False, arm, "I3", f"support {S:.3f} < tau {tau:.2f} at {LNAME[req]}", detail)
    # I4: argument binding over the bound slots
    beta = cfg.beta_for(tool)
    binding: Dict[str, Any] = {}
    for slot, lbeta in beta.items():
        vals = short_args({slot: args.get(slot)}).get(slot, [])
        for v in vals:
            best = ledger.best_label(v)
            binding[f"{slot}={v}"] = {"best_label": LNAME.get(best, "NONE"), "ell_beta": LNAME[lbeta]}
            if best < lbeta:
                detail["binding"] = binding
                return Decision(False, arm, "I4",
                                f"{slot}={v!r} is named by no atom at label >= {LNAME[lbeta]} "
                                f"(best: {LNAME.get(best, 'none')})", detail)
    detail["binding"] = binding
    return Decision(True, arm, None, f"admitted (S={S:.3f} >= {tau:.2f}; {len(beta)} bound slots)", detail)


# ------------------------------------------------------------------ baselines
def decide_b1(ledger: Ledger, tool: str, args: Dict[str, Any]) -> Decision:
    """Argument–instruction matching: every short argument value must appear
    in the user's instruction. No labels, no slot policy, no provenance."""
    if tool not in P.PROTECTED:
        return Decision(True, "b1", None, "unprotected tool")
    user_atoms = [a for a in ledger.atoms if a.channel == "user"]
    for slot, vals in short_args(args).items():
        for v in vals:
            if not any(a.names(v) for a in user_atoms):
                return Decision(False, "b1", "B1", f"{slot}={v!r} not in the user instruction")
    return Decision(True, "b1", None, "all argument values appear in the user instruction")


def decide_b2(ledger: Ledger, tool: str, args: Dict[str, Any]) -> Decision:
    """Tool filter (CaMeL lineage, operational approximation): a protected
    sink may not receive a value whose provenance is a tool result unless the
    user turn also names it."""
    if tool not in P.PROTECTED:
        return Decision(True, "b2", None, "unprotected tool")
    user_atoms = [a for a in ledger.atoms if a.channel == "user"]
    tool_atoms = ledger.tool_atoms()
    for slot, vals in short_args(args).items():
        for v in vals:
            tool_sourced = any(a.names(v) for a in tool_atoms)
            user_named = any(a.names(v) for a in user_atoms)
            if tool_sourced and not user_named:
                return Decision(False, "b2", "B2", f"{slot}={v!r} is tool-sourced and not user-named")
    return Decision(True, "b2", None, "no tool-sourced value reaches the sink")


def decide_b2strict(ledger: Ledger, tool: str, args: Dict[str, Any]) -> Decision:
    if tool not in P.PROTECTED:
        return Decision(True, "b2strict", None, "unprotected tool")
    return Decision(False, "b2strict", "B2s", "protected tool blocked unconditionally")


def decide_b3(ledger: Ledger, tool: str, args: Dict[str, Any], cfg: PolicyConfig) -> Decision:
    """I4 alone."""
    if tool not in P.PROTECTED:
        return Decision(True, "b3", None, "unprotected tool")
    for slot, lbeta in cfg.beta_for(tool).items():
        for v in short_args({slot: args.get(slot)}).get(slot, []):
            best = ledger.best_label(v)
            if best < lbeta:
                return Decision(False, "b3", "I4", f"{slot}={v!r} unbound (best {LNAME.get(best, 'none')} < {LNAME[lbeta]})")
    return Decision(True, "b3", None, "all bound slots named")


def decide(arm: str, ledger: Ledger, tool: str, args: Dict[str, Any], cfg: PolicyConfig) -> Decision:
    if arm in ("no-defense",):
        return Decision(True, arm, None, "no defense")
    if arm in ("dei", "dei+gate"):
        return decide_dei(ledger, tool, args, cfg, arm=arm)
    if arm == "b1":
        return decide_b1(ledger, tool, args)
    if arm == "b2":
        return decide_b2(ledger, tool, args)
    if arm == "b2strict":
        return decide_b2strict(ledger, tool, args)
    if arm == "b3":
        return decide_b3(ledger, tool, args, cfg)
    raise ValueError(f"unknown arm {arm}")


def shadow_all(ledger: Ledger, tool: str, args: Dict[str, Any], cfg: PolicyConfig) -> Dict[str, Dict[str, Any]]:
    """Every arm's verdict on the same proposed call (diagnostic; the enforced
    arm is the one that shapes the trajectory)."""
    return {arm: decide(arm, ledger, tool, args, cfg).as_dict()
            for arm in ("dei", "b1", "b2", "b2strict", "b3")}
