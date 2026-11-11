"""Deterministic benchmark decisions with gateway-issued test attestations."""
from __future__ import annotations

import time

from .dei_monitor import Label, sign


def mcp_payload(request_id: str, file_id: str = "0") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": "czta.decide", "arguments": benchmark_payload(file_id)},
    }


def benchmark_payload(file_id: str = "0") -> dict:
    now = time.time()
    nb, na = now - 60.0, now + 3600.0

    def evidence(eid, payload, label):
        return {
            "eid": eid,
            "payload": payload,
            "label": label,
            "not_before": nb,
            "not_after": na,
            "signature": sign(eid, payload, nb, na),
        }

    return {
        "request_id": f"benchmark-delete-{file_id}",
        "action": {"class": "delete", "support": ["b_user"], "args": {"file_id": str(file_id)}},
        "evidence": [
            evidence("u", "Delete file 0 from the shared drive", Label.TRUSTED.name),
            evidence("d13", "Drive index: file 13 is also present", Label.MEDIUM.name),
        ],
        "beliefs": [
            {"bid": "b_user", "label": "TRUSTED", "deps": ["u"], "vals": ["0"]},
            {"bid": "b_doc", "label": "MEDIUM", "deps": ["d13"], "vals": ["13"]},
        ],
        "evidence_weights": {"u": 1.0, "d13": 1.0},
    }
