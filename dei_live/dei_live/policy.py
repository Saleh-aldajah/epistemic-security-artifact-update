"""
policy.py — the deployed policy objects (Definition 1) for the four AgentDojo
v1.2 suites, in one place so they can be frozen, hashed and deposited.

  C_prot        protected tool -> action class
  beta          action class -> {bound slot: ell_beta}   (I4)
  ell_req       action class -> required support label    (I3)
  tau           action class -> support threshold         (I3)
  ell_min       floor for evidential roots                 (I1)
  irreversible  classes the gate audits                    (Alg. 2)

Design rule for beta (registered): a target that LEAVES the trust boundary
(an e-mail recipient, a money recipient, a Slack user or channel, a URL, a
shared-with address, an amount) must be named by a TRUSTED atom (the user's
own instruction); an INTERNAL handle that the user can only designate
indirectly (an e-mail/file/event id, a hotel/restaurant/company name that
tools enumerate) must be named by some attested atom (MEDIUM suffices), which
excludes model-invented handles but not injected ones. Free text (subjects,
bodies, descriptions) and dates/times are not bound.

Everything here is data; `policy_json()` is what gets hashed into the deposit.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict

from .ledger import LABEL

T, M = "TRUSTED", "MEDIUM"

# tool -> action class (C_prot); tools not listed are unprotected
PROTECTED: Dict[str, str] = {
    # workspace (+ travel shares send_email / calendar tools)
    "send_email": "send",
    "delete_email": "delete",
    "delete_file": "delete",
    "share_file": "share",
    "create_calendar_event": "write",
    "add_calendar_event_participants": "write",
    "cancel_calendar_event": "write",
    "reschedule_calendar_event": "write",
    "append_to_file": "write",
    "create_file": "write",
    # banking
    "send_money": "send",
    "schedule_transaction": "send",
    "update_scheduled_transaction": "write",
    "update_password": "write",
    "update_user_info": "write",
    # slack
    "send_direct_message": "send",
    "send_channel_message": "send",
    "add_user_to_channel": "write",
    "invite_user_to_slack": "write",
    "remove_user_from_slack": "delete",
    "post_webpage": "write",
    # travel
    "reserve_hotel": "book",
    "reserve_car_rental": "book",
    "reserve_restaurant": "book",
}

# per-tool bound slots with ell_beta (I4). Keyed by tool because the same
# class has different slot names in different tools.
BETA: Dict[str, Dict[str, str]] = {
    "send_email": {"recipients": T, "cc": T, "bcc": T, "attachments": M},
    "delete_email": {"email_id": M},
    "delete_file": {"file_id": M},
    "share_file": {"email": T, "file_id": M},
    "create_calendar_event": {"participants": T},
    "add_calendar_event_participants": {"participants": T, "event_id": M},
    "cancel_calendar_event": {"event_id": M},
    "reschedule_calendar_event": {"event_id": M},
    "append_to_file": {"file_id": M},
    "create_file": {},
    "send_money": {"recipient": T, "amount": T},
    "schedule_transaction": {"recipient": T, "amount": T},
    "update_scheduled_transaction": {"id": M, "recipient": T, "amount": T},
    "update_password": {"password": T},
    "update_user_info": {"first_name": T, "last_name": T, "street": T, "city": T},
    "send_direct_message": {"recipient": T},
    "send_channel_message": {"channel": T},
    "add_user_to_channel": {"user": T, "channel": T},
    "invite_user_to_slack": {"user": T, "user_email": T},
    "remove_user_from_slack": {"user": T},
    "post_webpage": {"url": T},
    "reserve_hotel": {"hotel": M},
    "reserve_car_rental": {"company": M},
    "reserve_restaurant": {"restaurant": M},
}

ELL_REQ: Dict[str, str] = {"send": T, "delete": T, "share": T, "write": T, "book": T}
TAU: Dict[str, float] = {"send": 0.45, "delete": 0.45, "share": 0.45, "write": 0.45, "book": 0.45}
ELL_MIN = M
IRREVERSIBLE = {"send", "delete", "share", "book"}   # the gate audits these classes
# slots whose values are free text / temporal and never enter support extraction
FREE_TEXT_SLOTS = {"subject", "body", "content", "description", "title", "query",
                   "start_time", "end_time", "new_start_time", "new_end_time",
                   "start_day", "end_day", "date", "permission", "recurring"}
SUPPORT_MAX_LEN = 80   # longer argument values are treated as free text

# Directive-root support (the registered "citation contract", checked
# mechanically): a TRUSTED user atom supports action class c iff it expresses
# c with one of these verbs. The user's instruction then enters support(a)
# at TRUSTED for I3; I4 still binds the targets.
DIRECTIVE_LEXICON: Dict[str, tuple] = {
    "send":   ("send", "email", "e-mail", "mail", "message", "dm", "forward", "reply", "transfer",
               "pay", "wire", "notify", "text", "remind", "tell", "let .* know", "ping"),
    "delete": ("delete", "remove", "erase", "trash", "clear", "discard", "get rid"),
    "share":  ("share", "give .* access", "grant", "allow .* to see", "send .* the file"),
    "write":  ("create", "add", "schedule", "reschedule", "update", "change", "set", "append",
               "write", "invite", "post", "cancel", "rename", "edit", "move", "modify", "put",
               "make", "note", "save", "record", "book", "reserve", "publish"),
    "book":   ("book", "reserve", "reservation", "booking", "get me a table", "rent"),
}


def policy_json(tau_override: float | None = None,
                lbeta_override: Dict[str, str] | None = None) -> str:
    """Canonical JSON of the policy objects (the thing that gets hashed)."""
    beta = {t: dict(s) for t, s in BETA.items()}
    if lbeta_override:
        for t, s in beta.items():
            for slot in s:
                if slot in lbeta_override:
                    s[slot] = lbeta_override[slot]
    tau = dict(TAU)
    if tau_override is not None:
        tau = {k: tau_override for k in tau}
    obj = {"lambda": {"user": "TRUSTED", "system": "TRUSTED", "tool": "MEDIUM", "model": "UNTRUSTED"},
           "ell_min": ELL_MIN, "C_prot": PROTECTED, "beta": beta, "ell_req": ELL_REQ, "tau": tau,
           "irreversible": sorted(IRREVERSIBLE), "free_text_slots": sorted(FREE_TEXT_SLOTS),
           "S": "sum(w)/(1+sum(w)) over attested cited atoms with label >= ell_req, w=1",
           "pi": "no endorsement authority in this domain: no label is ever raised after ingress",
           "support": "cited support of an action = atoms naming at least one short argument value, "
                      "plus user atoms whose text expresses the action class (DIRECTIVE_LEXICON)",
           "directive_lexicon": {k: list(v) for k, v in DIRECTIVE_LEXICON.items()},
           "gate": {"delta2": "cited tool atoms below ell_req that are not the sole binder of any bound slot (OBSERVED, not enforced)",
                    "delta3": "tool atoms not in support(a) (ENFORCED: a flip quarantines)", "recommit_temperature": 0.0,
                    "flip": "canonical action differs, no action, or re-commitment error (conservative)",
                    "rationale": "at atom granularity delta2 cannot separate dependence on needed MEDIUM data from a co-located plant; its flips are reported as the resolution limit"}}
    return json.dumps(obj, sort_keys=True, indent=1)


def policy_hash() -> str:
    return hashlib.sha256(policy_json().encode()).hexdigest()


def lbl(name: str) -> int:
    return LABEL[name]
