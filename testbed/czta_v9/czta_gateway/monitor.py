"""Build the I1–I4 reference monitor from one decision request."""
from __future__ import annotations

from .dei_monitor import Belief, DEIMonitor, Evidence, Label, Policy

PROTECTED = {"delete", "send", "share", "book"}


def make_policy(arm: str) -> Policy:
    beta = {}
    if arm == "A2":
        beta = {
            "delete": {"file_id": Label.TRUSTED},
            "send": {"recipient": Label.TRUSTED},
            "share": {"recipient": Label.TRUSTED},
            "book": {"target": Label.TRUSTED},
        }
    return Policy(
        ell_min=Label.MEDIUM,
        protected_classes=set(PROTECTED),
        ell_req={name: Label.TRUSTED for name in PROTECTED},
        tau={name: 0.45 for name in PROTECTED},
        authorized_endorsements=set(),
        beta=beta,
    )


def monitor_from_payload(payload: dict, arm: str) -> DEIMonitor:
    monitor = DEIMonitor(make_policy(arm))
    for item in payload.get("evidence", []):
        monitor.ingest_evidence(Evidence(
            eid=item["eid"],
            payload=item["payload"],
            label=Label[item["label"]],
            not_before=float(item["not_before"]),
            not_after=float(item["not_after"]),
            signature=item.get("signature"),
        ))
    for item in payload.get("beliefs", []):
        result = monitor.update_belief(Belief(
            bid=item["bid"],
            label=Label[item["label"]],
            deps=set(item.get("deps", [])),
            endorsed_by=list(item.get("endorsed_by", [])),
            vals={str(v) for v in item.get("vals", [])},
        ))
        if result.verdict.name == "BLOCK":
            raise ValueError(f"belief update blocked at {result.invariant}: {result.reason}")
    return monitor
