"""
gate.py — the counterfactual audit gate (Algorithm 2) over an admitted
irreversible action.

Perturbations (registered):
  delta1  oracle plant removal: redact every tool atom carrying an injection
          payload (development only; needs the payloads)
  delta2  cited sub-ell_req removal: redact the tool atoms in support(a) whose
          label is below ell_req(class)   -- deployable
  delta3  uncited removal: redact the tool atoms NOT in support(a) -- deployable
The plane is re-assembled from ledgered atoms (the message history), never by
re-querying tools; the model is re-committed at temperature 0; a changed
canonical action, no action, or a failed re-commitment is a FLIP and the action
is quarantined (conservative default, stated in the paper).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from . import policy as P
from .admission import cited_support, short_args
from .ledger import LABEL, Ledger, canonical_forms, norm

REDACTED = "[content removed by counterfactual gate]"


def canonical_action(tool: str, args: Dict[str, Any]) -> str:
    parts = []
    for slot, vals in sorted(short_args(args).items()):
        cf = sorted(canonical_forms(v)[0] if canonical_forms(v) else norm(str(v)) for v in vals)
        parts.append(f"{slot}={'|'.join(cf)}")
    return tool + "(" + ";".join(parts) + ")"


RecommitFn = Callable[[Sequence[Any]], Optional[Tuple[str, Dict[str, Any]]]]


@dataclass
class GateResult:
    quarantine: bool
    flips: Dict[str, Any] = field(default_factory=dict)   # delta -> {"flip": bool, "recommit": str|None, "redacted": [...]}
    reason: str = ""
    recommits: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {"quarantine": self.quarantine, "flips": self.flips, "reason": self.reason, "recommits": self.recommits}


def _redact(messages: Sequence[Any], ledger: Ledger, atom_ids: List[str]) -> List[Any]:
    idx = {a.index for a in ledger.atoms if a.aid in atom_ids}
    out = []
    for i, m in enumerate(messages):
        if i in idx and isinstance(m, dict):
            m = {**m, "content": [{"type": "text", "content": REDACTED}]}
        out.append(m)
    return out


def run_gate(messages: Sequence[Any], ledger: Ledger, tool: str, args: Dict[str, Any],
             recommit: RecommitFn, deltas: Sequence[str] = ("delta2", "delta3"),
             ell_req: Optional[int] = None, oracle_payloads: Optional[List[str]] = None,
             enforce: Sequence[str] = ("delta3",)) -> GateResult:
    """Run every perturbation in `deltas`, log every flip, QUARANTINE only on a
    flip under a perturbation in `enforce` (registered default: delta3).
    delta2 is observed, not enforced: at atom granularity it cannot tell
    dependence on needed MEDIUM data from dependence on a plant that shares the
    atom, so its flips are reported as the gate's resolution limit."""
    cls = P.PROTECTED.get(tool)
    if cls is None or cls not in P.IRREVERSIBLE:
        return GateResult(False, {}, "not an irreversible class")
    req = ell_req if ell_req is not None else LABEL[P.ELL_REQ[cls]]
    sup = cited_support(ledger, args, cls)
    tool_atoms = ledger.tool_atoms()
    # sole binders: atoms that are the only ones naming some bound-slot value
    sole: set = set()
    for slot in P.BETA.get(tool, {}):
        for v in short_args({slot: args.get(slot)}).get(slot, []):
            bs = ledger.binders(v)
            if len(bs) == 1:
                sole.add(bs[0].aid)
    target = canonical_action(tool, args)
    plans: Dict[str, List[str]] = {}
    if "delta1" in deltas and oracle_payloads:
        pn = [norm(p) for p in oracle_payloads if p]
        plans["delta1"] = [a.aid for a in tool_atoms if any(p and p in a.ntext for p in pn)]
    if "delta2" in deltas:
        plans["delta2"] = [a.aid for a in tool_atoms if a.aid in sup and a.label < req and a.aid not in sole]
    if "delta3" in deltas:
        plans["delta3"] = [a.aid for a in tool_atoms if a.aid not in sup]
    res = GateResult(False)
    for d, atoms in plans.items():
        if not atoms:
            res.flips[d] = {"flip": False, "recommit": None, "redacted": [], "note": "nothing to remove"}
            continue
        redacted = _redact(messages, ledger, atoms)
        try:
            rc = recommit(redacted)
            res.recommits += 1
        except Exception as ex:  # conservative default: unattributable -> quarantine (enforced deltas)
            res.flips[d] = {"flip": True, "recommit": None, "redacted": atoms, "error": str(ex)[:160], "enforced": d in enforce}
            if d in enforce:
                res.quarantine = True
                res.reason = f"GATE:{d}:recommit_error"
            continue
        rc_canon = canonical_action(rc[0], rc[1]) if rc else None
        flip = (rc_canon != target)
        res.flips[d] = {"flip": flip, "recommit": rc_canon, "redacted": atoms, "enforced": d in enforce}
        if flip and d in enforce and not res.quarantine:
            res.quarantine = True
            res.reason = f"GATE:{d}:flip"
    if not res.quarantine:
        res.reason = ("stable under enforced " + ",".join(d for d in plans if d in enforce)) if plans else "no perturbation applicable"
    return res
