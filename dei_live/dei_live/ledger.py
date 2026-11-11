"""
ledger.py — the epistemic ledger of one AgentDojo episode, built from the
conversation the model saw. This is the TCB's view: channel labels are
assigned by WHERE content came from, never by what it says (no oracle).

Atoms
-----
  user:k    the user's turn(s)                  channel "user",   TRUSTED, attested (session)
  system:0  the system prompt                   channel "system", TRUSTED, attested (operator)
  tool:k    the k-th tool-result message        channel "tool",   MEDIUM,  attested (environment)
Model assertions (assistant text) are not atoms: they are UNTRUSTED and carry no
evidential standing. A value that appears only in model text is "model-originated".

Value recorder
--------------
vals(atom) is realised lazily: `names(atom, value)` decides whether the atom names
`value`, using canonical forms (lower-cased, punctuation-normalised, e-mail,
ISO-date, numeric) and token-boundary matching so that "0" does not match "10".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

LABEL = {"UNTRUSTED": 0, "MEDIUM": 1, "TRUSTED": 2}
LNAME = {v: k for k, v in LABEL.items()}

CHANNEL_LABEL = {"user": "TRUSTED", "system": "TRUSTED", "tool": "MEDIUM", "model": "UNTRUSTED"}


# --------------------------------------------------------------------------- text
def _text_of(message: Any) -> str:
    """Flatten an AgentDojo message's content blocks to one string."""
    c = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
    if c is None:
        return ""
    if isinstance(c, str):
        return c
    parts = []
    for b in c:
        if isinstance(b, dict):
            if b.get("type") in (None, "text"):
                parts.append(str(b.get("content", b.get("text", ""))))
        else:
            parts.append(str(getattr(b, "content", b)))
    return "\n".join(parts)


_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w@.\-+:/]+", re.UNICODE)


def norm(s: str) -> str:
    """Canonical text form: lower-case, collapse punctuation to spaces, single spaces."""
    s = str(s).lower().replace("_", " ")
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


_MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"])}
_MONTHS.update({m[:3]: i for m, i in list(_MONTHS.items())})
_DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_DATE_TXT = re.compile(r"\b(" + "|".join(sorted(_MONTHS, key=len, reverse=True)) + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?\b")
_DATE_NUM = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_NUM = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)(?![\w.])")


def canonical_forms(value: Any) -> List[str]:
    """All canonical forms under which a value may be named by an atom."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        out: List[str] = []
        for v in value:
            out.extend(canonical_forms(v))
        return out
    if isinstance(value, bool):
        return [str(value).lower()]
    if isinstance(value, (int, float)):
        s = ("%f" % value).rstrip("0").rstrip(".") if isinstance(value, float) else str(value)
        return [s]
    s = str(value).strip()
    forms = []
    n = norm(s)
    if n:
        forms.append(n)
    low = s.lower()
    # e-mail: also the local part is NOT a form (too weak); keep the full address only
    m = _DATE_ISO.search(low)
    if m:
        forms.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
        forms.append(f"{int(m.group(2)):02d}-{int(m.group(3)):02d}")  # month-day (year-less user phrasing)
    m = _DATE_TXT.search(low)
    if m:
        mo = _MONTHS[m.group(1)]
        d = int(m.group(2))
        forms.append(f"{mo:02d}-{d:02d}")
        if m.group(3):
            forms.append(f"{m.group(3)}-{mo:02d}-{d:02d}")
    m = _DATE_NUM.search(low)
    if m:
        forms.append(f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}")
    return [f for f in dict.fromkeys(forms) if f]


def _date_forms_in_text(text: str) -> List[str]:
    low = text.lower()
    out = []
    for m in _DATE_ISO.finditer(low):
        out.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
        out.append(f"{int(m.group(2)):02d}-{int(m.group(3)):02d}")
    for m in _DATE_TXT.finditer(low):
        mo = _MONTHS[m.group(1)]
        d = int(m.group(2))
        out.append(f"{mo:02d}-{d:02d}")
        if m.group(3):
            out.append(f"{m.group(3)}-{mo:02d}-{d:02d}")
    for m in _DATE_NUM.finditer(low):
        out.append(f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}")
    return out


@dataclass
class Atom:
    aid: str
    channel: str
    label: int
    attested: bool
    content: str
    index: int                      # position in the message list
    tool_name: Optional[str] = None # for tool atoms: which tool produced it
    _norm: Optional[str] = None
    _dates: Optional[List[str]] = None

    @property
    def ntext(self) -> str:
        if self._norm is None:
            self._norm = norm(self.content)
        return self._norm

    @property
    def dates(self) -> List[str]:
        if self._dates is None:
            self._dates = _date_forms_in_text(self.content)
        return self._dates

    def names(self, value: Any) -> bool:
        """vals(atom) ∋ value — the value recorder's membership test."""
        forms = canonical_forms(value)
        if not forms:
            return False
        nt = self.ntext
        for f in forms:
            if re.fullmatch(r"\d{2}-\d{2}|\d{4}-\d{2}-\d{2}", f):
                if f in self.dates:
                    return True
                continue
            if len(f) < 2 and not f.isdigit():
                continue
            # token-boundary match in the normalised text
            if re.search(r"(?<![\w@.\-+])" + re.escape(f) + r"(?![\w@.\-+])", nt):
                return True
        return False


@dataclass
class Ledger:
    atoms: List[Atom] = field(default_factory=list)

    @classmethod
    def from_messages(cls, messages: Sequence[Any]) -> "Ledger":
        atoms: List[Atom] = []
        n_user = n_tool = n_sys = 0
        for i, m in enumerate(messages):
            role = m.get("role") if isinstance(m, dict) else getattr(m, "role", None)
            if role == "user":
                atoms.append(Atom(f"user:{n_user}", "user", LABEL["TRUSTED"], True, _text_of(m), i)); n_user += 1
            elif role == "system":
                atoms.append(Atom(f"system:{n_sys}", "system", LABEL["TRUSTED"], True, _text_of(m), i)); n_sys += 1
            elif role == "tool":
                tc = m.get("tool_call") if isinstance(m, dict) else getattr(m, "tool_call", None)
                tname = getattr(tc, "function", None) if tc is not None else None
                if not isinstance(tname, str):
                    tname = getattr(tname, "name", None)
                atoms.append(Atom(f"tool:{n_tool}", "tool", LABEL["MEDIUM"], True, _text_of(m), i, tool_name=tname)); n_tool += 1
            # assistant messages are model assertions: not atoms
        return cls(atoms)

    def binders(self, value: Any) -> List[Atom]:
        return [a for a in self.atoms if a.names(value)]

    def tool_atoms(self) -> List[Atom]:
        return [a for a in self.atoms if a.channel == "tool"]

    def best_label(self, value: Any) -> int:
        """Highest label of any atom naming the value; -1 if model-originated."""
        bs = self.binders(value)
        return max((a.label for a in bs), default=-1)
